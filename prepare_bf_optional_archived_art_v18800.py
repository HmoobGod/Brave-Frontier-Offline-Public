"""v188 candidate: stage 54 archived BF1 portraits in an opt-in encyclopedia only.

Never overwrite the existing 127 curated 2022 thumbnails. Never activate
historical enemy encounters, gameplay battle sprites, AI, drops or saves.
Feature PR must receive independent Claude review BEFORE merge.
"""
from pathlib import Path
import base64,gzip,hashlib,io,json,zipfile
R=Path(__file__).resolve().parent
D=R/"source_data"
ASSETS=R/"app/src/main/assets"
META=json.loads((D/"bf_global_original_unit_catalog_meta.json").read_text("utf8"))
def sha(b):return hashlib.sha256(b).hexdigest()
rawcat=base64.b64decode((D/"bf_global_original_unit_catalog.json.gz.b64").read_text("ascii"),validate=True)
assert sha(rawcat)==META["catalogGzipSha256"]
archive=json.loads(gzip.decompress(rawcat))
assert len(archive["units"])==2291
curated={r["id"] for r in archive["units"] if r["thumbnail"]}
assert len(curated)==127
p=R/"source_assets/bf1/BF1_Global_Archived_54_Enemy_Thumbnails_v183.zip.b64"
data=base64.b64decode(p.read_text("ascii"),validate=True)
assert sha(data)=="0030b4bac35055b4ca5c4791464f56e406a37e74d4c9539f46711da8289734fd"
assert len(data)==381418
with zipfile.ZipFile(io.BytesIO(data)) as z:
 assert z.testzip() is None
 ledger=json.loads(z.read("BF1_54_Archived_Portrait_Provenance_v183.json"))
 assert ledger["schema"]=="bf-global-archived-fifty-four-portrait-source-bundle-v183"
 assert len(ledger["records"])==54
 ids={row["unitId"] for row in ledger["records"]}
 assert len(ids)==54 and not ids.intersection(curated)
 assert ids.issubset({u["id"] for u in archive["units"]})
 for row in ledger["records"]:
  uid=row["unitId"]
  name=f"content/unit/img/unit_ills_thum_{uid}.png"
  assert row["originalArchivePath"]==name
  assert row["authentic2022Formation"] is False
  assert row["authentic2022BattlefieldSprite"] is False
  blob=z.read(name)
  assert blob.startswith(b"\x89PNG\r\n\x1a\n")
  assert len(blob)==row["bytes"] and sha(blob)==row["sha256"]
  destination=ASSETS/f"content/unit_historical_archive/unit_ills_thum_{uid}.png"
  destination.parent.mkdir(parents=True,exist_ok=True)
  if destination.is_file():assert destination.read_bytes()==blob,"cannot overwrite existing staged art"
  else:destination.write_bytes(blob)
 assert len(list((ASSETS/"content/unit_historical_archive").glob("unit_ills_thum_*.png")))==54
 # Original curated art, all 127, must remain intact in its separate directory.
 assert len(list((ASSETS/"content/unit_archive").glob("unit_ills_thum_*.png")))==127
assert "bf_global_offline_demo_v7" in (ASSETS/"index.html").read_text("utf8")
print("PASS v188 staged 54 authentic historical BF1 PNGs under opt-in research art path; no save, 2022 native formation or battle activation")
