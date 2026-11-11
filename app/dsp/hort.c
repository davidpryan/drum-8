/* SPDX-License-Identifier: GPL-3.0-only
 * Copyright (C) 2026 Leo Kuroshita (@kurogedelic), Hügelton Instruments
 * Drum machine fork: 2026 DEADACTIVE */
/* Hortator's drum models for the kit (hort.h). The models are Hortator's files, unchanged (dsp/hort/dm_*.c, from
 * github.com/DeadActive/hortator at 44c9ad4); this file gives them what they read of Hortator: its voice (core.h
 * dvoice_t, less the sample player's state), the track's eight SOUND knobs and its note (core.h track_t), the shared
 * blocks of Felucca's dsp.c and Hortator's dm_dsp.c they call (copied as they are there, but pow2_q16, which reads
 * its own table here: Felucca's reads the synth's pitch table), and the tables of Felucca's tools/gen_tables.py
 * (tools/gen_hort_tables.py). A new model: its file in dsp/hort/, its state in dm_state_t, a row of MODELS. */
#include "hort.h"

#ifdef PLAT_HOST
#define HORT_POOL
#else
#define HORT_POOL __attribute__((section(".pool")))   /* (the pool: zeroed at start, as .bss) */
#endif

#include "hort_tables.inc"

/* ---- Felucca's dsp.c ---- */
#define VOICE_FS 24000           /* per-voice level: one voice peaks near -6 dBFS before the master */

static inline int32_t mulq15(int32_t a, int32_t b) { return (a * b) >> 15; }
/* a * k / 65536 without 64-bit: a up to 2^31, k Q16 */
static inline int32_t mulq16(int32_t a, uint32_t k)
{
    return (int32_t)(((a >> 16) * (int32_t)k) + (int32_t)(((uint32_t)(a & 0xFFFF) * k) >> 16));
}
static inline int32_t clamp(int32_t v, int32_t lo, int32_t hi) { return v < lo ? lo : v > hi ? hi : v; }

/* sine, linearly interpolated between the 1024 table points (plain lookup: THD -55 dB) */
static inline int32_t sine_i(uint32_t ph)
{
    uint32_t i = ph >> 22;
    int32_t a = SINE[i], b = SINE[(i + 1u) & 1023u];
    return a + (((b - a) * (int32_t)((ph >> 7) & 0x7FFFu)) >> 15);
}

static inline uint32_t noise32(int32_t *st)
{
    uint32_t s = (uint32_t)*st;
    s ^= s << 13;
    s ^= s >> 17;
    s ^= s << 5;
    *st = (int32_t)s;
    return s;
}

/* Trapezoidal SVF (A. Simper), unconditionally stable. Coefficients per
 * block in Q13; signals stay within +-150000 so products fit in 32 bits. */
typedef struct { int32_t a1, a2, a3; } tsvf_t;
static inline void tsvf_coef(tsvf_t *c, int32_t cut, int32_t reso)   /* cut: 0..127 << 8 */
{
    int32_t i, g, den, k = 8192 - reso * 7600 / 127;   /* damping 2.0 .. ~0.15 (Q12) */
    cut = clamp(cut, 0, 127 << 8);
    i = cut >> 8;
    g = SVF_G[i];
    if (i < 127)                                       /* between table points: sweeps without 128 steps */
        g += ((SVF_G[i + 1] - g) * (cut & 255)) >> 8;
    den = 4096 + ((g * (g + k)) >> 12);
    c->a1 = (int32_t)((4096u << 13) / (uint32_t)den);
    c->a2 = (c->a1 * g) >> 12;
    c->a3 = (c->a2 * g) >> 12;
}

/* 2^(i/192), Q16: pitch ratios in 1/16 semitones, d16 >= -3072 (16 octaves down). (Felucca's eng_sample.c takes the
 * octave's fraction from its pitch table; here from POW2_192) */
static uint32_t pow2_q16(int32_t d16)
{
    uint32_t u = (uint32_t)(d16 + 192 * 16), oct = u / 192u;     /* no loop for negative d16 */
    uint32_t r = 65536u + POW2_192[u % 192u];
    return oct >= 16u ? r << (oct - 16u) : r >> (16u - oct);
}

/* ---- Hortator's core.h: the voice (less its sample player's state) and what the models read of a track ---- */
typedef struct { int32_t a1, a2, a3, k; } dsvf_t;   /* dm_dsp.c: SVF with LP / BP / HP */

/* dm_state.h: each model's own state */
typedef struct {                        /* KTRX (dm_ktrx.c) */
    uint32_t inc0, inc_d, inc_f, inc_r, ph_h;
    int32_t e_d, e_t, e_a, e_s, e_h, e_n;
    int32_t punch, sub, th, cgain, nlev;
    uint32_t k_n, d_amp, d_ramp, e_amp, e_r;
    uint8_t first;
} ktrx_t;
typedef union {
    ktrx_t kt;
} dm_state_t;

typedef struct {                 /* one drum voice; the fields' meaning is the model's */
    uint8_t active, vel;
    uint32_t age;                /* hit order (voice stealing) */
    uint32_t t;                  /* samples since the hit (models that need it) */
    uint32_t ph[3], inc[3];      /* oscillator phases and increments */
    int32_t env[3];              /* envelopes, Q24 (1 << 24 = full) */
    uint32_t k[3];               /* their per-sample factors, Q16 (DECAY_K) */
    dsvf_t c[2];                 /* filters */
    int32_t f[4];                /* filter states (2 per filter) */
    int32_t x[4];                /* model scratch: gains, amounts */
    int32_t rng;                 /* noise state, seeded per hit */
    int32_t last;                /* last sample added to the output (declick when cut) */
    dm_state_t ms;               /* M1-C model state (dm_state.h) */
} dvoice_t;

enum { P_E0, P_E1, P_E2, P_E3, P_E4, P_E5, P_E6, P_E7, P_COUNT };   /* the model's: TUNE DECAY TONE CHAR + 4 extras */
typedef struct track {
    int16_t p[P_COUNT];
    int8_t nt;                   /* the playing note's offset from C4: models read TUNE through dm_tune */
} track_t;

/* ---- Hortator's dm_dsp.c ---- */
/* Drum model building blocks, all fixed point. Envelopes are Q24 (ENV1 = full) and fall by a
 * per-sample factor from DECAY_K (Q16; index 0..127 = 5 ms .. 4 s to -60 dB, exponential). */
#define ENV1 (1 << 24)
#define ENV_END (1 << 10)                    /* -84 dB: the voice ends */
#define HZ(f) ((uint32_t)((f) * 97391.548))  /* phase increment of f Hz (2^32 / 44100); constants only */

static inline uint32_t dk(int32_t idx) { return DECAY_K[clamp(idx, 0, 127)]; }
static inline int32_t env_q15(int32_t e) { return e >> 9; }
static inline int32_t vel_gain(const dvoice_t *v) { return v->vel * 258; }       /* 127 -> 32766 */
static inline int32_t dnoise(dvoice_t *v) { return (int32_t)noise32(&v->rng) >> 16; }
static inline void env_step(dvoice_t *v, uint32_t i) { v->env[i] = mulq16(v->env[i], v->k[i]); }

/* inc * 2^(semis / 12); at trigger time only (a divide in pow2_q16, a 64-bit product) */
static uint32_t inc_tune(uint32_t inc, int32_t semis)
{
    return (uint32_t)(((uint64_t)inc * pow2_q16(clamp(semis, -48, 48) * 16)) >> 16);
}

/* TUNE as the models read it: the knob plus the playing step's note offset (a drum: +-24 semitones) */
static inline int32_t dm_tune(const struct track *t) { return t->p[P_E0] + clamp(t->nt, -24, 24); }

/* Simper SVF as tsvf (dsp.c), with the band-pass and high-pass outputs */
static void dsvf_coef(dsvf_t *c, int32_t cut, int32_t reso)       /* cut 0..127 << 8, reso 0..127 */
{
    tsvf_t t;
    tsvf_coef(&t, cut, reso);
    c->a1 = t.a1;
    c->a2 = t.a2;
    c->a3 = t.a3;
    c->k = 8192 - reso * 7600 / 127;          /* damping, Q12, as tsvf_coef */
}

static inline int32_t dsvf_tick(const dsvf_t *c, int32_t in, int32_t *ic1, int32_t *ic2, int32_t *bp, int32_t *hp)
{
    int32_t v3 = in - *ic2;
    int32_t v1 = (c->a1 * *ic1 + c->a2 * v3) >> 13;
    int32_t v2 = *ic2 + ((c->a2 * *ic1 + c->a3 * v3) >> 13);
    *ic1 = clamp(2 * v1 - *ic1, -150000, 150000);
    *ic2 = clamp(2 * v2 - *ic2, -150000, 150000);
    *bp = v1;
    *hp = in - ((c->k * v1) >> 12) - v2;
    return v2;
}

static inline void dm_end(dvoice_t *v)
{
    v->active = 0;
    v->last = 0;
}

/* ---- the models (Hortator's files; each one's DM_*_DEF, its row of Hortator's DMODELS, is not used: the kit has
 * its own knobs' names and defaults, drumline.c) ---- */
#include "hort/dm_ktrx.c"

static const struct {
    void (*trigger)(track_t *t, dvoice_t *v);
    void (*render)(track_t *t, dvoice_t *v, int32_t *out, uint32_t n);
} MODELS[NHM] = {
    [HM_BDTRX] = {ktrx_trigger, ktrx_render},
};

/* ---- the kit's side: a slot is one hit, its track (the knobs as the hit found them) and its voice ---- */
typedef struct {
    track_t t;
    dvoice_t v;
    uint8_t model;
} hslot_t;
static hslot_t hslot[NHORT] HORT_POOL;

void hort_start(int s, int model, const int16_t kn[8], int vel, int semi, uint32_t seed)
{
    hslot_t *h = &hslot[(uint32_t)s % NHORT];
    uint8_t *z = (uint8_t *)h;
    uint32_t i;
    for (i = 0; i < sizeof *h; i++)
        z[i] = 0;
    h->model = (uint8_t)((uint32_t)model % NHM);
    for (i = 0; i < 8; i++)
        h->t.p[P_E0 + i] = kn[i];
    h->t.nt = (int8_t)clamp(semi, -24, 24);
    h->v.active = 1;
    h->v.vel = (uint8_t)clamp(vel, 1, 127);
    h->v.rng = (int32_t)(seed | 1u);                    /* (a xorshift: never 0) */
    MODELS[h->model].trigger(&h->t, &h->v);
}

int hort_render(int s, float *t, int m)
{
    hslot_t *h = &hslot[(uint32_t)s % NHORT];
    int32_t buf[32];
    int i, o;
    for (o = 0; o < m; o += 32) {
        int n = m - o < 32 ? m - o : 32;
        for (i = 0; i < n; i++)
            buf[i] = 0;
        if (h->v.active)                                /* (the models add to their output) */
            MODELS[h->model].render(&h->t, &h->v, buf, (uint32_t)n);
        for (i = 0; i < n; i++)
            t[o + i] = (float)buf[i] * (1.0f / 32768.0f);
    }
    return h->v.active;
}
