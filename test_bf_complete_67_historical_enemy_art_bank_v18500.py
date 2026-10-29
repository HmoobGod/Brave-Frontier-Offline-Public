"""v185: finish original BF1 archived battle visual source for 67 historical enemy IDs.

No native 2022 enemy wave/formations/AI/drops or original animation
playback claims. Does not stage or activate any Android assets.
"""
from pathlib import Path
import base64,hashlib,io,json,zipfile

R=Path(__file__).resolve().parent
D=R/"source_data"
old=(R/"source_assets/bf1/BF1_Global_54_Historical_Battle_Visuals_v184.zip.b64")
new=(R/"source_assets/bf1/BF1_Global_13_Historical_Battle_Visuals_v185.zip.b64")
f184=base64.b64decode(old.read_text("ascii"),validate=True)
f185=base64.b64decode(new.read_text("ascii"),validate=True)
assert hashlib.sha256(f184).hexdigest()=="1c450f3487cbb4ec4c6a7103d35ec5b6680d575de4094c6fc39f0ff4084d9914"
assert len(f185)==394697
assert hashlib.sha256(f185).hexdigest()=="81136fa4ba29f7d8a58da3d5583ea10536c6d2ba48d383338d94dfa6b9e5dd3a"
srcSHA={
 "BF1_unit_part001.zip":"c0f03306a4e5efd2513c982ac58b12fff2d72c9ff978b19a839f8932536fc846",
 "BF1_unit_part002.zip":"09f1f3ee682886c3382ac9e3679f2b9d35c056b76d4999913124aa68ca024056"
}
historic=json.loads((D/"bf_global_historical_encounters_v120.json").read_text("utf8"))["missions"]
hist200=[json.loads(p.read_text("utf8")) for p in sorted((D/"historical_2014_v200").glob("mission_*.json"))]
hist178=[json.loads(p.read_text("utf8")) for p in sorted((D/"historical_2014_v178").glob("mission_*.json"))]
assert len(historic)==4 and len(hist200)==17 and len(hist178)==6
missions=historic+hist200+hist178
ids={e["unitId"] for m in missions for w in m["waves"] for e in w["enemies"]}
assert len(ids)==67
precovered={10022,10030,10031,10040,10041,10050,10051,10061,10071,10081,10082,10102,10103}
assert len(precovered)==13

# Check source-perfect 54+13 ID sets and per-file original art provenance.
v184_ids=set()
with zipfile.ZipFile(io.BytesIO(f184)) as z:
 assert z.testzip() is None
 for part in (1,2,3):
  part_zip=z.read(f"BF1_Global_18_Archived_Enemy_Battle_Visuals_Part{part}_v184.zip")
  with zipfile.ZipFile(io.BytesIO(part_zip)) as q:
   m=json.loads(q.read(f"BF1_Battle_Visuals_Part{part}_Provenance_v184.json"))
   assert m["native2022EnemyFormationVerified"] is False
   assert m["native2022BattleSpriteAssignmentVerified"] is False
   assert m["sourceArchiveSha256"]==srcSHA
   assert len(m["unitIds"])==18
   assert not v184_ids.intersection(m["unitIds"])
   v184_ids.update(m["unitIds"])
assert len(v184_ids)==54 and not v184_ids.intersection(precovered)
assert ids==v184_ids|precovered

with zipfile.ZipFile(io.BytesIO(f185)) as z:
 assert z.testzip() is None
 ledger_name="BF1_13_Enemy_Visuals_Provenance_v185.json"
 m=json.loads(z.read(ledger_name))
 assert m["schema"]=="bf-global-original-bf1-thirteen-enemy-battle-visuals-v185"
 assert m["unitCount"]==13 and set(m["unitIds"])==precovered
 assert m["sourceArchiveSha256"]==srcSHA
 assert m["native2022EnemyFormationVerified"] is False
 assert m["native2022BattleSpriteAssignmentVerified"] is False
 assert len(m["files"])==74
 assert len(z.namelist())==75
 assert {e["path"] for e in m["files"]}|{ledger_name}==set(z.namelist())
 for e in m["files"]:
  uid=e["unitId"]
  assert uid in precovered and e["sourceArchive"] in srcSHA
  assert str(uid) in e["path"]
  blob=z.read(e["path"])
  assert len(blob)==e["bytes"] and hashlib.sha256(blob).hexdigest()==e["sha256"]
  if e["path"].endswith(".png"):
   assert blob.startswith(b"\x89PNG\r\n\x1a\n")
  else:assert e["path"].endswith(".csv")
 for uid in precovered:
  assert {f"content/unit/img/unit_anime_{uid}.png",
          f"content/unit/img/unit_ills_battle_{uid}.png",
          f"content/unit/cgg/unit_cgg_{uid}.csv",
          f"content/unit/cgs/unit_idle_cgs_{uid}.csv",
          f"content/unit/cgs/unit_atk_cgs_{uid}.csv"}.issubset({e["path"] for e in m["files"]})
 assert sum(e["path"].endswith(".png") for e in m["files"])==26
 assert sum(e["path"].endswith(".csv") for e in m["files"])==48
assert 300+len(m["files"])==374
assert "v185" not in (R/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
assert "bf_global_offline_demo_v7" in (R/"app/src/main/assets/index.html").read_text("utf8")
print("PASS v185: all 67 historical enemy unit IDs have source-archived animation atlases, battle illustration PNGs, CGG/CGS files; read-only; no 2022 enemy AI/formation or Android activation")
