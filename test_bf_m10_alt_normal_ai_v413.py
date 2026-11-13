"""v413: independently pinned 2014 alternate wave-four attack-only evidence.

No user account, save, 2022 group/wave, or gameplay data is written.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
D=ROOT/"source_data"
source=json.loads((D/"bf_m10_alternate_2014_action_evidence_v413.json").read_text("utf8"))
alt=json.loads((D/"bf_mission10_dual_2014_capture_v411.json").read_text("utf8"))
assert source["schema"]=="bf-global-2014-m10-alternate-normal-attack-evidence-v413"
assert source["sourceEra"]==2014 and source["missionId"]==10 and source["wave"]==4
assert source["original2022Confirmed"] is False
assert source["changesCanonicalBattle"] is False
assert source["changesRewardsOrSave"] is False
assert source["source"]["repository"]=="cheahjs/bravefrontier_data"
assert source["source"]["gitBlobSha"]==alt["alternate"]["gitBlobSha"]
assert source["source"]["sourcePath"]==alt["alternate"]["sourcePath"]
assert source["normalAttack"]=={
 "type":"attack","parameters":"-1","percent":100,
 "targetCondition":"random","targetType":2,"conditions":0,
 "actionsPerTurn":"1~1","skills":0,
}
assert [r["slot"] for r in source["enemies"]]==[0,1,2]
assert all(type(v) is int for r in source["enemies"] for k,v in r.items() if k!="name")
assert [{key:r[key] for key in ("name","unitId","hp","atk","def","aiId")}
        for r in source["enemies"]]==alt["wave4Alternate"]
assert source["enemies"]==[
 {"slot":0,"unitId":10030,"name":"Burny","hp":800,"atk":320,"def":50,"aiId":1},
 {"slot":1,"unitId":50030,"name":"Glowy","hp":850,"atk":340,"def":60,"aiId":1},
 {"slot":2,"unitId":30030,"name":"Mossy","hp":830,"atk":340,"def":90,"aiId":1},
]
js=(ROOT/"app/src/main/assets/bf200_historical_wave_lab.js").read_text("utf8")
builder=(ROOT/"prepare_historical_wave_lab_v200.py").read_text("utf8")
fulltest=(ROOT/"test_bf_historical_wave_lab_v200.py").read_text("utf8")
assert "BF200_M10_AI_PLACEHOLDER" in js
assert "BF200_M10_AI_READY" in builder
assert "BF200_M10_AI_READY" in fulltest
assert "witness.source?.gitBlobSha!==m10Alternate.gitBlobSha" in js
assert "action.type" in js and "action.targetType" in js
assert "sourceBacked:true" in js
assert "nativeRandomTargetImplemented:false" in js
assert "syntheticHarm:Math.max(12,Math.ceil(source.atk/12))" in js
assert "2014 source AI:" in fulltest
for forbidden in ("localStorage", "saveProgress(", "BFAndroid", "XMLHttpRequest", "fetch("):
 assert forbidden not in js,forbidden
assert len(js.encode("utf8"))<65536
print("PASS v413: exact original 2014 alternate normal actions (3/3), "
      "no 2022 claim, no save/economy/AI promotion")
