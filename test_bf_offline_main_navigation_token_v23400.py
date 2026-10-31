"""v234 source contract: only an explicit native page start can reset a failed main load.

Source-shape checks and mutations are not Android WebView callback timing tests.
Physical device tests and existing v7 save smoke remain mandatory.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
java = (ROOT / "app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf-8")
manifest = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf-8")
preflight = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf-8")
workflow = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf-8")

START = "@Override public void onPageStarted(WebView view, String url,"
ERROR = "@Override public void onReceivedError(WebView view,"
RENDERER = "@Override public boolean onRenderProcessGone("
FINISHED = "@Override public void onPageFinished(WebView view, String url) {"
RETRY = '.setPositiveButton("Try again", (dialog, which) -> {'
CLOSE = '.setNegativeButton("Close", (dialog, which) -> {'
CREATE = 'game.addJavascriptInterface(new SaveBridge(), "BFAndroid");'
CONTAINER = 'gameContainer.addView(game, new FrameLayout.LayoutParams(-1, -1));'
TOKEN_TRUE = "nativeMainLoadRequested = true;"
TOKEN_FALSE = "nativeMainLoadRequested = false;"
FAILED_FALSE = "offlinePageLoadFailed = false;"
TOKEN_GUARD = "if (!nativeMainLoadRequested) return;"
URL_GUARD = "if (view != game || !OFFLINE_MAIN_PAGE.equals(url)) return;"
MAIN_LOAD = 'game.loadUrl("file:///android_asset/index.html");'
RETRY_LOAD = "failedView.loadUrl(OFFLINE_MAIN_PAGE);"
# N1/N2: accept formatting variation, forbid all unreviewed reset locations.
CLEAR_ASSIGNMENT = re.compile(r"\bofflinePageLoadFailed\s*=\s*false\s*;")
FIELD_INITIALIZER = re.compile(r"\bprivate\s+boolean\s+offlinePageLoadFailed\s*=\s*false\s*;")
# N3: extra native navigation methods would need a deliberate token audit.
ALTERNATE_LOAD = re.compile(r"\.(?:reload|loadData|loadDataWithBaseURL)\s*\(")

def span(source, start, end):
    assert source.count(start) == 1, f"Missing/nonunique anchor: {start}"
    rest = source.split(start, 1)[1]
    assert end in rest, f"Missing end anchor: {end}"
    return rest.split(end, 1)[0]

def executable(section):
    # These callback prefixes contain no quoted URLs with // or Java text-blocks.
    # Match executable statements, not comments pretending to be live guards.
    return re.sub(r"/\*[\s\S]*?\*/|//[^\n]*", "", section)

def statement(section, literal):
    return bool(re.search(r"(?m)^[ \t]*" + re.escape(literal) + r"[ \t]*$", section))

def validate(source):
    assert source.count("private boolean nativeMainLoadRequested = false;") == 1
    start = executable(span(source, START, ERROR))
    error = executable(span(source, ERROR, RENDERER))
    renderer = executable(span(source, RENDERER, "// Load the independent navigation layer"))
    finished = executable(span(source, FINISHED, "// v0.54:"))
    retry = executable(span(source, RETRY, CLOSE))
    # The create section contains a file:// URL literal; do not strip comments there.
    create = span(source, CREATE, CONTAINER)
    destroy = executable(span(source, "@Override protected void onDestroy() {", "super.onDestroy();"))

    assert URL_GUARD in start and statement(start, TOKEN_GUARD)
    assert statement(start, TOKEN_FALSE) and statement(start, FAILED_FALSE)
    assert start.index(URL_GUARD) < start.index(TOKEN_GUARD) < start.index(TOKEN_FALSE)
    assert start.index(TOKEN_FALSE) < start.index(FAILED_FALSE) < start.index("dismissOfflinePageError();")
    assert "request == null || !request.isForMainFrame()" in error
    assert "!OFFLINE_MAIN_PAGE.equals(String.valueOf(request.getUrl()))" in error
    assert statement(error, TOKEN_FALSE)
    assert error.index("request == null || !request.isForMainFrame()") < error.index(TOKEN_FALSE)
    assert error.index("!OFFLINE_MAIN_PAGE.equals(String.valueOf(request.getUrl()))") < error.index(TOKEN_FALSE)
    assert error.index(TOKEN_FALSE) < error.index("offlinePageLoadFailed = true;")

    # N1/N2: only the field initializer and token-verified page-start clear failure.
    # Reject both "flag = false" and "flag=false" in Retry or any callback/method.
    assert len(FIELD_INITIALIZER.findall(source)) == 1
    assert len(CLEAR_ASSIGNMENT.findall(source)) == 2
    assert len(CLEAR_ASSIGNMENT.findall(start)) == 1
    assert not CLEAR_ASSIGNMENT.search(retry)
    assert statement(retry, TOKEN_TRUE) and RETRY_LOAD in retry
    assert retry.index(TOKEN_TRUE) < retry.index(RETRY_LOAD)
    assert statement(create, TOKEN_TRUE) and MAIN_LOAD in create
    assert create.index(TOKEN_TRUE) < create.index(MAIN_LOAD)

    assert renderer.index("if (view != game) return false;") < renderer.index(TOKEN_FALSE)
    assert statement(renderer, TOKEN_FALSE) and statement(destroy, TOKEN_FALSE)
    assert finished.index("if (view != game) return;") < finished.index(
        "if (!OFFLINE_MAIN_PAGE.equals(url) || offlinePageLoadFailed) return;")
    assert finished.index("if (!OFFLINE_MAIN_PAGE.equals(url) || offlinePageLoadFailed) return;") < finished.index("view.evaluateJavascript(")

    # T3/T4: callback must never re-arm a reset token.
    assert all(TOKEN_TRUE not in block for block in (start, error, renderer, finished, destroy))
    # T5: exactly two explicit native requests (onCreate and Try again).
    assert len(re.findall(r"(?m)^[ \t]*" + re.escape(TOKEN_TRUE) + r"[ \t]*$", source)) == 2
    assert len(re.findall(r"\.loadUrl\s*\(", source)) == 2
    # N3: no hidden second navigation through another WebView load API.
    assert not ALTERNATE_LOAD.search(source)
    # Android Back's established single game.goBack() is intentionally preserved;
    # it is unrelated navigation and cannot clear a latched failure token.
    assert len(re.findall(r"\.goBack\s*\(", source)) == 1

validate(java)

def mutate_section(source, begin, end, old, new):
    segment = span(source, begin, end)
    assert segment.count(old) == 1, f"Bad mutation anchor: {old}"
    return source.replace(begin + segment, begin + segment.replace(old, new, 1), 1)

def reject(mutated):
    try:
        validate(mutated)
    except AssertionError:
        return
    raise AssertionError("Adversarial source mutation improperly accepted")

# T1: commented-out guard must not pass as executable.
reject(mutate_section(java, START, ERROR, TOKEN_GUARD, "// " + TOKEN_GUARD))
reject(mutate_section(java, START, ERROR, TOKEN_GUARD, "/* " + TOKEN_GUARD + " */"))
# T2: a commented-out error invalidation must fail.
reject(mutate_section(java, ERROR, RENDERER, TOKEN_FALSE, "// " + TOKEN_FALSE))
reject(mutate_section(java, ERROR, RENDERER, TOKEN_FALSE, "/* " + TOKEN_FALSE + " */"))
# T3: an error cannot re-arm the token before setting failure.
reject(mutate_section(java, ERROR, RENDERER, "offlinePageLoadFailed = true;",
                      TOKEN_TRUE + "\n                offlinePageLoadFailed = true;"))
# T4: an onPageFinished callback cannot re-arm the token.
reject(mutate_section(java, FINISHED, "// v0.54:",
                      "if (!OFFLINE_MAIN_PAGE.equals(url) || offlinePageLoadFailed) return;",
                      "if (!OFFLINE_MAIN_PAGE.equals(url) || offlinePageLoadFailed) return;\n                " + TOKEN_TRUE))
# T5: extra native page loads without a token are rejected.
reject(mutate_section(java, CREATE, CONTAINER, MAIN_LOAD,
                      MAIN_LOAD + "\n        game.loadUrl(OFFLINE_MAIN_PAGE);"))
# R1 regression: no failure clearing before a new page-start.
reject(mutate_section(java, RETRY, CLOSE, TOKEN_TRUE, FAILED_FALSE + "\n                        " + TOKEN_TRUE))

# N1: whitespace-only mutations of the same Retry bug must be rejected.
reject(mutate_section(java, RETRY, CLOSE, TOKEN_TRUE,
                      "offlinePageLoadFailed=false;\n                        " + TOKEN_TRUE))
# N2/N4: clearing failure outside a token-consumed start is prohibited.
reject(mutate_section(java, FINISHED, "// v0.54:",
                      "if (!OFFLINE_MAIN_PAGE.equals(url) || offlinePageLoadFailed) return;",
                      "offlinePageLoadFailed=false;\n                " +
                      "if (!OFFLINE_MAIN_PAGE.equals(url) || offlinePageLoadFailed) return;"))
reject(mutate_section(java, RENDERER, "// Load the independent navigation layer",
                      TOKEN_FALSE, TOKEN_FALSE + "\n                offlinePageLoadFailed = false;"))
reject(mutate_section(java, "private void dismissRendererFailureDialog() {",
                      "private static final String OFFLINE_MAIN_PAGE",
                      "rendererFailureDialog = null;",
                      "rendererFailureDialog = null;\n        offlinePageLoadFailed=false;"))
# N3: alternate APIs can silently produce extra page navigations.
for extra_call in ("game.reload();",
                   'game.loadData("<html></html>", "text/html", "utf-8");',
                   'game.loadDataWithBaseURL(null, "<html></html>", "text/html", "utf-8", null);'):
    reject(mutate_section(java, CREATE, CONTAINER, MAIN_LOAD,
                          MAIN_LOAD + "\n        " + extra_call))

# The model is illustrative: it cannot simulate WebView scheduling/races.
class Navigation:
    def __init__(self):
        self.pending = False
        self.failed = False
        self.clears = 0

    def native_load(self):
        self.pending = True  # does not clear an existing failure

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
n.started()  # duplicate from the failed navigation must not clear it
assert n.failed and n.clears == 1
n.started(main=False)
assert n.failed
n.native_load()  # Retry tap leaves the failure latched
assert n.failed
n.started()  # valid explicit new navigation starts
assert not n.failed and n.clears == 2
n.failed_main()
n.native_load()
n.failed_main()  # failing before start invalidates the token
n.started()
assert n.failed

assert len(re.findall(r"^\s*python3 test_bf_offline_main_navigation_token_v23400.py$", workflow, re.M)) == 1
assert preflight.count("test_bf_offline_main_navigation_token_v23400.py") == 2
assert "android.permission.INTERNET" not in manifest
assert "localStorage" not in java and "bf_global_offline_demo_v7" not in java
print("PASS v234: one-shot main navigation reset, fail-closed Retry, commented guard and token re-arm mutations rejected")
