"""v232 source contract: a new exact packaged main-page load clears prior failure state.

These assertions do not simulate Android WebView callback ordering; real-device
page-error, retry, and renderer-loss acceptance still applies.
"""
from pathlib import Path
import re

r = Path(__file__).resolve().parent
java = (r/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf-8")
manifest = (r/"app/src/main/AndroidManifest.xml").read_text("utf-8")
workflow = (r/".github/workflows/build-debug-apk.yml").read_text("utf-8")
preflight = (r/".github/workflows/android-back-ui-source-preflight.yml").read_text("utf-8")

assert java.count("onPageStarted(WebView view, String url,") == 1
webview = java.split("game.setWebViewClient(new WebViewClient() {", 1)[1]
started = webview.split("onPageStarted(WebView view, String url,", 1)[1].split("onReceivedError(WebView view,", 1)[0]
received = webview.split("onReceivedError(WebView view,", 1)[1].split("onRenderProcessGone(", 1)[0]
finished = webview.split("onPageFinished(WebView view, String url)", 1)[1].split("try {", 1)[0]

assert "super.onPageStarted(view, url, favicon);" in started
guard = "if (view != game || !OFFLINE_MAIN_PAGE.equals(url)) return;"
assert guard in started
assert started.index(guard) < started.index("offlinePageLoadFailed = false;")
assert started.index("offlinePageLoadFailed = false;") < started.index("dismissOfflinePageError();")
assert "request == null || !request.isForMainFrame()" in received
assert "!OFFLINE_MAIN_PAGE.equals(String.valueOf(request.getUrl()))" in received
assert received.index("offlinePageLoadFailed = true;") < received.index("offerOfflinePageRetry(view);")
assert "if (!OFFLINE_MAIN_PAGE.equals(url) || offlinePageLoadFailed) return;" in finished
assert java.count("offlinePageLoadFailed = true;") == 1
assert 'failedView.loadUrl(OFFLINE_MAIN_PAGE);' in java
assert 'game.loadUrl("file:///android_asset/index.html");' in java
assert "rendererFailureDialog" in java and "dismissRendererFailureDialog();" in java
assert len(re.findall(r"^\s*python3 test_bf_offline_page_reload_v23200.py$",workflow,re.M)) == 1
assert "test_bf_offline_page_reload_v23200.py" in preflight
assert "android.permission.INTERNET" not in manifest
assert "localStorage" not in java and "bf_global_offline_demo_v7" not in java
print("PASS v232: exact main-page start clears stale error; failures still block injection; no save/network changes")
