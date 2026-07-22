# Zeep Prop Hunt Audio

Maintainer-curated audio content for the unofficial **Prop Hunt mod for Zeepkist**.

This repository exists so taunts and gameplay sounds can be reviewed, licensed, versioned, and released independently from the mod itself. The Prop Hunt mod will be distributed through **Modkist**; its source code and binaries do not live in this repository.

> **Current status:** repository bootstrap. There is not yet a public core audio-pack release. Players should not clone this repository into their game installation.

## Why audio has its own repository

Prop Hunt needs every player in a lobby to resolve the same stable sound IDs. A central repository gives the project:

- clear authorship, licensing, transcripts, and attribution for every clip;
- a narrow, auditable set of maintainer-selected sources;
- automated checks for paths, metadata, formats, duration, and hashes;
- immutable, versioned release packs rather than mutable files from `main`;
- a canonical manifest the mod can compare with the locally installed pack;
- an audio release cadence that is independent from Modkist code releases.

The mod is expected to check for an updated release manifest asynchronously when Prop Hunt opens. It should continue using the last verified local pack when offline, install updates only after signature and hash verification, and never replace content during an active match. A host will advertise the exact required core manifest hash so joining players cannot enter with mismatched audio.

## What belongs here

- Role-specific and role-neutral positional taunts
- Hunter weapon and impact sounds
- Prop damage, disguise, lock, and movement cues
- Lobby and interface feedback
- Round announcements and victory/defeat stings
- Captions, transcripts, attribution, licenses, manifests, and build tooling

The initial inventory and priority list are in [docs/SOUND_INVENTORY.md](docs/SOUND_INVENTORY.md). Technical IDs and pack rules are in [docs/TECHNICAL_SPEC.md](docs/TECHNICAL_SPEC.md). The measured Kenney shortlist and local listening workflow are in [docs/KENNEY_CANDIDATES.md](docs/KENNEY_CANDIDATES.md).

This repository does **not** contain:

- the Prop Hunt mod, plugin DLL, or networking code;
- Zeepkist game assets copied from a game installation;
- map files or Steam Workshop levels;
- audio without documented redistribution rights.

## Contribution policy

This repository does **not** accept unsolicited audio files, audio links, voice recordings, or pull requests that add sounds. A license checkbox cannot establish authorship, and operating a public upload queue would create avoidable copyright and moderation risk.

Maintainers select audio from a deliberately narrow set of sources with independently verifiable rights, retain provenance records, and publish only the files needed by the mod. At present the intended baseline is selected material from Kenney's CC0 asset collections. The whole upstream collection will not be redistributed.

Documentation, validation, release tooling, captions, and corrections are still welcome; see [CONTRIBUTING.md](CONTRIBUTING.md). Use the content-problem issue form to report a technical, attribution, or rights concern about something already published.

## Player guide

The relationship between this pack, Modkist, and multiplayer compatibility is explained in [docs/PROP_HUNT_GUIDE.md](docs/PROP_HUNT_GUIDE.md).

## Project status and affiliation

This is an unofficial community project. It is not the official Zeepkist soundtrack or an official Zeepkist content distribution channel. Zeepkist names and game assets remain the property of their respective owners.
