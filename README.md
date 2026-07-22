# Zeep Prop Hunt Audio

Community-maintained audio content for the unofficial **Prop Hunt mod for Zeepkist**.

This repository exists so taunts and gameplay sounds can be reviewed, licensed, versioned, and released independently from the mod itself. The Prop Hunt mod will be distributed through **Modkist**; its source code and binaries do not live in this repository.

> **Current status:** repository bootstrap. There is not yet a public core audio-pack release. Players should not clone this repository into their game installation.

## Why audio has its own repository

Prop Hunt needs every player in a lobby to resolve the same stable sound IDs. A central repository gives the project:

- clear authorship, licensing, transcripts, and attribution for every clip;
- pull-request review for new community submissions;
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

The initial inventory and priority list are in [docs/SOUND_INVENTORY.md](docs/SOUND_INVENTORY.md). Technical IDs and pack rules are in [docs/TECHNICAL_SPEC.md](docs/TECHNICAL_SPEC.md).

This repository does **not** contain:

- the Prop Hunt mod, plugin DLL, or networking code;
- Zeepkist game assets copied from a game installation;
- map files or Steam Workshop levels;
- audio without documented redistribution rights.

## Submit a sound

Please read [CONTRIBUTING.md](CONTRIBUTING.md) and [LICENSES.md](LICENSES.md) first.

1. Open an **Audio submission** issue with the clip's origin, author, license, transcript, and content disclosures.
2. Wait for an initial provenance/content check before spending time preparing a pull request.
3. Submit a pull request containing the lossless master and its complete manifest entry.
4. Automation and maintainers review the asset. Approved submissions enter a future release; published releases are never silently changed.

Opening an issue does not guarantee acceptance. The project may reject audio that is legally unclear, excessively loud or long, hard to understand, disruptive in repeated play, or inconsistent with the mod's content policy.

## Review schedule

- New submission issues should receive an initial acknowledgement within **seven days**.
- Maintainers normally perform full listening/provenance review in a **biweekly batch**.
- Release packs are published when a coherent group of approved sounds is ready, rather than on a fixed calendar.
- Security, rights-holder, and licensing-removal reports are handled as soon as practical and do not wait for the normal review batch.

These are service goals for a volunteer project, not guaranteed deadlines. Queue status or maintainer availability will be posted in the repository when the cadence changes.

## Player guide

The relationship between this pack, Modkist, and multiplayer compatibility is explained in [docs/PROP_HUNT_GUIDE.md](docs/PROP_HUNT_GUIDE.md).

## Project status and affiliation

This is an unofficial community project. It is not the official Zeepkist soundtrack or an official Zeepkist content distribution channel. Zeepkist names and game assets remain the property of their respective owners.
