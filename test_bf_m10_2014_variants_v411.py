"""Strict source-only checks for two distinct 2014 Start of Adventure captures."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
S=ROOT/"source_data"
data=json.loads((S/"bf_mission10_dual_2014_capture_v411.json").read_text("utf8"))
archive=json.loads((S/"bf_global_historical_encounters_v120.json").read_text("utf8"))
economy=json.loads((S/"bf_global_original_2022_live_quest_economy_v142.json").read_text("utf8"))
manifest=json.loads((ROOT/"QUEST_SOURCE_MANIFEST.json").read_text("utf8"))
rows=[m for m in archive["missions"] if m["id"]==10]
assert len(rows)==1
original=rows[0]
assert data["schema"]=="bf-global-mission10-dual-2014-capture-v411"
assert data["sourceEra"]==2014 and data["historicalPracticeOnly"] is True
assert data["native2022FormationsVerified"] is False
assert data["native2022EnemyAIAndDropsVerified"] is False
assert data["originalGameRewardsEnabled"] is False
assert data["missionId"]==original["id"]==10
assert data["missionName"]==original["name"]=="Start of Adventure"
assert data["primary"]=={"sourcePath":original["sourcePath"],"gitBlobSha":original["gitBlobSha"]}
assert original["gitBlobSha"]=="556829bc0639e417ecd4dbc99ef28c44da25c621"
assert data["alternate"]["sourcePath"]=="missions_parsed/Start of Adventure_2014-14-10-08-34.json"
assert data["alternate"]["gitBlobSha"]=="c6a9d86b7e72a079ebdaa48b84864d078e5568e3"
assert len(original["waves"])==data["waves"]==5
assert sum(len(w["enemies"]) for w in original["waves"])==data["enemySlots"]==11
assert data["identicalOtherWaves"]==[1,2,3,5]
assert data["onlyChangedWave"]==4
assert original["waves"][3]["enemies"]==data["wave4Original"]
assert [e["name"] for e in data["wave4Original"]]==["Squirty","Gloomy","Sparky"]
assert [e["name"] for e in data["wave4Alternate"]]==["Burny","Glowy","Mossy"]
assert [(e["unitId"],e["hp"],e["atk"],e["def"],e["aiId"]) for e in data["wave4Alternate"]]==[
    (10030,800,320,50,1),(50030,850,340,60,1),(30030,830,340,90,1)]
assert all(type(e["hp"]) is int and e["hp"]>0 and type(e["aiId"]) is int and e["aiId"]==1
           for e in data["wave4Alternate"])
assert data["observations"]["bothHaveOneNormalAttackPerEnemy"] is True
assert data["observations"]["normalAttackWeightPercent"]==100
assert data["observations"]["targetSelection"]=="random"
assert data["observations"]["itemDropTablesUnchangedAcrossBothCaptures"] is True
assert data["observations"]["serverGeneratorInferences"]
assert "not inspected" in data["observations"]["warning"]
assert "2022" in data["observations"]["warning"]
assert [r for r in economy["records"] if r[0]==10]==[[10,10,2,5,3,20,300,0]]
assert [q for q in manifest["quests"] if q["missionId"]==10][0]["battles"]==5
js=(ROOT/"app/src/main/assets/bf200_historical_wave_lab.js").read_text("utf8")
assert "BF200_M10_ALT_" in js and "mission10AlternateAvailable" in js
assert "captureVariant" in js
assert "current?.captureVariant==='alternate'&&current?.wave===3" in js
for forbidden in ("localStorage","saveProgress(","BFAndroid","fetch(","XMLHttpRequest"):
    assert forbidden not in js,forbidden
assert "bf_global_offline_demo_v7" not in js
assert len(js.encode("utf8"))<65536
print("PASS v411: two pinned 2014 captures, 5 waves, 11 enemies, wave 4 alternate, no original 2022 or save claims")
