# Prop Hunt mod guide

## What it is

Prop Hunt is an unofficial multiplayer mode built on Zeepkist's level loading, rendering, physics, and editor ecosystem. Props hide by disguising themselves as map objects while hunters search for and shoot them. The mode uses its own realtime multiplayer layer because vanilla Zeepkist racing synchronization is not designed for realtime player-versus-player combat.

Prop Hunt maps remain valid Zeepkist levels so creators can build them in the familiar editor and publish them through the Steam Workshop. The mod interprets Prop Hunt-specific assets and zones when running the mode.

## Where to install the mod

The mod itself will be distributed through **Modkist**. This repository does not ship or install the plugin. The Modkist listing and player installation link will be added here when the public package is available.

Players should use the Modkist package rather than copying files from this repository. Release audio packs are intended to be installed and verified by the mod's content updater.

## Why every player needs the same audio pack

Network messages contain stable sound IDs—not arbitrary file paths or audio bytes. Each client resolves the ID from its verified local pack. Before ready-up, the host advertises the exact required core-pack manifest hash. A client with missing or different content must update before joining.

This provides:

- identical taunt selection for every participant;
- predictable captions and attribution;
- no mid-match downloads;
- no arbitrary audio supplied by a lobby host;
- offline use of the last locally verified pack.

## Expected update flow

1. Opening Prop Hunt loads the last verified local pack.
2. The mod asynchronously checks the latest published release manifest.
3. If an update exists, the player receives a clear update action/status.
4. The release manifest's detached signature and the archive hash are verified before extraction.
5. Installation is swapped atomically only while outside an active session.
6. Lobby admission checks the installed manifest against the host requirement.

The mod should not execute or trust mutable files directly from the repository's default branch. Only immutable release assets and cryptographically verified manifests are distribution inputs.

## Audio settings and accessibility

The planned mode includes separate control over taunt/gameplay audio and captions for spoken announcements. Taunts are positional: their purpose is to create playful risk by revealing a prop's approximate host-authoritative location. A client cannot choose an arbitrary file or claim a false sound position.

## For map creators

Do not embed the core taunt pack in `.zeeplevel` files. Maps and audio are separate compatibility boundaries:

- levels come from local development or Steam Workshop;
- the core audio pack comes from this repository's signed/versioned release channel;
- the Prop Hunt plugin comes from Modkist.

This separation keeps Workshop maps playable in vanilla Zeepkist and avoids duplicating audio in every map.
