"""v258: packaged UI original-image path completeness and basic image integrity.

Source-only mode checks authored asset refs and registration without requiring
build-generated sprites. Full mode runs AFTER the original asset preparation step
in signed Android CI. Does not inspect/modify gameplay, save or installed APK.
"""
from pathlib import Path
import json
import re
import struct
import sys

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
JS = (ASSETS / "bf_home_nav.js").read_text("utf8")
CSS = (ASSETS / "bf_home_nav.css").read_text("utf8")
WF = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf8")
PRE = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
MAN = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf8")

# Author-controlled static image references in the actual Global navigation
# JS and CSS; this excludes runtime unit portraits, which vary with the save.
ART = sorted(set(re.findall(
    r"content/[a-zA-Z0-9_./-]+\.(?:png|jpg|jpeg)",
    JS + "\n" + CSS
)))
assert len(ART) >= 35, ("unexpectedly small original UI art inventory", len(ART))
assert any(x.startswith("content/home/") for x in ART)
assert any(x.startswith("content/battle/") for x in ART)
assert any(x.startswith("content/mission_select/") for x in ART)
assert any(x.startswith("content/party_edit/") for x in ART)
assert any(x.startswith("content/footer/") for x in ART)
for ref in ART:
    p = Path(ref)
    assert not p.is_absolute() and ".." not in p.parts, ref
    assert p.parts[0] == "content" and len(p.parts) >= 3, ref
assert "test_bf_ui_asset_paths_v25800.py --source-only" in PRE
assert WF.count("python3 test_bf_ui_asset_paths_v25800.py") == 1
assert "python3 prepare_original_home_assets.py" in WF
assert "python3 prepare_original_battle_controls.py" in WF
assert WF.index("python3 prepare_original_battle_controls.py") < WF.index(
    "python3 test_bf_ui_asset_paths_v25800.py"
)
assert "android.permission.INTERNET" not in MAN
assert len(JS.encode("utf8")) < 128 * 1024
assert len(CSS.encode("utf8")) < 128 * 1024
print("PASS v258 source:", len(ART), "static Global UI image references, safe paths and CI order")
if "--source-only" in sys.argv[1:]:
    raise SystemExit(0)

# Files must really exist in the built source tree, not just be named in CSS.
total_bytes = 0
for ref in ART:
    file = ASSETS / ref
    assert file.is_file(), ("Missing referenced UI artwork", ref)
    data = file.read_bytes()
    assert len(data) > 32, ("Truncated referenced UI artwork", ref)
    if ref.endswith(".png"):
        assert data.startswith(b"\x89PNG\r\n\x1a\n") and data[12:16] == b"IHDR", ref
        width, height = struct.unpack(">II", data[16:24])
        assert 0 < width <= 8192 and 0 < height <= 8192, (ref,width,height)
    else:
        assert data[:2] == b"\xff\xd8" and data[-2:] == b"\xff\xd9", ref
    total_bytes += len(data)
assert total_bytes > 15000, ("Implausibly small total UI art", total_bytes)
print("PASS v258 packaged UI artwork:", len(ART), "original referenced images;", total_bytes, "bytes")
