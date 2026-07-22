#!/usr/bin/env python3
"""Build a local soundboard for a curated subset of Kenney audio assets."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import webbrowser
from dataclasses import asdict, dataclass
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPOSITORY_ROOT / "work" / "kenney-audition"


@dataclass(frozen=True)
class Candidate:
    group: str
    relative_path: str


def numbered(group: str, prefix: str, values: range, digits: int = 3) -> list[Candidate]:
    return [Candidate(group, f"{prefix}{value:0{digits}d}.ogg") for value in values]


CANDIDATES: list[Candidate] = [
    *numbered("Impact - prop soft", "Audio/Impact Sounds/Audio/impactSoft_medium_", range(5)),
    *numbered("Impact - world generic", "Audio/Impact Sounds/Audio/impactGeneric_light_", range(5)),
    *numbered("Impact - wood", "Audio/Impact Sounds/Audio/impactWood_medium_", range(5)),
    *numbered("Impact - metal", "Audio/Impact Sounds/Audio/impactMetal_light_", range(5)),
    *numbered("Impact - glass", "Audio/Impact Sounds/Audio/impactGlass_light_", range(5)),
    *numbered("Weapon A - Sci-Fi laserSmall", "Audio/Sci-Fi Sounds/Audio/laserSmall_", range(5)),
    *[Candidate("Weapon B - Digital laser", f"Audio/Digital Audio/Audio/laser{value}.ogg") for value in range(1, 10)],
    *[Candidate("Disguise - apply phaserUp", f"Audio/Digital Audio/Audio/phaserUp{value}.ogg") for value in range(1, 8)],
    *[Candidate("Disguise - remove phaserDown", f"Audio/Digital Audio/Audio/phaserDown{value}.ogg") for value in range(1, 4)],
    *numbered("UI - accept confirmation", "Audio/Interface Sounds/Audio/confirmation_", range(1, 5)),
    *numbered("UI - back", "Audio/Interface Sounds/Audio/back_", range(1, 5)),
    *numbered("UI - error", "Audio/Interface Sounds/Audio/error_", range(1, 9)),
    *numbered("UI - ready toggle", "Audio/Interface Sounds/Audio/toggle_", range(1, 5)),
    *numbered("UI - disguise preview select", "Audio/Interface Sounds/Audio/select_", range(1, 9)),
]


def add_named(group: str, directory: str, names: list[str]) -> None:
    CANDIDATES.extend(Candidate(group, f"{directory}/{name}.ogg") for name in names)


add_named("Voice style - Synth Voice 2", "Audio/Synth Voice 2/Audio", ["ready", "gameStart", "youWin"])
add_named("Voice style - Synth Voice 1", "Audio/Synth Voice 1/Audio", ["ready", "game_start", "you_win"])
add_named("Voice style - human male", "Audio/Voiceover Pack/Audio (Male)", ["ready", "go", "you_win"])
add_named("Voice style - human female", "Audio/Voiceover Pack/Audio (Female)", ["ready", "go", "you_win"])
add_named("Synth Voice 2 - round", "Audio/Synth Voice 2/Audio", [
    "timeUp", "hurryUp", "eliminated", "victory", "defeat", "youLose", "suddenDeath"
])
add_named("Synth Voice 2 - neutral taunts", "Audio/Synth Voice 2/Audio", [
    "areYouReady", "letsDoThis", "okay", "yes", "hurryUp", "lookOut"
])
add_named("Synth Voice 2 - prop taunts", "Audio/Synth Voice 2/Audio", [
    "goAway", "giveUp", "imTooTired", "iCannotDoThat", "untouchable", "targetLost", "youNeedMoreCredits"
])
add_named("Synth Voice 2 - hunter taunts", "Audio/Synth Voice 2/Audio", [
    "targetInRange", "targetEngaged", "requestingPermissionToEngage",
    "stealthTerminationConfirmed", "surrenderOrDie", "eliminate"
])


def source_pack(relative_path: str) -> str:
    parts = Path(relative_path).parts
    if len(parts) < 2 or parts[0] != "Audio":
        raise ValueError(f"Candidate is not inside a dedicated Audio pack: {relative_path}")
    return parts[1]


def verify_licenses(root: Path) -> dict[str, str]:
    licenses: dict[str, str] = {}
    for pack in sorted({source_pack(candidate.relative_path) for candidate in CANDIDATES}):
        license_path = root / "Audio" / pack / "License.txt"
        if not license_path.is_file():
            raise FileNotFoundError(f"Missing license for {pack}: {license_path}")
        license_text = license_path.read_text(encoding="utf-8", errors="replace")
        if "Creative Commons Zero" not in license_text or "CC0" not in license_text:
            raise RuntimeError(f"Expected explicit CC0 license in {license_path}")
        licenses[pack] = str(license_path)
    return licenses


def probe(path: Path) -> dict[str, object]:
    command = [
        "ffprobe", "-v", "error", "-select_streams", "a:0",
        "-show_entries", "stream=channels,sample_rate",
        "-show_entries", "format=duration", "-of", "json", str(path)
    ]
    try:
        value = json.loads(subprocess.run(command, check=True, capture_output=True, text=True).stdout)
    except (FileNotFoundError, subprocess.CalledProcessError, json.JSONDecodeError):
        return {}
    stream = value.get("streams", [{}])[0]
    audio_format = value.get("format", {})
    return {
        "durationSeconds": round(float(audio_format.get("duration", 0)), 3),
        "channels": int(stream.get("channels", 0)),
        "sampleRateHz": int(stream.get("sample_rate", 0)),
    }


def safe_group(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def render(entries: list[dict[str, object]], licenses: dict[str, str]) -> str:
    groups: dict[str, list[dict[str, object]]] = {}
    for entry in entries:
        groups.setdefault(str(entry["group"]), []).append(entry)

    sections: list[str] = []
    for group, items in groups.items():
        cards = []
        for item in items:
            source = html.escape(str(item["source"]))
            local = html.escape(str(item["local"]))
            metadata = item.get("metadata", {})
            details = (
                f'{metadata.get("durationSeconds", "?")} s · '
                f'{metadata.get("channels", "?")} ch · '
                f'{metadata.get("sampleRateHz", "?")} Hz'
            )
            cards.append(f'''<article class="clip" data-source="{source}">
  <h3>{html.escape(Path(source).stem)}</h3>
  <p>{html.escape(details)}</p>
  <audio controls preload="none" src="{local}"></audio>
  <div class="decisions">
    <button data-value="keep">Keep</button><button data-value="maybe">Maybe</button><button data-value="reject">Reject</button>
  </div>
</article>''')
        sections.append(f'<section><h2>{html.escape(group)}</h2><div class="grid">{"".join(cards)}</div></section>')

    license_items = "".join(
        f"<li>{html.escape(pack)} — {html.escape(path)}</li>" for pack, path in licenses.items()
    )
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kenney audio audition</title>
<style>
:root {{ color-scheme: dark; font-family: system-ui,sans-serif; background:#111827; color:#e5e7eb }}
body {{ margin:0 auto; padding:2rem; max-width:1500px }} h1,h2 {{ color:#fff }}
.toolbar {{ position:sticky; top:0; background:#111827ee; padding:1rem 0; z-index:2 }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:1rem }}
.clip {{ padding:1rem; border:1px solid #374151; border-radius:.75rem; background:#1f2937 }}
.clip h3 {{ margin:.1rem 0; font-size:1rem; overflow-wrap:anywhere }} .clip p {{ color:#9ca3af; font-size:.85rem }}
audio {{ width:100% }} button {{ margin:.7rem .35rem 0 0; padding:.45rem .7rem; border:1px solid #4b5563; border-radius:.4rem; background:#111827; color:#fff }}
button.active[data-value=keep] {{ background:#166534 }} button.active[data-value=maybe] {{ background:#854d0e }} button.active[data-value=reject] {{ background:#991b1b }}
</style></head><body>
<h1>Kenney audio audition</h1>
<p>Curated candidates only. Decisions stay in this browser until exported; no file here is part of the public pack.</p>
<div class="toolbar"><button id="export">Export decisions as JSON</button> <span id="summary"></span></div>
{''.join(sections)}
<h2>Verified source licenses</h2><ul>{license_items}</ul>
<script>
const key='zeep-kenney-audition-v1'; const saved=JSON.parse(localStorage.getItem(key)||'{{}}');
function refresh() {{ const counts={{keep:0,maybe:0,reject:0}}; document.querySelectorAll('.clip').forEach(card=>{{ const value=saved[card.dataset.source]; card.querySelectorAll('button[data-value]').forEach(button=>button.classList.toggle('active',button.dataset.value===value)); if(value) counts[value]++; }}); document.querySelector('#summary').textContent=`Keep ${{counts.keep}} · Maybe ${{counts.maybe}} · Reject ${{counts.reject}}`; }}
document.querySelectorAll('button[data-value]').forEach(button=>button.addEventListener('click',()=>{{ const card=button.closest('.clip'); saved[card.dataset.source]=button.dataset.value; localStorage.setItem(key,JSON.stringify(saved)); refresh(); }}));
document.querySelector('#export').addEventListener('click',()=>{{ const blob=new Blob([JSON.stringify(saved,null,2)],{{type:'application/json'}}); const link=document.createElement('a'); link.href=URL.createObjectURL(blob); link.download='kenney-audio-decisions.json'; link.click(); URL.revokeObjectURL(link.href); }}); refresh();
</script></body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kenney-root", type=Path, required=True, help="Root of Kenney Game Assets All-in-1")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--open", action="store_true", dest="open_browser")
    args = parser.parse_args()

    root = args.kenney_root.resolve()
    output = args.output.resolve()
    licenses = verify_licenses(root)
    audio_output = output / "audio"
    audio_output.mkdir(parents=True, exist_ok=True)

    entries: list[dict[str, object]] = []
    for candidate in CANDIDATES:
        source = root.joinpath(*Path(candidate.relative_path).parts)
        if not source.is_file():
            raise FileNotFoundError(source)
        group_dir = audio_output / safe_group(candidate.group)
        group_dir.mkdir(parents=True, exist_ok=True)
        destination = group_dir / source.name
        shutil.copy2(source, destination)
        entries.append({
            **asdict(candidate),
            "source": candidate.relative_path,
            "local": destination.relative_to(output).as_posix(),
            "metadata": probe(source),
        })

    report_path = output / "candidates.json"
    report_path.write_text(json.dumps({"licenses": licenses, "candidates": entries}, indent=2), encoding="utf-8")
    page_path = output / "index.html"
    page_path.write_text(render(entries, licenses), encoding="utf-8")
    print(f"Built {len(entries)} candidates at {page_path}")
    if args.open_browser:
        webbrowser.open(page_path.as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

