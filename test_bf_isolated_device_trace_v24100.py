"""v241 defensive source and mutation gate for isolated on-device trace.

Static source gate plus real Java/Android Gradle build in full workflow.
A real Android-device callback sequence remains an owner's acceptance test.
"""
from pathlib import Path
import re

R = Path(__file__).resolve().parent
J = (R / "app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
P = (R / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
W = (R / ".github/workflows/build-debug-apk.yml").read_text("utf8")
G = (R / "app/build.gradle").read_text("utf8")
M = (R / "app/src/main/AndroidManifest.xml").read_text("utf8")

def uncomment(s):
    return re.sub(r'/\*.*?\*/|//[^\n]*', '', s, flags=re.S)

def part(s, a, b):
    assert s.count(a) == 1, f"missing / duplicate starting anchor {a}"
    rest = s.split(a, 1)[1]
    assert b in rest, f"missing ending anchor {b}"
    return rest.split(b, 1)[0]

def must_start(s, expr):
    assert re.match(expr, uncomment(s)), f"missing leading package-guard: {expr}"

def validate_isolation(src):
    start = "private boolean isIsolatedTraceApp() {"
    end = "private void clearPendingBack() {"
    whole = part(src, start, end)
    gate = uncomment(part(src, start,
                         "private void appendIsolatedTrace("))
    # Match the whole gate body: no early return or || fallback, and
    # no operand may be moved into a comment to bypass identity isolation.
    assert re.fullmatch(
        r'\s*return\s+"org\.bravefrontier\.offline\.diagnostic"'
        r'\.equals\(getPackageName\(\)\)\s*&&\s*'
        r'\(getApplicationInfo\(\)\.flags\s*&\s*'
        r'android\.content\.pm\.ApplicationInfo\.FLAG_DEBUGGABLE\)'
        r'\s*!=\s*0\s*;\s*', gate
    ), "Diagnostic package AND debuggable gate must be the entire method"

    capture = part(src, "private void appendIsolatedTrace(String event, WebView view, boolean mainPage) {",
                   "private String isolatedTraceText() {")
    text = part(src, "private String isolatedTraceText() {",
                "private void dismissIsolatedTraceDialog() {")
    show = part(src, "private void showIsolatedTrace() {",
                "private String isolatedFailureSuffix() {")
    suffix = part(src, "private String isolatedFailureSuffix() {",
                  "private void addIsolatedTraceControl() {")
    button = part(src, "private void addIsolatedTraceControl() {",
                  end)
    must_start(capture, r'\s*if\s*\(!isIsolatedTraceApp\(\)\)\s*return\s*;')
    must_start(text, r'\s*if\s*\(!isIsolatedTraceApp\(\)\)\s*return\s*""\s*;')
    must_start(show, r'\s*if\s*\(!isIsolatedTraceApp\(\)\s*\|\|\s*isFinishing\(\)\s*\|\|\s*isDestroyed\(\)\)\s*return\s*;')
    must_start(button, r'\s*if\s*\(!isIsolatedTraceApp\(\)\s*\|\|\s*gameContainer\s*==\s*null\)\s*return\s*;')
    assert re.fullmatch(
        r'\s*return\s+isIsolatedTraceApp\(\)\s*\?\s*"\\n\\nDiagnostic events:\\n"\s*\+\s*isolatedTraceText\(\)\s*:\s*""\s*;\s*',
        uncomment(suffix)
    ), "Non-diagnostic dialog suffix must be empty"
    assert len(re.findall(r'\bcase "', capture)) == 11
    for name in ("initialRequested","retryRequested","onPageStarted","startAccepted",
                 "onReceivedErrorMain","onReceivedErrorSubresource","failureLatched",
                 "rendererGone","onPageFinished","injectionAttempt","activityDestroy"):
        assert 'case "' + name + '"' in capture
    assert "default: return;" in capture
    assert "if (isolatedTrace.size() >= 16) isolatedTrace.removeFirst();" in capture
    assert "isolatedTrace.addLast(line);" in capture
    for token in ("(view == game)", "mainPage", "nativeMainLoadRequested",
                  "offlinePageLoadFailed", "(offlinePageFailureDialog != null)"):
        assert token in capture

    # Include the UI copy block: don't accidentally extract URLs or save info
    # outside the specific append method.
    for token in ("getUrl(", "getOriginalUrl(", "getTitle(",
                  "getIntent(", "getFilesDir(", "getExternalStorage(",
                  "localStorage", "saveProgress", "saveToWrite", "request.get",
                  "error.get", "JSONObject", "SharedPreferences"):
        assert token not in uncomment(whole), "private-data/API leak: " + token

    assert re.search(
        r'final\s+String\s+report\s*=\s*"BF Offline Diagnostic / coarse events only\\n"\s*\+\s*isolatedTraceText\(\)\s*;',
        uncomment(show))
    copy_start = '.setPositiveButton("Copy event text", (dialog, which) -> {'
    assert uncomment(show).count(copy_start) == 1
    callback = uncomment(show).split(copy_start, 1)[1].split("})", 1)[0]
    assert len(re.findall(r'\bsetPrimaryClip\s*\(', uncomment(whole))) == 1
    assert len(re.findall(r'\bsetPrimaryClip\s*\(', callback)) == 1
    assert re.search(
        r'clipboard\.setPrimaryClip\(\s*'
        r'android\.content\.ClipData\.newPlainText\(\s*'
        r'"BF Offline Diagnostic"\s*,\s*report\s*\)\s*\)',
        callback), "Clipboard contents must be fixed coarse report only"
    assert "getSystemService(CLIPBOARD_SERVICE)" in callback
    assert "button.setOnClickListener(v -> showIsolatedTrace());" in button
    assert 'button.setText("TRACE");' in button
    assert "android.view.Gravity.BOTTOM | android.view.Gravity.END" in button
    assert "bounds.setMargins(0, 0, (int) (8 * density), (int) (84 * density));" in button
    assert "gameContainer.addView(button, bounds);" in button
    # Keep dialog Activity-owned to prevent WindowLeaked during recreation.
    dismiss = part(src, "private void dismissIsolatedTraceDialog() {",
                   "private void showIsolatedTrace() {")
    assert "isolatedTraceDialog.dismiss();" in dismiss
    assert "isolatedTraceDialog = null;" in dismiss
    assert "dismissIsolatedTraceDialog();" in show
    assert "isolatedTraceDialog = shown;" in show
    assert "shown.setOnDismissListener(" in show
    assert "shown.show();" in show
    destroy = part(src, "@Override protected void onDestroy() {", "super.onDestroy();")
    assert "dismissIsolatedTraceDialog();" in destroy
    assert destroy.index("dismissIsolatedTraceDialog();") < destroy.index("dismissRendererFailureDialog();")
    assert "appendIsolatedTrace(event, view, mainPage);" in src
    assert src.count("addIsolatedTraceControl();") == 1
    assert src.index("gameContainer.addView(game, new FrameLayout.LayoutParams(-1, -1));") < src.index(
        "addIsolatedTraceControl();") < src.index("setContentView(gameContainer);")
    assert src.count("isolatedFailureSuffix()") == 3
    assert "android.util.Log.d(\"BFOfflineTrace\"," in src

validate_isolation(J)
assert "applicationIdSuffix '.diagnostic'" in G
assert "android.permission.INTERNET" not in M
assert P.count("test_bf_isolated_device_trace_v24100.py") == 2
assert W.count("test_bf_isolated_device_trace_v24100.py") == 1

# Execute adversarial mutations against the real validator. Controls do not
# replace actual Gradle, packaging, or owner-device acceptance tests.
def change(before, after):
    assert J.count(before) >= 1, "mutation anchor missing"
    return J.replace(before, after, 1)

def reject(name, changed):
    assert changed != J, "no mutation: " + name
    try:
        validate_isolation(changed)
    except AssertionError:
        return
    raise AssertionError("Rejected-source test accepted unsafe change: " + name)

mutations = {
    "OR bypass": change('".diagnostic".equals(getPackageName()) &&',
                        '".diagnostic".equals(getPackageName()) ||'),
    "inverted package": change(
        '"org.bravefrontier.offline.diagnostic".equals(getPackageName()) &&',
        '!"org.bravefrontier.offline.diagnostic".equals(getPackageName()) &&'),
    "early unconditional pass": change(
        "private boolean isIsolatedTraceApp() {",
        "private boolean isIsolatedTraceApp() { if (true) return true;"),
    "commented debug guard": change(
        "android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE) != 0;",
        "/*android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE) != 0;*/ true;"),
    "unguarded trace": change(
        "private void appendIsolatedTrace(String event, WebView view, boolean mainPage) {\n        if (!isIsolatedTraceApp()) return;",
        "private void appendIsolatedTrace(String event, WebView view, boolean mainPage) {"),
    "unguarded text": change(
        'private String isolatedTraceText() {\n        if (!isIsolatedTraceApp()) return "";',
        "private String isolatedTraceText() {"),
    "unguarded button": change(
        "private void addIsolatedTraceControl() {\n        if (!isIsolatedTraceApp() || gameContainer == null) return;",
        "private void addIsolatedTraceControl() {"),
    "unguarded show": change(
        "private void showIsolatedTrace() {\n        if (!isIsolatedTraceApp() || isFinishing() || isDestroyed()) return;",
        "private void showIsolatedTrace() {"),
    "unguarded suffix": change(
        'return isIsolatedTraceApp() ? "\\n\\nDiagnostic events:\\n" + isolatedTraceText() : "";',
        'return "\\n\\nDiagnostic events:\\n" + isolatedTraceText();'),
    "captures page title": change("String line = event +", "String title=view.getTitle(); String line = event +"),
    "captures original URL": change("String line = event +", "String url=view.getOriginalUrl(); String line = event +"),
    "clipboard URL": change('"BF Offline Diagnostic", report));',
                             '"BF Offline Diagnostic", game.getUrl()));'),
    "unintended autoclipping": change(
        "        shown.show();", "        shown.show();\n        clipboard.setPrimaryClip(report);"),
    "menu obscured": change("(int) (84 * density)", "(int) (8 * density)"),
    "lifecycle dismissal lost": change(
        "        dismissIsolatedTraceDialog();\n        dismissRendererFailureDialog();",
        "        dismissRendererFailureDialog();")
}
for k, source in mutations.items():
    reject(k, source)
print("PASS v241 follow-up: guard AND, all consumers, no URL/save leaks, bounded UI/copy, 15 mutation probes, Menu clear, dialog lifecycle")
