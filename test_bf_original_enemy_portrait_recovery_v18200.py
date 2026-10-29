"""v182 deterministic original Global *portrait* recovery backlog for historical enemy IDs.

A 2022 unit-catalog ID match or thumbnail is not proof of any native 2022
enemy wave, battlefield sprite, animation or AI. This writes an optional
CI artifact only to app/build/outputs/source-audit, never the installed APK.
"""
from collections import Counter
from pathlib import Path
import base64, gzip, hashlib, json

R=Path(__file__).resolve().parent
D=R/"source_data"
m=json.loads((D/"bf_global_original_unit_catalog_meta.json").read_text("utf8"))
assert m["schema"]=="bf-global-unit-archive-package-v1"
raw_gz=base64.b64decode((D/"bf_global_original_unit_catalog.json.gz.b64").read_text("ascii"))
assert hashlib.sha256(raw_gz).hexdigest()==m["catalogGzipSha256"]
raw=gzip.decompress(raw_gz)
assert hashlib.sha256(raw).hexdigest()==m["catalogJsonSha256"]
assert len(raw)==m["catalogJsonBytes"]
catalog=json.loads(raw)
assert catalog["schema"]=="bf-global-unit-archive-2022-v1"
units=catalog["units"]
by_id={row["id"]:row for row in units}
assert len(by_id)==len(units)==m["catalogRecordCount"]==2291
thumbs={id for id,row in by_id.items() if row["thumbnail"]}
assert len(thumbs)==m["thumbnailCount"]==127

v120=json.loads((D/"bf_global_historical_encounters_v120.json").read_text("utf8"))["missions"]
v200=[json.loads(p.read_text("utf8")) for p in
      sorted((D/"historical_2014_v200").glob("mission_*.json"))]
v178=[json.loads(p.read_text("utf8")) for p in
      sorted((D/"historical_2014_v178").glob("mission_*.json"))]
assert (len(v120),len(v200),len(v178))==(4,17,6)
missions=sorted(v120+v200+v178,key=lambda x:x["id"])
source=json.loads((D/"bf_global_original_2022_live_quest_economy_v142.json").read_text("utf8"))
assert source["sourceArchiveSha256"]=="69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
by_quest={row[0]:row for row in source["records"]}
assert len(by_quest)==106

usage=Counter()
per_unit_missions={}
per_unit_waves={}
total_waves=total_slots=0
for mission in missions:
 id=mission["id"]
 assert len(mission["waves"])==by_quest[id][3]
 for i,w in enumerate(mission["waves"],1):
  assert w["wave"]==i and w["enemies"]
  for e in w["enemies"]:
   uid=e["unitId"]
   assert type(uid) is int and uid in by_id,(id,i,uid)
   usage[uid]+=1
   per_unit_missions.setdefault(uid,set()).add(id)
   per_unit_waves.setdefault(uid,set()).add((id,i))
   total_slots+=1
  total_waves+=1
assert (len(missions),total_waves,total_slots)==(27,168,456)
assert len(usage)==67
assert len(set(usage)&thumbs)==13
assert len(set(usage)-thumbs)==54
thumbnail_slots=sum(usage[uid] for uid in usage if uid in thumbs)
assert thumbnail_slots==104 and total_slots-thumbnail_slots==352

missing=[]
for uid in sorted(set(usage)-thumbs,key=lambda id:(-usage[id],id)):
 row=by_id[uid]
 name=row.get("name")
 missing.append({
  "unitId":uid,
  "source2022Name":name if isinstance(name,str) and name else None,
  "historical2014EnemyPlacements":usage[uid],
  "historical2014MissionIds":sorted(per_unit_missions[uid]),
  "historical2014DistinctWaves":len(per_unit_waves[uid]),
  "candidate2022ThumbnailFile":f"unit_ills_thum_{uid}.png",
  "thumbnailPresentInCuratedArchive":False,
  "verified2022BattlefieldSprite":False,
  "verified2022EnemyFormation":False
 })
assert len(missing)==54
assert sum(x["historical2014EnemyPlacements"] for x in missing)==352
assert all(x["historical2014EnemyPlacements"]>=1 for x in missing)

report={
 "schema":"bf-global-2022-unit-portrait-recovery-backlog-v182",
 "2022CatalogSourceSha256":m["catalogJsonSha256"],
 "provenance":"Historical captured 2014 Global enemies versus source-pinned 2022 Global UNIT CATALOG only",
 "notice":"A matched unit ID or a portrait thumbnail is NOT an original 2022 enemy formation, 2022 battlefield sprite, AI or drops",
 "historical2014Missions":27,
 "historical2014Waves":168,
 "historical2014EnemyPlacements":456,
 "uniqueHistoricalEnemyIds":67,
 "allHistoricalEnemyIdsFoundIn2022UnitCatalog":True,
 "uniqueIdsWithCurated2022Thumbnails":13,
 "historicalPlacementsWithCurated2022Thumbnails":104,
 "uniqueIdsMissingCurated2022Thumbnails":54,
 "historicalPlacementsMissingCurated2022Thumbnails":352,
 "rankedMissingPortraitBacklog":missing
}
# Place ONLY in Gradle's ignored build tree, not src/main/assets or source_data.
out=R/"app/build/outputs/source-audit/BraveFrontier-v182-historical-enemy-portrait-backlog.json"
out.parent.mkdir(parents=True,exist_ok=True)
encoded=json.dumps(report,sort_keys=True,indent=2,ensure_ascii=True)+"\n"
if out.exists():
 assert out.read_text("utf8")==encoded,"Nondeterministic art report"
else:
 out.write_text(encoded,encoding="utf8")
assert json.loads(out.read_text("utf8"))==report
assert "bf_global_offline_demo_v7" in (R/"app/src/main/assets/index.html").read_text("utf8")
assert "historical_2014_v178" not in (R/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
print("PASS v182: 67 source 2022 unit IDs, 13 portraits, 54 missing; 104 of 456 historical enemy placements have curated thumbnails; NO battle sprites or enemy formations verified")
print("ART_RECOVERY_BACKLOG="+str(out.relative_to(R)))
