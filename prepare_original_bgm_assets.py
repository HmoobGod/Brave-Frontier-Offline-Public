"""Copy byte-verified, original BF1 Global MP3s into the offline Android APK.
Never fetches from the network or touches save data. Idempotent and fail-closed.
"""
from pathlib import Path
import json, hashlib

ROOT=Path(__file__).resolve().parent
META=json.loads((ROOT/"source_data/bf_global_original_bgm.json").read_text("utf-8"))
assert META["schema"]=="bf-global-original-quest-audio-v1"
assert {t["file"] for t in META["tracks"]}=={
    "bf010_map_grass.mp3","bf011_map_firecave.mp3","bf006_btl_boss.mp3"}
assert len(META["tracks"])==3
assert sorted(sum([t["missionIds"] for t in META["tracks"]],[])) == [1,2,10,11,12,20,21,22,23]
for track in META["tracks"]:
    src=ROOT/"source_assets/bf1/audio"/track["file"]
    dest=ROOT/"app/src/main/assets/content/sound"/track["file"]
    raw=src.read_bytes()
    assert len(raw)==track["bytes"],f"Original audio size mismatch: {src}"
    assert raw[:3]==b"ID3",f"Original audio header invalid: {src}"
    assert hashlib.sha256(raw).hexdigest()==track["sha256"],f"Audio content mismatch: {src}"
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.is_file() and dest.read_bytes()==raw:
        print("Verified existing original BF1 sound:",track["file"])
    else:
        dest.write_bytes(raw)
        print("Staged lossless original BF1 sound:",track["file"])
print("PASS: exactly three archive-verifiable BF1 sound tracks; no network.")
