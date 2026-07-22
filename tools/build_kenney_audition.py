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
    purpose: str
    relative_path: str


PURPOSES: list[tuple[str, str]] = [
    ("taunt.all", "Taunt — either role"),
    ("taunt.prop", "Taunt — prop"),
    ("taunt.hunter", "Taunt — hunter"),
    ("weapon.fire", "Hunter weapon fire"),
    ("weapon.dry_fire", "Weapon unavailable / dry fire"),
    ("weapon.reload", "Weapon reload"),
    ("weapon.cooldown_ready", "Weapon cooldown ready"),
    ("weapon.hit_confirm", "Local validated-hit confirmation"),
    ("impact.prop", "Impact on a disguised prop"),
    ("impact.world", "Generic scenery impact"),
    ("impact.wood", "Wood impact"),
    ("impact.metal", "Metal impact"),
    ("impact.plastic", "Plastic impact"),
    ("impact.glass", "Glass impact"),
    ("player.prop_hurt", "Prop-player hurt reaction"),
    ("player.eliminated", "World-positioned elimination"),
    ("disguise.preview", "Disguise candidate preview"),
    ("disguise.invalid", "Invalid disguise candidate"),
    ("disguise.apply", "Apply disguise"),
    ("disguise.remove", "Remove disguise"),
    ("movement.prop_lock", "Lock prop orientation / position"),
    ("movement.prop_unlock", "Unlock prop movement"),
    ("footstep.hunter", "Hunter footstep"),
    ("footstep.prop", "Prop movement / footstep"),
    ("prop.scrape", "Prop scrape / drag"),
    ("ui.accept", "UI accept / confirm"),
    ("ui.back", "UI back / cancel"),
    ("ui.error", "UI error / invalid action"),
    ("ui.ready", "Player enters ready state"),
    ("ui.unready", "Player leaves ready state"),
    ("ui.player_join", "Lobby player joined"),
    ("ui.player_leave", "Lobby player left"),
    ("ui.countdown_tick", "General countdown tick"),
    ("ui.last_seconds_tick", "Urgent final-seconds tick"),
    ("ui.hover", "UI hover"),
    ("ui.notification", "General UI notification"),
    ("round.hiding_start", "Hiding phase starts"),
    ("round.seeking_start", "Hunters released"),
    ("round.prop_win", "Props win"),
    ("round.hunter_win", "Hunters win"),
    ("round.local_win", "Local player victory announcement"),
    ("round.local_loss", "Local player defeat announcement"),
    ("round.local_eliminated", "Local player enters spectating"),
    ("round.thirty_seconds", "Thirty-second warning"),
    ("round.ten_seconds", "Ten-second warning"),
    ("round.time_up", "Round time expired"),
    ("round.last_prop", "Last prop alive"),
    ("round.overtime", "Overtime / sudden death"),
    ("round.cancelled", "Round or session cancelled"),
    ("round.ambient_stinger", "Non-positional tension stinger"),
]
PURPOSE_LABELS = dict(PURPOSES)


def numbered(group: str, purpose: str, prefix: str, values: range, digits: int = 3) -> list[Candidate]:
    return [Candidate(group, purpose, f"{prefix}{value:0{digits}d}.ogg") for value in values]


CANDIDATES: list[Candidate] = [
    *numbered("Impact - prop soft", "impact.prop", "Audio/Impact Sounds/Audio/impactSoft_medium_", range(5)),
    *numbered("Impact - world generic", "impact.world", "Audio/Impact Sounds/Audio/impactGeneric_light_", range(5)),
    *numbered("Impact - wood", "impact.wood", "Audio/Impact Sounds/Audio/impactWood_medium_", range(5)),
    *numbered("Impact - metal", "impact.metal", "Audio/Impact Sounds/Audio/impactMetal_light_", range(5)),
    *numbered("Impact - glass", "impact.glass", "Audio/Impact Sounds/Audio/impactGlass_light_", range(5)),
    *numbered("Weapon A - Sci-Fi laserSmall", "weapon.fire", "Audio/Sci-Fi Sounds/Audio/laserSmall_", range(5)),
    *[Candidate("Weapon B - Digital laser", "weapon.fire", f"Audio/Digital Audio/Audio/laser{value}.ogg") for value in range(1, 10)],
    *[Candidate("Disguise - apply phaserUp", "disguise.apply", f"Audio/Digital Audio/Audio/phaserUp{value}.ogg") for value in range(1, 8)],
    *[Candidate("Disguise - remove phaserDown", "disguise.remove", f"Audio/Digital Audio/Audio/phaserDown{value}.ogg") for value in range(1, 4)],
    *numbered("UI - accept confirmation", "ui.accept", "Audio/Interface Sounds/Audio/confirmation_", range(1, 5)),
    *numbered("UI - back", "ui.back", "Audio/Interface Sounds/Audio/back_", range(1, 5)),
    *numbered("UI - error", "ui.error", "Audio/Interface Sounds/Audio/error_", range(1, 9)),
    *numbered("UI - ready toggle", "ui.ready", "Audio/Interface Sounds/Audio/toggle_", range(1, 5)),
    *numbered("UI - disguise preview select", "disguise.preview", "Audio/Interface Sounds/Audio/select_", range(1, 9)),
]


def add_named(group: str, purpose: str, directory: str, names: list[str]) -> None:
    CANDIDATES.extend(Candidate(group, purpose, f"{directory}/{name}.ogg") for name in names)


def add_named_purposes(group: str, directory: str, values: list[tuple[str, str]]) -> None:
    CANDIDATES.extend(Candidate(group, purpose, f"{directory}/{name}.ogg") for name, purpose in values)


add_named_purposes("Voice style - Synth Voice 2", "Audio/Synth Voice 2/Audio", [
    ("ready", "round.hiding_start"), ("gameStart", "round.seeking_start"), ("youWin", "round.local_win")
])
add_named_purposes("Voice style - Synth Voice 1", "Audio/Synth Voice 1/Audio", [
    ("ready", "round.hiding_start"), ("game_start", "round.seeking_start"), ("you_win", "round.local_win")
])
add_named_purposes("Voice style - human male", "Audio/Voiceover Pack/Audio (Male)", [
    ("ready", "round.hiding_start"), ("go", "round.seeking_start"), ("you_win", "round.local_win")
])
add_named_purposes("Voice style - human female", "Audio/Voiceover Pack/Audio (Female)", [
    ("ready", "round.hiding_start"), ("go", "round.seeking_start"), ("you_win", "round.local_win")
])
add_named_purposes("Synth Voice 2 - round", "Audio/Synth Voice 2/Audio", [
    ("timeUp", "round.time_up"), ("hurryUp", "round.thirty_seconds"),
    ("eliminated", "round.local_eliminated"), ("victory", "round.local_win"),
    ("defeat", "round.local_loss"), ("youLose", "round.local_loss"),
    ("suddenDeath", "round.overtime")
])
add_named("Synth Voice 2 - neutral taunts", "taunt.all", "Audio/Synth Voice 2/Audio", [
    "areYouReady", "letsDoThis", "okay", "yes", "hurryUp", "lookOut"
])
add_named("Synth Voice 2 - prop taunts", "taunt.prop", "Audio/Synth Voice 2/Audio", [
    "goAway", "giveUp", "imTooTired", "iCannotDoThat", "untouchable", "targetLost", "youNeedMoreCredits"
])
add_named("Synth Voice 2 - hunter taunts", "taunt.hunter", "Audio/Synth Voice 2/Audio", [
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
            purpose = str(item["purpose"])
            purpose_label = PURPOSE_LABELS[purpose]
            review_key = html.escape(f"{purpose}::{item['source']}")
            metadata = item.get("metadata", {})
            details = (
                f'{metadata.get("durationSeconds", "?")} s · '
                f'{metadata.get("channels", "?")} ch · '
                f'{metadata.get("sampleRateHz", "?")} Hz'
            )
            cards.append(f'''<article class="clip" data-key="{review_key}" data-source="{source}" data-purpose="{html.escape(purpose)}" data-group="{html.escape(group)}">
  <div class="clip-heading"><div><h3>{html.escape(Path(source).stem)}</h3><p>{html.escape(details)}</p></div><span class="state">Pending</span></div>
  <div class="purpose"><span>Proposed purpose</span><strong>{html.escape(purpose_label)}</strong><code>{html.escape(purpose)}</code></div>
  <audio controls preload="none" src="{local}"></audio>
  <div class="decision-row" role="group" aria-label="Review decision">
    <button type="button" class="decision" data-value="approve">Approve for this purpose</button>
    <button type="button" class="decision" data-value="disapprove">Disapprove</button>
  </div>
  <div class="disapproval" hidden>
    <label>Why disapprove?
      <select class="reason">
        <option value="">Choose a reason…</option>
        <option value="poor_for_prop_hunt">Poor fit for Prop Hunt</option>
        <option value="suggest_other_purpose">Suggest for a different purpose</option>
      </select>
    </label>
    <label class="alternate-wrap" hidden>Suggested purpose
      <select class="alternate-purpose"><option value="">Choose another purpose…</option></select>
    </label>
  </div>
  <label class="notes-label">Optional notes<textarea class="notes" rows="2" placeholder="Tone, mix, repetition, or assignment notes"></textarea></label>
</article>''')
        sections.append(f'<section class="candidate-group"><h2>{html.escape(group)}</h2><div class="grid">{"".join(cards)}</div></section>')

    license_items = "".join(
        f"<li>{html.escape(pack)} — {html.escape(path)}</li>" for pack, path in licenses.items()
    )
    purpose_data = json.dumps([{"id": purpose_id, "label": label} for purpose_id, label in PURPOSES])
    entry_data = json.dumps([
        {
            "key": f"{entry['purpose']}::{entry['source']}",
            "source": entry["source"],
            "group": entry["group"],
            "proposedPurpose": entry["purpose"],
            "metadata": entry["metadata"],
        }
        for entry in entries
    ])
    template = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Prop Hunt audio assignment review</title>
<style>
:root { color-scheme:dark; font-family:Inter,ui-sans-serif,system-ui,sans-serif; background:#0b1020; color:#e8edf7 }
* { box-sizing:border-box } body { margin:0 auto; padding:0 2rem 4rem; max-width:1600px }
[hidden] { display:none!important }
header { padding:2.5rem 0 1.25rem } h1 { margin:0; font-size:clamp(2rem,4vw,3.5rem); letter-spacing:-.04em }
header p { max-width:850px; color:#aab5c8; font-size:1.05rem; line-height:1.55 }
.toolbar { position:sticky; top:0; z-index:5; display:flex; flex-wrap:wrap; gap:.75rem; align-items:end; padding:1rem; margin:0 -1rem 2rem; border:1px solid #27324a; border-radius:0 0 1rem 1rem; background:#0b1020f2; backdrop-filter:blur(12px) }
.toolbar label { min-width:170px; flex:1 } .toolbar .search { flex:2; min-width:220px }
label { display:grid; gap:.35rem; color:#aab5c8; font-size:.8rem; font-weight:650; letter-spacing:.02em }
select,input,textarea { width:100%; border:1px solid #394761; border-radius:.55rem; background:#111a2d; color:#f5f7fb; padding:.65rem .75rem; font:inherit }
textarea { resize:vertical } button { border:1px solid #41506b; border-radius:.55rem; background:#18233a; color:#f5f7fb; padding:.68rem .9rem; font-weight:700; cursor:pointer }
button:hover { border-color:#7182a1; background:#202e49 } #submit { background:#3758d6; border-color:#5877ee; white-space:nowrap }
#summary { flex-basis:100%; color:#aab5c8; font-size:.9rem } #submit-result { flex-basis:100%; min-height:1.2rem; color:#8dd8ab }
.candidate-group { margin:2.5rem 0 } .candidate-group>h2 { margin:0 0 1rem; font-size:1.35rem }
.grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(315px,1fr)); gap:1rem }
.clip { display:grid; gap:.85rem; align-content:start; padding:1rem; border:1px solid #2d3952; border-radius:.9rem; background:linear-gradient(145deg,#141e33,#10182a); box-shadow:0 12px 30px #02061730 }
.clip.approved { border-color:#2f8f5b } .clip.disapproved { border-color:#aa4854 } .clip.invalid { outline:2px solid #f59e0b }
.clip-heading { display:flex; gap:1rem; justify-content:space-between; align-items:start }.clip h3 { margin:0; font-size:1rem; overflow-wrap:anywhere }.clip p { margin:.2rem 0 0; color:#8290a8; font-size:.8rem }
.state { padding:.25rem .48rem; border-radius:999px; background:#26334b; color:#bcc7d9; font-size:.72rem; font-weight:800; text-transform:uppercase }.approved .state { background:#174d32; color:#a7f3c4 }.disapproved .state { background:#612a32; color:#fecdd3 }
.purpose { display:grid; gap:.2rem; padding:.7rem; border-radius:.6rem; background:#0b1325 }.purpose span { color:#75839b; font-size:.72rem; text-transform:uppercase; letter-spacing:.08em }.purpose strong { font-size:.95rem }.purpose code { color:#8ea6ff; font-size:.78rem }
audio { width:100%; height:40px }.decision-row { display:grid; grid-template-columns:1.35fr 1fr; gap:.55rem }.decision.active[data-value=approve] { background:#17643c; border-color:#36ad6e }.decision.active[data-value=disapprove] { background:#762d38; border-color:#cf5868 }
.disapproval { display:grid; grid-template-columns:1fr 1fr; gap:.65rem; padding:.75rem; border:1px solid #4c3340; border-radius:.65rem; background:#211520 }.notes-label { margin-top:auto }
.empty { padding:3rem; text-align:center; color:#8290a8 }.license { margin-top:3rem; color:#8997ad; font-size:.8rem }.license li { margin:.35rem 0; overflow-wrap:anywhere }
@media(max-width:700px) { body { padding:0 1rem 3rem }.toolbar { margin:0 -.5rem 1.5rem }.disapproval { grid-template-columns:1fr }.grid { grid-template-columns:1fr } }
</style></head><body>
<header><h1>Prop Hunt audio assignment review</h1>
<p>Preview each curated Kenney candidate and approve it for its proposed gameplay purpose. If it is wrong for that assignment, mark it as a poor overall fit or redirect it to another purpose. Progress saves automatically in this browser.</p></header>
<form id="review-form">
<div class="toolbar">
  <label class="search">Find a clip<input id="search" type="search" placeholder="Filename, group, or purpose"></label>
  <label>Purpose<select id="purpose-filter"><option value="all">All purposes</option></select></label>
  <label>Decision<select id="decision-filter"><option value="all">All decisions</option><option value="pending">Pending</option><option value="approve">Approved</option><option value="disapprove">Disapproved</option></select></label>
  <button id="submit" type="submit">Submit reviewed decisions</button>
  <div id="summary" aria-live="polite"></div><div id="submit-result" aria-live="polite"></div>
</div>
__SECTIONS__
<div id="empty" class="empty" hidden>No clips match the current filters.</div>
</form>
<section class="license"><h2>Verified source licenses</h2><ul>__LICENSES__</ul></section>
<script>
const PURPOSES=__PURPOSES__; const ENTRIES=__ENTRIES__; const storageKey='zeep-kenney-assignment-review-v2';
const saved=JSON.parse(localStorage.getItem(storageKey)||'{}'); const cards=[...document.querySelectorAll('.clip')];
const purposeLabel=Object.fromEntries(PURPOSES.map(item=>[item.id,item.label]));
const purposeFilter=document.querySelector('#purpose-filter');
for(const purpose of PURPOSES){ const option=new Option(`${purpose.label} (${purpose.id})`,purpose.id); purposeFilter.add(option); }
for(const card of cards){ const select=card.querySelector('.alternate-purpose'); for(const purpose of PURPOSES){ if(purpose.id!==card.dataset.purpose) select.add(new Option(`${purpose.label} (${purpose.id})`,purpose.id)); } }
function stateFor(card){ return saved[card.dataset.key]||{}; }
function persist(){ localStorage.setItem(storageKey,JSON.stringify(saved)); refresh(); }
function updateCard(card){
  const state=stateFor(card); card.classList.toggle('approved',state.decision==='approve'); card.classList.toggle('disapproved',state.decision==='disapprove');
  for(const button of card.querySelectorAll('.decision')) button.classList.toggle('active',button.dataset.value===state.decision);
  card.querySelector('.state').textContent=state.decision==='approve'?'Approved':state.decision==='disapprove'?'Disapproved':'Pending';
  const panel=card.querySelector('.disapproval'); panel.hidden=state.decision!=='disapprove';
  card.querySelector('.reason').value=state.reason||''; const alternateWrap=card.querySelector('.alternate-wrap'); alternateWrap.hidden=state.reason!=='suggest_other_purpose';
  card.querySelector('.alternate-purpose').value=state.suggestedPurpose||''; card.querySelector('.notes').value=state.notes||'';
}
function refresh(){
  let approved=0,disapproved=0,pending=0,visible=0; const term=document.querySelector('#search').value.trim().toLowerCase(); const decision=document.querySelector('#decision-filter').value; const purpose=purposeFilter.value;
  for(const card of cards){ updateCard(card); const state=stateFor(card); if(state.decision==='approve') approved++; else if(state.decision==='disapprove') disapproved++; else pending++;
    const haystack=`${card.dataset.source} ${card.dataset.group} ${card.dataset.purpose} ${purposeLabel[card.dataset.purpose]}`.toLowerCase(); const decisionValue=state.decision||'pending';
    const show=(!term||haystack.includes(term))&&(decision==='all'||decision===decisionValue)&&(purpose==='all'||purpose===card.dataset.purpose); card.hidden=!show; if(show) visible++;
  }
  for(const section of document.querySelectorAll('.candidate-group')) section.hidden=![...section.querySelectorAll('.clip')].some(card=>!card.hidden);
  document.querySelector('#empty').hidden=visible!==0; document.querySelector('#summary').textContent=`${approved} approved · ${disapproved} disapproved · ${pending} pending · ${visible} shown`;
}
for(const card of cards){
  for(const button of card.querySelectorAll('.decision')) button.addEventListener('click',()=>{ const previous=stateFor(card); saved[card.dataset.key]={...previous,decision:button.dataset.value}; if(button.dataset.value==='approve'){ saved[card.dataset.key].reason=null; saved[card.dataset.key].suggestedPurpose=null; } card.classList.remove('invalid'); persist(); });
  card.querySelector('.reason').addEventListener('change',event=>{ const state=stateFor(card); state.reason=event.target.value||null; if(state.reason!=='suggest_other_purpose') state.suggestedPurpose=null; saved[card.dataset.key]=state; card.classList.remove('invalid'); persist(); });
  card.querySelector('.alternate-purpose').addEventListener('change',event=>{ const state=stateFor(card); state.suggestedPurpose=event.target.value||null; saved[card.dataset.key]=state; card.classList.remove('invalid'); persist(); });
  card.querySelector('.notes').addEventListener('input',event=>{ const state=stateFor(card); state.notes=event.target.value; saved[card.dataset.key]=state; localStorage.setItem(storageKey,JSON.stringify(saved)); });
  card.querySelector('audio').addEventListener('play',event=>{ for(const audio of document.querySelectorAll('audio')) if(audio!==event.target) audio.pause(); });
}
for(const control of [document.querySelector('#search'),purposeFilter,document.querySelector('#decision-filter')]) control.addEventListener('input',refresh);
document.querySelector('#review-form').addEventListener('submit',async event=>{
  event.preventDefault(); const invalid=[]; for(const card of cards){ card.classList.remove('invalid'); const state=stateFor(card); if(state.decision==='disapprove'&&(!state.reason||(state.reason==='suggest_other_purpose'&&!state.suggestedPurpose))){ card.classList.add('invalid'); invalid.push(card); } }
  if(invalid.length){ document.querySelector('#submit-result').textContent=`Complete the disapproval details on ${invalid.length} highlighted clip(s).`; invalid[0].scrollIntoView({behavior:'smooth',block:'center'}); return; }
  const reviews=ENTRIES.filter(entry=>saved[entry.key]?.decision).map(entry=>{ const state=saved[entry.key]; return {...entry,proposedPurposeLabel:purposeLabel[entry.proposedPurpose],decision:state.decision,disapprovalReason:state.reason||null,suggestedPurpose:state.suggestedPurpose||null,suggestedPurposeLabel:state.suggestedPurpose?purposeLabel[state.suggestedPurpose]:null,notes:(state.notes||'').trim()}; });
  const payload={schemaVersion:1,submittedAt:new Date().toISOString(),sourceCollection:'Kenney Game Assets All-in-1 3.6.0',possiblePurposes:PURPOSES,reviews,summary:{total:cards.length,reviewed:reviews.length,approved:reviews.filter(item=>item.decision==='approve').length,disapproved:reviews.filter(item=>item.decision==='disapprove').length,unreviewed:cards.length-reviews.length}};
  const text=JSON.stringify(payload,null,2); const blob=new Blob([text],{type:'application/json'}); const link=document.createElement('a'); link.href=URL.createObjectURL(blob); link.download='kenney-audio-review.json'; link.click(); URL.revokeObjectURL(link.href);
  try{ await navigator.clipboard.writeText(text); document.querySelector('#submit-result').textContent=`Downloaded kenney-audio-review.json and copied ${reviews.length} reviewed decisions to the clipboard.`; }catch{ document.querySelector('#submit-result').textContent=`Downloaded kenney-audio-review.json with ${reviews.length} reviewed decisions.`; }
});
refresh();
</script></body></html>'''
    return (template
        .replace("__SECTIONS__", "".join(sections))
        .replace("__LICENSES__", license_items)
        .replace("__PURPOSES__", purpose_data)
        .replace("__ENTRIES__", entry_data))


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
