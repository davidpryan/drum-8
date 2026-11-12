# The four knobs of each drum model

On Steps and on EDIT's first page the four knobs are the picked drum's own. This table is what they are for each of
the 73 models, read from `app/dsp/drumline.c` (`DM_KNOB`) and `app/dsp/hort_models.inc` (`HORT_KNOBS`). The plan's
names for the four places are TUNE, DECAY, TONE and BITE; the screen shows the model's own name for each.

Almost every model already has its pitch on knob 1 and its length on knob 2, so nothing was reordered. The models
marked * differ; they are left as their authors laid them out and listed at the end for David to decide.

| Model | Knob 1 (TUNE) | Knob 2 (DECAY) | Knob 3 (TONE) | Knob 4 (BITE) |
|---|---|---|---|---|
| kick | pitch | length | punch | tone |
| snare | pitch | length | wires | punch |
| hat | pitch | length | metal | focus |
| clap * | tone | length | spread | tail |
| shaker * | color | length | swell | return |
| tambourine * | tone | length | jingle | hiss |
| string | pitch | length | bright | pluck |
| conga | pitch | length | slide | drive |
| tom | pitch | length | sweep | rate |
| fm | pitch | length | mod | feedback |
| sample * | sample | pitch | start | reverse |
| x kick | pitch | length | tone | sweep |
| x snare | pitch | length | tone | snap |
| x hat | pitch | length | tone | res |
| x clap * | tone | length | drive | - |
| x tom | pitch | length | tone | sweep |
| x rim | pitch | length | tone | sweep |
| x fm | pitch | length | ratio | mod decay |
| x noise * | tone | length | drive | - |
| clang | pitch | length | color | metal |
| sophie | pitch | length | color | metal |
| 909 kick | pitch | decay | attack | sweep |
| 909 snare | pitch | decay | snappy | tone |
| 909 tom | pitch | decay | attack | size |
| 909 rim * | pitch | drive | shape | - |
| 909 clap * | tone | tail | drive | shape |
| 909 hat | pitch | decay | drive | shape |
| 909 open | pitch | decay | drive | shape |
| 909 ride | pitch | decay | drive | shape |
| 909 crash | pitch | decay | drive | shape |
| k808 | tune | decay | tone | dip |
| k909 | tune | decay | sweep | click |
| s808 | tune | decay | tone | snap |
| s909 | tune | decay | body | snap |
| c808 | tune | decay | tone | tail |
| c909 | tune | decay | tone | sprd |
| hatc | tune | decay | tone | brite |
| hato | tune | decay | tone | brite |
| cymb | tune | decay | tone | bal |
| cowb | tune | decay | tone | tail |
| c tom | tune | decay | noise | drop |
| c conga | tune | decay | slap | drop |
| rim | tune | decay | tone | drive |
| clave | tune | decay | click | drop |
| boom | tune | decay | tone | punch |
| punch | tune | decay | tone | fm |
| snap | tune | decay | tone | snap |
| crack | tune | decay | fm | snap |
| metal | tune | decay | tone | noise |
| hiss | tune | decay | tone | noise |
| skin | tune | decay | tone | head |
| fm perc | tune | decay | index | ratio |
| bdtrx | tune | decay | sweep | sdec |
| sdtrx | tune | decay | snap | tone |
| tmtrx | tune | decay | ramp | rdec |
| cgtrx | tune | decay | ramp | rdec |
| cptrx | tune | decay | clpy | hard |
| rstrx | tune | decay | dist | - |
| cbtrx | tune | decay | enh | damp |
| chtrx | tune | decay | gap | hpf |
| ohtrx | tune | decay | gap | hpf |
| cytrx | tune | decay | rich | top |
| shtrx | tune | decay | att | rev |
| cltrx | tune | decay | dual | enh |
| b2trx | tune | decay | ramp | hold |
| bdefm | tune | decay | ramp | rdec |
| sdefm | tune | decay | nois | ndec |
| tmefm | tune | decay | ramp | rdec |
| cpefm | tune | decay | clps | cdec |
| rsefm | tune | decay | mod | hpf |
| cbefm | tune | decay | snap | fb |
| hhefm | tune | decay | trem | tfrq |
| cyefm | tune | decay | fb | hpf |

## The models that differ

8 of 73:

- **clap**: tone, length, spread, tail
- **shaker**: color, length, swell, return
- **tambourine**: tone, length, jingle, hiss
- **sample**: sample, pitch, start, reverse
- **x clap**: tone, length, drive, -
- **x noise**: tone, length, drive, -
- **909 rim**: pitch, drive, shape, -
- **909 clap**: tone, tail, drive, shape

Options for these: leave them (as now); or swap two knobs in `tp_page_param` for the model so pitch-like and
length-like knobs sit first. Locks are stored by parameter, so a swap would not disturb saved projects.
