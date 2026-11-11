# Plan: Grids as a perform option

Status: a plan. Nothing here is built. What is built is the GRIDS generator that writes to the pattern
(`app/ui.c` `act_grids`, `app/gen_grids.h`).

## What it would be

Today GRIDS writes a kick, a snare and a hat lane into the pattern once, and you edit the result. As a perform option
it plays instead of being written: while it is on, the kit's kick, snare and hat lanes come from the drum map at
X, Y and FILL as the sequencer runs, and turning those three knobs changes the beat while it plays. Letting go gives
the written pattern back. This is how Hortator uses Grids (a track's pattern source is a Grids lane) and what the
Eurorack module does.

## How it should feel

- **A throw, not a mode.** LOOM-8 already has throws: momentary effects held from the keys and recorded on the
  THROW track if you like (`app/seq/seq.h` `PX_*`: mute, stutter, repeat, echo and so on). GRIDS becomes one more:
  held, the kit plays the map; released, its pattern. Double-tap to latch, as the other firmwares' punch-ins do.
- **Three knobs while it is held:** X, Y and FILL on knobs 1 to 3, CHAOS on knob 4. The kit grid shows what is playing
  as hollow cells over the written pattern, so you see both.
- **"Keep" writes it.** While it is on, SELECT writes what is playing into the pattern (the generator that exists
  today, with the knobs' values), so a beat you find by turning can be kept and edited.
- **Which lanes:** the kit's first three keys, as the generator. A later step: three picks in the kit's list.

## What changes in the code

1. **The sequencer asks before it fires a kit step.** A kit step's hits go out through `emit_drum`
   (`app/seq/seq.c`). When GRIDS is on for the track, the three lanes' hits for the step come from `grids_hit`
   instead of the step's bits; the other eight lanes, the step's velocity, tricks, chance and locks are untouched.
   The call is a table read and three multiplies a lane: cheap enough for the audio interrupt, where the
   sequencer runs.
2. **State the interrupt can read.** X, Y, FILL, CHAOS and an on bit per kit track, written by the UI and read by
   the sequencer, as the scene's kit mutes are today (`seq_t.kmute`: a `volatile` word a track). About six bytes a
   kit track.
3. **Chaos and accents, which the generator leaves out.** Chaos needs Grids' random generator stepped once a bar
   (Hortator's `grids_step` shows the order). Accents need a level a hit: a kit step has one velocity for all its
   sounds, so an accent would be sent as the hit's velocity at `emit_drum`, not stored.
4. **The thirty-second notes.** The map has 32 steps a bar and the grid 16. The generator writes the even ones. Live,
   the odd ones could play as a ratchet on the step before, which is where the map's hat rolls are.
5. **The throw itself.** A new `PX_GRIDS` beside the others: its key on the throws page, its cell on the THROW track
   ("GRD"), its place in the momentary and latched logic, and its knobs on the page while held.
6. **Saving.** Held and gone needs nothing saved. Latched across a save needs X, Y, FILL, CHAOS and the on bit in
   the project: a new project format number and a migration in `app/project.c`, as each earlier format added.

## Order of work

1. The sequencer hook and its state, switched from a debug command in the simulator; a scenario that checks the
   hits that go out against `grids_hit`.
2. The throw: key, cell, hold and latch, the three knobs.
3. The hollow cells on the kit grid, and "keep".
4. Chaos, accents as velocity, the thirty-seconds as ratchets.
5. Saving a latched GRIDS in the project.

Steps 1 to 3 are the feature. 4 and 5 can wait.

## Costs and risks

- **Flash:** the map's table is already in (about 2.4 KB, for the generator). The hook, the throw and the drawing are
  code only; the image has about 11 KB free.
- **RAM:** about 50 bytes. The pool has about 800 bytes above the margin the build insists on.
- **Timing:** the hook runs in the audio interrupt on every kit step. It must not call anything that waits or
  allocates; `grids_level` does neither.
- **Scenes keep sound mutes for the first four kits only** (`NKITM` 4, from LOOM-8's three kits). With eight kits
  that is already short, and a per-kit GRIDS state would want the same widening.
- **The tests in `tests/parked/`** include the ones that exercised throws on synth tracks; the throw's new tests
  should be written for kits from the start.
