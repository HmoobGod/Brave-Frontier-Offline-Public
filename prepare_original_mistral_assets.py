"""Stage the exact, source-hashed original Global Mistral area artwork.

Read-only; source files are immutable, downloaded separately from the user's
original BF1 area ZIP. Does not change the game core, quests or save schema.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
metadata=json.loads((ROOT/"source_data/bf_global_mistral_map.json").read_text("utf-8"))
assert metadata["schema"]=="bf-global-mistral-map-v1"
assert metadata["land"]=={"id":1,"areaId":100,"name":"Mistral","originalMapImage":"area_0001.jpg","originalBannerImage":"area_plate_0001.png","requiredMission":0}
assert [(x["id"],x["areaId"],x["x"],x["y"],x["requires"]) for x in metadata["dungeons"]]==[
    (1,100,400,780,0),(10,100,378,829,0),(20,100,36,698,12)]
for data in metadata["art"]:
    path=ROOT/"source_assets/bf1/area"/data["file"]
    raw=path.read_bytes()
    assert len(raw)==data["bytes"],("source image changed",path)
    assert hashlib.sha256(raw).hexdigest()==data["sha256"],("source hash mismatch",path)
    assert tuple(raw[:2]) == ((255,216) if path.suffix==".jpg" else (137,80)),path
    dest=ROOT/"app/src/main/assets/content/area"/data["file"]
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.is_file() and dest.read_bytes()==raw:
        print("Verified Mistral map image:",dest.name)
    else:
        dest.write_bytes(raw)
        print("Staged original Mistral map image:",dest.name)
print("PASS verified original Global Mistral artwork and source dungeon markers.")
