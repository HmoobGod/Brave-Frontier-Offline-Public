"""v230 integrated-only source checks, not device or Java runtime verification."""
from pathlib import Path
import re

root = Path(__file__).resolve().parent
java = (root/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
css = (root/"app/src/main/assets/bf_home_nav.css").read_text("utf8")
nav = (root/"app/src/main/assets/bf_home_nav.js").read_text("utf8")
manifest = (root/"app/src/main/AndroidManifest.xml").read_text("utf8")
workflow = (root/".github/workflows/build-debug-apk.yml").read_text("utf8")

required = [
    "test_bf_android_back_home_v22500.py",
    "test_bf_engine_webview_recovery_v22600.py",
    "test_bf_engine_ui_touch_v22700.py",
    "test_bf_engine_ui_asset_budget_v22800.py",
    "test_bf_offline_page_recovery_v22900.py",
    "test_bf_prepared_amdahl_full_android_chain_v20800.py",
]
for test in required:
    assert (root/test).is_file(), test
    assert len(re.findall(r"^\s*python3? "+re.escape(test)+r"$", workflow, re.M)) == 1, test

# Feature/source composition: ensure the consolidated HEAD retained the actual
# native features, not just the named test files.
for token in (
    "UI_BACK_JS", "backDispatchToken", "UI_BACK_TIMEOUT_MS",
    "onRenderProcessGone(", "dismissOfflinePageError();",
    "onReceivedError(WebView view,", "offerOfflinePageRetry(view);",
    "if (!OFFLINE_MAIN_PAGE.equals(url) || offlinePageLoadFailed) return;",
    "packagedUiResourceLimit(String file)",
    '"bf_home_nav.js".equals(file) || "bf_home_nav.css".equals(file)',
    "NAV_RESOURCE_LIMIT_BYTES = 128 * 1024",
    "UI_RESOURCE_LIMIT_BYTES = 64 * 1024",
):
    assert token in java, "Missing integrated native feature: "+token
for token in ("/* v227: Home/route touch", "min-height:60px;", "touch-action:manipulation;",
              "focus-visible", "prefers-reduced-motion:reduce"):
    assert token in css, "Missing integrated UI feature: "+token
assert css.rfind("min-height:60px;") > css.index("/* v227: Home/route touch")
assert "window.BF_homeNav = {go,get current()" in nav
assert "android.permission.INTERNET" not in manifest
assert 'android:usesCleartextTraffic="false"' in manifest

# Tests prove only source composition. Device acceptance and native compile
# must be verified separately. Player-save values are NOT modified.
assert "localStorage" not in java
assert "bf_global_offline_demo_v7" not in java
print("PASS v230: v225-v229 engine/UI source and CI gates composed without gameplay/save modifications")
