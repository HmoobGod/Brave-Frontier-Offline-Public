"""v181 read-only 2014 enemy IDs x 2022 Global unit-catalog COVERAGE audit.

An ID existing in both archives is NOT proof that the 2014 enemy formation,
HP/ATK/DEF, art, AI or rewards was used in original 2022 battles.
"""
import base64, gzip, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
D=ROOT/"source_data"
meta=json.loads((D/"bf_global_original_unit_catalog_meta.json").read_text("utf8"))
assert meta["schema"]=="bf-global-unit-archive-package-v1"
packed=base64.b64decode((D/"bf_global_original_unit_catalog.json.gz.b64").read_text("ascii"))
assert hashlib.sha256(packed).hexdigest()==meta["catalogGzipSha256"]
raw=gzip.decompress(packed)
assert hashlib.sha256(raw).hexdigest()==meta["catalogJsonSha256"]
assert len(raw)==meta["catalogJsonBytes"]
archive=json.loads(raw)
assert archive["schema"]=="bf-global-unit-archive-2022-v1"
units=archive["units"]
assert len(units)==meta["catalogRecordCount"]==2291
unit_ids={item["id"] for item in units}
assert len(unit_ids)==2291
thumbs={item["id"] for item in units if item["thumbnail"]}
assert len(thumbs)==meta["thumbnailCount"]==127

old=json.loads((D/"bf_global_historical_encounters_v120.json").read_text("utf8"))["missions"]
middle=[json.loads(p.read_text("utf8")) for p in
        sorted((D/"historical_2014_v200").glob("mission_*.json"))]
new=[json.loads(p.read_text("utf8")) for p in
     sorted((D/"historical_2014_v178").glob("mission_*.json"))]
assert (len(old),len(middle),len(new))==(4,17,6)
missions=sorted(old+middle+new,key=lambda x:x["id"])
expected_ids=[1,2,10,11,20,21,30,31,40,41,42,50,51,52,60,61,70,71,
              200,202,240,300,330,332,333,334,364]
assert [m["id"] for m in missions]==expected_ids
quest=json.loads((D/"bf_global_original_2022_live_quest_economy_v142.json").read_text("utf8"))
assert quest["sourceArchiveSha256"]=="69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
q={row[0]:row for row in quest["records"]}
assert len(q)==106

all_enemy_ids=[]
per_mission=[]
wave_total=slot_total=0
for m in missions:
 mid=m["id"]
 assert m["sourcePath"].startswith("missions_parsed/")
 assert len(m["gitBlobSha"])==40
 assert len(m["waves"])==q[mid][3]
 slots=[]
 for i,wave in enumerate(m["waves"],1):
  assert wave["wave"]==i and wave["enemies"]
  for e in wave["enemies"]:
   assert isinstance(e["name"],str) and e["name"]
   assert type(e["unitId"]) is int and e["unitId"]>=0
   assert all(type(e[k]) is int and e[k]>=0 for k in ("hp","atk","def","aiId"))
   slots.append(e["unitId"])
 assert slots
 all_enemy_ids.extend(slots)
 per_mission.append({"id":mid,"2014Waves":len(m["waves"]),"2014EnemySlots":len(slots),
    "slotsWith2022UnitId":sum(x in unit_ids for x in slots),
    "slotsWith2022Thumbnail":sum(x in thumbs for x in slots)})
 wave_total+=len(m["waves"])
 slot_total+=len(slots)
assert (len(missions),wave_total,slot_total)==(27,168,456)
assert sum(x["2014EnemySlots"] for x in per_mission)==456
unique=set(all_enemy_ids)
matched=sorted(unique & unit_ids)
unmatched=sorted(unique - unit_ids)
thumb_matches=sorted(unique & thumbs)
assert set(thumb_matches).issubset(set(matched))
assert sum(x["slotsWith2022UnitId"] for x in per_mission)==sum(i in unit_ids for i in all_enemy_ids)
assert sum(x["slotsWith2022Thumbnail"] for x in per_mission)==sum(i in thumbs for i in all_enemy_ids)
report={
 "schema":"bf-global-cross-era-2014-enemy-2022-unit-id-coverage-v181",
 "interpretation":"ID existence and 2022 archive thumbnail COVERAGE ONLY, not authentic 2022 enemy formations or art",
 "historical2014Missions":27,"historical2014Waves":168,"historical2014EnemySlots":456,
 "original2022UnitArchiveRecords":2291,"original2022CuratedUnitThumbnails":127,
 "uniqueHistoricalEnemyUnitIds":len(unique),"idsAlsoIn2022UnitCatalog":len(matched),
 "idsAbsentFrom2022UnitCatalog":unmatched,
 "idsWithCurated2022Thumbnail":len(thumb_matches),
 "missions":per_mission}
assert report["interpretation"].endswith("not authentic 2022 enemy formations or art")
# No app and no user save writes: this script merely produces stdout evidence.
java=(ROOT/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
builder=(ROOT/"prepare_historical_wave_lab_v200.py").read_text("utf8")
assert "historical_2014_v178" not in java and "historical_2014_v178" not in builder
assert "bf_global_offline_demo_v7" in (ROOT/"app/src/main/assets/index.html").read_text("utf8")
print("PASS v181: 27 historical 2014 missions / 168 waves / 456 enemy slots; source-pinned 2022 unit catalog coverage, no combat/save promotion")
print("CROSS_ERA_COVERAGE_REPORT="+json.dumps(report,sort_keys=True,separators=(",",":")))
