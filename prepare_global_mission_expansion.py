"""Expand the archived BF1 Global mission catalog at build time.

The core 4.5 MB HTML is kept byte-identical in Git. A narrow, assertive
idempotent insertion into its generated Android asset uses source_data JSON.
This happens before CI browser tests and Android Gradle packaging.

Original mission IDs, unlocks, energy, battles and standard rewards are from
F_MISSION_MST_1_Ver1118. Encounter generation and actual special drops remain
explicitly DEMO/unverified.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "app/src/main/assets/index.html"
MANIFEST = ROOT / "source_data/bf_global_missions_21_23.json"
source = json.loads(MANIFEST.read_text("utf-8"))
assert source["schema"] == "bf-global-mission-expansion-v1"
rows = source["missions"]
assert [r["missionId"] for r in rows] == [21,22,23]
assert [(r["requires"],r["battles"],r["energy"],r["exp"],r["zel"],r["karma"])
        for r in rows] == [(20,5,3,35,450,0),(21,5,4,50,500,0),(22,6,5,80,600,0)]
assert all(r["dungeonId"] == 20 and r["background"] == "dungeon_battle_10200.jpg" for r in rows)
assert all(r["missionNameKey"] == f'MST_DUNGEONS_MISSION_{r["missionId"]}_NAME' for r in rows)
assert all(r["dungeonNameKey"] == "MST_DUNGEONS_DUNGEON_20_NAME" for r in rows)
assert [r["missionId"] for r in rows] == list(range(21,24))

html = HTML.read_text("utf-8")
marker = "window.BF_QUEST_BACKGROUNDS="
begin,end = "/* BF_CAVE_20_BEGIN */","/* BF_CAVE_20_END */"
original = "window.BF_QUEST_CATALOG="
assert html.count(original) == 1
assert html.count(marker) == 1
catalog_chunk = html.split(original,1)[1]
if begin in html:
    catalog = catalog_chunk.split("];"+begin,1)[0] + "]"
else:
    catalog = catalog_chunk.split(";"+marker,1)[0]
existing = json.loads(catalog)
assert [q["missionId"] for q in existing] == [1,2,10,11,12,20]
assert all(q["background"] in ("dungeon_battle_10100.jpg","dungeon_battle_10200.jpg") for q in existing)
assert len({r["missionId"] for r in existing+rows}) == 9

payload = begin+"window.BF_QUEST_CATALOG.push("+",".join(json.dumps(row, separators=(",",":"),ensure_ascii=True) for row in rows)+");"+end
if html.count(begin) == 1 and html.count(end) == 1:
    assert payload in html, "Existing quest expansion differs from source manifest; refusing to overwrite"
    print("Verified existing 21–23 quest insertion; no changes.")
elif begin not in html and end not in html:
    old = "];"+marker
    assert html.count(old) == 1
    html = html.replace(old, "];"+payload+marker, 1)
    HTML.write_text(html, "utf-8")
    print("Prepared original IDs 21–23 and 9-mission catalog from verified BF1 Global MST.")
else:
    raise SystemExit("Incomplete quest patch marker; refusing to modify original source")
