"""v221 APK regression: byte-original Legend Stone thumbnail, no save/API change."""
from pathlib import Path
import hashlib
import json
import zipfile

R = Path(__file__).resolve().parent
A = R / "app/src/main/assets"
APK = R / "app/build/outputs/apk/debug/app-debug.apk"
META = json.loads((R / "source_data/bf_global_2022_legend_stone_item_art_v221.json").read_text("utf8"))
IMAGE = "content/item/item_thum_111000.png"
JS = "bf15300_legend_stone_merit_source.js"
SOURCE_SHA = "c3decdc9ce4403cf12bf022b0ff233f802b11883105d125a6c0877d85135e0e7"
assert META["sourceAssetPath"] == IMAGE and META["pngSha256"] == SOURCE_SHA
asset = (A / IMAGE).read_bytes()
assert len(asset) == 6370 and hashlib.sha256(asset).hexdigest() == SOURCE_SHA
js = (A / JS).read_bytes()
assert b"bf22100-legend-stone-item-icon" in js
assert b"content/item/item_thum_111000.png" in js
with zipfile.ZipFile(APK) as apk:
    assert apk.testzip() is None
    assert apk.read("assets/" + IMAGE) == asset
    assert apk.read("assets/" + JS) == js
    html = apk.read("assets/index.html")
    assert b"bf_global_offline_demo_v7" in html
    java = (R / "app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
    assert 'readPackagedText("bf15300_legend_stone_merit_source.js")' in java
    assert "applicationId 'org.bravefrontier.offline'" in (R / "app/build.gradle").read_text("utf8")
    assert "android.permission.INTERNET" not in (R / "app/src/main/AndroidManifest.xml").read_text("utf8")
assert META["changesGameplay"] is False and META["changesSaves"] is False
print("PASS v221 real APK: byte-original 2022 Legend Stone PNG and read-only source panel, unchanged v7 app identity")
