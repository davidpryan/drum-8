/* SPDX-License-Identifier: GPL-3.0-or-later
 * Copyright 2012 Emilie Gillet (Mutable Instruments Grids: grids/pattern_generator.cc)
 * C port for the FM-1 drum firmware: 2026 DEADACTIVE (Hortator's firmware/src/grids.c: grids_byte, grids_mix,
 * grids_level, as they are there) */
/* Grids' drum map for WARP-8's GRIDS generator (ui.c act_grids): the level (0..255) of an instrument (0 kick,
 * 1 snare, 2 hats) at one of its 32 steps, between the four nodes around a place on the map. A hit where the level is
 * above what the fill leaves. The map's steps are 1/32 notes: WARP-8 writes its sixteenths, the even ones. No chaos
 * and no accents here: the result is written to the pattern, to be edited. */
#pragma once
#include <stdint.h>
#include "dsp/hort/grids_tables.h"

static const uint8_t GRIDS_MAP[5][5] = {         /* drum_map[x][y]: node numbers */
    {10, 8, 0, 9, 11}, {15, 7, 13, 12, 6}, {18, 14, 4, 5, 3}, {23, 16, 21, 1, 2}, {24, 19, 17, 20, 22},
};
static uint32_t grids_byte(int32_t v) { v = v < 0 ? 0 : v > 127 ? 127 : v; return (uint32_t)v * 2u + ((uint32_t)v >> 6); }
static uint32_t grids_mix(uint32_t a, uint32_t b, uint32_t bal) { return (a * (255u - bal) + b * bal) >> 8; }   /* U8Mix */
/* ReadDrumMap: the level (0..255) of channel ch at step, between the four nodes around x, y (bytes) */
static uint32_t grids_level(uint32_t step, uint32_t ch, uint32_t x, uint32_t y)
{
    uint32_t i = x >> 6, j = y >> 6, off = ch * 32u + (step & 31u), xb = (x << 2) & 255u, yb = (y << 2) & 255u;
    const uint8_t *a = GRIDS_NODE[GRIDS_MAP[i][j]], *b = GRIDS_NODE[GRIDS_MAP[i + 1u][j]];
    const uint8_t *c = GRIDS_NODE[GRIDS_MAP[i][j + 1u]], *d = GRIDS_NODE[GRIDS_MAP[i + 1u][j + 1u]];
    (void)GRIDS_EUCLID;                              /* (its Euclidean table: not used, WARP-8's EUCLID is its own) */
    return grids_mix(grids_mix(a[off], b[off], xb), grids_mix(c[off], d[off], xb), yb);
}
/* a hit of channel ch at sixteenth s16, at x, y and fill (each a knob, 0..127) */
static int grids_hit(int s16, int ch, int x, int y, int fill)
{
    return grids_level((uint32_t)s16 * 2u, (uint32_t)ch, grids_byte(x), grids_byte(y)) > (~grids_byte(fill) & 255u);
}
