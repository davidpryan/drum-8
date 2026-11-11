/* SPDX-License-Identifier: GPL-3.0-only */
/* Hortator's drum models in the kit (dsp/hort.c): each a file of Hortator's (github.com/DeadActive/hortator,
 * firmware/src/dm_*.c, GPL-3.0-only, 2026 DEADACTIVE; on Felucca, Copyright (C) 2026 Leo Kuroshita), unchanged in
 * dsp/hort/, behind the little of Hortator's voice and track they read. Fixed point, mono, 44.1 kHz, as they are
 * there; the kit takes their output as floats. A hit plays in one of NHORT slots every kit shares (drumline.c
 * hort_own, as the 909 models' d9_slot). */
#pragma once
#include <stdint.h>

#define NHORT 4                       /* hits sounding at once, every kit together (a fifth takes the oldest's) */
enum { HM_BDTRX, NHM };               /* the models ported: BDTRX (dm_ktrx.c), the measured digital sine kick */

/* a hit in slot s: the model's eight knobs as Hortator has them (kn[0] TUNE in semitones, -24..24; the rest 0..127),
 * the velocity 1..127, the note's offset in semitones (Hortator's step note: +-24), a seed for its noise */
void hort_start(int s, int model, const int16_t kn[8], int vel, int semi, uint32_t seed);
/* m samples of slot s into t (1.0 = Hortator's full scale); 0 once the hit has ended (t is then silent) */
int hort_render(int s, float *t, int m);
