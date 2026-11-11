# WARP-8

A drum machine firmware for the M-VAVE FM-1: [LOOM-8](https://github.com/charlesvestal/fm1-loom)'s sequencer, mixer,
effects and pages, with its synth engines taken out and [Hortator](https://github.com/DeadActive/hortator)'s drum
models put into the kit. A fork of LOOM-8 by Charles Vestal; the drum models are DEADACTIVE's, on Leo Kuroshita's
Felucca. GPL-3.0-only as a whole (`LICENSING.md`).

**Status: builds and passes its tests in the simulator. Not yet run on an FM-1.**

What is different from LOOM-8:

- **Every track can be a kit.** A new project is eight kits of eleven keys. The engines left are kit, sample, slice
  and MIDI out; knit, rayon, jacquard, bellows, cane, voile and acid do not play (a track saved with one loads as a
  sample track).
- **73 drum models on a key**: LOOM-8's 30 and 43 of Hortator's 45 (all but SAMPL and ACID), with Hortator's own
  knobs on the key's two pages: the 808 and 909 family, Plaits' kicks, snares and hats, SKIN, FM, and the TRX and EFM
  voices measured from the Machinedrum.
- **DRUM SOUND** in a kit key's SELECT list: 143 of Hortator's factory presets, each a model and its knobs, onto the
  key shown.
- **Six more factory kits** made of those presets: TRX, EFM, 808, 909, Modern, Hard.
- **A kit's Steps page is a grid** of its eleven keys, each a lane of sixteen steps: a black key picks the lane, the
  white keys write it.
- **Generators**: a lane held on the grid has its hits, rotation, variation and clearing on the knobs; the Generate
  page (SEQ's third on a kit) previews Euclid, mutate and Grids on the grid and SEL writes them. `docs/GRIDS-PERFORM.md`
  is a plan for Grids played live.
- **Voices**: eight Hortator hits at once over all kits, four of LOOM-8's 909 models, one string, eight sample or
  slice voices (LOOM-8: sixteen synth voices, eight 909, two strings, three kits).
- **Its own identity**: the package is `warp.fwsc`, identity `FM-1_18`, USB name `WARP-8 FM-1`, and its projects carry
  their own tag, so it starts fresh on an FM-1 that had LOOM-8 (LOOM-8's projects are not read; a LOOM-8 backup's
  kits and presets still restore).

The site, with the web installer and the emulator: <https://davidpryan.github.io/drum-8/> (`tools/publish_pages.sh`).

Not done: a manual of its own (the site carries LOOM-8's, under a note), the tests in `tests/parked/`, and the dead engines' source and pages, which are still
in the tree. Bringing in a newer Hortator: `tools/import_hortator.sh PATH`, then `tools/gen_hort_models.py` and
`tools/gen_hort_presets.py`.

Build it as LOOM-8 (`BUILDING.md`): `./build.sh` makes `app/build/warp.fwsc`, `./build.sh --host` the simulator,
`tests/run_tests.sh` runs the tests.

What follows is LOOM-8's own README, for everything the two share.

---

# LOOM-8 for the M-VAVE FM-1

LOOM-8 turns the M-VAVE FM-1 into a pocket groovebox: eight instrument tracks, each in its own colour, on
eleven engines (seven synths: knit, rayon, jacquard, bellows, cane, voile and acid, a TB-303; a sample player, a break slicer, a drum kit, and MIDI out to drive another synth), 93 factory presets; a 64-step sequencer with step tricks and parameter locks; players (arp,
strum, hold); weave, which crosses two patterns (bar by bar, step by step, or one's rhythm with the other's
notes); throws (momentary effects); a conductor track that moves the song through a progression; two
send-effect tracks (the reverb with the PlayStation's reverbs among its modes), a mixer with EQ
and a compressor on the master, scenes and a song. MIDI over USB, Bluetooth and the TRS jack, and as a USB MIDI host
for a keyboard or synth (through a powered hub). Built on
[fm1-base](https://github.com/charlesvestal/fm1-base) and [felucca-bsp](https://github.com/hugelton/felucca-bsp),
from [Felucca](https://github.com/hugelton/Felucca) by Leo Kuroshita (Hügelton Instruments), with X0X's sequencer
discipline and Polly's menu paradigm.

- **Read the manual**: [docs/MANUAL.md](docs/MANUAL.md), with a ten-minute quick start, every page and gesture, and screenshots
- **Try it in your browser** (no FM-1 needed): <https://charlesvestal.github.io/fm1-loom/emu/>
- **Install it** (Chrome or Edge, with the FM-1 plugged in): <https://charlesvestal.github.io/fm1-loom/install/>
- **Download the firmware file**: [releases](https://github.com/charlesvestal/fm1-loom/releases)

Installing is at your own risk, though it's hard to get stuck: the web installer can put M-VAVE's
firmware back, and an FM-1 that keeps crashing starts in a safe mode.

The design is in `docs/superpowers/specs/2026-10-15-xy1-design.md`.

Your projects and presets can be backed up to a computer and put back (the site's Backup page), and the screen
mirrored to it and played from there (the Mirror page); your own
samples load from their WAV files with `tools/loom_samples.py` (see the manual).

## Building and testing

LOOM-8 is an app (`app/`) on fm1-base, a git submodule (`base/`): clone with `--recursive`. See `BUILDING.md`.
`tests/run_tests.sh` runs everything on the host, silently (the audio goes to WAV files). `LICENSING.md` says
where the code comes from. LOOM-8 is GPL-3.0-only as a whole (`COPYING`), for its acid engine and 909 models; most of its files are
MPL-2.0 (`LICENSE`), each on its own.

## Credits

The platform: fm1-base and felucca-bsp (MPL-2.0), from Felucca by Leo Kuroshita (Hügelton Instruments), with his
permission (felucca-bsp#4). cane and voile: Mutable Instruments Braids by Emilie Gillet (MIT). acid: X0X's 303, from Open303 by Robin Schmidt (MIT), with jc303's Devilfish ranges by midilab (GPL-3.0) and dm-Rat's RAT drive by Dave Mollen (GPL-3.0). The reverb's PlayStation modes: PSXVerb (MIT). The x drums: after MACHINEDRUM by Omodaka9375 (MIT); sophie: Sophie by Matt Estela (MIT); clang: digisophie (MIT). The factory breaks: free loops by u/FCTRYBEATS,
with their permission; the plate reverb and the 909 kick, snare and clap: 9W9 by athousanddetails, under MPL-2.0 with his permission; the 909 kit models: 9W9's circuits by athousanddetails (GPL-3.0); the acid engine's and the 909 sampler's speed-ups: Optimist (GPL-3.0); the 909 hat: ER-99's sample by Matthew Cieplak, through 9W9 (GPL-3.0, in the sound bank only); the 909 cymbals (hat, open hat, ride, crash): ER-99's samples by Matthew Cieplak, through 9W9, played by 9W9's sampler (GPL-3.0, in the resource region beside the firmware); the recorded instruments: Versilian Studios Chamber
Orchestra 2 Community Edition (CC0). The fonts: Barlow and Terminus (SIL OFL 1.1). The second core's lessons: Melodee (keremimo) and Jangada (zednaked). The USB MIDI host: Melodee's, by Adrien Tibi and Kerem Kilic (MPL-2.0, in felucca-bsp).
Bluetooth MIDI and Bluetooth audio: Optimist's own stack by Henri David (MPL-2.0, in fm1-base), with Android's SBC
encoder (Apache-2.0) and micro-ecc by Kenneth MacKay (BSD-2-Clause); the radio's start-up tables and calibration
after JieLi's AC79 SDK (Apache-2.0).
The idea of a browser emulator: Groove OS.

LOOM-8's way of working owes a great deal to teenage engineering's OP-XY; LOOM-8 is not affiliated with
teenage engineering.
