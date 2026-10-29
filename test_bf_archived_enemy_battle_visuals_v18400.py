"""v184: verify source-perfect archived BF1 animations and battle portraits.

No assumption of 2022 game-version equality, source combat, formation, AI,
damage, drops or sprite playback timing.
"""
from pathlib import Path
import base64,hashlib,io,json,re,zipfile

R=Path(__file__).resolve().parent
packed=R/"source_assets/bf1/BF1_Global_54_Historical_Battle_Visuals_v184.zip.b64"
source_b64=packed.read_text("ascii")
assert re.fullmatch(r"[A-Za-z0-9+/=\r\n]+",source_b64)
raw=base64.b64decode(source_b64,validate=True)
assert len(raw)==1722500
assert hashlib.sha256(raw).hexdigest()=="1c450f3487cbb4ec4c6a7103d35ec5b6680d575de4094c6fc39f0ff4084d9914"
expected_parts={
 1:("BF1_Global_18_Archived_Enemy_Battle_Visuals_Part1_v184.zip","01658a91b9668d2639da59e819bf9e8658845027d24669fe61f9f503f838305c"),
 2:("BF1_Global_18_Archived_Enemy_Battle_Visuals_Part2_v184.zip","03a24ef13508d7332ef3a6a8605c012878409f0421268d3d8116a04c81b594e1"),
 3:("BF1_Global_18_Archived_Enemy_Battle_Visuals_Part3_v184.zip","74e31408b555967c9d740d4d3b419decb1a12d8721c69242721c6f61dda429bb"),
}
source_archives={
 "BF1_unit_part001.zip":"c0f03306a4e5efd2513c982ac58b12fff2d72c9ff978b19a839f8932536fc846",
 "BF1_unit_part002.zip":"09f1f3ee682886c3382ac9e3679f2b9d35c056b76d4999913124aa68ca024056",
}
# v183 independently proved those precise 54 IDs have archived unit thumbnails.
v183=base64.b64decode((R/"source_assets/bf1/BF1_Global_Archived_54_Enemy_Thumbnails_v183.zip.b64").read_text("ascii"),validate=True)
assert hashlib.sha256(v183).hexdigest()=="0030b4bac35055b4ca5c4791464f56e406a37e74d4c9539f46711da8289734fd"
with zipfile.ZipFile(io.BytesIO(v183)) as x:
 previous=json.loads(x.read("BF1_54_Archived_Portrait_Provenance_v183.json"))
 expected_ids={e["unitId"] for e in previous["records"]}
assert len(expected_ids)==54

seen_ids=set()
all_paths=set()
total_files=total_png=total_csv=0
with zipfile.ZipFile(io.BytesIO(raw)) as outer:
 assert outer.testzip() is None
 index="BF1_Global_Enemy_Battle_Visuals_v184_MultiPart_Manifest.json"
 assert set(outer.namelist())=={index}|{n for n,_ in expected_parts.values()}
 cover=json.loads(outer.read(index))
 assert len(cover)==3
 for part,(name,sha) in expected_parts.items():
  stored=outer.read(name)
  assert hashlib.sha256(stored).hexdigest()==sha
  with zipfile.ZipFile(io.BytesIO(stored)) as src:
   assert src.testzip() is None
   ledger_name=f"BF1_Battle_Visuals_Part{part}_Provenance_v184.json"
   ledger=json.loads(src.read(ledger_name))
   assert ledger["schema"]=="bf-global-archived-eighteen-battle-visuals-part-v184"
   assert ledger["part"]==part and ledger["totalParts"]==3
   assert ledger["sourceArchiveSha256"]==source_archives
   assert ledger["native2022EnemyFormationVerified"] is False
   assert ledger["native2022BattleSpriteAssignmentVerified"] is False
   ids=ledger["unitIds"]
   assert len(ids)==18 and len(set(ids))==18
   assert not seen_ids.intersection(ids)
   seen_ids.update(ids)
   assert len(ledger["entries"])>=72
   assert len(src.namelist())==len(ledger["entries"])+1
   entries={e["path"]:e for e in ledger["entries"]}
   assert len(entries)==len(ledger["entries"])
   assert set(src.namelist())=={ledger_name}|set(entries)
   for e in ledger["entries"]:
    assert e["unitId"] in ids
    assert e["archive"] in source_archives
    assert e["path"].startswith("content/unit/")
    assert str(e["unitId"]) in e["path"]
    assert e["path"] not in all_paths
    all_paths.add(e["path"])
    buf=src.read(e["path"])
    assert len(buf)==e["bytes"] and hashlib.sha256(buf).hexdigest()==e["sha256"]
    if e["path"].endswith(".png"):
     assert buf.startswith(b"\x89PNG\r\n\x1a\n")
     total_png+=1
    else:
     assert e["path"].endswith(".csv")
     total_csv+=1
    total_files+=1
   for uid in ids:
    for p in (f"content/unit/img/unit_anime_{uid}.png",
              f"content/unit/img/unit_ills_battle_{uid}.png",
              f"content/unit/cgg/unit_cgg_{uid}.csv",
              f"content/unit/cgs/unit_idle_cgs_{uid}.csv",
              f"content/unit/cgs/unit_atk_cgs_{uid}.csv"):
     assert p in entries,(part,p)
 assert seen_ids==expected_ids
 assert total_files==300 and total_png==108 and total_csv==192
 assert [x["part"] for x in cover]==[1,2,3]
 assert [x["sha256"] for x in cover]==[expected_parts[k][1] for k in (1,2,3)]
# Source bank has not been activated or used to replace any player/boss sprite.
j=(R/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
assert "v184" not in j
assert "bf_global_offline_demo_v7" in (R/"app/src/main/assets/index.html").read_text("utf8")
print("PASS v184: 54 archived BF1 unit anime sheets + 54 battle illustrations + 192 animation CSVs, exact source bytes; no 2022 formation/AI assertions, no Android/save activation")
