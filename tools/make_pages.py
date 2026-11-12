#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
"""Make the WARP-8 site for GitHub Pages (https://davidpryan.github.io/drum-8/), with LOOM-8's site builder (its
pages, renamed: every page says WARP-8 but the manual, which is LOOM-8's own, under a note):

  index.html                    what LOOM-8 is, and the ways in: try, install, download, manual, source
  manual/index.html             docs/MANUAL.md as a page (tools/make_manual.py), its screenshots in img/
  img/                          screenshots (docs/img)
  emu/                          LOOM-8 in the browser (app/build/emu, from ./build.sh --web)
  words/                        the screen reader's words files (app/web/words, from app/words.tsv)
  install/index.html            the web installer (fm1-base's web/installer.html, with fm1ports.js, fm1pkg.js, fm1ota.js and
                                the package's metadata inlined; Chrome or Edge, Web MIDI)
  backup/index.html             backup and restore in the browser (fm1-base's web/backup/index.html: the projects and
                                the user presets; the samples, app/web/backup/extras.js, in a section of the file)
  mirror/index.html             the screen and the panel on the computer (fm1-base's web/mirror/index.html; Chrome or
                                Edge, Web MIDI)
  samples/index.html            the user sample bank in the browser (app/web/samples/: add, replace, rename, reorder,
                                remove; loom_samples.js inlined)
  firmware/loom-VERSION.fwsc    the package the installer writes; also the download
  firmware/loom-VERSION-res.bin the resource region beside it (the 909 cymbals), which the installer writes after it
  firmware/m-bootloader-X.Y.fwsc  m-bootloader (MIT, fm1-base's web/m-bootloader), offered after the firmware

  tools/make_pages.py app/build/loom-0.1.fwsc 0.1 OUT_DIR

The package must be a release build (./build.sh --release X.Y): its identity, FM-1_10XXYYZZ, is what
the installer checks the download against and what the FM-1 reports after the install."""
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC / "base" / "tools"))
import make_site as base_site  # noqa: E402  (fm1-base's: the installer, the backup page, the package format)
from make_site import product_of, strip_module  # noqa: E402

import os  # noqa: E402
REPO = os.environ.get("LOOM_REPO") or "https://github.com/davidpryan/drum-8"   # (LOOM_REPO: a fork's site links its own)
NAME = "WARP-8"
LOOM = "@@LOOM@@"                     # LOOM-8 where a page means LOOM-8 itself (main() renames the rest)
# the app's look (app/pages.c THEMES[0], "tape deck"): its eight track inks, and the site's palette from it: dark is the
# FM-1's screen, light the same browns on cream paper. Every page of the site wears it (dress()), whatever names its own
# stylesheet gives the colours, with a header to go between them.
TRACKS = ["#e6b432", "#d66030", "#a0aa46", "#46aaa0", "#6e96c8", "#b46e96", "#d2aa78", "#96be96"]
PALETTE = {
    "light": {"bg": "#f4ecdc", "card": "#fffaf0", "now": "#e9dcc4", "rule": "#d8c6a8", "muted": "#6a5440", "ink": "#24180f",
              "accent": "#8a5a00", "on": "#ffffff", "teal": "#2a7a72", "bad": "#b3261e", "focus": "#2f5f9a", "wave": "#a08a6e"},
    "dark": {"bg": "#18120e", "card": "#2c221a", "now": "#46382a", "rule": "#4a3c2e", "muted": "#beaa8c", "ink": "#f4e6c8",
             "accent": "#e6b432", "on": "#18120e", "teal": "#46aaa0", "bad": "#ff7a5c", "focus": "#8fb4e0", "wave": "#786450"},
}


def tokens(p):
    """the palette under every name the site's pages use for it (the landing's, the manual's, the installer's, the
    backup's, the emulator's, the samples page's)"""
    names = {"bg": ("ground", "bg"), "card": ("card", "panel"), "now": ("now",), "rule": ("rule", "line"),
             "muted": ("muted", "dim"), "ink": ("ink", "fg"), "accent": ("accent",), "on": ("on-accent", "keytext"),
             "teal": ("teal",), "bad": ("bad", "red"), "focus": ("focus",), "wave": ("wave",)}
    out = [f"--{n}: {p[k]};" for k, ns in names.items() for n in ns]
    out.append(f"--key: {p['ink']};")
    return " ".join(out)


SITE_CSS = """<style>
:root { --panel-lit: #e6b432; --panel-lit-ink: #18120e; --panel-lit-white: #f0d58a; --panel-lit-black: #46aaa0;
        --panel-dim: #6b5a2e; --panel-dim-white: #e4d8b4; --panel-dim-black: #8fbdb7; }   /* (the FM-1's lights: fm1panel.js; as app/web/emu) */
:root { %s color-scheme: light; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { %s color-scheme: dark; } }
:root[data-theme="dark"] { %s color-scheme: dark; }
.lm-top { max-width: 64rem; margin: 0 auto 28px; display: flex; flex-wrap: wrap; align-items: center; gap: .3rem 1.4rem;
          padding: 14px 0 12px; border-bottom: 1px solid var(--rule); font: 600 1rem/1.4 "Barlow", "Helvetica Neue", Arial, sans-serif; }
.lm-top .lm-brand { display: inline-flex; align-items: center; gap: .55rem; color: var(--ink); text-decoration: none;
                    font: 700 1.35rem/1 "Barlow Semi Condensed", "Barlow", sans-serif; letter-spacing: .02em; }
.lm-top .lm-threads { display: inline-flex; gap: 3px; }
.lm-top .lm-threads i { width: 4px; height: 18px; border-radius: 2px; }
.lm-top nav { display: flex; flex-wrap: wrap; gap: .2rem 1.1rem; margin-left: auto; }
.lm-top nav a { color: var(--muted); text-decoration: none; padding: 2px 0; border-bottom: 2px solid transparent; }
.lm-top nav a:hover, .lm-top nav a:focus-visible { color: var(--ink); }
.lm-top nav a[aria-current="page"] { color: var(--ink); border-bottom-color: var(--accent); }
@media (max-width: 520px) { .lm-top nav { margin-left: 0; width: 100%%; } }
</style>""" % (tokens(PALETTE["light"]), tokens(PALETTE["dark"]), tokens(PALETTE["dark"]))

SECTIONS = [("emu/", "Try it"), ("kit/", "Manual"), ("manual/", "@@LOOM@@ manual"), ("install/", "Install"), ("samples/", "Samples"),
            ("backup/", "Backup"), ("mirror/", "Mirror")]


def dress(page, here):
    """a page of the site in the app's colours, with the site's header; here: its section ("" the front page)"""
    up = "../" if here else ""
    threads = "".join(f'<i style="background:{c}"></i>' for c in TRACKS)
    links = "".join(f'<a href="{up}{d}"' + (' aria-current="page"' if d == here else "") + f">{t}</a>"
                    for d, t in SECTIONS)
    links += f'<a href="{REPO}">Source</a>'
    top = (f'<header class="lm-top"><a class="lm-brand" href="{up or "./"}"' + (' aria-current="page"' if not here else "") +
           f'><span class="lm-threads" aria-hidden="true">{threads}</span>WARP-8</a>'
           f'<nav aria-label="WARP-8">{links}</nav></header>')
    if page.count("</head>") != 1 or not re.search(r"<body[^>]*>", page):
        raise SystemExit(f"dress: {here or 'index'}: no head or body")
    page = page.replace("</head>", SITE_CSS + "</head>")
    return re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + top, page, count=1)

LANDING = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>WARP-8</title>
<meta name="description" content="A pocket drum machine for the M-VAVE FM-1: LOOM-8's sequencer with every track a drum kit, and Hortator's drum models and sounds on the keys.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;600&family=Barlow+Semi+Condensed:wght@600;700&display=swap">
<style>
:root { --ground: #f4f3f1; --ink: #1c1c20; --muted: #66666e; --rule: #dcdbd8; --card: #ffffff; --accent: #c8306f; color-scheme: light; }
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) { --ground: #000; --ink: #ebebee; --muted: #9a9aa2; --rule: #2e2e34; --card: #141418; --accent: #ff5caa; color-scheme: dark; }
}
:root[data-theme="dark"] { --ground: #000; --ink: #ebebee; --muted: #9a9aa2; --rule: #2e2e34; --card: #141418; --accent: #ff5caa; color-scheme: dark; }
body { background: var(--ground); color: var(--ink); margin: 0; padding-inline: 16px; padding-block: 48px 64px;
       font: 400 17px/1.6 "Barlow", "Helvetica Neue", Arial, sans-serif; }
main { max-width: 42rem; margin: 0 auto; }
h1 { font: 700 3rem/1 "Barlow Semi Condensed", "Barlow", sans-serif; margin: 0 0 .7rem; }
h2 { font: 700 1.4rem "Barlow Semi Condensed", "Barlow", sans-serif; margin: 2.2rem 0 .6rem; }
.threads { display: flex; gap: 6px; margin: 0 0 1.4rem; }
.threads span { flex: 1; height: 6px; border-radius: 3px; }
.lede { font-size: 1.15rem; margin: 0 0 1.6rem; max-width: 36rem; }
.video { aspect-ratio: 16 / 9; margin: 0 0 1.4rem; border-radius: 14px; overflow: hidden; border: 1px solid var(--rule); background: #000; }
.video iframe { width: 100%; height: 100%; border: 0; display: block; }
.shots { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin: 0 0 1.8rem; }
.shots img { width: 100%; height: auto; border-radius: 14px; image-rendering: pixelated; border: 1px solid var(--rule); }
.status { border: 1px solid var(--rule); background: var(--card); border-radius: 14px; padding: 12px 16px; margin: 0 0 1.6rem; }
.ways { display: grid; gap: 12px; margin: 0 0 1rem; }
.ways a { display: block; text-decoration: none; color: var(--ink); background: var(--card); border: 1px solid var(--rule);
          border-radius: 14px; padding: 14px 18px; }
.ways a:hover, .ways a:focus-visible { border-color: var(--accent); outline: none; }
.ways strong { font: 600 1.25rem "Barlow Semi Condensed", "Barlow", sans-serif; color: var(--accent); display: block; }
.ways span { color: var(--muted); font-size: .95rem; }
ul.feat { padding-left: 1.2rem; }
ul.feat li { margin: 0 0 .5rem; }
p.small { color: var(--muted); font-size: .9rem; }
a { color: var(--accent); }
code { font-size: .9em; }
</style>
</head>
<body>
<main>
<h1>WARP-8</h1>
<div class="threads" aria-hidden="true">__THREADS__</div>
<p class="lede">A pocket drum machine for the M-VAVE FM-1: <a href="https://github.com/charlesvestal/fm1-loom">@@LOOM@@</a>'s
sequencer, mixer and effects around a single kit of eleven drums, and <a href="https://deadactive.github.io/hortator/">Hortator</a>'s
drum models and factory sounds on the keys.</p>
<div class="shots">
  <img src="img/warp-steps.png" width="240" height="240" alt="Steps: the picked drum's sixteen steps as bars of velocity, its chance, ratchets and locks marked under them, the other drums thin beneath">
  <img src="img/warp-kit.png" width="240" height="240" alt="HOME on a kit: eleven rows, a drum each, with its steps and its level; the knobs are the tempo, every drum's length, the swing and the kit">
  <img src="img/warp-generate.png" width="240" height="240" alt="The Generate page with Grids: the hits it would write outlined over the kick, snare and hat lanes, its X, Y and fill on the knobs">
</div>
<div class="status"><strong>Version __VERSION__. Not yet tested on an FM-1.</strong> It builds and passes its tests in the
simulator; nobody has run this build on the hardware. It installs and uninstalls the way every fm1-base firmware
does, and the installer can put M-VAVE's own firmware back, but until someone has tried it, treat it as an experiment.
Installing is at your own risk. It starts with fresh projects: back up @@LOOM@@ first if you have work in it.</div>
<nav class="ways" aria-label="Get WARP-8">
  <a href="emu/"><strong>Try it in the browser</strong><span>The same code the FM-1 runs, with sound. No FM-1 needed.</span></a>
  <a href="install/"><strong>Install</strong><span>From Chrome or Edge, with the FM-1 connected by USB. Nothing to install on the computer.</span></a>
  <a href="kit/"><strong>Read the manual</strong><span>The kit, its keys and its held buttons: what WARP-8 does its own way.</span></a>
  <a href="manual/"><strong>Read @@LOOM@@'s manual</strong><span>For the rest: the sample and slice tracks, the mixer, the effects and saving work as @@LOOM@@'s do; its synth engines are not here.</span></a>
  <a href="samples/"><strong>Samples</strong><span>Put your own samples on the FM-1: add, replace, rename, reorder and remove up to 32.</span></a>
  <a href="backup/"><strong>Backup</strong><span>Save your projects, presets and samples to a file, and load them back later.</span></a>
  <a href="mirror/"><strong>Mirror</strong><span>The FM-1's screen on your computer, live, and its buttons, keys and knobs to play from there.</span></a>
  <a href="firmware/__PKG__"><strong>Download __PKG__</strong><span>For the command-line installer: <code>python3 base/tools/fm1_install.py __PKG__</code></span></a>
  <a href="__REPO__"><strong>Source</strong><span>GitHub, GPL-3.0. A fork of @@LOOM@@ by Charles Vestal, with Hortator's drum models by DEADACTIVE, on Felucca by Leo Kuroshita (Hügelton Instruments).</span></a>
</nav>

<h2>What's in it</h2>
<ul class="feat">
  <li><b>One kit of eleven drums</b>, each a drum model with its own knobs, envelope, filter, pan and sends, beside a sample track, a slice track and the throws.</li>
  <li><b>73 drum models</b>: @@LOOM@@'s thirty and 43 of Hortator's: the 808 and 909 family, Plaits' kicks, snares and hats, a struck membrane, FM, and the TRX and EFM voices measured from the Machinedrum.</li>
  <li><b>DRUM SOUND</b>: 143 of Hortator's factory sounds by type (kick, snare, hat, clap, tom, perc, cymbal), each on the key and heard as you turn to it. On a kit's pads the PRESETS knob steps through whole kits the same way.</li>
  <li><b>Sixteen factory kits</b>, six of them made of Hortator's sounds: TRX, EFM, 808, 909, Modern, Hard.</li>
  <li><b>One rule for the keys</b>: a black key is a drum, a white key is a step of the picked drum, on every page of the kit. Hold a step, a drum or a button and the knobs and keys are its.</li>
  <li><b>HOME is the whole pattern</b>, a row a drum, and you write it there: the tempo, every drum's length, the swing and the kit on its knobs. ALGORITHM picks the drum on every page; PRESETS is the kit on HOME, the pattern on SEQ, the drum's next sound on EDIT.</li>
  <li><b>Steps is the picked drum alone</b>: a bar each step's velocity, its chance, ratchets and locks marked, the other drums thin beneath, and the drum's own four knobs under your hand. A drum can have a length of its own and run against the others.</li>
  <li><b>A held step</b>: velocity, chance, ratchets and nudge on the knobs; on a sound page, the page's knobs locked to that step. The nudge is each drum's own: a snare can drag while the kick on the same step stays put.</li>
  <li><b>A colour for each drum</b>, the same on every page: its row, its steps, its pad, its key.</li>
  <li><b>A sound browser</b>: PRESETS on a drum lists Hortator's 143 sounds by engine, each heard as you turn to it; ALGORITHM jumps to the next engine.</li>
  <li><b>Generators</b>: hold a drum and the knobs set its hits, turn it, vary it; the Generate page previews Euclid, mutate and Mutable Instruments' Grids before it writes them. <b>Grids is also a throw</b>: held, the kick, snare and hat play from the drum map, and SEL keeps what you hear.</li>
  <li><b>Held buttons, from any page</b>, each drawing its keys: GLO for the mutes, solo and a fill (at once or at the bar line), FX for the throws. EDIT held, a knob turns every drum's.</li>
  <li><b>A Scenes page</b> beside HOME: every track's pattern in the scene on a knob of its own, the tracks' mutes on the black keys, the kit's drums and their mutes, the scenes on the white keys.</li>
  <li><b>ALL</b> on an effect's Mix strip: every track into FX I or FX II.</li>
  <li><b>An FX sequence</b>, a fifth sequence beside the kit, the sample track, the slice track and the throws: its steps hold amounts for the two effects, in eleven lanes, and can ramp from one to the next.</li>
  <li><b>Twenty-four throws</b>: @@LOOM@@'s twelve, and twelve more in the second octave: thin, roll, buzz, soft, hard, rise, drop, down, a low-pass, delay and reverb throws, a crusher.</li>
  <li>@@LOOM@@'s <b>sequencer</b>: eight patterns of up to 64 steps, tricks and parameter locks on any step, weave, throws, scenes and a song.</li>
  <li>Two <b>send effects</b>, a mixer with EQ and a compressor on the master.</li>
</ul>
<h2>What's not</h2>
<ul class="feat">
  <li>@@LOOM@@'s synth engines (knit, rayon, jacquard, bellows, cane, voile, acid), its other tracks, its conductor and its weave track.</li>
  <li>Hortator's ACID and SAMPL models, and their eight presets.</li>
</ul>
<p class="small">To go back to the official firmware, use the installer's "Back to the stock firmware", or
M-VAVE's updater, M-UPGRADE, from <a href="https://www.m-vave.com/download">m-vave.com/download</a>. @@LOOM@@'s
way of working owes a great deal to teenage engineering's OP-XY. M-VAVE, FM-1, Machinedrum and OP-XY are trademarks of
their owners; WARP-8 is not affiliated with any of them, nor with @@LOOM@@ or Hortator.</p>
</main>
</body>
</html>
"""


def main(pkg, version, out):
    pkg, out = Path(pkg), Path(out)
    raw = pkg.read_bytes()
    product = product_of(raw)
    if not re.fullmatch(r"FM-1_18\d{6}", product):
        raise SystemExit(f"{pkg}: identity {product!r}: make a release build (./build.sh --release X.Y)")
    if b"FELUCCA-LOADER-1" not in raw:
        raise SystemExit(f"{pkg}: no update loader in it")
    name = f"warp-{re.sub(r'[^A-Za-z0-9.-]', '-', version)}.fwsc"
    if out.exists():
        shutil.rmtree(out)
    for d in ("install", "firmware", "backup", "mirror"):
        (out / d).mkdir(parents=True)
    shutil.copy(pkg, out / "firmware" / name)
    # the resource region (the 909 cymbals: fm1.toml resources), checked, beside it: the installer writes it after
    res_src, res_name = pkg.with_name(pkg.stem + "-res.bin"), Path(name).stem + "-res.bin"
    if not res_src.exists():
        raise SystemExit(f"make_pages: no {res_src} (./build.sh --release writes it; gh release download it with the package)")
    sys.path.insert(0, str(SRC / "base" / "tools"))
    from fm1_resources import ResError, payload_of
    try:
        payload_of(res_src.read_bytes())
    except ResError as e:
        raise SystemExit(f"make_pages: {res_src}: {e}")
    shutil.copy(res_src, out / "firmware" / res_name)
    # m-bootloader (MIT), which the installer offers after the firmware, with its licence (as fm1-base's sites)
    boot = SRC / "base" / "web" / "m-bootloader" / f"fm1-uboot-{base_site.MBOOT_VERSION}.fwsc"
    boot_name = f"m-bootloader-{base_site.MBOOT_VERSION}.fwsc"
    shutil.copy(boot, out / "firmware" / boot_name)
    shutil.copy(SRC / "base" / "web" / "m-bootloader" / "LICENSE", out / "firmware" / "m-bootloader-LICENSE.txt")
    for lic in sorted((SRC / "base" / "LICENSES").glob("*.txt")):   # fm1-base's parts under other licences (the JieLi
        shutil.copy(lic, out / "firmware" / lic.name)               # SDK files, the Bluetooth stack's Apache / BSD parts)
    page = (SRC / "base" / "web" / "installer.html").read_text(encoding="utf-8")
    lib = "\n".join(strip_module((SRC / "base" / "web" / f).read_text(encoding="utf-8"))   # (as fm1-base's make_site)
                     for f in ("fm1ports.js", "fm1pkg.js", "fm1ota.js"))
    meta = json.dumps({"version": version, "product": product, "pkg": "../firmware/" + name,
                       "backup": True,                              # (the site's backup page: the installer links it)
                       "res": "../firmware/" + res_name,           # (the resource region: written after the firmware)
                       "boot": {"pkg": "../firmware/" + boot_name, "version": base_site.MBOOT_VERSION,
                                "sha256": hashlib.sha256(boot.read_bytes()).hexdigest()}})
    for mark in ("/*LIB*/", "/*META*/"):
        if page.count(mark) != 1:
            raise SystemExit(f"base/web/installer.html must contain {mark} once")
    conf = base_site.read_conf(SRC / "app" / "fm1.toml")
    credits = conf.get("credits", "").replace("Built on fm1-base and felucca-bsp, from Felucca by Leo Kuroshita (Hügelton "
                                              "Instruments). ", "")        # (the page says that part itself)
    credits = credits.replace("LOOM-8", LOOM)                               # (LOOM-8 itself, whose fork this is)
    for key, val in (("RES", conf["resources_what"]), ("RES_JA", conf["resources_what_ja"]),   # (fm1.toml)
                     ("NAME", NAME), ("REPO", REPO), ("REPO_SHORT", REPO.replace("https://", "")),
                     ("LICENSE", conf.get("licence", "MPL-2.0")), ("CREDITS", " " + credits if credits else "")):
        page = page.replace("{{" + key + "}}", val)
    # since 0.7 the breaks are a pack for the user bank: say so where the firmware is installed
    warn = '<p data-t="warn">'
    if page.count(warn) != 1:
        raise SystemExit(f"base/web/installer.html must contain {warn} once")
    page = page.replace(warn, '<p class="note"><b>Not yet tested on an FM-1.</b> This build passes its tests in the '
                        'simulator; nobody has run it on the hardware. The installer can put the stock firmware back.</p>\n  '
                        '<p class="note"><b>The sample models\' sounds live in the sample bank.</b> The installer adds '
                        'them (the sample kits\' drums, the instruments, the sweep and the vinyl: 86 KB) after your '
                        'samples, which keep their numbers; if your samples leave no room for them, it asks first. The '
                        'four breaks are on <a href="../samples/">the samples page</a>: "Add the breaks".</p>\n  ' + warn)
    page = page.replace("</style>", "  .note { border-left: 4px solid var(--accent); padding: 4px 0 4px 12px; }\n</style>", 1)
    # the installer's own steps for LOOM-8 (base/web/installer.html APP): the factory set into the sample bank
    app_js = ("(() => {\n" + strip_module((SRC / "app" / "web" / "samples" / "loom_samples.js").read_text(encoding="utf-8"))
              + "\n" + (SRC / "app" / "web" / "install_app.js").read_text(encoding="utf-8") + "\nreturn { before, after };\n})()")
    if page.count("/*APP*/") != 1:
        raise SystemExit("base/web/installer.html must contain /*APP*/ once")
    (out / "install" / "index.html").write_text(page.replace("/*LIB*/", lib).replace("/*META*/", meta)
                                                .replace("/*APP*/", app_js), encoding="utf-8")
    # the backup page's own section: the sample bank (app/web/backup/extras.js on the samples page's code)
    extras = ("const EXTRAS = (() => {\n" +
              strip_module((SRC / "app" / "web" / "samples" / "loom_samples.js").read_text(encoding="utf-8")) + "\n" +
              (SRC / "app" / "web" / "backup" / "extras.js").read_text(encoding="utf-8") + "})();")
    note = ("\n  <li>The samples go in the file too. A restore sends them after LOOM-8 has said yes on its screen, which "
            "takes about 20 seconds more. An older backup has no samples, so a restore from it leaves the samples as they "
            "are.</li>")
    terminal = ("You can also do it from a terminal, in LOOM-8's repository: <code>python3 base/tools/fm1_backup.py</code> "
                "for the projects and presets (the same files: it leaves their samples alone), and "
                "<code>python3 tools/loom_samples.py backup</code> / <code>restore</code> for the samples (its restore "
                "takes this page's files too).")
    tools = base_site.tool_pages(SRC / "app", conf, {"NAME": NAME, "EXTRAS_JS": extras, "EXTRA": note,
                                                     "TERMINAL": terminal})
    (out / "backup" / "index.html").write_text(tools["backup/index.html"], encoding="utf-8")
    (out / "mirror" / "index.html").write_text(tools["mirror/index.html"], encoding="utf-8")
    # the samples page, its bank code (app/web/samples/loom_samples.js) inlined
    spage = (SRC / "app" / "web" / "samples" / "index.html").read_text(encoding="utf-8")
    if spage.count("/*LIB*/") != 1:
        raise SystemExit("app/web/samples/index.html must contain /*LIB*/ once")
    slib = strip_module((SRC / "app" / "web" / "samples" / "loom_samples.js").read_text(encoding="utf-8"))
    (out / "samples").mkdir()
    (out / "samples" / "index.html").write_text(spage.replace("/*LIB*/", slib), encoding="utf-8")
    # the break pack (out of the firmware since 0.7): the samples page's "Add the breaks" fetches these
    import gen_samples
    import sampleio
    # LOOM-8's own sounds (out of the firmware since 0.8): the installer and the samples page add them to the bank
    (out / "samples" / "factory.bin").write_bytes(sampleio.user_bank(gen_samples.factory_set()))
    (out / "samples" / "breaks").mkdir()
    for brk, f, _, _ in gen_samples.RECORDINGS:
        shutil.copy(gen_samples.SAMPLE_DIR / f, out / "samples" / "breaks" / f"{brk}.wav")
    shutil.copytree(SRC / "docs" / "img", out / "img")
    threads = "".join(f'<span style="background:{c}"></span>' for c in TRACKS)
    (out / "index.html").write_text(LANDING.replace("__VERSION__", html.escape(version)).replace("__PKG__", name)
                                    .replace("__REPO__", REPO).replace("__THREADS__", threads), encoding="utf-8")
    (out / "manual").mkdir()
    subprocess.run([sys.executable, str(SRC / "tools" / "make_manual.py"), str(SRC / "docs" / "MANUAL.md"),
                    str(out / "manual" / "index.html")], check=True)
    for f in (out / "manual" / "index.html",):    # the manual's pictures are the site's img/
        f.write_text(f.read_text(encoding="utf-8").replace('src="img/', 'src="../img/'), encoding="utf-8")
    (out / "kit").mkdir()                         # WARP-8's own manual for the kit (docs/WARP-8.md)
    subprocess.run([sys.executable, str(SRC / "tools" / "make_manual.py"), str(SRC / "docs" / "WARP-8.md"),
                    str(out / "kit" / "index.html")], check=True)
    kf = out / "kit" / "index.html"
    kf.write_text(kf.read_text(encoding="utf-8").replace('src="img/', 'src="../img/').replace("LOOM-8", LOOM), encoding="utf-8")
    # the manual is LOOM-8's own: say so at its top, and keep its name through the renaming below
    mf = out / "manual" / "index.html"
    banner = ('<p style="border-left:4px solid var(--accent);padding:4px 0 4px 12px"><b>This is LOOM-8\'s manual.</b> '
              'WARP-8\'s own, for the kit, its keys and its held buttons, is <a href="../kit/">here</a>. The sample and '
              'slice tracks, the mixer, the effects and saving work as written here; the synth engines (knit, rayon, '
              'jacquard, bellows, cane, voile, acid) are not in WARP-8, and a project is one kit, not eight tracks.</p>')
    mt = mf.read_text(encoding="utf-8").replace("LOOM-8", LOOM)
    mf.write_text(re.sub(r"(<h1[^>]*>)", lambda m: banner.replace("LOOM-8", LOOM) + m.group(1), mt, count=1), encoding="utf-8")
    emu = SRC / "app" / "build" / "emu"
    if not (emu / "app.wasm").exists():
        raise SystemExit("no app/build/emu/app.wasm: run ./build.sh --web (needs Emscripten)")
    shutil.copytree(emu, out / "emu")
    # the screen reader's words files (fm1-reader): every one ever made, for the devices that point at them
    shutil.copytree(SRC / "app" / "web" / "words", out / "words")
    for path, here in (("index.html", ""), ("manual/index.html", "manual/"), ("kit/index.html", "kit/"), ("install/index.html", "install/"),
                       ("backup/index.html", "backup/"), ("mirror/index.html", "mirror/"), ("samples/index.html", "samples/"),
                       ("emu/index.html", "emu/")):
        f = out / path
        f.write_text(dress(f.read_text(encoding="utf-8"), here), encoding="utf-8")
    # every page says WARP-8 where LOOM-8's pages said LOOM-8; LOOM (the sentinel) is LOOM-8 itself
    for f in out.rglob("*.html"):
        t = f.read_text(encoding="utf-8")
        f.write_text(t.replace("LOOM-8", NAME).replace(LOOM, "LOOM-8"), encoding="utf-8")
    (out / ".nojekyll").write_text("")
    print(f"site: {out}: index.html, manual/, install/ ({product}), backup/, mirror/, samples/, emu/, words/, firmware/{name} ({len(raw)} B)")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:4])
