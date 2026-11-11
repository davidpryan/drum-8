# Parked tests

WARP-8 took LOOM-8's synth engines out of the build (knit, rayon, jacquard, bellows, cane, voile, acid) and starts a
project as eight kits. These scenarios were written for LOOM-8's band of synth tracks and are not run by
`tests/run_tests.sh` until they are rewritten or dropped.

They test engines or presets that are gone: `demo_cmds`, `guard`, `loadmodel`, `osc2fine`, `sub`, `ux_sound`,
`ux_chords`, `projects` (the random band's voice modes), `holdedit` (the engine picker's old range).

They test things WARP-8 still has, on tracks it no longer starts with, and need rewriting for kit or sample tracks:
`ccendless`, `copyempty`, `copypaste`, `edits`, `midicc`, `midiengine`, `slice`.

The unit tests `tests/host/synth_test.sh` and `tests/host/braids_test.sh` are not run either: most of what they
check is the engines that are gone. The voice's filters, envelopes and character stage, which the sample and slice
engines still use, are in `synth_test.c` on a knit voice and need moving to a sample voice.
