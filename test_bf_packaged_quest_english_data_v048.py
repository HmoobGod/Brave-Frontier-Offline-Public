"""Verify the v0.48 original Global text extraction in the signed APK."""
from pathlib import Path
from zipfile import ZipFile
import json

ROOT = Path(__file__).resolve().parent
base = json.loads((ROOT / "source_data/bf_global_quest_en_2022.json").read_text("utf-8"))
missions = list(base["missions"])
for f in ("bf_global_egor_snowfield_v045.json",
          "bf_global_forest_of_beasts_v046.json",
          "bf_global_magutagal_v047.json"):
    missions.extend(json.loads((ROOT / "source_data" / f).read_text("utf-8"))["english"])
descriptions = {r["id"]: r["description"] for r in missions}
assert len(descriptions) == 21
apk = ROOT / "app/build/outputs/apk/debug/app-debug.apk"
with ZipFile(apk) as z:
    html = z.read("assets/index.html").decode("utf-8")
    nav = z.read("assets/bf_home_nav.js")
    assert html.count("/* BF_GLOBAL_QUEST_TEXT_DATA_V048 */") == 1
    assert html.count("window.BF_QUEST_ENGLISH_DESCRIPTIONS=") == 1
    literal = json.dumps(descriptions, sort_keys=True, ensure_ascii=True,
                         separators=(",", ":")).replace("<", "\\u003c")
    assert "window.BF_QUEST_ENGLISH_DESCRIPTIONS=Object.freeze(" + literal + ");" in html
    assert len(nav) < 65536, len(nav)
    assert b"BF_GLOBAL_QUEST_TEXT_DATA_V048" in nav
    assert b"Thunder Blasting Wetlands" in nav
    assert b"The Thundering Strategist" in nav
    assert b"Magutagal Wetlands" in nav
    assert b"bf_global_offline_demo_v7" in z.read("assets/index.html")
    for older in ("BF_EVOLUTION_ROADMAP_V039", "BF_BATTLE_BB_GUIDE_V040",
                  "BF_EXPERIMENTAL_SBB_V044", "BF_EGOR_SNOWFIELD_V045",
                  "BF_FOREST_OF_BEASTS_V046", "BF_MAGUTAGAL_WETLANDS_V047"):
        assert html.count("/* " + older + " */") == 1, older
print("PASS v0.48 packaged: all 21 exact Global descriptions, smaller nav, v7 and v0.39–v0.47")
