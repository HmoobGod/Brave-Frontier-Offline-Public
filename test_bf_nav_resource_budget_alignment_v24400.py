"""v244: legacy navigation-size tests agree with the Android packaged loader.

Source-only gate. The original quest and dungeon tests still run end-to-end in
the APK workflow; this gate only audits their resource-size assertions.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
JAVA = (ROOT / "app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
WORKFLOW = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf8")
PREFLIGHT = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")

LEGACY = (
    "test_bf_quest_english_data_v048.py",
    "test_bf_remains_mirza_v049.py",
    "test_bf_monsters_nest_v050.py",
    "test_bf_tower_of_mistral_v051.py",
)
assert re.search(r"NAV_RESOURCE_LIMIT_BYTES\s*=\s*128\s*\*\s*1024", JAVA)
assert re.search(r"UI_RESOURCE_LIMIT_BYTES\s*=\s*64\s*\*\s*1024", JAVA)
assert 'return "bf_home_nav.js".equals(file) || "bf_home_nav.css".equals(file)' in JAVA
assert "? NAV_RESOURCE_LIMIT_BYTES : UI_RESOURCE_LIMIT_BYTES;" in JAVA
assert 'if (out.size() + count > maxBytes) throw new IOException("Oversized UI resource");' in JAVA

for filename in LEGACY:
    script = (ROOT / filename).read_text("utf8")
    assert "bf_home_nav.js" in script, filename
    assert len(re.findall(r"(?m)^assert len\([^\n]+\)\s*<=\s*128\s*\*\s*1024\b", script)) == 1, filename
    assert "< 65536" not in script, filename
    assert WORKFLOW.count(f"python {filename}") == 1, filename

assert WORKFLOW.count("python3 test_bf_nav_resource_budget_alignment_v24400.py") == 1
assert PREFLIGHT.count("test_bf_nav_resource_budget_alignment_v24400.py") == 2
for filename in ("bf_home_nav.js", "bf_home_nav.css"):
    count = (ASSETS / filename).stat().st_size
    assert 0 < count <= 128 * 1024, (filename, count)
assert "test_bf_engine_ui_asset_budget_v22800.py" in WORKFLOW
print("PASS v244: v048-v051 tests share Android nav-only 128KiB cap; other UI stays 64KiB")
