"""v189: stage only original-byte historical BF1 108x108 battle illustrations.

Research art in Unit Encyclopedia ONLY, independent opt-in, never a verified
2022 Global battlefield sprite assignment or a new playable enemy.
Source ZIPs were already committed/reviewed in v184/v185. No save writes.
"""
from pathlib import Path
import base64, hashlib, io, json, struct, zipfile

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
BANK184 = ROOT / "source_assets/bf1/BF1_Global_54_Historical_Battle_Visuals_v184.zip.b64"
BANK185 = ROOT / "source_assets/bf1/BF1_Global_13_Historical_Battle_Visuals_v185.zip.b64"
THUMBS183 = ROOT / "source_assets/bf1/BF1_Global_Archived_54_Enemy_Thumbnails_v183.zip.b64"
SHA184 = "1c450f3487cbb4ec4c6a7103d35ec5b6680d575de4094c6fc39f0ff4084d9914"
SHA185 = "81136fa4ba29f7d8a58da3d5583ea10536c6d2ba48d383338d94dfa6b9e5dd3a"
SHA183 = "0030b4bac35055b4ca5c4791464f56e406a37e74d4c9539f46711da8289734fd"
EARLY13 = {10022, 10030, 10031, 10040, 10041, 10050, 10051,
           10061, 10071, 10081, 10082, 10102, 10103}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read_bank(path, expected):
    raw = base64.b64decode("".join(path.read_text("ascii").split()), validate=True)
    assert digest(raw) == expected, "Original source archive hash mismatch"
    return zipfile.ZipFile(io.BytesIO(raw))

with read_bank(THUMBS183, SHA183) as thumbs:
    assert thumbs.testzip() is None
    reference = json.loads(thumbs.read("BF1_54_Archived_Portrait_Provenance_v183.json"))
    recovered54 = {row["unitId"] for row in reference["records"]}
    assert len(recovered54) == 54 and recovered54.isdisjoint(EARLY13)

images = {}
def stage_entry(archive, row):
    uid = row["unitId"]
    path = f"content/unit/img/unit_ills_battle_{uid}.png"
    if row["path"] != path:
        return
    assert uid not in images, "Duplicate source battle illustration"
    img = archive.read(path)
    assert len(img) == row["bytes"] and digest(img) == row["sha256"]
    assert img[:16] == b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    assert struct.unpack(">II", img[16:24]) == (108, 108), "Not a static battle illustration"
    images[uid] = img

with read_bank(BANK184, SHA184) as outer:
    assert outer.testzip() is None
    for part in range(1, 4):
        filename = f"BF1_Global_18_Archived_Enemy_Battle_Visuals_Part{part}_v184.zip"
        with zipfile.ZipFile(io.BytesIO(outer.read(filename))) as inner:
            assert inner.testzip() is None
            ledger = json.loads(inner.read(f"BF1_Battle_Visuals_Part{part}_Provenance_v184.json"))
            assert ledger["native2022EnemyFormationVerified"] is False
            assert ledger["native2022BattleSpriteAssignmentVerified"] is False
            for record in ledger["entries"]:
                stage_entry(inner, record)
assert set(images) == recovered54

with read_bank(BANK185, SHA185) as bank:
    assert bank.testzip() is None
    ledger = json.loads(bank.read("BF1_13_Enemy_Visuals_Provenance_v185.json"))
    assert ledger["native2022EnemyFormationVerified"] is False
    assert ledger["native2022BattleSpriteAssignmentVerified"] is False
    assert set(ledger["unitIds"]) == EARLY13
    for record in ledger["files"]:
        stage_entry(bank, record)
assert set(images) == recovered54 | EARLY13 and len(images) == 67

dest = ASSETS / "content/unit_historical_battle_archive"
dest.mkdir(parents=True, exist_ok=True)
for uid, blob in images.items():
    path = dest / f"unit_ills_battle_{uid}.png"
    if path.exists():
        assert path.read_bytes() == blob, "Attempt to overwrite different staged artwork"
    else:
        path.write_bytes(blob)
assert {p.name for p in dest.iterdir() if p.is_file()} == {
    f"unit_ills_battle_{uid}.png" for uid in images
}, "Unexpected archived battle image staged"
assert len(list((ASSETS / "content/unit_archive").glob("unit_ills_thum_*.png"))) == 127
assert len(list((ASSETS / "content/unit_historical_archive").glob("unit_ills_thum_*.png"))) == 54
assert "bf_global_offline_demo_v7" in (ASSETS / "index.html").read_text("utf8")
print("PASS v189: 67 original-byte archived BF1 battle illustrations staged separately; no combat or save changes")
