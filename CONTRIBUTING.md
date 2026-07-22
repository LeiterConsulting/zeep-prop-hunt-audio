# Contributing audio

Thank you for helping make Prop Hunt more expressive. Audio submissions carry more provenance and licensing risk than ordinary code changes, so the project uses an issue-first workflow.

## Before submitting

Open an **Audio submission** issue. Provide:

- a proposed stable ID and category;
- your GitHub identity and the credited author name;
- whether you recorded/created the clip yourself;
- the exact license being offered;
- source and license URLs for third-party source material;
- a verbatim transcript and player-facing caption for spoken audio;
- disclosure of synthetic generation or processing tools;
- confirmation that the clip contains no cloned or imitated real-person voice;
- content warnings or potentially disruptive characteristics.

Do not upload copyrighted film, television, game, music, meme, or streamer clips because they are popular. Public availability is not permission to redistribute.

## Accepted licensing baseline

New original submissions should normally be offered under **CC0-1.0** or **CC-BY-4.0**. See [LICENSES.md](LICENSES.md). Do not submit material with noncommercial, no-derivatives, personal-use-only, platform-limited, or unclear terms.

By opening a pull request, you attest that you have the right to submit every included asset under its declared license and that the repository may reproduce, normalize, encode, package, and redistribute it under those terms.

## Audio guidelines

- Submit a lossless WAV master, preferably 48 kHz PCM.
- Positional one-shots should normally be mono.
- Taunts should normally be 1-4 seconds and must not exceed 6 seconds.
- Avoid clipping, excessive silence, baked reverb, and aggressive stereo effects.
- Avoid slurs, harassment, sexual content, protected-character impersonation, copyrighted music, and excessive screaming.
- Spoken audio needs an accurate transcript and concise caption.
- A sound should remain tolerable when heard repeatedly during a full match.

Final encoding and loudness normalization are performed by project tooling. Do not repeatedly transcode a lossy source.

## Pull request layout

After issue triage, add:

1. The lossless source under the matching `masters/` category.
2. A complete asset record in `manifest.json`.
3. Any attribution text required by the license.
4. The issue number in the pull-request description.

Use lowercase stable IDs such as:

```text
taunt.prop.cardboard_confidence
taunt.hunter.checking_twice
weapon.fire.pop_01
round.hunter_win.default
```

IDs are permanent API-like identifiers. Do not encode an author name, pack version, file extension, or display-order number into an ID unless it distinguishes a genuine variant.

## Review process

Automation checks the manifest and repository structure. Maintainers separately review:

- provenance and licensing;
- speech/transcript accuracy;
- content and moderation concerns;
- in-game intelligibility, loudness, duration, and repetition fatigue;
- whether the proposed category and stable ID fit the catalog.

Maintainers may request edits, defer an otherwise valid sound until a coherent release batch, or decline it. At least one maintainer approval is required; spoken taunts should receive a second listen before release.

## Changes to existing sounds

Do not replace the bytes behind a released ID in place. A material audio change receives a new ID or appears in a new pack version with an explicit migration. Published release archives and manifests are immutable.

## Non-audio contributions

Documentation, validation tooling, schema improvements, captions, and attribution corrections are welcome through ordinary pull requests. Licensing or rights-holder concerns may be filed privately through GitHub's repository contact/security mechanism when public disclosure would be inappropriate.

