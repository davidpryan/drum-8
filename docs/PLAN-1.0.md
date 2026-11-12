# Plan: WARP-8 as a drum machine with one grammar

Status: **phases 0 to 9 and the manual are built** on branch `grammar` (2026-11-11, simulator only; section 8 says
what was built and where it departs from the plan). Written 2026-11-11 from the concept report (https://claude.ai/artifact/7feFvqs3u71XkB77NMY2iQ) after a
pass over the UI against the code at `5d92bf5` (release 0.5). Nothing here is built. Where the concept and this file
differ, this file is right: section 2 lists what the pass changed and why.

The aim in one line: **on the kit, white keys are steps and black keys are drums on every page; holding a step, a
drum or a button turns the knobs and keys into that thing's; nothing that exists today is lost.**

---

## 1. Rules for every agent

Read these before touching anything.

1. **Work only in `~/Dropbox/fm1-warp8`**, on a branch `grammar` cut from `main`. One commit per phase, message in
   the repo's style (a plain sentence saying what the firmware now does). Do not push, publish the site, or cut a
   release; David does that.
2. **`firmware.json` is modified in the working tree and is not ours.** Do not commit, revert or stash it.
3. **One agent at a time in `app/ui.c` and `app/pages.c`.** Almost every phase edits both (5,050 and 6,383 lines).
   Phases run in order. The only work that can run beside a phase is marked "parallel" in section 4.
4. **Build and test** (see the memory note and `BUILDING.md`):
   - `colima start`, then `PYTHON=python3.11 AC79_SDK=~/.jieli/ac79-sdk ./build.sh` (firmware) and `./build.sh --host`
     (simulator).
   - `tests/run_tests.sh` after the package is built. It takes over ten minutes when `emcc` is present: run it in
     the background.
   - `tools/layout_sweep.py` must pass after any drawing change. Lane and key names on screen are capitals.
5. **Everything new is gated by `kit_ui()`** (`pages.c:616`: the kit track selected, not large type). Large type
   and the sample, slice and throw tracks keep LOOM-8's behaviour. Do not change what a key does when `kit_ui()` is
   false.
6. **Every phase adds or extends one scenario in `tests/scenarios/*.xy`** that drives the new behaviour through the
   host (`tap`, `turn`, `tapkey`, `expect`, `said`, `shot`; see `kitflow.xy` for the style, `app/host.c` for the
   commands). Holding a button is `press NAME` ... `release NAME` (as `tools/layout_sweep.py` uses); `spin` turns an
   encoder while one is held. Add a host command in the phase that needs one that does not exist.
7. **Say what the user did.** Each new action calls `say()` with a short title and detail, as its neighbours do, so
   the screen message and the spoken output (`sp_*`) stay complete. Update `leds()` (`ui.c:4223`) in the same phase
   as the keys it lights.
8. **Flash and RAM.** After each phase record the image size and pool headroom in section 6. The app slot is
   581,564 B; 0.4 was 574,560 B; 0.5 has not been measured. If a phase leaves under 2 KB, stop and do phase R
   (reclaim) before going on. `tools/size_fns.py` needs every `-O2` unit listed.
9. **The device has no `string.h`.** `ui.any_btn` means "a button was ever pressed"; use `ui.btn` for "held now".
10. **Never claim hardware behaviour.** Nothing has run on an FM-1. Report what the simulator and tests show.
11. **Stop and ask** when a phase's "decision" line is unanswered, when a test that passed before fails for a
    reason outside your change, or when the behaviour you find in the code differs from what this file says it is.

---

## 2. What the UI pass found

Each row is a problem in the concept as published, checked against the code, and what the plan does instead.

| # | Concept said | What the code or a closer look shows | Plan |
|---|---|---|---|
| U1 | Hold REC = fill | REC held while playing is momentary record, and its knobs are the record settings (`rec_down`, `rec_knob`, `rec_settings`). | Fill stays a held key: white 16 in the GLO layer, moved there with the mutes. |
| U2 | Tap SEL = "yes, print" | SEL already means yes: it confirms a question, picks a list row, writes on Generate, and otherwise opens the page's action list (`button_up` `B_SEL`). HOME is already no and back. SEL held + a knob clears that knob's automation. | Keep all of it. No change to SEL. |
| U3 | Hold SEL = 16 patterns, kit shelf | There are 8 patterns a track (`NPATT`), 32 scenes, a 64-slot song. A scene already is "pattern per track plus mutes", launched from the white keys on HOME at the bar line. | No SEL layer. Scenes move from HOME's white keys to **HOME held + white keys**. No format change, the song still works. The kit shelf is dropped: PRESETS on HOME changes kit. |
| U4 | Mutes on hold GLO (David's choice) | HOME held is LOOM-8's shift (undo, fine tempo, the track, step components). Mutes there crowd it. | As chosen. This also frees HOME held for scenes (U3). |
| U5 | BEAT's knobs are the drum's macros; SELECT turns to tempo | HOME's knobs today are tempo, length, swing, kit. Hiding tempo behind a page turn is a step back, and a page that shows the whole kit should turn whole-kit knobs. | HOME keeps tempo, length, swing, kit. Macros are the knobs on Steps and on EDIT's first page. |
| U6 | Black key = play and select | While playing, a black key on Steps picks the drum without sounding it, on purpose (`key_down`: "no preview over the beat"). Stopped, it sounds. Keys play as a keyboard with SEQ held or while recording. | Keep. The rule is "black key picks the drum; it sounds when stopped". |
| U7 | Hold a step = velocity, chance, ratchet, nudge everywhere | Two things exist: on Steps the held step's knobs are the trig (velocity, length, chance, pitch); on EDIT pages the knobs lock that page's parameters (`kit_edit_steps`, `lock_knob`). | Keep both and name them on screen: the held-step banner reads `STEP n · TRIG` on HOME and Steps, `STEP n · LOCK` on sound pages. The trig knobs are velocity, chance, ratchet, nudge (D2, decided). |
| U8 | Steps = one drum in detail | Steps is already a grid of 11 lanes x 16 (0.2, David's choice), and HOME is a second grid. Once HOME's white keys write steps, the two overlap. | David said yes (2026-11-11): Steps becomes one drum in detail; the grid is HOME's. Phase 6. |
| U9 | GENERATE on ARP, playing live | Generate is SEQ's third page and previews on the grid; SEL writes. The live version is already designed as a throw in `docs/GRIDS-PERFORM.md`. | Generate stays where it is. Live Grids is the `PX_GRIDS` throw from that plan (phase 8). ARP is untouched. |
| U10 | Hold FX = eleven new punch-ins (reverse, tape stop, freeze) and per-drum rolls on white keys | The twelve throws exist (`PX_*`), with keys, latch and recording on the Throws page. Reverse, tape stop and freeze would be new DSP in a full image. White keys as drums breaks the keys rule inside the layer. | Hold FX = the Throws page for as long as it is held (phase 4). No new effects. Per-drum rolls, if built later, go on the **black** keys (phase 10). |
| U11 | Hold ARP = "rolls" of sound or lane | Never specified, and "roll" also meant note repeat. Lane variation exists (a drum held: MUTATE). `do_random_sounds` exists. | No ARP layer. A RANDOM SOUND row in the drum's SEL list (phase 9). |
| U12 | Hold LFO + knob records motion | REC held on a sound page while playing already records the knob (`rec_settings`, `seq_rec_knob`). | Nothing to build. |
| U13 | Sample and slice as lanes 12 and 13 | They are tracks with their own pages, steps that carry a note or a slice, and their own patterns. Folding them into the kit is a rewrite of `kit_ui()`'s premise. | Stay tracks, reached as now (HOME held + ALGORITHM). D3, decided. |
| U14 | A held button draws its map at once | Help cards appear after 900 ms and only when nothing else was pressed (`holds`, `CARD_MS`). A map on every tap would flash. | Layers with keys (GLO, FX, HOME) draw their map after 200 ms held or on the first key, whichever is first. Other buttons keep the 900 ms card. |
| U15 | Morph on HOME K4 | How the second kit state is set was never said. | Last, and only after a short design note is agreed (phase 12). |
| U16 | Saves lost on new flash chips | `base/device/fm1_flash_ok.h` accepts both parts (0x856014, 0xB36014) and has tests. | Not a code task. It stays on the hardware checklist. |
| U17 | Chance, A:B, FILL on one dial | That is how K3 on a held step works today, with `accel()`. | Keep. |
| U18 | White keys still edit the pattern on the live Generate page | You would edit steps you cannot hear. | Gone with U9: the throw shows hollow cells over the written pattern, and SELECT keeps it. |

Small things to hold to while building:

- A step's tap toggles at the release, and only if nothing was edited while it was held (`STEP_TAP_MS` 700). Keep
  that on every page that gains steps.
- Several steps held edit together (`ui.held` is a mask). Keep that too.
- With steps held on Steps, a black key puts that drum on the held steps. That stays; it is why "a drum held" only
  counts when no step is held (`lane_held`).
- The shared LFO page (`P_GLFO`) uses white keys 1-12 to pick the sound it moves, and the master and setup pages
  play the keys. These stay as exceptions; the manual lists them.

---

## 3. The target, page by page (kit selected, normal type)

Keys with nothing held, everywhere except the exceptions above:

- **Black key:** picks the drum (sounds it when stopped). Held past the tap time with no step held: the lane layer.
- **White key:** the step of the picked drum in the bar shown. Tap toggles; held, the knobs are the step's.
- **OCT− / OCT+:** the bar shown (as on Steps today); with a step held, its nudge (as today).

| Button | Tap | Held |
|---|---|---|
| HOME | The pattern: 11 rows. K1 tempo, K2 length, K3 swing, K4 and PRESETS kit, ALGORITHM drum. Twice: Song. Also no and back. | Shift, as today (REC undo, K1 fine tempo, ALGORITHM track). **New:** white keys launch scenes 1-16, OCT pages to 17-32; a long hold captures or clears, as on HOME today. |
| SEQ | Steps, Bar, Generate. Steps' knobs become the drum's macros (phase 5). PRESETS pattern. | As today (keys play, PLAY from the bar, bar jump). |
| EDIT | The drum: macros first (phase 5), then the model's other knobs, key, sends. PRESETS next sound of the type. | **New:** a knob turned moves that parameter on all eleven drums (phase 9), if EDIT held has no job today (check `page_btn_held(B_EDIT)` in `kit_edit_steps`). |
| ENV, LFO | As today. **New:** white keys are steps here too, and a held step locks the page's knobs. | Help card. |
| FX | As today (character, sends, FX I, FX II, Throws). White keys are steps except on Throws. | **New:** the Throws page while held: its keys fire, its knob works, the screen shows it. Release returns. |
| ARP | As today. | Help card. |
| GLO | Mix and the master pages, as today. | **New:** mutes. Black keys mute a drum. White 1-3 mute KIT, SMP, SLC. White 15 clears every mute. White 16 is a fill while held. K1: at once, or at the bar. |
| SEL | Yes; the page's list; writes on Generate. | A knob turned clears its automation (today). |
| REC, PLAY, SAVE | As today. | As today. |

---

## 4. Phases

Each phase lists what to build, where, how to prove it, and what to leave alone. Function names and line numbers
are from `5d92bf5`; find them again by name.

### Phase 0. Baseline (no behaviour change)

- Cut `grammar` from `main`. Build firmware and host. Run the suite.
- Fill the first row of section 6: image size, pool headroom above the build's margin, tests passed.
- Run `tools/layout_sweep.py`; note its result.
- Read `docs/GRIDS-PERFORM.md`, `tests/scenarios/kitflow.xy`, `kitgrid.xy`, `generators.xy`, and in `ui.c`:
  `key_down`, `key_up`, `button_up`, `holds`, `knob_do`, `leds`; in `pages.c`: `kit_ui`, `kit_edit_steps`,
  `lane_held`, `steps_page`, `draw_kit_home`, `kit_grid`.
- **Done when:** numbers are recorded and the suite's pass count matches the last release's (71).

### Phase R. Reclaim flash (only when rule 8 says so)

- Candidates, in order: the pages and list rows that 0.5 cannot reach (tracks 4-8, conductor, weave track:
  `P_PLAYERS*`, `P_WEAVE`, the brain's pages, `weave_*` in `ui.c`); their drawing in `pages.c`; then the dead
  engines' source.
- Remove one group at a time, rebuild, record bytes won, run the suite. Move tests that only exercised removed
  pages to `tests/parked/` with a line in its README.
- Do not change the project format or engine numbers.
- **Done when:** at least 8 KB is free.

### Phase 1. Mutes and fill move to GLO held

- **Build:** in `key_down`, the block under `home_held()` (drum mutes on black keys, track mutes on white 1-3, fill
  on white 16) moves under "GLO held" (`ui.btn >> B_GLO & 1u`), setting `ui.btn_used` for GLO so its release opens
  no page. Add white 15: clear `seq.kmute` for the kit and `seq.mute` for the three tracks, `say("MUTES", "cleared")`.
  `KM_FILL`'s release in `key_up` is unchanged.
- **K1 while GLO is held:** a project setting "mutes at: once / the bar". At the bar, a mute key press is stored and
  applied by the sequencer at the next bar line, the way a cued scene is. Use a reserved project byte (see how
  `proj.rsv[2]` holds `SCENES_AT_END`); no format number change. Show the pending state on the key's LED (dim
  blink) and in the layer map.
- **Remove:** black keys muting on HOME with nothing held (`P_ARRANGE` branch, `kit_sound_mute(trk, b)`). Phase 2
  gives that key its new job; until then it picks the drum.
- **LEDs:** while GLO is held, black keys lit = sounding, dim = muted.
- **Leave alone:** Mix's own keys when `kit_ui()` is false; scenes still store and recall the kit's mutes.
- **Test:** new `tests/scenarios/glomutes.xy`: hold GLO, tap black 3, `expect kmute 8`; white 15 clears; white 16
  held sets fill and a `FILL` step fires; at-the-bar mode applies on the bar line and not before. Update
  `kitflow.xy` where it mutes from HOME.
- **Done when:** both scenarios and the suite pass.

### Phase 2. HOME: white keys are steps, scenes go to HOME held

- **Build:** on `P_ARRANGE` with `kit_ui()`:
  - White key, nothing held: the Steps behaviour (`KM_STEP`, toggle at release, held = the step). Reuse the Steps
    branch of `key_down`/`key_up`; do not copy it. The simplest route is to let `P_ARRANGE` count as a steps page
    for the kit in the key paths (a helper like `kit_steps_here()` that is true for `steps_page(p)` and, with
    `kit_ui()`, for `P_ARRANGE`), then widen it in phase 3.
  - Black key: pick the drum, as on Steps. Held: the lane layer (`lane_held` must accept this page).
  - HOME held + white key: `scene_key(k, ui.scene_pg * 16 + w, ...)` exactly as HOME's white keys call it today,
    including the long hold (`KM_SCENE` in `holds`). Guard: if a step is held, HOME + white stays the step
    components (existing).
  - OCT with HOME held: the scene page. OCT alone on HOME: the bar shown.
- **Knobs on HOME with a step held:** the trig knobs, as on Steps (`step_knob`). With a drum held: `lane_knob`.
- **Draw:** `draw_kit_home` shows the bar in view and its playhead; when HOME is held it shows the scene map
  (phase 4 draws the layer maps; here a one-line strip "SCENE n" is enough).
- **Song page (`P_SONG`):** unchanged; its white keys still insert scenes.
- **Test:** extend `kitflow.xy` (or new `homesteps.xy`): on HOME `tapkey b0`, `tapkey w0`, `expect drumhits`;
  hold a step and turn K1, expect the velocity; hold HOME and tap white 2, expect the scene cued; `scenes.xy` and
  `sceneclear.xy` adapted to the held form.
- **Done when:** a beat can be written, heard and switched between two scenes without leaving HOME.

### Phase 3. White keys are steps on every kit page

- **Build:** widen the helper from phase 2 to the ENV group, the FX group except `P_THROWS`, the LFO group, Mix
  (`P_MIX`), and ARP's pages on a kit. `kit_edit_steps()` already does this for the EDIT group: follow it
  (`ui.lockpg = page + 1`, so a held step locks that page's knobs through `lock_knob`). Where a page's knobs
  cannot be locked (Mix levels, master pages), a held step falls back to the trig knobs.
- **Black keys** on those pages: pick the drum; held = lane layer. On Mix this replaces "tap mutes, hold solos" for
  the kit only; mutes are GLO held (phase 1). Keep solo: GLO held + a black key held past `STEP_TAP_MS` solos that
  drum while held (the `KM_SOLO` pattern in `holds`).
- **Exceptions that stay:** `P_GLFO` (white keys pick the LFO's sound), `P_MASTER*`, `P_SETUP`, `P_STATUS`,
  `P_THROWS`, any open list or question.
- **LEDs:** white keys show the picked drum's steps and the playhead on all these pages.
- **Test:** new `stepsanywhere.xy`: on Envelope, Character and Mix, a white key toggles the step of the picked drum;
  a held step plus a knob writes a lock on Envelope and a velocity on Mix. `pages.xy` and `kitedit.xy` still pass.
- **Done when:** the rule in section 3 holds on every page not listed as an exception.

### Phase 4. Layer maps, and FX held = throws

- **FX held:** while `ui.btn >> B_FX & 1u` on a kit, keys go to `punch_key(k, 1/0)` with `glob` true, the Throws
  page's knob works, and the screen draws the Throws page. Set `btn_used` on the first key or knob so the release
  opens no page. Latching follows the Throws page's setting. With REC on, the throws record as they do there.
- **Layer maps:** for GLO, FX and HOME, replace the 900 ms help card with a map drawn after 200 ms held or at the
  first key (rule U14). A map is the page drawn for that layer: the 27 keys in two rows with a two or three letter
  capital label each, state shown (muted, latched, cued), and the knob strip. One function,
  `draw_layer(int btn)`, in `pages.c`, using the kit grid's cell sizes and the theme's inks.
- **Budget:** this is the phase most likely to cost flash (three maps). Keep labels in one table.
- **Test:** `fxhold.xy`: hold FX, tap the stutter key, `expect` the throw on, release the key, off; release FX, the
  page is the one before. `shot` each map for the layout sweep.
- **Done when:** the three layers each show their keys while held and leave no trace when released.

### Phase 5. Four macros in fixed places

- **Names (D4, decided):** K1 TUNE, K2 DECAY, K3 TONE, K4 BITE. TONE and BITE are whichever two knobs of the model
  matter most; the screen shows the model's own name for them under the fixed position.
- **Parallel work (can run beside phases 1-4, touches no UI file):** a table of the two picks for each of the 73
  models. Hortator's 43: add two columns to `tools/gen_hort_models.py`'s output (`hort_models.inc`), chosen from
  each `DM_*_DEF` row; every Hortator model has TUNE and DECAY already. LOOM-8's 30: a static table beside the
  model definitions in `app/dsp/drumline.c`. Where a model has no tune or no decay, mark the slot empty; the knob
  then does nothing and the screen shows a dash. Deliver the table with a one-line reason per model in
  `docs/MACROS.md` for David to audition and correct.
- **Build:** EDIT's first page (`P_ENGINE`) shows the four macros in that order; the model's remaining knobs follow
  on Engine 2 (and a third page if a model has more than eight). Locks address parameters, not knob positions (checked in
  phase 0: `lock_knob` finds its lane by the parameter `tp_page_param` returns). So do the reorder as a per-model
  permutation inside `tp_page_param` for the kit's Engine pages, and leave every model's parameter slots
  (`TP_DRUM(sound, DP_*)`) where they are. Stored projects, locks and MIDI CC numbers are then unaffected. Do not
  renumber a model's knobs.
- **Steps' knobs** (`steps_knob`) on a kit become the same four macros of the picked drum. What they did moves:
  pattern is PRESETS (already); length and swing are HOME's K2 and K3 (already); the step scale goes to the Bar
  page's list (`A_*` row "STEP SCALE") since Bar's four knobs are taken.
- **Test:** `macros.xy`: for three models of different families, K1 on Steps changes the tune parameter and K2 the
  decay; a held step on EDIT then K3 writes a lock on the TONE parameter; a 0.5 project (fixture) loads with its
  locks on the same parameters as before.
- **Done when:** the same hand movement tunes any drum from Steps and from EDIT.

### Phase 6. Steps as one drum in detail (decided: yes)

- **Build:** `P_STEPS` on a kit draws the picked drum's 16 steps large: a bar per step for velocity; under it the
  chance or condition, the ratchet count, a dot for locks; the other ten drums as thin rows beneath. The 11-lane
  grid remains HOME's. Generate keeps its grid preview.
- **Keys and knobs do not change in this phase**: only the drawing. A drum held still shows its lane's knobs; a
  step held still shows the banner from U7. In large type Steps keeps LOOM-8's cells (rule 5).
- **Test:** `kitgrid.xy` moves its grid checks to HOME; a new `shot` of the detail view with a velocity, a chance,
  a FILL condition, a ratchet and a locked step on screen; layout sweep.
- **Done when:** every per-step value a held step can set is visible on Steps without holding anything.

### Phase 7. The held step's knobs (decided: yes)

- **Build:** on the kit, a held step on HOME and Steps gives K1 velocity, K2 chance (unchanged dial), K3 ratchet,
  K4 nudge. Ratchet writes an `SC_MULTIPLY` trick into the step's first free trick slot and removes it at 1;
  if both slots hold other tricks, say so and do nothing. Nudge is what OCT does on a held step today (keep OCT
  too). Length and pitch remain on the tricks page (ARP on a held step) and as a TUNE lock on EDIT.
- **Test:** `ratchet.xy`: K3 to 3 on a step gives three hits in that step; K3 back to 1 clears the trick.

### Phase 8. Live Grids as a throw

- Follow `docs/GRIDS-PERFORM.md`, steps 1 to 3 of its order of work (the sequencer hook and state, the `PX_GRIDS`
  throw with X, Y, FILL, CHAOS on the knobs while held, hollow cells on the grid and SELECT to keep). It appears in
  the FX layer from phase 4 with no further work. Steps 4 and 5 of that file wait.
- The hook runs in the audio interrupt: no waiting, no allocation.

### Phase 9. Control-all and one drum's random sound

- **Control-all:** with EDIT held on a kit sound page, a knob adds its turn to that parameter on all eleven drums
  (relative, each clamped to its own range). One undo snapshot per hold (`undo_sounds`). First read what EDIT held
  does today (`page_btn_held(B_EDIT)` switches `kit_edit_steps` off, so the keys play); the keys must keep that.
- **Random sound:** a RANDOM SOUND row in the drum's SEL list picks a random preset of the drum's type
  (`HPT_OF`, as PRESETS steps through them), with `undo_sound` first.
- **Test:** `ctlall.xy`.

### Phase 10. Later, each needing a short note agreed first

- **Per-drum rolls:** FX held + a black key held repeats that drum at the Throws page's rate. Needs a per-sound
  target in `engine_punch`. Key pressure for roll level needs `APP_TOUCH` (off today; the lower 20 keys only).
- **Perform knobs that spring back:** K1-K4 in the FX layer on the kit bus filter, crush and the two sends,
  restored at release.
- **Morph:** a second value per macro per drum, a range, and a way to set it. Write `docs/MORPH.md` first.
- **More than one undo level**, if the pool allows.
- **Kit as text** on the web page, and the kit shelf if David still wants it.

### Phase 11. The manual (parallel from phase 3 on; touches only docs and `tools/make_manual.py`)

- `docs/MANUAL.md` is LOOM-8's. Write WARP-8's from section 3 of this file and the code, with screens from
  `tools/gen_screens.sh` (never drawn by hand). List the exceptions from section 2. Update the help cards' text
  for buttons whose hold changed.

---

## 5. Decisions (all made by David, 2026-11-11)

| | Question | Decision |
|---|---|---|
| D1 | Does Steps become one drum in detail, leaving the 11-lane grid to HOME? | Yes. Phase 6, after phase 2. |
| D2 | Held step on the kit: velocity, chance, ratchet, nudge in place of velocity, length, chance, pitch? | Yes. Phase 7. Length and pitch stay reachable (tricks page; TUNE lock on EDIT). |
| D3 | Sample and slice tracks stay tracks? | Yes for now. |
| D4 | Macro names TUNE, DECAY, TONE, BITE? | Yes, with the model's own names shown beneath. |
| D5 | Fill on GLO held + white 16? | Yes. |

No phase waits on a decision. Mutes on GLO held was decided earlier the same day.

---|---|---|
| D1 | Does Steps become one drum in detail, leaving the 11-lane grid to HOME? | **Decided: yes** (David, 2026-11-11). Build phase 6 after phase 2, so HOME can write steps before Steps loses its grid. |
| D2 | Held step on the kit: velocity, chance, ratchet, nudge in place of velocity, length, chance, pitch? | Yes. Ratchet is used far more on drums than length; pitch stays as a TUNE lock. |
| D3 | Sample and slice tracks stay tracks? | Yes for now. |
| D4 | Macro names TUNE, DECAY, TONE, BITE? | Yes, with the model's own names shown beneath. |
| D5 | Fill on GLO held + white 16 (it cannot be REC held)? | Yes. |

Phases 1 to 6, 8 and 9 need none of the open ones answered except D4 (phase 5) and D5 (phase 1).

---

## 6. Measurements (fill in as you go)

| After | Image (B) | Free of 581,564 | Pool headroom (B) | Tests passed | Layout sweep |
|---|---|---|---|---|---|
| 0.4 (from notes) | 574,560 | 7,004 | not recorded | 76 | |
| Phase 0 (0.5, `5d92bf5`) | 574,680 | 6,884 | 17,292 (pool 326,772 of 344,064); .data+.bss 94,740 of 98,304 | 71 of 71 | pass, normal and large type |
| Phase 1 | 575,316 | 6,248 | 17,292; .data+.bss 94,748 | 72 of 72 | pass, normal and large type |
| Phase 2 | not measured | | | 55 scenarios | |
| Phase 3 | 576,384 | 5,180 | 17,292 | 55 scenarios | |
| Reclaim (R) | 573,136 | 8,428 | 17,292 | 55 scenarios | |
| Phase 4 | 574,784 | 6,780 | 17,292 | 56 scenarios | |
| Phase 5 | not measured | | | 57 scenarios | |
| Phase 6 | not measured | | | 58 scenarios | |
| Phase 7 | 577,088 | 4,476 | 17,292 | 59 scenarios | |
| Phase 8 | 577,664 | 3,900 | 17,292 | 60 scenarios | |
| Phase 9 | 577,840 | 3,724 | 17,292; .data+.bss 94,724 | 61 scenarios | |
| Final (`seq.c` restored) | 577,504 | 4,060 | 17,292; .data+.bss 94,724 | FINALROW | |

"Scenarios" rows were checked with every `tests/scenarios/*.xy` in the simulator; the full suite (unit tests,
update path, layout sweeps, browser build) ran after phases 0, 1 and 9.

---

## 7. Hardware checklist (David, any time; none of it blocks the phases)

1. Install 0.5. Does it boot, play, save, and keep the save across power-off? Note the flash part if the installer
   shows it.
2. A heavy kit playing: any dropouts? (`tools/hw_bench.py`, `tools/measure_load.sh`.)
3. Hold GLO or FX with one hand and reach the keys with the other: comfortable?
4. Is 200 ms right for a layer map, and 700 ms for a step's tap?

---

## 8. What was built (2026-11-11), and where it departs from this plan

Built, each with a scenario: phase 1 `glomutes.xy`; 2 `homesteps.xy`; 3 `stepsanywhere.xy`; 4 `layers.xy`;
5 `macros.xy`; 6 `lane.xy`; 7 `ratchet.xy`; 8 `grids.xy`; 9 `ctlall.xy`. The manual is `docs/WARP-8.md`.

Departures:

- **Phase R** did not delete pages. It taught the build what 0.5 already guarantees (one kit, on track 1; three
  instrument tracks; sample and slice the only engines), so the compiler drops the rest: `is_drum`, `is_midi`,
  `is_acid`, `sel_trk` in `pages.c`, `EG_LIVE` where the engine is read. 3.2 KB. (The same in `seq.c` broke the
  sequencer's own unit test, which runs synth tracks, and was taken back; the image came out smaller without it.) A track or
  engine outside those now behaves as the kit or as a sample track; `solo.xy` was rewritten for the reachable tracks.
- **Phase 3:** a drum held is its lane on the pages where a step's knobs are its trig (HOME, Steps, the effects, Mix,
  ARP), not on the sound pages. There, holding a drum's key while turning a knob is how a sound is shaped, and the
  lane's HITS knob would rewrite the pattern under the hand.
- **Phase 4:** FX held is not a drawn map of its own: the page becomes Throws for as long as FX is held, which
  already draws its keys. GLO and HOME have `draw_layer`.
- **Phase 5:** no knob was reordered. 65 of the 73 models already have pitch on knob 1 and length on knob 2
  (`docs/MACROS.md` lists the eight that differ, for David). Steps' knobs became the drum's four; the steps' scale
  went to Bar's knob 3 (the kit's swing is HOME's), not to a list row.
- **Phase 7:** the old knobs were kept one SELECT turn away while a step is held (length and pitch in semitones),
  since a TUNE lock is not the same thing as the step's pitch.
- **Phase 8:** steps 1 and 2 of `GRIDS-PERFORM.md` and "keep". GRIDS is a key of the Throws page (the fifteenth white
  key, the first one free), not a `PX_*` bit: every key of the two octaves has a throw. So it is not recorded on the
  THROW track. Not built: the hollow cells over the grid, chaos, accents, the thirty-second notes, saving a latched
  GRIDS. The sequencer reads the map through `seq_t.grids_fn`, set by the UI, because the map's table lives in the
  UI's unit.
- **Phase 9:** as planned. The undo joins turns made within a moment into one step back, as elsewhere.
- **Phase 10** was not started: each item needs its note agreed first. About 4 KB of flash is left for it.
- **Help cards** for GLO are gone (its map replaces them); FX, EDIT and the others keep theirs. Their text was not
  rewritten.
