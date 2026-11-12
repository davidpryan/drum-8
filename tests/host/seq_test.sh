#!/bin/sh
# SPDX-License-Identifier: MPL-2.0
# LOOM-8 sequencer tests: build and run tests/host/seq_test.c against seq.c and pattern.c (no libm,
# no synth: the sequencer only needs synth.h's enums).
#   sh tests/host/seq_test.sh
set -eu
cd "$(dirname "$0")/../.."
CC="${CC:-cc}"
mkdir -p build/host
$CC -O2 -ffp-contract=off -std=c99 -Wall -Wextra -Wdouble-promotion -Werror -DPLAT_HOST -DSEQ_LOOM_THROWS \
    -Iapp -Iapp/seq -Iapp/dsp -Ibase/include \
    -o build/host/seq_test tests/host/seq_test.c app/seq/seq.c app/seq/pattern.c
build/host/seq_test
# WARP-8's own: the same sequencer as the firmware builds it (no SEQ_LOOM_THROWS: one group of throws, the FX sequence)
$CC -O2 -ffp-contract=off -std=c99 -Wall -Wextra -Wdouble-promotion -Werror -Wno-unused-function -DPLAT_HOST \
    -Iapp -Iapp/seq -Iapp/dsp -Ibase/include \
    -o build/host/seq_test_warp tests/host/seq_test.c app/seq/seq.c app/seq/pattern.c
build/host/seq_test_warp
