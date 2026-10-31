"""v236 native debug callback trace source gate (NOT an Android timing test)."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
java = (ROOT / "app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf-8")
manifest = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf-8")
preflight = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf-8")
full_ci = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf-8")

def section(source, start, end):
    assert source.count(start) == 1, start
    rest = source.split(start, 1)[1]
    assert end in rest, end
    return rest.split(end, 1)[0]

method = section(java, "private void traceOfflinePage(String event, WebView view, boolean mainPage) {",
                 "private void dismissOfflinePageError() {")
debug_guard = "android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE"
log = 'android.util.Log.d("BFOfflineTrace",'
assert method.count(debug_guard) == 1
assert method.count(log) == 1
assert method.index(debug_guard) < method.index(log)
assert 'getApplicationInfo().flags &' in method
assert '== 0) return;' in method
assert len(re.findall(r'\btraceOfflinePage\(', java)) == 11  # declaration + 10 event sites
for marker in (
    '"initialRequested"', '"retryRequested"', '"onPageStarted"',
    '"startAccepted"', '"onReceivedErrorMain"', '"onReceivedErrorSubresource"',
    '"failureLatched"', '"rendererGone"', '"onPageFinished"',
    '"injectionAttempt"', '"activityDestroy"'
):
    assert marker in java, marker

# Only hard-coded event labels and coarse booleans are allowed in the helper.
assert all(expr in method for expr in (
    "(view == game)", "mainPage", "nativeMainLoadRequested",
    "offlinePageLoadFailed", "(offlinePageFailureDialog != null)"))
assert all(secret not in method for secret in (
    "localStorage", "SaveBridge", "saveToWrite", "pendingUpload",
    "P.", "S.", "getUrl(", "JSONObject", "Uri", "request",
    "exception", "error.get", "getIntent()"))
assert 'event + " current="' in method and ' + " dialog="' in method
assert 'android.permission.INTERNET' not in manifest
assert "bf_global_offline_demo_v7" not in method

started = section(java, "@Override public void onPageStarted(WebView view, String url,",
                  "@Override public void onReceivedError(WebView view,")
assert started.index('traceOfflinePage("onPageStarted"') < started.index("if (view != game")
assert started.index("nativeMainLoadRequested = false;") < started.index('traceOfflinePage("startAccepted"')
finished = section(java, "@Override public void onPageFinished(WebView view, String url) {",
                   "// v0.54:")
assert finished.index('traceOfflinePage("onPageFinished"') < finished.index("if (view != game) return;")
assert finished.index("if (!OFFLINE_MAIN_PAGE.equals(url) || offlinePageLoadFailed) return;") < finished.index(
    'traceOfflinePage("injectionAttempt"') < finished.index('view.evaluateJavascript(')
error = section(java, "@Override public void onReceivedError(WebView view,",
                "@Override public boolean onRenderProcessGone(")
assert error.index("offlinePageLoadFailed = true;") < error.index(
    'traceOfflinePage("failureLatched"')

assert preflight.count("test_bf_android_offline_callback_trace_v23600.py") == 2
assert len(re.findall(r'^\s*python3 test_bf_android_offline_callback_trace_v23600.py$', full_ci, re.M)) == 1

# Adversarial snippets fail if debug guard is removed or sensitive fields are logged.
def valid_method(s):
    return s.count(debug_guard) == 1 and s.index(debug_guard) < s.index(log) and all(
        word not in s for word in ("saveToWrite", "localStorage", "getUrl("))
assert not valid_method(method.replace(debug_guard, "0"))
assert not valid_method(method.replace(log, "saveToWrite; " + log))
assert not valid_method(method.replace(log, "view.getUrl(); " + log))
print("PASS v236: debug-only callback tracing, correct event boundaries, no save or URL logging")
