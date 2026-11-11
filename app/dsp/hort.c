/* SPDX-License-Identifier: GPL-3.0-only
 * Copyright (C) 2026 Leo Kuroshita (@kurogedelic), Hügelton Instruments
 * Drum machine fork: 2026 DEADACTIVE */
/* Hortator's drum models for the kit (hort.h). The models, their shared blocks (dm_dsp.c, phys_dsp.c) and Felucca's
 * dsp.c are Hortator's files (dsp/hort/, tools/import_hortator.sh: the commit in dsp/hort/UPSTREAM); this file gives
 * them what they read of the rest of Hortator: its voice (core.h dvoice_t, less the sample player's state), a track's
 * eight SOUND knobs, note and declick tail (core.h track_t), the block's size and count, the tables of Felucca's
 * tools/gen_tables.py (tools/gen_hort_tables.py), and pow2_q16 (Felucca's eng_sample.c reads the synth's pitch table
 * for it; here its own). A slot is one of Hortator's tracks with one voice: a track there is what a kit's key is
 * here. */
#include "hort.h"

#ifdef PLAT_HOST
#include <string.h>
#define HORT_POOL
#else
void *memset(void *d, int c, unsigned n);            /* (felucca-bsp chip/libc.c: the device has no string.h) */
void *memcpy(void *d, const void *s, unsigned n);
#define HORT_POOL __attribute__((section(".pool")))   /* (the pool: zeroed at start, as .bss) */
#endif

#include "hort_tables.inc"
#define FS 44100
#define CTL 32                   /* Hortator's block: a render call makes this many at most */
#define NTRK NHORT               /* Hortator's tracks: here the slots (dm_memb.c: a body each) */

/* ---- Hortator's core.h ---- */
typedef struct { int32_t a1, a2, a3, k; } dsvf_t;   /* dm_dsp.c: SVF with LP / BP / HP */
#include "hort/dm_state.h"
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
    int32_t dtail;               /* declick: last output of cut voices, decaying (here: not heard) */
} track_t;
static track_t trk[NTRK] HORT_POOL;

/* ---- Felucca's dsp.c, and pow2_q16 ---- */
#include "hort/dsp.c"
/* 2^(i/192), Q16: pitch ratios in 1/16 semitones, d16 >= -3072 (16 octaves down) */
static uint32_t pow2_q16(int32_t d16)
{
    uint32_t u = (uint32_t)(d16 + 192 * 16), oct = u / 192u;     /* no loop for negative d16 */
    uint32_t r = 65536u + POW2_192[u % 192u];
    return oct >= 16u ? r << (oct - 16u) : r >> (16u - oct);
}

/* ---- Hortator's models (each file's DM_*_DEF, its row of Hortator's DMODELS, is read by tools/gen_hort_models.py,
 * not compiled) ---- */
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-function"   /* (blocks of theirs no model here calls) */
#include "hort/dm_dsp.c"
#include "hort/phys_dsp.c"
#include "hort/dm_kick.c"
#include "hort/dm_snare.c"
#include "hort/dm_metal.c"
#include "hort/dm_perc.c"
#include "hort/dm_memb.c"
#include "hort/dm_fm.c"
#include "hort/dm_ktrx.c"
#include "hort/dm_sdtrx.c"
#include "hort/dm_xttrx.c"
#include "hort/dm_trxn.c"
#include "hort/dm_rstrx.c"
#include "hort/dm_trxm.c"
#include "hort/dm_trxcb.c"
#include "hort/dm_cltrx.c"
#include "hort/dm_b2trx.c"
#include "hort/dm_bdefm.c"
#include "hort/dm_efmn.c"
#include "hort/dm_efmm.c"
#pragma GCC diagnostic pop

#define HORT_ROW(id, name, pad, pad4, trig, rend, n) {trig, rend},
static const struct {
    void (*trigger)(track_t *t, dvoice_t *v);
    void (*render)(track_t *t, dvoice_t *v, int32_t *out, uint32_t n);
} MODELS[NHM] = {HORT_MODELS(HORT_ROW)};
static const int8_t RANGE[NHM][8][2] = {HORT_RANGES};

/* ---- the kit's side: a slot is one hit, its track (trk[s]: the knobs as the hit found them) and its voice. The
 * 808 metal bank is one for every voice of a block in Hortator (dm_metal.c: six squares running on); here each voice
 * renders on its own, so each slot keeps its own phases, put in the bank's place around its render ---- */
typedef struct {
    dvoice_t v;
    uint32_t metal[6];
    uint8_t model;
} hslot_t;
static hslot_t hslot[NHORT] HORT_POOL;
static uint32_t hits;

void hort_start(int s, int model, const uint8_t kn[8], int decay_add, int vel, int semi, uint32_t seed)
{
    hslot_t *h = &hslot[(uint32_t)s % NHORT];
    track_t *t = &trk[(uint32_t)s % NHORT];
    int i;
    h->model = (uint8_t)((uint32_t)model % NHM);
    for (i = 0; i < 8; i++) {
        const int lo = RANGE[h->model][i][0], hi = RANGE[h->model][i][1];
        int k = kn[i] & 127;
        if (i == 1)
            k = clamp(k + decay_add, 0, 127);
        t->p[P_E0 + i] = (int16_t)(lo < 0 ? clamp(k - 64, lo, hi) : hi == 127 ? k : k * (hi + 1) / 128);
    }
    t->nt = (int8_t)clamp(semi, -24, 24);
    t->dtail = 0;
    memset(&h->v, 0, sizeof h->v);                      /* (Hortator's dv_init) */
    h->v.active = 1;
    h->v.vel = (uint8_t)clamp(vel, 1, 127);
    h->v.age = ++hits;
    h->v.rng = (int32_t)(seed | 1u);                    /* (a xorshift: never 0) */
    MODELS[h->model].trigger(t, &h->v);
}

int hort_render(int s, float *out, int m)
{
    hslot_t *h = &hslot[(uint32_t)s % NHORT];
    track_t *t = &trk[(uint32_t)s % NHORT];
    int32_t buf[CTL];
    int i, o;
    for (o = 0; o < m; o += CTL) {
        int n = m - o < CTL ? m - o : CTL;
        for (i = 0; i < n; i++)
            buf[i] = 0;
        if (h->v.active) {                              /* (the models add to their output) */
            memcpy(metal_ph, h->metal, sizeof metal_ph);
            dblock++;                                   /* (a block of this voice's own: the bank made for it) */
            MODELS[h->model].render(t, &h->v, buf, (uint32_t)n);
            memcpy(h->metal, metal_ph, sizeof metal_ph);
        }
        for (i = 0; i < n; i++)
            out[o + i] = (float)buf[i] * (1.0f / 32768.0f);
    }
    return h->v.active;
}
