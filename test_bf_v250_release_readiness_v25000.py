"""v250: release-candidate source guard for the owner's next install checkpoint.

This gate does NOT install an APK, confirm a device or change the owner's
Current app/save. The exact-head full Android workflow must still pass.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
WF = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf8")
PRE = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
GRADLE = (ROOT / "app/build.gradle").read_text("utf8")
MAN = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf8")
J = (ROOT / "app/src/main/assets/bf_home_nav.js").read_bytes()
C = (ROOT / "app/src/main/assets/bf_home_nav.css").read_bytes()

# The in-place update identity and certificate must remain the same.
assert "applicationId 'org.bravefrontier.offline'" in GRADLE
assert "applicationIdSuffix '.diagnostic'" in GRADLE
assert "storeFile file(" in GRADLE and "bf-development-debug.keystore" in GRADLE
assert "signingConfig signingConfigs.debug" in GRADLE
assert "project.findProperty('ciVersionCode')" in GRADLE
assert "versionName '250.00.0-demo'" in GRADLE
assert "versionName '174.00.0-demo'" not in GRADLE
assert "BF_DEBUG_KEYSTORE_B64" in WF
assert "printf '%s' " in WF and "base64 --decode" in WF
assert "android.permission.INTERNET" not in MAN
assert 'android:usesCleartextTraffic="false"' in MAN

# No wider permission or replacement of the user's Current app is necessary.
assert 0 < len(J) <= 128 * 1024
assert 0 < len(C) <= 128 * 1024
assert "test_bf_nav_resource_budget_alignment_v24400.py" in WF
for name in (
    "test_bf_home_ui_priority_v24200.py",
    "test_bf_home_ui_accessibility_v24300.py",
    "test_bf_home_semantic_hierarchy_v24500.py",
    "test_bf_home_preview_nameplates_v24600.py",
    "test_bf_home_shortcuts_mobile_v24700.py",
    "test_bf_home_squad_mobile_v24800.py",
    "test_bf_home_ui_release_readiness_v24900.py",
):
    assert re.search(r"\bpython3? " + re.escape(name) + r"\b", WF), name

# Source and APK migration tests must run in the signed build's CI pipeline.
for name in (
    "test_bf_real_v124_save_upgrade_v16500.py",
    "test_bf_packaged_real_v124_save_upgrade_v16500.py",
    "test_bf_legacy_v7_save_loading_v20500.py",
    "test_bf_packaged_imp_canonical_v17100.py",
    "test_bf_isolated_diagnostic_build_v23700.py",
):
    assert re.search(r"\bpython3? " + re.escape(name) + r"\b", WF), name

# The default installable debug APK and diagnostic APKs remain distinct;
# downloadable artifacts are produced by green CI, NOT local save mutation.
assert re.search(
    r"name:\s*BraveFrontierOffline-demo-debug-apk\s*\n\s*path:\s*app/build/outputs/apk/debug/app-debug.apk",
    WF
)
assert re.search(
    r"name:\s*BraveFrontierOffline-isolated-diagnostic-apk\s*\n\s*path:\s*app/build/outputs/apk/diagnostic/app-diagnostic.apk",
    WF
)
assert "if-no-files-found: error" in WF
assert "gradle --no-daemon" in WF
assert WF.count("python3 test_bf_v250_release_readiness_v25000.py") == 1
assert PRE.count("test_bf_v250_release_readiness_v25000.py") == 2
print("PASS v250 source: unchanged app identity/signing, offline manifest, save tests, Home UI gates and named APK artifacts")

if "--source-only" in sys.argv:
    raise SystemExit(0)

# Full Android CI is required in addition to source tests; do not imply
# human acceptance or direct APK installation from this script.
print("PASS v250 pre-release contract (not physical device or owner save acceptance)")
