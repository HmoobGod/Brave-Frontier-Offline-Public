"""v221: read-only proof of original 2022 Legend Stone item thumbnail bytes.

No user saves, gameplay, inventory or item grants are opened or changed.
An owner-local optional original ZIP recheck can independently reproduce hashes.
"""
from pathlib import Path
import hashlib
import json
import os
import struct
import zipfile

R = Path(__file__).resolve().parent
metadata = json.loads((R / "source_data/bf_global_2022_legend_stone_item_art_v221.json").read_text("utf8"))
prior = json.loads((R / "source_data/bf_global_2022_legend_stone_exchange_v137.json").read_text("utf8"))
icon = R / "app/src/main/assets/content/item/item_thum_111000.png"
js = (R / "app/src/main/assets/bf15300_legend_stone_merit_source.js").read_text("utf8")
source_sha = "69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
pack_sha = "735c50613f55a84d8a3717a4ee53ef513c694031aa44963c43e24b597f134e2c"
master_sha = "0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474"
icon_sha = "c3decdc9ce4403cf12bf022b0ff233f802b11883105d125a6c0877d85135e0e7"
git_blob_sha = "ce0dc4d12c3ad5806e1cf6e41424484dbf3ba924"

assert metadata["schema"] == "bf-global-2022-original-legend-stone-item-thumbnail-v221"
assert metadata["sourceArchiveSha256"] == prior["sourceArchiveSha256"] == source_sha
assert metadata["sourceItemMasterSha256"] == prior["sourceFileSha256"]["itemMaster"] == master_sha
assert metadata["sourceItemMaster"] == "3-mst-translated/F_ITEM_MST_Ver1027.json"
assert metadata["originalBF1Pack"] == "BF1_item_part001.zip"
assert metadata["originalBF1PackSizeBytes"] == 4205647
assert metadata["originalBF1PackSha256"] == pack_sha
assert (metadata["itemId"], metadata["sourceItemType"], metadata["sourceMaxStack"]) == (110100, 4, 999)
assert metadata["sourceItemName"] == "神越の魂石"
assert metadata["originalThumbnail"] == prior["sourceItem"]["itemThumbnail"] == "item_thum_111000.png"
assert prior["sourceItem"]["itemId"] == "110100"
assert prior["sourceItem"]["itemType"] == "4"
assert prior["sourceItem"]["itemMaxStack"] == "999"
assert metadata["sourceAssetPath"] == "content/item/item_thum_111000.png"

data = icon.read_bytes()
assert len(data) == metadata["pngByteLength"] == 6370
assert hashlib.sha256(data).hexdigest() == metadata["pngSha256"] == icon_sha
assert hashlib.sha1(b"blob " + str(len(data)).encode() + b"\x00" + data).hexdigest() == metadata["pngGitBlobSha1"] == git_blob_sha
assert data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR"
assert struct.unpack(">II", data[16:24]) == (98, 98)
assert (metadata["pixelWidth"], metadata["pixelHeight"]) == (98, 98)

assert js.count("content/item/item_thum_111000.png") == 1
assert js.count("bf22100-legend-stone-item-icon") == 1
assert "panel.append(title,visual,paragraph,history,notice)" in js
assert all(marker not in js for marker in (
    "saveProgress(", "localStorage.", "P.materials=", "P.unitExp=",
    "Math.random(", "fetch(", "XMLHttpRequest("))
for flag in ("visualReferenceOnly",):
    assert metadata[flag] is True
for flag in ("liveItemAcquisitionEnabled", "originalPlayerInventoryAuthenticated",
             "playableSevenStarEnabled", "changesGameplay", "changesCombat", "changesSaves"):
    assert metadata[flag] is False

owner_master = os.environ.get("BF_ORIGINAL_2022_MST_ZIP")
if owner_master:
    raw = Path(owner_master).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source_sha
    with zipfile.ZipFile(owner_master) as z:
        original = z.read(metadata["sourceItemMaster"])
    assert hashlib.sha256(original).hexdigest() == master_sha
    matches = [r for r in json.loads(original) if r.get("itemId") == "110100"]
    assert len(matches) == 1
    assert matches[0]["itemThumbnail"] == metadata["originalThumbnail"]
    assert matches[0]["itemName"] == metadata["sourceItemName"]

owner_pack = os.environ.get("BF_ORIGINAL_2022_ITEM_PACK_ZIP")
if owner_pack:
    raw = Path(owner_pack).read_bytes()
    assert len(raw) == 4205647 and hashlib.sha256(raw).hexdigest() == pack_sha
    with zipfile.ZipFile(owner_pack) as z:
        assert z.read(metadata["sourceAssetPath"]) == data

print("PASS v221: 2022 Global Legend Stone original PNG source, icon identity, image dimensions and no save/game changes")
