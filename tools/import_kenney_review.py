#!/usr/bin/env python3
"""Materialize a completed Kenney review into the development audio catalog."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path, PurePosixPath


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPOSITORY_ROOT / "manifest.json"
SELECTION_PATH = REPOSITORY_ROOT / "sources" / "kenney-core-selection.json"
AUDIO_ROOT = REPOSITORY_ROOT / "audio"
LICENSE_ROOT = REPOSITORY_ROOT / "licenses" / "kenney"
SOURCE_COLLECTION = "Kenney Game Assets All-in-1 3.6.0"
VOICE_TEXT = {
    "ready": "Ready",
    "go": "Go",
    "you_win": "You win",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_slug(value: str) -> str:
    value = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", value)
    value = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return value


def source_pack(relative_source: str) -> str:
    parts = PurePosixPath(relative_source).parts
    if len(parts) < 4 or parts[0] != "Audio":
        raise ValueError(f"Unexpected Kenney source path: {relative_source}")
    return parts[1]


def asset_slug(relative_source: str) -> str:
    path = PurePosixPath(relative_source)
    stem = normalize_slug(path.stem)
    parent = path.parent.name.lower()
    if parent == "audio (female)":
        return f"female_{stem}"
    if parent == "audio (male)":
        return f"male_{stem}"
    return stem


def probe(path: Path) -> dict[str, int]:
    command = [
        "ffprobe", "-v", "error", "-select_streams", "a:0",
        "-show_entries", "stream=channels,sample_rate",
        "-show_entries", "format=duration", "-of", "json", str(path),
    ]
    value = json.loads(subprocess.run(command, check=True, capture_output=True, text=True).stdout)
    stream = value["streams"][0]
    return {
        "durationMs": max(1, round(float(value["format"]["duration"]) * 1000)),
        "channels": int(stream["channels"]),
        "sampleRateHz": int(stream["sample_rate"]),
    }


def copy_exact(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if sha256(source) != sha256(destination):
            raise FileExistsError(f"Refusing to replace different existing content: {destination}")
        return
    shutil.copy2(source, destination)


def accepted_reviews(review: dict[str, object]) -> list[dict[str, object]]:
    summary = review.get("summary")
    if not isinstance(summary, dict) or summary.get("unreviewed") != 0:
        raise ValueError("A complete review with zero unreviewed candidates is required.")
    accepted: list[dict[str, object]] = []
    for item in review.get("reviews", []):
        decision = item.get("decision")
        if decision == "approve":
            target = item.get("proposedPurpose")
        elif decision == "disapprove" and item.get("disapprovalReason") == "suggest_other_purpose":
            target = item.get("suggestedPurpose")
        else:
            continue
        if not isinstance(target, str) or not target:
            raise ValueError(f"Accepted review has no target purpose: {item}")
        accepted.append({"source": item["source"], "purpose": target})
    return accepted


def materialize(review_path: Path, kenney_root: Path) -> tuple[int, int]:
    review = json.loads(review_path.read_text(encoding="utf-8"))
    if review.get("schemaVersion") != 1:
        raise ValueError("Unsupported Kenney review schema.")
    if review.get("sourceCollection") != SOURCE_COLLECTION:
        raise ValueError("The review targets a different Kenney source collection.")

    selected = accepted_reviews(review)
    if not selected:
        raise ValueError("The review did not accept any audio.")

    assets: list[dict[str, object]] = []
    events: dict[str, list[str]] = defaultdict(list)
    selected_ids: set[str] = set()
    selected_paths: set[str] = set()
    selected_packs: set[str] = set()
    selection_entries: list[dict[str, str]] = []

    for selection in sorted(selected, key=lambda item: (str(item["purpose"]), str(item["source"]))):
        relative_source = str(selection["source"])
        purpose = str(selection["purpose"])
        source_path = kenney_root.joinpath(*PurePosixPath(relative_source).parts)
        if not source_path.is_file():
            raise FileNotFoundError(source_path)

        pack = source_pack(relative_source)
        slug = asset_slug(relative_source)
        asset_id = f"{purpose}.{slug}"
        relative_output = PurePosixPath("audio", *purpose.split("."), f"{slug}.ogg").as_posix()
        if asset_id in selected_ids:
            raise ValueError(f"Stable asset ID collision: {asset_id}")
        if relative_output in selected_paths:
            raise ValueError(f"Output path collision: {relative_output}")
        selected_ids.add(asset_id)
        selected_paths.add(relative_output)
        selected_packs.add(pack)

        output_path = REPOSITORY_ROOT.joinpath(*PurePosixPath(relative_output).parts)
        copy_exact(source_path, output_path)
        measured = probe(output_path)
        transcript = VOICE_TEXT.get(normalize_slug(PurePosixPath(relative_source).stem)) if pack == "Voiceover Pack" else None
        category = purpose.split(".", 1)[0]
        role = purpose.split(".", 1)[1] if category == "taunt" else "none"
        tags = ["kenney", "spoken" if transcript else "sound-effect"]
        tags.append("positional" if category in {"taunt", "weapon", "impact", "player", "disguise", "movement", "footstep", "prop"} else "non-positional")

        assets.append({
            "id": asset_id,
            "category": category,
            "role": role,
            "file": relative_output,
            "sha256": sha256(output_path),
            "bytes": output_path.stat().st_size,
            **measured,
            "author": "Kenney",
            "license": "CC0-1.0",
            "source": f"{SOURCE_COLLECTION} / {pack}",
            "attribution": "Kenney (CC0); attribution is appreciated but not required.",
            "transcript": transcript,
            "caption": transcript,
            "tags": tags,
        })
        events[purpose].append(asset_id)
        selection_entries.append({
            "source": relative_source,
            "purpose": purpose,
            "assetId": asset_id,
            "file": relative_output,
        })

    for pack in sorted(selected_packs):
        source_license = kenney_root / "Audio" / pack / "License.txt"
        if not source_license.is_file():
            raise FileNotFoundError(source_license)
        text = source_license.read_text(encoding="utf-8", errors="replace")
        if "Creative Commons Zero" not in text or "CC0" not in text:
            raise ValueError(f"Expected explicit CC0 license: {source_license}")
        copy_exact(source_license, LICENSE_ROOT / f"{normalize_slug(pack)}.txt")

    manifest = {
        "$schema": "./manifest.schema.json",
        "manifestVersion": 1,
        "pack": {
            "id": "zeep-prop-hunt-audio-core",
            "version": "0.1.0-dev",
            "channel": "development",
        },
        "assets": assets,
        "events": {event: variants for event, variants in sorted(events.items())},
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    SELECTION_PATH.parent.mkdir(parents=True, exist_ok=True)
    selection_record = {
        "sourceCollection": SOURCE_COLLECTION,
        "sourceLicense": "CC0-1.0",
        "reviewSchemaVersion": review["schemaVersion"],
        "reviewSubmittedAt": review.get("submittedAt"),
        "reviewSummary": review.get("summary"),
        "selected": selection_entries,
    }
    SELECTION_PATH.write_text(json.dumps(selection_record, indent=2) + "\n", encoding="utf-8")
    return len(assets), len(events)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--kenney-root", type=Path, required=True)
    args = parser.parse_args()
    asset_count, event_count = materialize(args.review.resolve(), args.kenney_root.resolve())
    print(f"Materialized {asset_count} approved assets across {event_count} events.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

