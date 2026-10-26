"""v0.48: data-driven, offline original Global quest descriptions.

Use only existing source-authenticated 2022 English fixtures. This is a
presentation refactor; it adds no quests, economy rules, or save fields.
Run after prepare_magutagal_v047.py and before the browser tests.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "source_data"
ASSETS = ROOT / "app/src/main/assets"
base = json.loads((BASE / "bf_global_quest_en_2022.json").read_text("utf-8"))
assert base["schema"] == "bf-global-quest-sgtext-english-v1"
assert base["provenance"]["archiveSha256"] == (
    "4dccce4eeb6a89cc0cf5718badff7af95046c891882e42c05c6eaca81f9d6285"
)
missions = list(base["missions"])
assert [row["id"] for row in missions] == [1, 2, 10, 11, 12, 20, 21, 22, 23]
for filename, schema in (
    ("bf_global_egor_snowfield_v045.json", "bf-global-egor-snowfield-v045"),
    ("bf_global_forest_of_beasts_v046.json", "bf-global-forest-of-beasts-v046"),
    ("bf_global_magutagal_v047.json", "bf-global-magutagal-v047"),
):
    obj = json.loads((BASE / filename).read_text("utf-8"))
    assert obj["schema"] == schema
    assert obj["sources"]["languageSha256"] == base["provenance"]["archiveSha256"]
    assert len(obj["english"]) == 4
    missions.extend(obj["english"])
expected = [1, 2, 10, 11, 12, 20, 21, 22, 23, 30, 31, 32, 33,
            40, 41, 42, 43, 50, 51, 52, 53]
assert [row["id"] for row in missions] == expected
descriptions = {}
for row in missions:
    mission_id = row["id"]
    assert row["key"] == f"MST_DUNGEONS_MISSION_{mission_id}_NAME"
    assert row["descriptionKey"] == f"MST_DUNGEONS_MISSION_{mission_id}_DESCRIPTION"
    assert isinstance(row["name"], str) and row["name"]
    assert isinstance(row["description"], str) and row["description"]
    assert mission_id not in descriptions
    descriptions[mission_id] = row["description"]

nav = (ASSETS / "bf_home_nav.js").read_text("utf-8")
assert "BF_GLOBAL_QUEST_TEXT_DATA_V048" in nav
assert "window.BF_QUEST_ENGLISH_DESCRIPTIONS" in nav
assert len(nav.encode("utf-8")) < 65536, "nav asset grew past 64 KiB"
html = ASSETS / "index.html"
s = html.read_text("utf-8")
assert "bf_global_offline_demo_v7" in s
for previous in ("/* BF_EGOR_SNOWFIELD_V045 */",
                 "/* BF_FOREST_OF_BEASTS_V046 */",
                 "/* BF_MAGUTAGAL_WETLANDS_V047 */"):
    assert s.count(previous) == 1, previous
marker = "/* BF_GLOBAL_QUEST_TEXT_DATA_V048 */"
encoded = json.dumps(descriptions, sort_keys=True, ensure_ascii=True,
                     separators=(",", ":")).replace("<", "\\u003c")
payload = "window.BF_QUEST_ENGLISH_DESCRIPTIONS=Object.freeze(" + encoded + ");"
if s.count(marker) == 1:
    assert s.count(payload) == 1, "v0.48 source text changed after staging"
    print("PASS v0.48 original Global quest text already staged")
else:
    assert s.count(marker) == 0 and s.count(payload) == 0
    assert s.count("window.BF_QUEST_BACKGROUNDS=") == 1
    s = s.replace("window.BF_QUEST_BACKGROUNDS=",
                  marker + payload + "window.BF_QUEST_BACKGROUNDS=", 1)
    assert s.count(marker) == 1 and s.count(payload) == 1
    html.write_text(s, "utf-8")
    print("PASS v0.48 source-authenticated English descriptions staged offline; save v7 untouched")
