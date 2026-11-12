# Plan: the FX sequence

Status: a plan, written 2026-11-12 against `77315bf` (after release 0.9). David asked for something like the throws
where effects come in at different points, in different amounts, over a sequence; and then for it to be built as a
fifth kind of sequence beside the kit, the sample track, the slice track and the throws. Section 6 says what was
built.

## 1. What it is

A fifth sequence, **FX**, whose steps hold amounts, not notes. It has eleven lanes, one for each thing an effect
can be given:

| Lane | Black key | What a step's amount sets |
|---|---|---|
| I ALL | 1 | How much of every track goes into FX I on that step |
| I knob 1 to 4 | 2 to 5 | FX I's own four knobs (a delay's time, repeats, tone ...) |
| II ALL | 6 | How much of every track goes into FX II |
| II knob 1 to 4 | 7 to 10 | FX II's own four knobs |
| I > II | 11 | FX I's send into FX II |

A step with an amount holds that amount for the step. A step without one leaves the knob where the hand set it. So
"reverb on everything on the last beat of the bar, at 80%" is four steps of II ALL at 80. With the pattern's SHAPE
(Bar's knob 4) up, the amounts are joined by ramps, so two steps make a swell.

It is like the throws in that it is a pattern of effect moves that plays with the beat and belongs to a scene. It
differs in that a throw is on or off, and this has an amount.

## 2. Why this shape

- **No new project format.** LOOM-8's conductor is a sequenced track with eight patterns and a place in every scene,
  and WARP-8 cannot reach it. The FX sequence is that track (`AUX_BRAIN`). Its steps stay empty of notes, so the
  conductor's own behaviour (chords for followers) never happens.
- **No new engine code.** A step's amount is a parameter lock, and the engine already takes locks on the effect
  tracks (`engine.c s_lock`: `epar` and `aux_changed`). ALL is the effect track's `TP_SEND1` (0.8), read every block.
- **One translation in the sequencer.** A lane on the FX sequence is stored under the conductor's track with a
  parameter id that stands for an effect's parameter (`seq.h fxseq_to`): `TP_E1..E4` are FX I's knobs, `TP_X1..X4`
  FX II's, `TP_SEND1` FX I's ALL, `TP_SEND2` FX II's ALL, `TP_LEVEL` FX I's send into FX II. `lock_put` and
  `lane_forget` (the only two places a lock leaves the sequencer) send it to the effect's track.
- **Every step counts.** On other tracks an unlocked step gives a knob back only if the step plays. The FX sequence
  has no notes, so there every unlocked step gives the knob back (unless SHAPE is up, which holds and ramps).

## 3. The UI

- **Reaching it:** ALGORITHM on SEQ goes kit drums, SMP, SLC, THR, **FX**, and round. HOME held + ALGORITHM too.
- **Steps:** the picked lane's sixteen steps as bars, as tall as their amounts; the other ten lanes thin beneath.
  A black key picks a lane (as it picks a drum on the kit). A white key is a step: a tap gives it the lane's last
  amount, or takes it off. Held, knob 1 is its amount.
- **Knob 1 with nothing held:** the parameter itself, where it rests between the steps.
- **Bar:** the pattern's length is HOME's way no longer (it is not the kit), so Steps' LOOM-8 knobs are kept on Bar:
  quantise, note, groove, SHAPE. PRESETS on SEQ is the pattern, as on every track.
- **Scenes:** a fifth row, FX, with its pattern and playhead. The four knobs stay the first four rows' patterns; the
  FX row's pattern is HOME held + knob 4 with the row selected, or PRESETS on its SEQ page. The fifth black key
  mutes it: muted, no amount is applied.
- **The other buttons** (EDIT, ENV, LFO, ARP) have nothing for this track and go back to the instrument played
  last, as ENV and LFO already do from the throws. FX opens the effects' own pages.

## 4. Order of work

1. The sequencer: the translation, "every step counts", a muted FX sequence applies nothing. A unit test in
   `tests/host/seq_test.c` that a step's amount reaches the effect track and goes back.
2. Selecting it: `sel_trk`, `track_step`, the SEQ chain, its name.
3. Steps: the keys, the held step's knob, the lane view, the LEDs.
4. Scenes: the fifth row and its mute.
5. A scenario, the manual, the sizes.

## 5. Costs and risks

- **Flash:** 3,964 B were free. Letting the conductor's track be selected again gives back some of what the build
  had dropped as unreachable. If it does not fit, the lane view is the part to simplify.
- **Lanes:** each lane used takes one of the project's 96 lock lanes, shared with every drum's locks.
- **The effects run a block behind on the second core**, so an amount lands up to about 6 ms late. A step is 125 ms
  at 120 BPM.
- **An effect's knob moved by the FX sequence** shows its rest value on the effect's own page, not the moving one.
- **Not in this plan:** recording knob moves into the lanes with REC held; amounts for the kit's character, the
  master, or the planned DJ filter; an FX sequence longer or shorter than a lane's own (it has one length).

## 6. What was built (2026-11-12)

All of sections 1 to 4, as planned. `seq.h` `AUX_FXSEQ`, `fxseq_to`; `seq.c` `lock_send`, `FXSEQ()`; `pages.c`
`FXL_ID`, `fxl_val`, `fxl_name`, `fx_lane`, `SCENE_ROW` (five rows); `ui.c` `fxl_step`, the branches in `step_toggle`,
`step_knob`, `steps_knob`, `key_down`, `track_select`, `track_step`. Tests: `t_fxseq` in `tests/host/seq_test.c`
(run by a second build of the sequencer as the firmware has it), `tests/scenarios/fxseq.xy`, `seqchain.xy`.

- Steps' four knobs for it are REST, LENGTH, SCALE and SHAPE (the plan had left length and scale to Bar).
- The track's name is FX. A project made before has the conductor's patterns at a step a beat; an FX pattern with no
  amounts in it is put to sixteenths when the project is read, and a new project starts that way.
- Checked by ear's stand-in: with II ALL on steps 13 to 16 a reverb tail follows the bar; without, silence.
- Cost: 2.2 KB of flash. 1,760 B are left.
- The picked lane is `ui.dsound`, shared with the kit's picked drum: coming back to the kit, the drum picked is the
  lane's number.
