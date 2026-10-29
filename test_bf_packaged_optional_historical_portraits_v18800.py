"""v188 signed-package gate: original archive and opt-in historical portraits.

This test inspects the actual Gradle-built APK, not just prepared source assets.
It does not verify original 2022 battle fidelity or real-device save migration.
"""
from pathlib import Path
import base64
import gzip
import hashlib
import io
import json
import os
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent
APK = ROOT / "app/build/outputs/apk/debug/app-debug.apk"
ASSETS = ROOT / "app/src/main/assets"
SOURCE = ROOT / "source_assets/bf1/BF1_Global_Archived_54_Enemy_Thumbnails_v183.zip.b64"
CURATED = ROOT / "source_assets/bf1/BF1_Global_2022_Unit_Archive_Thumbs_Curated.zip.b64"
CATALOG = ROOT / "source_data/bf_global_original_unit_catalog.json.gz.b64"
META = json.loads((ROOT / "source_data/bf_global_original_unit_catalog_meta.json").read_text("utf-8"))

def sha(blob):
    return hashlib.sha256(blob).hexdigest()

assert APK.is_file(), "Signed/debug APK must be built before v188 packaged gate"
original = base64.b64decode("".join(SOURCE.read_text("ascii").split()), validate=True)
assert len(original) == 381418
assert sha(original) == "0030b4bac35055b4ca5c4791464f56e406a37e74d4c9539f46711da8289734fd"
curated = base64.b64decode("".join(CURATED.read_text("ascii").split()), validate=True)
assert sha(curated) == META["thumbnailZipSha256"]
cat_gz = base64.b64decode("".join(CATALOG.read_text("ascii").split()), validate=True)
assert sha(cat_gz) == META["catalogGzipSha256"]
catalog = json.loads(gzip.decompress(cat_gz))
assert len(catalog["units"]) == META["catalogRecordCount"] == 2291
original_ids = {u["id"] for u in catalog["units"] if u["thumbnail"]}
assert len(original_ids) == META["thumbnailCount"] == 127

with zipfile.ZipFile(io.BytesIO(original)) as source, \
     zipfile.ZipFile(io.BytesIO(curated)) as cur, \
     zipfile.ZipFile(APK) as apk:
    assert source.testzip() is None
    assert cur.testzip() is None
    assert apk.testzip() is None
    ledger = json.loads(source.read("BF1_54_Archived_Portrait_Provenance_v183.json"))
    assert ledger["schema"] == "bf-global-archived-fifty-four-portrait-source-bundle-v183"
    records = ledger["records"]
    ids = {record["unitId"] for record in records}
    assert len(records) == len(ids) == 54
    assert not ids.intersection(original_ids)
    assert ids.issubset({unit["id"] for unit in catalog["units"]})

    names = set(apk.namelist())
    extra = [name for name in names if name.startswith("assets/content/unit_historical_archive/")]
    assert len(extra) == 54, f"Unexpected APK historical art count: {len(extra)}"
    expected_extra = set()
    for row in records:
        unit_id = row["unitId"]
        orig = f"content/unit/img/unit_ills_thum_{unit_id}.png"
        assert row["originalArchivePath"] == orig
        assert row["authentic2022Formation"] is False
        assert row["authentic2022BattlefieldSprite"] is False
        image = source.read(orig)
        packaged = f"assets/content/unit_historical_archive/unit_ills_thum_{unit_id}.png"
        expected_extra.add(packaged)
        assert packaged in names, f"Missing staged portrait: {packaged}"
        assert len(image) == row["bytes"] and sha(image) == row["sha256"]
        assert apk.read(packaged) == image, f"APK portrait bytes changed: {packaged}"
    assert set(extra) == expected_extra

    curated_names = [n for n in cur.namelist() if not n.endswith("/")]
    assert len(curated_names) == 127
    for path in curated_names:
        packaged = "assets/" + path
        assert packaged in names, f"Missing curated portrait: {packaged}"
        assert apk.read(packaged) == cur.read(path), f"Curated artwork changed: {path}"

    archive_js = apk.read("assets/bf_global_unit_archive.js").decode("utf-8")
    archive_css = apk.read("assets/bf_global_unit_archive.css").decode("utf-8")
    assert archive_js == (ASSETS / "bf_global_unit_archive.js").read_text("utf-8")
    assert archive_css == (ASSETS / "bf_global_unit_archive.css").read_text("utf-8")
    match = re.search(r"historicalArtIds\s*=\s*new Set\(\[([0-9,\s]+)\]\)", archive_js)
    assert match, "Missing numeric archived-art allowlist in compiled JS"
    id_list = [int(value.strip()) for value in match.group(1).split(",")]
    assert len(id_list) == 54 and set(id_list) == ids, "APK archive allowlist differs from ledger"
    assert 'id="bf-v188-historical-art" type="checkbox" />' in archive_js, "Opt-in must ship unchecked"
    assert "Archived BF1 art · exact 2022 Global client revision unverified" in archive_js
    assert "content/unit_historical_archive/unit_ills_thum_" in archive_js
    assert "ART PENDING" in archive_js
    assert "localStorage.setItem(" not in archive_js and "saveProgress(" not in archive_js

    html = apk.read("assets/index.html").decode("utf-8")
    assert "bf_global_offline_demo_v7" in html
    assert html == (ASSETS / "index.html").read_text("utf-8")
    payload = re.search(r'<script type="application/json" id="bf-global-unit-catalog-data">(.*?)</script>', html, re.S)
    assert payload, "Missing 2022 source catalog in compiled HTML"
    shipped_catalog = json.loads(payload.group(1))
    assert len(shipped_catalog["units"]) == 2291
    assert sum(bool(u["thumbnail"]) for u in shipped_catalog["units"]) == 127

# Inspect COMPILED AndroidManifest.xml permissions through the SDK, not just the
# source manifest (which may be altered at manifest merge time).
sdk = Path(os.environ.get("ANDROID_HOME", os.environ.get("ANDROID_SDK_ROOT", "")))
aapt = sdk / "build-tools/35.0.0/aapt"
assert aapt.is_file(), f"Android SDK aapt missing: {aapt}"
permissions = subprocess.run(
    [str(aapt), "dump", "permissions", str(APK)], check=True,
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
).stdout
assert "package:" in permissions, "Could not inspect built Android permissions"
assert "android.permission.INTERNET" not in permissions, "Unexpected internet permission in APK"
print("PASS v188 packaged APK: 54 ledger-exact opt-in PNGs, 127 original PNGs, "
      "2,291 records, default-OFF allowlist, v7 save marker and no INTERNET permission")
