"""v229 static contract: packaged main-frame failure offers native retry without editing saves."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
java = (ROOT / "app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf-8")
manifest = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf-8")
nav = (ROOT / "app/src/main/assets/bf_home_nav.js").read_text("utf-8")

def has(text):
    assert text in java, "Missing native startup recovery guard: " + text

has('private static final String OFFLINE_MAIN_PAGE = "file:///android_asset/index.html";')
has("private boolean offlinePageLoadFailed = false;")
has("private android.app.AlertDialog offlinePageFailureDialog;")
has("private void offerOfflinePageRetry(WebView failedView)")
has("if (offlinePageFailureDialog != null || game != failedView ||")
has("isFinishing() || isDestroyed()) return;")
has('.setTitle("Offline game could not start")')
has(".setPositiveButton(\"Try again\", (dialog, which) -> {")
has("offlinePageLoadFailed = false;")
has("failedView.loadUrl(OFFLINE_MAIN_PAGE);")
has(".setNegativeButton(\"Close\", (dialog, which) -> {")
has(".setCancelable(false)")
has("private void dismissOfflinePageError()")
has("offlinePageFailureDialog.dismiss();")
has("onReceivedError(WebView view,")
has("android.webkit.WebResourceRequest request")
has("android.webkit.WebResourceError error")
has("request == null || !request.isForMainFrame()")
has("!OFFLINE_MAIN_PAGE.equals(String.valueOf(request.getUrl()))")
has("offlinePageLoadFailed = true;")
has("offerOfflinePageRetry(view);")
has("if (!OFFLINE_MAIN_PAGE.equals(url) || offlinePageLoadFailed) return;")
has('game.loadUrl("file:///android_asset/index.html");')
has("onRenderProcessGone(")
has("dismissOfflinePageError();")
has("onDestroy()")

# Scope restrictions: new branch must not introduce save manipulation or Internet.
section=java[java.index("private boolean offlinePageLoadFailed"):java.index("private static final int PICK_BACKGROUND")]
assert "localStorage" not in section and "save" not in section.lower().replace("saved progress","").replace("saved data",""), "Unexpected save manipulation"
assert 'window.BF_homeNav = {go,get current()' in nav
assert "android.permission.INTERNET" not in manifest
assert 'android:usesCleartextTraffic="false"' in manifest
assert java.count("offerOfflinePageRetry(view);") == 1
assert java.count("onReceivedError(WebView view,") == 1

# Clearly distinguish WebView main-frame load failure from subresource errors.
assert re.search(r"if \(view != game \|\| request == null \|\| !request\.isForMainFrame\(\) \|\|\s*!OFFLINE_MAIN_PAGE\.equals\(String\.valueOf\(request\.getUrl\(\)\)\)\) return;",java)
print("PASS v229: offline main-frame-only retry, render-error cleanup, no save changes or INTERNET permission")
