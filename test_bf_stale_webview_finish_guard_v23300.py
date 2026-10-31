"""v233 source safety gate: onPageFinished must not inject on an obsolete WebView.

Static contract only; Android runtime callback-order and real-save smoke still required.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
java = (ROOT / "app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf-8")
manifest = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf-8")
workflow = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf-8")
preflight = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf-8")

signature = "@Override public void onPageFinished(WebView view, String url) {"
assert java.count(signature) == 1
finished = java.split(signature, 1)[1].split("// v0.54:", 1)[0]
super_call = "super.onPageFinished(view, url);"
identity_guard = "if (view != game) return;"
url_guard = "if (!OFFLINE_MAIN_PAGE.equals(url) || offlinePageLoadFailed) return;"
injection = "view.evaluateJavascript("
assert super_call in finished
assert identity_guard in finished
assert url_guard in finished
assert injection in finished
assert finished.index(super_call) < finished.index(identity_guard)
assert finished.index(identity_guard) < finished.index(url_guard)
assert finished.index(url_guard) < finished.index(injection)

# Preserve the v229/v232 failed-load injection block and v231 renderer disposal.
assert "offlinePageLoadFailed = true;" in java
assert 'if (view != game || !OFFLINE_MAIN_PAGE.equals(url)) return;' in java
assert "dismissRendererFailureDialog();" in java
assert 'failedView.loadUrl(OFFLINE_MAIN_PAGE);' in java
assert 'game.loadUrl("file:///android_asset/index.html");' in java

# Reject comments masquerading as the required executable guard.
# This narrow callback prefix contains no Java string literal with comment markers.
def check_order(sample):
    section = sample.split(signature, 1)[1].split("// v0.54:", 1)[0]
    executable = re.sub(r"/\\*.*?\\*/|//[^\\n]*", "", section, flags=re.S)
    guard_statement = r"(?m)^[ \\t]*if \\(view != game\\) return;[ \\t]*$"
    if not re.search(guard_statement, executable):
        return False
    return (executable.index(super_call) < executable.index(identity_guard) <
            executable.index(url_guard) < executable.index(injection))

assert check_order(java)
def mutate_finished(new_guard):
    mutated = finished.replace(identity_guard, new_guard, 1)
    assert mutated != finished
    return java.replace(signature + finished, signature + mutated, 1)

assert not check_order(mutate_finished(""))
assert not check_order(mutate_finished("if (view == game) return;"))
assert not check_order(mutate_finished("if (view != game) { /* missing return */ }"))
assert not check_order(mutate_finished("// " + identity_guard))
assert not check_order(mutate_finished("/* " + identity_guard + " */"))

assert len(re.findall(r"^\s*python3 test_bf_stale_webview_finish_guard_v23300.py$", workflow, re.M)) == 1
assert preflight.count("test_bf_stale_webview_finish_guard_v23300.py") == 2
assert "android.permission.INTERNET" not in manifest
assert "localStorage" not in java and "bf_global_offline_demo_v7" not in java
print("PASS v233: stale WebView completion ignored before UI injection; offline save/network guards preserved")
