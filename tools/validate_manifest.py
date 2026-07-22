#!/usr/bin/env python3
"""Dependency-free structural and content validation for the audio manifest."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "manifest.json"
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
HASH_PATTERN = re.compile(r"^[a-f0-9]{64}$")
ALLOWED_LICENSES = {"CC0-1.0", "CC-BY-4.0"}
ALLOWED_ROLES = {"all", "prop", "hunter", "none"}
ALLOWED_CATEGORIES = {
    "taunt", "weapon", "impact", "player", "disguise", "movement", "ui", "round"
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate() -> list[str]:
    errors: list[str] = []
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Cannot read manifest.json: {exc}"]

    if manifest.get("manifestVersion") != 1:
        fail(errors, "manifestVersion must be 1")

    pack = manifest.get("pack")
    if not isinstance(pack, dict) or pack.get("id") != "zeep-prop-hunt-audio-core":
        fail(errors, "pack.id must be zeep-prop-hunt-audio-core")

    assets = manifest.get("assets")
    if not isinstance(assets, list):
        return errors + ["assets must be an array"]

    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for index, asset in enumerate(assets):
        label = f"assets[{index}]"
        if not isinstance(asset, dict):
            fail(errors, f"{label} must be an object")
            continue

        asset_id = asset.get("id")
        if not isinstance(asset_id, str) or len(asset_id) > 128 or not ID_PATTERN.fullmatch(asset_id):
            fail(errors, f"{label}.id is invalid")
        elif asset_id in seen_ids:
            fail(errors, f"duplicate asset id: {asset_id}")
        else:
            seen_ids.add(asset_id)

        category = asset.get("category")
        role = asset.get("role")
        if category not in ALLOWED_CATEGORIES:
            fail(errors, f"{label}.category is invalid")
        if role not in ALLOWED_ROLES:
            fail(errors, f"{label}.role is invalid")
        if category == "taunt" and role not in {"all", "prop", "hunter"}:
            fail(errors, f"{label}: taunts require all, prop, or hunter role")

        relative = asset.get("file")
        if not isinstance(relative, str):
            fail(errors, f"{label}.file is required")
            continue
        pure_path = PurePosixPath(relative)
        if pure_path.is_absolute() or ".." in pure_path.parts or not relative.startswith("audio/"):
            fail(errors, f"{label}.file is not a safe audio/ relative path")
            continue
        if pure_path.suffix.lower() not in {".ogg", ".wav"}:
            fail(errors, f"{label}.file has an unsupported extension")
        if relative in seen_paths:
            fail(errors, f"duplicate asset path: {relative}")
        seen_paths.add(relative)

        local_path = ROOT.joinpath(*pure_path.parts)
        if not local_path.is_file():
            fail(errors, f"missing file: {relative}")
            continue

        expected_hash = asset.get("sha256")
        if not isinstance(expected_hash, str) or not HASH_PATTERN.fullmatch(expected_hash):
            fail(errors, f"{label}.sha256 is invalid")
        else:
            actual_hash = hashlib.sha256(local_path.read_bytes()).hexdigest()
            if actual_hash != expected_hash:
                fail(errors, f"hash mismatch: {relative}")

        if asset.get("bytes") != local_path.stat().st_size:
            fail(errors, f"byte count mismatch: {relative}")
        if asset.get("license") not in ALLOWED_LICENSES:
            fail(errors, f"{label}.license is not accepted")

        transcript = asset.get("transcript")
        caption = asset.get("caption")
        if (transcript is None) != (caption is None):
            fail(errors, f"{label}: transcript and caption must both be present or null")

    tracked_audio = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "audio").rglob("*")
        if path.is_file()
    } if (ROOT / "audio").exists() else set()
    unlisted = tracked_audio - seen_paths
    if unlisted:
        fail(errors, "unlisted release audio: " + ", ".join(sorted(unlisted)))

    events = manifest.get("events")
    if not isinstance(events, dict):
        fail(errors, "events must be an object")
    else:
        for event_id, variants in events.items():
            if not isinstance(event_id, str) or not ID_PATTERN.fullmatch(event_id):
                fail(errors, f"invalid event id: {event_id!r}")
                continue
            if not isinstance(variants, list) or not variants:
                fail(errors, f"event {event_id} must have at least one variant")
                continue
            if len(variants) != len(set(variants)):
                fail(errors, f"event {event_id} contains duplicate variants")
            for variant in variants:
                if not isinstance(variant, str) or variant not in seen_ids:
                    fail(errors, f"event {event_id} references unknown asset: {variant!r}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Audio manifest validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
