"""v180: 27 captured 2014 Global source quests vs pinned 2022 quest wave counts.

This is CROSS-ERA COUNT PARITY only. Never asserts original 2022 enemy
identity, formation, AI, drop rates, status mechanics or other combat behavior.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent
D=ROOT/"source_data"
v120=json.loads((D/"bf_global_historical_encounters_v120.json").read_text("utf8"))
old=v120["missions"]
archive2014=[json.loads(p.read_text("utf8"))
             for p in sorted((D/"historical_2014_v200").glob("mission_*.json"))]
six=[json.loads(p.read_text("utf8"))
     for p in sorted((D/"historical_2014_v178").glob("mission_*.json"))]
assert len(old)==4 and len(archive2014)==17 and len(six)==6
assert "2014" in v120["caution"] and "NOT confirmed 2022" in v120["caution"]
all2014=sorted(old+archive2014+six,key=lambda m:m["id"])
ids=[1,2,10,11,20,21,30,31,40,41,42,50,51,52,60,61,70,71,
     200,202,240,300,330,332,333,334,364]
assert [row["id"] for row in all2014]==ids
assert len(set(ids))==27
source=json.loads((D/"bf_global_original_2022_live_quest_economy_v142.json").read_text("utf8"))
assert source["readOnly"] is True and source["year"]==2022
assert source["total"]==106 and len(source["records"])==106
assert source["sourceArchiveSha256"]=="69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
assert source["missionMasterSha256"]=="d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83"
assert source["columns"]==["missionId","missionDungeonId","requiredMissionId",
                          "missionBattleCount","missionEnergyUse","exp","zel","karma"]
by_id={row[0]:row for row in source["records"]}
assert len(by_id)==106 and set(ids).issubset(by_id)
observations=[]
for m in all2014:
 mid=m["id"]
 assert isinstance(m["name"],str) and m["name"]
 assert m["sourcePath"].startswith("missions_parsed/")
 assert len(m["gitBlobSha"])==40
 assert all(c in "0123456789abcdef" for c in m["gitBlobSha"])
 waves=m["waves"]
 assert waves and len(waves)==by_id[mid][3],(mid,len(waves),by_id[mid][3])
 assert [w["wave"] for w in waves]==list(range(1,len(waves)+1))
 slots=0
 for w in waves:
  assert w["enemies"]
  for e in w["enemies"]:
   assert e["name"] and all(type(e[k]) is int and e[k]>=0
    for k in ("unitId","hp","atk","def","aiId"))
   slots+=1
 if mid in (300,330,332,333,334,364):
  assert m["sourceEra"]=="historical-2014-not-2022"
  for key in ("native2022FormationVerified","native2022EnemyAIVerified",
              "native2022DropRatesVerified"):
   assert m[key] is False
 observations.append((mid,len(waves),slots))
assert len(observations)==27
assert sum(w for _,w,_ in observations)==168
assert sum(n for _,_,n in observations)==456
assert len([x for x in observations if by_id[x[0]][3]!=x[1]])==0
# Neither the live Java loader nor historical 21-quest practice builder loads
# the newer six retained 2014 mission records.
java=(ROOT/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
builder=(ROOT/"prepare_historical_wave_lab_v200.py").read_text("utf8")
assert "historical_2014_v178" not in java
assert "historical_2014_v178" not in builder
assert "(D/'historical_2014_v200').glob('mission_*.json')" in builder
assert "bf_global_offline_demo_v7" in (ROOT/"app/src/main/assets/index.html").read_text("utf8")
print("PASS v180: 27 historical 2014 missions, 168 source waves, 456 enemy slots; 27/27 original 2022 WAVE COUNTS match. Enemy formations/AI/drops NOT verified and NEVER activated.")
