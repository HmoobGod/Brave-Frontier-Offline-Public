"""v234 static regression: only the first explicit native main load resets page failure.

This validates source wiring and a small reference callback-state model, not real
Android WebView callback timing or device/save acceptance.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
java = (ROOT / "app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf-8")
manifest = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf-8")
preflight = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf-8")
workflow = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf-8")

def span(start, end):
    assert java.count(start) == 1, start
    return java.split(start, 1)[1].split(end, 1)[0]

assert java.count("private boolean nativeMainLoadRequested = false;") == 1
start = span("@Override public void onPageStarted(WebView view, String url,",
             "@Override public void onReceivedError(WebView view,")
url_guard = "if (view != game || !OFFLINE_MAIN_PAGE.equals(url)) return;"
token_guard = "if (!nativeMainLoadRequested) return;"
consume = "nativeMainLoadRequested = false;"
clear_failure = "offlinePageLoadFailed = false;"
dismiss = "dismissOfflinePageError();"
assert all(x in start for x in (url_guard, token_guard, consume, clear_failure, dismiss))
assert start.index(url_guard) < start.index(token_guard) < start.index(consume)
assert start.index(consume) < start.index(clear_failure) < start.index(dismiss)

error = span("@Override public void onReceivedError(WebView view,",
             "@Override public boolean onRenderProcessGone(")
assert error.index("request == null || !request.isForMainFrame()") < error.index(consume)
assert error.index("!OFFLINE_MAIN_PAGE.equals(String.valueOf(request.getUrl()))") < error.index(consume)
assert error.index(consume) < error.index("offlinePageLoadFailed = true;")
retry = span(".setPositiveButton(\"Try again\", (dialog, which) -> {",
             ".setNegativeButton(\"Close\", (dialog, which) -> {")
assert retry.index(clear_failure) < retry.index("nativeMainLoadRequested = true;")
assert retry.index("nativeMainLoadRequested = true;") < retry.index("failedView.loadUrl(OFFLINE_MAIN_PAGE);")
create = span('game.addJavascriptInterface(new SaveBridge(), "BFAndroid");',
              'gameContainer.addView(game, new FrameLayout.LayoutParams(-1, -1));')
assert create.index("nativeMainLoadRequested = true;") < create.index(
    'game.loadUrl("file:///android_asset/index.html");')
renderer = span("@Override public boolean onRenderProcessGone(",
                "// Load the independent navigation layer")
assert renderer.index("if (view != game) return false;") < renderer.index(consume)
destroy = span("@Override protected void onDestroy() {", "super.onDestroy();")
assert consume in destroy

# Model expected callback behavior; this does not invoke Android WebView.
class Navigation:
    def __init__(self):
        self.pending = False
        self.failed = False
        self.clears = 0

    def native_load(self):
        self.pending = True

    def started(self, main=True):
        if main and self.pending:
            self.pending = False
            self.failed = False
            self.clears += 1

    def failed_main(self):
        self.pending = False
        self.failed = True

n = Navigation()
n.native_load()
n.started()
n.failed_main()
n.started()  # duplicate start from failed navigation MUST NOT reset the failure
assert n.failed and n.clears == 1
n.started(main=False)  # missing subresource callback is irrelevant
assert n.failed
n.native_load()  # explicit owner Try again
n.started()
assert not n.failed and n.clears == 2
n.failed_main()
n.native_load()
n.failed_main()  # failure before start also invalidates the token
n.started()
assert n.failed

assert len(re.findall(r"^\s*python3 test_bf_offline_main_navigation_token_v23400.py$", workflow, re.M)) == 1
assert preflight.count("test_bf_offline_main_navigation_token_v23400.py") == 2
assert "android.permission.INTERNET" not in manifest
assert "localStorage" not in java and "bf_global_offline_demo_v7" not in java
print("PASS v234: only explicit native loads clear main-page failure; duplicate starts fail closed")
