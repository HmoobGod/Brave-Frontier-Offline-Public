"""v183: verify byte-exact archived BF1 unit portrait files, not playable enemies.

This archive is a historical art source bank only. An archived unit thumbnail
does not establish a native 2022 combat sprite, battle roster, AI, or drops.
"""
from pathlib import Path
import base64, gzip, hashlib, io, json, re, zipfile

R=Path(__file__).resolve().parent
D=R/"source_data"
packed_path=R/"source_assets/bf1/BF1_Global_Archived_54_Enemy_Thumbnails_v183.zip.b64"
raw_b64=packed_path.read_text("ascii")
assert re.fullmatch(r"[A-Za-z0-9+/=\r\n]+",raw_b64)
zipbytes=base64.b64decode(raw_b64,validate=True)
assert len(zipbytes)==381418
assert hashlib.sha256(zipbytes).hexdigest()=="0030b4bac35055b4ca5c4791464f56e406a37e74d4c9539f46711da8289734fd"

source_meta=json.loads((D/"bf_global_original_unit_catalog_meta.json").read_text("utf8"))
assert source_meta["sourceArchiveSha256"]=="ad937083a4d023228f8796d45e5edd6adaf575872270476be994121941db3556"
b64=base64.b64decode((D/"bf_global_original_unit_catalog.json.gz.b64").read_text("ascii"))
assert hashlib.sha256(b64).hexdigest()==source_meta["catalogGzipSha256"]
original=json.loads(gzip.decompress(b64))
assert original["schema"]=="bf-global-unit-archive-2022-v1"
by_id={u["id"]:u for u in original["units"]}
assert len(by_id)==2291

v120=json.loads((D/"bf_global_historical_encounters_v120.json").read_text("utf8"))["missions"]
v200=[json.loads(p.read_text("utf8")) for p in sorted((D/"historical_2014_v200").glob("mission_*.json"))]
v178=[json.loads(p.read_text("utf8")) for p in sorted((D/"historical_2014_v178").glob("mission_*.json"))]
assert (len(v120),len(v200),len(v178))==(4,17,6)
all_missions=v120+v200+v178
ids={e["unitId"] for m in all_missions for wave in m["waves"] for e in wave["enemies"]}
assert len(ids)==67 and ids.issubset(by_id)
missing={uid for uid in ids if not by_id[uid]["thumbnail"]}
assert len(missing)==54
assert sum(len(w["enemies"]) for m in all_missions for w in m["waves"])==456

with zipfile.ZipFile(io.BytesIO(zipbytes)) as z:
 assert z.testzip() is None
 names=z.namelist()
 assert len(names)==55 and len(set(names))==55
 ledger="BF1_54_Archived_Portrait_Provenance_v183.json"
 assert ledger in names
 report=json.loads(z.read(ledger))
 assert report["schema"]=="bf-global-archived-fifty-four-portrait-source-bundle-v183"
 assert report["numberOfPortraits"]==54
 assert report["originalSourceArchiveSha256"]==source_meta["sourceArchiveSha256"]
 assert report["totalPngBytes"]==377608
 assert len(report["records"])==54
 assert {e["unitId"] for e in report["records"]}==missing
 assert len({e["unitId"] for e in report["records"]})==54
 for e in report["records"]:
  uid=e["unitId"]
  name=f"content/unit/img/unit_ills_thum_{uid}.png"
  assert e["originalArchivePath"]==name
  assert e["authentic2022Formation"] is False
  assert e["authentic2022BattlefieldSprite"] is False
  blob=z.read(name)
  assert blob.startswith(b"\x89PNG\r\n\x1a\n")
  assert len(blob)==e["bytes"]
  assert hashlib.sha256(blob).hexdigest()==e["sha256"]
 assert set(names)=={ledger}|{f"content/unit/img/unit_ills_thum_{uid}.png" for uid in missing}
 assert sum(e["bytes"] for e in report["records"])==377608
# Explicit fail-closed: don't load extra historical portraits in Android yet.
java=(R/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
assert "BF1_Global_Archived_54_Enemy_Thumbnails_v183" not in java
assert "v183" not in java
assert "bf_global_offline_demo_v7" in (R/"app/src/main/assets/index.html").read_text("utf8")
print("PASS v183: 54 byte-exact archived BF1 PNG portraits recovered and independently SHA pinned; original 2022 formations/AI/field battle art NOT verified; no Android/save activation")
