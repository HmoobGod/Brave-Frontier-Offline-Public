"""v179: 2014 historical AI syntax is source evidence only, never 2022 AI."""
import json
from collections import Counter
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
D = ROOT/"source_data"
report=json.loads((D/"bf_global_historical_six_ai_evidence_v179.json").read_text("utf8"))
assert report["schema"]=="bf-global-historical-six-2014-ai-source-v179"
assert report["sourceEra"]=="2014 Global captured; NOT original 2022 native enemy AI"
assert report["gameplayMutation"] is False and report["saveMutation"] is False
assert report["sourceActionSemanticsDecoded"] is False
assert report["original2022AIConfirmed"] is False
assert len(report["patterns"])==13 and len(report["missions"])==6
expected_ids=[300,330,332,333,334,364]
assert [m["id"] for m in report["missions"]]==expected_ids
all_actions=Counter()
wave_count=slot_count=0
used_patterns=set()
for m in report["missions"]:
 old=json.loads((D/"historical_2014_v178"/f"mission_{m['id']}.json").read_text("utf8"))
 assert m["sourcePath"]==old["sourcePath"] and m["gitBlobSha"]==old["gitBlobSha"]
 assert len(m["waves"])==len(old["waves"])
 for widx,(new_wave,old_wave) in enumerate(zip(m["waves"],old["waves"])):
  assert len(new_wave)==len(old_wave["enemies"]) and len(new_wave)>0, (m["id"],widx)
  wave_count+=1
  for slot,(e,original) in enumerate(zip(new_wave,old_wave["enemies"])):
   assert type(e) is list and len(e)==4,(m["id"],widx,slot,e)
   unit,ai,counts,pattern_idx=e
   assert type(unit) is int and unit==original["unitId"]
   assert type(ai) is int and ai==original["aiId"]
   assert type(pattern_idx) is int and 0<=pattern_idx<len(report["patterns"])
   assert isinstance(counts,str) and re.fullmatch(r"[0-9]+~[0-9]+",counts),counts
   low,high=map(int,counts.split("~"))
   assert low>0 and low<=high<=6,(m["id"],widx,slot,counts)
   pattern=report["patterns"][pattern_idx]
   used_patterns.add(pattern_idx)
   assert set(pattern)=={"name","actions"}
   assert isinstance(pattern["name"],str) and pattern["name"]
   assert isinstance(pattern["actions"],list) and pattern["actions"]
   for action in pattern["actions"]:
    assert set(action)=={"action","conditions/set parameters","percent","target conditions","target type"}
    assert isinstance(action["action"],dict)
    assert set(action["action"])=={"type","parameters"}
    assert action["action"]["type"] in {"attack","skill","turn_end"}
    assert isinstance(action["action"]["parameters"],str)
    assert type(action["percent"]) is int and 0<=action["percent"]<=100
    assert isinstance(action["target conditions"],str)
    assert type(action["target type"]) is int
    conditions=action["conditions/set parameters"]
    assert isinstance(conditions,list)
    assert all(type(c) is dict and set(c)=={"type","parameters"} and
               isinstance(c["type"],str) and isinstance(c["parameters"],str)
               for c in conditions)
    all_actions[action["action"]["type"]]+=1
   slot_count+=1
assert (wave_count,slot_count)==(56,192),(wave_count,slot_count)
assert used_patterns==set(range(13))
assert all_actions=={"attack":330,"turn_end":25,"skill":28},all_actions
assert len({json.dumps(p,sort_keys=True,ensure_ascii=False) for p in report["patterns"]})==13
src=(D/"bf_global_historical_six_ai_evidence_v179.json").read_text("utf8")
assert "bf_global_offline_demo_v7" not in src
assert "2022 native enemy AI" in src and '"original2022AIConfirmed": false' in src
# This data is never part of the Android runtime or APK assets.
java=(ROOT/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
assert "bf_global_historical_six_ai_evidence_v179" not in java
assert not (ROOT/"app/src/main/assets/bf179_historical_six_ai.js").exists()
print("PASS v179: 6 original 2014 captures, 56 waves, 192 AI assignments, 13 literal action patterns, no 2022 claims or runtime activation")
