# Audio pack technical specification

## Pack identity

The required multiplayer pack is `zeep-prop-hunt-audio-core`. It has a semantic content version independent of the Prop Hunt plugin version. Published archives and their manifests are immutable.

The canonical manifest contains stable IDs, relative paths, file hashes, audio properties, transcripts/captions, provenance, and licensing. The pack's root identity is the SHA-256 digest of the canonical release manifest bytes. Public releases also carry a detached manifest signature verified with a public key embedded in the Modkist plugin package.

## Stable IDs

IDs use lowercase dot-separated segments:

```text
taunt.all.short_whistle
taunt.prop.cardboard_confidence
taunt.hunter.checking_twice
weapon.fire.pop_01
round.prop_win.default
```

An ID must never contain a path, extension, pack version, user-supplied absolute location, or mutable display text. Released IDs are not reused for unrelated audio.

## Source and release audio

- Archive masters as WAV, preferably 48 kHz PCM.
- Positional one-shots should normally be mono.
- UI and round stings may be stereo.
- Taunts should normally be 1-4 seconds, with a hard limit of 6 seconds.
- Release files use a single documented codec/encoder configuration chosen after in-game listening tests.
- Loudness is normalized consistently by event family, with measured values recorded in the manifest.
- Avoid baked spatial effects on sounds FMOD will position in 3D.

Lossless masters may move to Git LFS before binary submissions open. Built packs should be attached to GitHub Releases rather than consumed from a default-branch archive.

## Runtime update and admission

1. The plugin embeds a trusted repository/release endpoint and release-signing public key.
2. Prop Hunt opens using the last verified installed pack.
3. A remote check uses HTTP caching and a short timeout; failure does not destroy offline functionality.
4. Update archives download into staging.
5. The plugin verifies the manifest signature and archive/file hashes, validates safe relative paths, and rejects traversal/symlink content.
6. The verified pack is swapped atomically outside an active match.
7. The host advertises its required core manifest hash during lobby admission.
8. Clients must match before ready-up. Network events contain only stable sound IDs.

Do not mutate the installed pack mid-session, trust arbitrary host URLs, or download individual unverified files from `main`. Release signing and private-key custody must be established before unattended automatic installation is enabled; hashes alone do not establish trust when the manifest and archive come from the same host.

Optional packs require a future manifest-intersection negotiation. Until implemented, only the mandatory core pack is eligible for host-selected network taunts.
