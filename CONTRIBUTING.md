# Contributing

This repository does not accept public audio submissions. Do not attach, link, or open a pull request containing an unsolicited sound, voice recording, music file, or other media. Such contributions will be closed without evaluating whether the submitter's license claim is accurate.

## Contributions that are welcome

- Documentation corrections
- Manifest/schema and validation improvements
- Reproducible release tooling
- Caption or transcript corrections for existing catalog entries
- Technical bug reports against a published pack
- Attribution or rights-holder reports concerning published material

When reporting a rights concern, provide the stable asset ID, the basis of the concern, and a reliable way for maintainers to verify it. Avoid reposting the disputed media.

## Pull requests

Keep a pull request focused on one change, explain why it is needed, and run `python tools/validate_manifest.py`. A change to an existing released asset must not replace bytes behind a stable ID silently. Published release archives and manifests are immutable.

Audio is added only by maintainers from pre-approved, independently verified sources. The source-selection and provenance process occurs outside public pull requests.
