# Kenney audio investigation

Source inspected: **Kenney Game Assets All-in-1 3.6.0**.

The local collection contains 1,342 OGG audio files across 15 dedicated audio packs, plus a small number embedded in visual-asset packs. The `License.txt` files in each shortlisted source pack identify the work as Creative Commons Zero (CC0). The release repository should still credit Kenney and retain exact pack/version/source metadata even though attribution is not mandatory.

The completed listening review selected a deliberately small development catalog. This document records both the candidate rationale and result; no stable public pack has been released yet.

## Completed review result

All 115 shortlisted candidates were reviewed on 2026-07-22:

- **42 approved** across 16 gameplay events;
- **73 rejected** as poor fits for Prop Hunt;
- **0 reassigned** to alternate purposes;
- **0 left unreviewed**.

The approved catalog contains:

| Event | Approved variants |
| --- | ---: |
| `disguise.apply` | 4 |
| `disguise.preview` | 4 |
| `disguise.remove` | 2 |
| `impact.glass` | 3 |
| `impact.metal` | 3 |
| `impact.prop` | 3 |
| `impact.wood` | 4 |
| `impact.world` | 3 |
| `round.hiding_start` | 2 |
| `round.local_win` | 2 |
| `round.seeking_start` | 2 |
| `ui.accept` | 1 |
| `ui.back` | 1 |
| `ui.error` | 3 |
| `ui.ready` | 1 |
| `weapon.fire` | 4 |

All proposed Kenney taunts were rejected, so the core taunt groups intentionally remain empty. The nine long Digital Audio laser candidates were also rejected for excessive reverb; four shorter `Sci-Fi Sounds/laserSmall` variants form the selected weapon family.

The exact approved source-to-ID mapping is in [`../sources/kenney-core-selection.json`](../sources/kenney-core-selection.json). The imported OGG files preserve the exact reviewed bytes for development and in-game mix testing. They can be normalized or converted before the first immutable public release, but any processing must receive another listening pass and regenerate the manifest hashes.

## Proposed audio direction

Use a bright, tactile, arcade-like mix rather than realistic firearms or unrelated novelty sounds. A gameplay event should draw variants from one source family so repeated playback has variety without changing sonic meaning.

Preliminary family choices:

| Gameplay use | Kenney family | Current assessment |
| --- | --- | --- |
| General UI | `Interface Sounds` | Best single vocabulary for accept/back/error/toggle/select. Mostly short mono files. |
| Prop hit | `Impact Sounds/impactSoft_medium` | Five concise variants; visually neutral and less violent than punch sounds. |
| World miss | `Impact Sounds/impactGeneric_light` | Five concise variants suitable as the fallback surface. |
| Material impacts | `impactWood_medium`, `impactMetal_light`, `impactGlass_light` | Five variants per material from the same recording/design family. |
| Hunter weapon | `Sci-Fi Sounds/laserSmall` | Five 0.24-0.41 second variants. Better repetition behavior than the 1.27-2.18 second `Digital Audio/laser` family. |
| Disguise apply/remove | `Digital Audio/phaserUp` and `phaserDown` | Ten short related cues; directionality communicates apply versus remove. |
| Announcer and starter taunts | `Synth Voice 2` | Broadest coherent vocabulary; candidate clips are 0.55-2.22 seconds with similar measured levels. Must pass subjective tone/listening review. |

## Measured technical profile

All shortlisted sources are 44.1 kHz OGG. Positional Kenney effects are often stereo, so release processing should generate mono positional assets at the final agreed sample rate rather than shipping them unchanged.

| Family | Variants | Duration | Mean level range | Peak range |
| --- | ---: | ---: | ---: | ---: |
| `impactSoft_medium` | 5 | 0.12-0.18 s | -14.8 to -14.1 dB | -1.0 to -0.9 dB |
| `impactGeneric_light` | 5 | 0.12-0.14 s | -21.2 to -20.0 dB | -1.2 to -0.9 dB |
| `impactWood_medium` | 5 | 0.33 s | -22.7 to -22.1 dB | -1.1 to -1.0 dB |
| `impactMetal_light` | 5 | 0.21-0.48 s | -21.1 to -20.0 dB | -1.5 to -0.9 dB |
| `impactGlass_light` | 5 | 0.21 s | -21.8 to -19.9 dB | -1.6 to -0.8 dB |
| `laserSmall` | 5 | 0.24-0.41 s | -22.6 to -15.6 dB | -7.7 to -2.5 dB |
| `phaserUp` | 7 | 0.24-0.45 s | -30.0 to -27.8 dB | -15.3 to -10.2 dB |
| `phaserDown` | 3 | 0.26-0.43 s | -30.7 to -28.5 dB | -17.3 to -12.0 dB |
| Synth Voice 2 candidates | 29 | 0.55-2.22 s | -18.2 to -13.6 dB | -1.9 to -0.4 dB |

These measurements demonstrate family consistency, not final mix readiness. Phaser cues are substantially quieter than impacts and will need gain treatment. Loudness targets should be established inside Zeepkist with FMOD attenuation active.

## Candidate event arrays

The first listening pass should evaluate these complete families:

- `impact.prop`: all five `impactSoft_medium_000` through `_004` variants.
- `impact.world`: all five `impactGeneric_light_000` through `_004` variants.
- `impact.wood`, `impact.metal`, and `impact.glass`: five matching variants each.
- `weapon.fire`: all five `laserSmall_000` through `_004` variants, compared against the Digital Audio laser family before locking the style.
- `disguise.apply`: seven `phaserUp` variants.
- `disguise.remove`: three `phaserDown` variants.
- `ui.accept`, `ui.back`, `ui.error`, `ui.ready`, and `disguise.preview`: audition the matching Interface Sounds family, then retain only variants that convey the same meaning.

For Synth Voice 2, the shortlist is intentionally semantic:

- Neutral taunts: `areYouReady`, `letsDoThis`, `okay`, `yes`, `hurryUp`, `lookOut`.
- Prop taunts: `goAway`, `giveUp`, `imTooTired`, `iCannotDoThat`, `untouchable`, `targetLost`, `youNeedMoreCredits`.
- Hunter taunts: `targetInRange`, `targetEngaged`, `requestingPermissionToEngage`, `stealthTerminationConfirmed`, `surrenderOrDie`, `eliminate`.
- Round cues: `ready`, `gameStart`, `timeUp`, `hurryUp`, `eliminated`, `victory`, `defeat`, `youWin`, `youLose`, `suddenDeath`.

The voice-style comparison also includes representative clips from Synth Voice 1 and the male/female Voiceover Pack. Do not mix announcer voices casually; select one coherent announcer vocabulary after listening.

## Local audition board

Generate a local, ignored soundboard from the installed Kenney collection:

```powershell
python tools/build_kenney_audition.py --kenney-root "D:\Kenney Assets\Kenney Game Assets All-in-1 3.6.0" --open
```

The tool verifies every selected pack's bundled CC0 license, copies only the shortlist into ignored `work/`, measures basic audio properties, and opens a grouped assignment-review page. Each clip has a proposed gameplay purpose and can be approved for that purpose or disapproved as either **Poor for Prop Hunt** or **Suggest for a different purpose**. Alternate assignments use the complete purpose catalog. Progress persists locally, and submitting downloads `kenney-audio-review.json` with decisions, reasons, alternate purposes, notes, source paths, and measured metadata. Nothing is copied into the public `audio/` catalog by this command.

## Deferred families

- Music Jingles are intentionally deferred. Filenames identify instrumentation and index but not emotional meaning; victory/defeat selection requires a dedicated listening pass.
- Foley is reserved for later prop-specific movement polish.
- Realistic/military Voiceover phrases are excluded unless they fit the final playful tone.
- Music loops, casino sounds, and unrelated RPG/environmental sounds are out of scope for the core gameplay pass.

## Reproducing the reviewed development catalog

Given the same local Kenney collection and exported review file:

```powershell
python tools/import_kenney_review.py `
  --review "C:\path\to\kenney-audio-review.json" `
  --kenney-root "D:\Kenney Assets\Kenney Game Assets All-in-1 3.6.0"
python tools/validate_manifest.py
```

The importer includes approved and alternate-purpose decisions, ignores rejected candidates, copies only selected source files, retains the relevant CC0 notices, measures every output, and generates the manifest event arrays and sanitized selection record. It refuses to overwrite an existing output with different bytes.
