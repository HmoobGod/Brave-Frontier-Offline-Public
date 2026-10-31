"""v241 static and CI native-compilation guard: on-device diagnostic-only trace."""
from pathlib import Path
import re
R=Path(__file__).resolve().parent
J=(R/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
P=(R/".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
W=(R/".github/workflows/build-debug-apk.yml").read_text("utf8")
G=(R/"app/build.gradle").read_text("utf8")
M=(R/"app/src/main/AndroidManifest.xml").read_text("utf8")
def part(a,b):
    assert J.count(a)==1,a
    return J.split(a,1)[1].split(b,1)[0]
guard=part("private boolean isIsolatedTraceApp() {","private void appendIsolatedTrace(")
assert '"org.bravefrontier.offline.diagnostic".equals(getPackageName())' in guard
assert "ApplicationInfo.FLAG_DEBUGGABLE" in guard and "!= 0" in guard
assert "applicationIdSuffix '.diagnostic'" in G
assert "android.permission.INTERNET" not in M
cap=part("private void appendIsolatedTrace(String event, WebView view, boolean mainPage) {","private String isolatedTraceText() {")
assert "if (!isIsolatedTraceApp()) return;" in cap
assert "default: return;" in cap
assert "isolatedTrace.size() >= 16" in cap
assert "isolatedTrace.removeFirst()" in cap and "isolatedTrace.addLast(line)" in cap
assert len(re.findall(r'\bcase "',cap))==11
for label in ("initialRequested","retryRequested","onPageStarted","startAccepted",
              "onReceivedErrorMain","onReceivedErrorSubresource","failureLatched",
              "rendererGone","onPageFinished","injectionAttempt","activityDestroy"):
    assert 'case "'+label+'"' in cap
for token in ("localStorage","saveToWrite","getUrl(","request.get","error.get",
              "JSONObject","getFilesDir","getIntent(","deviceId"):
    assert token not in cap
report=part("private String isolatedTraceText() {","private void clearPendingBack() {")
for token in ('if (!isIsolatedTraceApp()) return','button.setText("TRACE")',
              'button.setOnClickListener(v -> showIsolatedTrace());',
              'android.view.Gravity.BOTTOM | android.view.Gravity.END',
              'setPrimaryClip(', 'isolatedTraceText()'):
    assert token in report
for token in ("localStorage","saveProgress","game.evaluateJavascript",
              "FileOutputStream","getExternalStorage"):
    assert token not in report
assert J.count("addIsolatedTraceControl();")==1
assert J.index("gameContainer.addView(game, new FrameLayout.LayoutParams(-1, -1));")<J.index(
    "addIsolatedTraceControl();")<J.index("setContentView(gameContainer);")
assert J.count("isolatedFailureSuffix()")==3
assert J.count("appendIsolatedTrace(event, view, mainPage);")==1
assert 'android.util.Log.d("BFOfflineTrace",' in J
assert "private final java.util.ArrayDeque<String> isolatedTrace" in J
assert P.count("test_bf_isolated_device_trace_v24100.py")==2
assert W.count("test_bf_isolated_device_trace_v24100.py")==1
print("PASS v241: bounded, read-only on-device diagnostic-only callback trace source gate")
