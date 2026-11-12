# WARP-8: playing the kit

This is the manual for what WARP-8 does differently from LOOM-8: the kit, its keys and its held buttons. The sample
track, the slice track, the effects, saving and everything else not described here work as in `MANUAL.md`, which is
still LOOM-8's.

Every screen here was drawn by the firmware in the simulator. WARP-8 has not yet been run on an FM-1.

## The one rule

With the kit selected:

- **A black key is a drum.** A tap picks it. Stopped, you hear it; while the pattern plays it is picked silently.
- **A white key is a step** of the picked drum, in the bar shown. A tap puts the drum on the step or takes it off.
- **Hold something and the knobs are its.** A step held: the step's. A drum held: its lane's. A button held: that
  button's keys and knobs, drawn on the screen while you hold.

This holds on every page of the kit. The exceptions are the Throws page, the shared LFO page (white keys pick the
sound it moves), the master and setup pages (the keys play), and the Song page (white keys add scenes to the song).

OCT− and OCT+ show the previous and next bar of the pattern. With a step held they nudge it.

## HOME: the whole pattern

<img src="img/warp-home.png" width="240" alt="HOME on the kit: eleven rows of sixteen steps, the picked drum brighter, each drum's level at the right" title="HOME">

Eleven rows, one per drum, sixteen steps at a time. The picked drum is brighter; its level is the bar at the right.

| Control | Does |
|---|---|
| Knob 1 | Tempo (HOME held: fine) |
| Knob 2 | Length of the pattern, for every drum |
| Knob 3 | Swing |
| Knob 4, PRESETS | The kit |
| ALGORITHM | The drum, silently |
| White keys | Steps of the picked drum |
| Black keys | Pick a drum; held, its lane (below) |

Press HOME again for the Song.

## SEQ: Steps, Bar, Generate

<img src="img/warp-steps.png" width="240" alt="Steps: the kick's sixteen steps as bars of velocity, a chance bar, an F for fill and ratchet ticks under them, a red dot on a locked step, the other drums as thin lines" title="Steps">

**Steps** shows the picked drum alone. Each step is a bar as tall as its velocity. Under a step:

- a short bar: its chance, as a share of the width. **A**: an A:B cycle. **F**: only in a fill. **N**: not in a fill.
- small ticks: its ratchets. A dot: another trick.
- a red dot at the top: the step holds locks.

The other ten drums run as thin lines beneath, so you can see where they fall.

The four knobs are the picked drum's own, the same four as EDIT's first page. For nearly every model that is pitch,
length and its two main tone controls (`MACROS.md` lists all 73). PRESETS changes the pattern.

**Bar**: knob 1 quantise, knob 2 note length, knob 3 the steps' scale, knob 4 the lock shape.

**Generate**: as before. The grid previews what it would write; SEL writes it.

### A step held

<img src="img/warp-step-held.png" width="240" alt="Step 9 held: the knobs read velocity, chance 60%, ratchet and nudge" title="A step held">

| Knob | Does |
|---|---|
| 1 | Velocity |
| 2 | Chance: always, 1 to 99%, then the A:B cycles, then fill and no fill |
| 3 | Ratchets, 1 to 9 hits in the step, then random |
| 4 | Nudge, earlier or later |

Turn SELECT while holding for the step's other knobs: length on knob 2 and pitch in semitones on knob 4. Turn it
again to come back.

<img src="img/warp-step-alt.png" width="240" alt="A step held after SELECT: the knobs read velocity, length, chance and pitch" title="The other knobs">

Press ARP while holding for the full list of tricks. Press EDIT, ENV, FX or LFO while holding to lock that page's
knobs on the step. Hold several steps and they change together. HOME + REC undoes.

A ratchet is a multiply trick that knob 3 puts on and takes off for you. If both of the step's tricks are already
something else, the screen says so and nothing changes.

### A drum held

Hold a black key on HOME or Steps:

| Knob | Does |
|---|---|
| 1 | Hits: that many, spread evenly |
| 2 | Rotate |
| 3 | Mutate |
| 4 | The drum's own length |

## EDIT, ENV, FX, LFO: the sound

These pages are the picked drum's, as before. What is new: the white keys are its steps here too. Tap one to write
it. Hold one and turn a knob to lock that knob for that step.

On the two effect pages, Mix and ARP's pages, where a step has nothing to lock, a held step's knobs are its velocity,
chance, ratchets and nudge.

**EDIT held:** turn a knob of the drum and it turns that knob on all eleven drums, each within its own range.
HOME + REC takes it back.

**RANDOM SOUND** in the drum's list (SEL on EDIT) puts another sound of its type on it.

## GLO held: mutes and fill

<img src="img/warp-glo-held.png" width="240" alt="GLO held: the keys drawn, the muted drum dark, K S L under the track keys, C and F under clear and fill" title="GLO held">

From any page, without leaving it:

| Key | Does |
|---|---|
| Black keys | Mute or unmute a drum. Held on: that drum alone, until you let go |
| White 1, 2, 3 | Mute the kit, the sample track, the slice track |
| White 15 | Clear every mute |
| White 16 | A fill while held: steps whose chance is "fill" play, "no fill" rest |
| Knob 1 | Mutes land at once, or at the next bar line |

A mute waiting for the bar blinks on its key. Stopping applies it.

## HOME held: scenes

<img src="img/warp-home-held.png" width="240" alt="HOME held: SCENES 1-16, the playing scene's key lit" title="HOME held">

From any page of the kit, the white keys are the scenes. A scene is a pattern for each track and the mutes.

- Tap a key: that scene at the next bar. Tap it again while it waits: now.
- An empty key makes a copy of the scene playing.
- Hold a key to be asked to clear its scene.
- OCT− and OCT+ with HOME held: scenes 1 to 16, or 17 to 32.

HOME held is also LOOM-8's shift: REC undoes, PLAY redoes, ALGORITHM picks the track, knob 1 is fine tempo.

## FX held: throws

<img src="img/warp-fx-held.png" width="240" alt="FX held: the Throws page, stutter lit on its key" title="FX held">

From any page of the kit, hold FX and the keys are the throws, as on the Throws page: mute, stutter, repeat, echo,
build, floor, jumble on the white keys, warble, pan, octave, chop, ring on the black. The lower octave works on the
drums. Let go of FX and you are back on your page with nothing left on, unless LATCH is on.

A tap of FX still opens its pages.

### GRIDS

<img src="img/warp-grids.png" width="240" alt="GRIDS on: the fifteenth white key lit, the knobs X, Y and FILL" title="GRIDS">

The fifteenth white key on the Throws page (so: FX held + that key) is GRIDS. While it is held, the kit's first three
drums play from the drum map and not from their steps. The other drums keep their steps.

| Control | Does |
|---|---|
| Knob 1, 2 | X and Y: where on the map |
| Knob 3 | FILL: how busy |
| SEL | Keep it: what is playing is written into the pattern |

With LATCH on, a press turns it on and the next turns it off. X, Y and FILL are the same ones Generate's GRIDS uses.

## What changed from 0.5

| 0.5 | Now |
|---|---|
| HOME held + keys: mutes and fill | GLO held + keys |
| HOME: white keys are scenes | HOME: white keys are steps; scenes are HOME held |
| HOME: a black key mutes a drum | It picks the drum |
| Steps: a grid of eleven lanes | The picked drum's lane; the grid is HOME's |
| Steps: knobs are pattern, length, scale, groove | The drum's four knobs. Pattern: PRESETS. Length, swing: HOME. Scale: Bar |
| Held step: velocity, length, chance, pitch | Velocity, chance, ratchets, nudge; SELECT for length and pitch |
| Mix with the kit selected: black keys mute and solo tracks | They pick drums. From another track they are the tracks, as before |
| Throws: on their page | Also FX held, from anywhere |

## Not built

- Chaos, accents and the map's thirty-second notes in GRIDS; GRIDS recorded on the THROW track; the hollow cells
  that would show the map over the written pattern.
- Rolls of one drum, knobs that spring back in the FX layer, kit morph, more than one level of undo, kits as text.
