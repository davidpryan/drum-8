/* SPDX-License-Identifier: GPL-3.0-only */
/* Hortator's drum models in the kit (dsp/hort.c): Hortator's own files (github.com/DeadActive/hortator, firmware/src,
 * GPL-3.0-only, 2026 DEADACTIVE; on Felucca, Copyright (C) 2026 Leo Kuroshita), as they are there, in dsp/hort/
 * (tools/import_hortator.sh), behind the little of Hortator's voice and track they read. Fixed point, mono, 44.1 kHz,
 * as they are there; the kit takes their output as floats. A hit plays in one of NHORT slots every kit shares
 * (drumline.c hort_own, as the 909 models' d9_slot). The models: all of Hortator's but SAMPL and ACID, in its order
 * (hort_models.inc, tools/gen_hort_models.py). */
#pragma once
#include <stdint.h>
#include "hort_models.inc"

#define NHORT 8                       /* hits sounding at once, every kit together (a ninth takes the oldest's) */
#define HORT_ENUM(id, name, pad, pad4, trig, rend, n) HM_##id,
enum { HORT_MODELS(HORT_ENUM) NHM };

/* a hit in slot s: the model's eight knobs as the kit has them, 0..127 (hort_models.inc HORT_RANGES: TUNE the knob
 * about 64, a list the knob's stretch), DECAY moved by decay_add steps (13 double it), the velocity 1..127, the
 * note's offset in semitones (Hortator's step note: +-24), a seed for its noise */
void hort_start(int s, int model, const uint8_t kn[8], int decay_add, int vel, int semi, uint32_t seed);
/* m samples of slot s into t (1.0 = Hortator's full scale); 0 once the hit has ended (t is then silent) */
int hort_render(int s, float *t, int m);
