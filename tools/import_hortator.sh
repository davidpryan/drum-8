#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-only
# Hortator's drum model sources into app/dsp/hort/, as they are there but for the two lines noted below.
#   tools/import_hortator.sh PATH/TO/hortator      (a checkout of github.com/DeadActive/hortator)
# Then: tools/gen_hort_models.py (the kit's tables of them, app/dsp/hort_models.inc) and tools/gen_hort_presets.py
# (its factory presets, app/dsp/hort_presets.inc).
# The files: Felucca's dsp.c; Hortator's dm_dsp.c and dm_state.h; phys_dsp.c (DaisySP's modal resonator, MIT); every
# model but SAMPL (dm_sample.c: the kit has its own sample model) and ACID (dm_acid.c: it needs a gate and a glide).
# Changed: `__attribute__((section(".pool")))` becomes HORT_POOL (dsp/hort.c: nothing on the host, where Mach-O has
# no such section), in dm_dsp.c and dm_memb.c.
set -eu
SRC="$1/firmware/src"
DST="$(dirname "$0")/../app/dsp/hort"
mkdir -p "$DST"
for f in dsp.c dm_dsp.c dm_state.h phys_dsp.c dm_kick.c dm_snare.c dm_metal.c dm_perc.c dm_memb.c dm_fm.c dm_ktrx.c \
         dm_sdtrx.c dm_xttrx.c dm_trxn.c dm_rstrx.c dm_trxm.c dm_trxcb.c dm_cltrx.c dm_b2trx.c dm_bdefm.c dm_efmn.c \
         dm_efmm.c; do
    sed 's/__attribute__((section(".pool")))/HORT_POOL/' "$SRC/$f" > "$DST/$f"
done
# Grids' drum map (Mutable Instruments, GPL-3.0-or-later): the nodes app/gen_grids.h reads
cp "$SRC/grids_tables.h" "$DST/grids_tables.h"
# its factory presets (tools/gen_hort_presets.py reads them)
cp "$1/tools/presets.json" "$(dirname "$0")/hort_presets.json"
git -C "$1" rev-parse HEAD > "$DST/UPSTREAM"
