"""v191 C2 packaged gate: no stripped 2022 provenance in compiled game HTML.
Check the exact built APK assets that Android loads, not a stand-in ZIP.
"""
from pathlib import Path
import hashlib,json,re,zipfile
ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/"app/src/main/assets"
APK=ROOT/"app/build/outputs/apk/debug/app-debug.apk"
master="d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83"
zip_source="69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
java=(ROOT/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
scripts=["bf10800_2022_encounter_reference_ledger.js","bf10900_stlamia_encounter_refs.js",
 "bf15100_amdahl_encounter_evidence.js","bf17400_original_2022_encounter_crossrefs.js",
 "bf19100_original_2022_dungeon_backdrops.js"]
assert all(java.index('readPackagedText("'+a+'")')<java.index('readPackagedText("'+b+'")')
 for a,b in zip(scripts,scripts[1:]))
def payload(html,name):
 match=re.search(r"window\."+name+r"=Object\.freeze\((\{.*?\})\);",html,re.S)
 assert match,name
 return json.loads(match.group(1))
with zipfile.ZipFile(APK) as archive:
 assert archive.testzip() is None
 html=archive.read("assets/index.html").decode("utf8")
 assert html==(ASSETS/"index.html").read_text("utf8")
 assert "bf_global_offline_demo_v7" in html
 m=payload(html,"BF_MORGAN_QUEST_DATA_V080")
 st=payload(html,"BF_STLAMIA_QUEST_DATA_V090")
 assert m["provenance"]=={"mastersZipSha256":zip_source,"missionMasterSha256":master}
 assert st["provenance"]=={"missionMasterSha256":master}
 assert len(m["quests"])==len(st["quests"])==36
 for filename in scripts:
  assert archive.read("assets/"+filename)==(ASSETS/filename).read_bytes()
 assert "content/dungeon/dungeon_battle_10700.jpg" in archive.namelist() or (
   "assets/content/dungeon/dungeon_battle_10700.jpg" in archive.namelist())
print("PASS v191 real APK: source provenance survives prepare and packaging; Java v108→v109→v151→v174→v191 order, v7 intact")
