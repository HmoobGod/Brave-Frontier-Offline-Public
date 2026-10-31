"""v225: Android Back respects in-page routes, without modifying the v7 save."""
from pathlib import Path
import re
import sys
import shutil

ROOT = Path(__file__).resolve().parent
java = (ROOT / "app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf-8")
nav = (ROOT / "app/src/main/assets/bf_home_nav.js").read_text("utf-8")
match = re.search(r'private static final String UI_BACK_JS\s*=\s*"([^"]+)";', java)
assert match, "Android route-back expression missing"
back_js = match.group(1)
assert "BF_homeNav" in back_js and "n.go('home')" in back_js
assert "n.current!=='home'" in back_js and "catch(e){return false;}" in back_js
assert "game.evaluateJavascript(UI_BACK_JS, handled ->" in java
assert "if (\"true\".equals(handled)) return;" in java
assert "fallbackAndroidBack();" in java and "backNavigationPending" in java
assert "if (isFinishing() || isDestroyed()) return;" in java
assert "if (game != null && game.canGoBack()) game.goBack();" in java
assert 'game.loadUrl("file:///android_asset/index.html")' in java
assert "window.BF_homeNav = {go,get current()" in nav
assert "bf_global_offline_demo_v7" not in back_js
if "--source-only" in sys.argv:
    print("PASS v225 source: Android back route, fallback, bounded dispatch and no save writes")
    raise SystemExit(0)

from playwright.sync_api import sync_playwright

# Test the actual first navigation module only. Later independent modules can
# use game data absent from the minimal fixture and are not required to test Back.
marker = "\n})();"
assert marker in nav
nav_bootstrap = nav.split(marker, 1)[0] + marker
assert "window.BF_homeNav = {go,get current()" in nav_bootstrap
html = """<!doctype html><html><head><meta charset="utf-8"></head><body>
<main class="wrap">
<section class="progresspanel">Save menu</section>
<section class="questpanel">Quest screen</section>
<section class="squadsetup">Units screen</section>
<section class="summonpanel">Summon screen</section>
</main></body></html>"""
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=(shutil.which("google-chrome") or shutil.which("google-chrome-stable") or shutil.which("chromium")), args=["--no-sandbox"])
    page = browser.new_page()
    page.route("https://bf-v225-ui.test/", lambda route: route.fulfill(
        status=200, content_type="text/html", body=html))
    page.goto("https://bf-v225-ui.test/")
    page.evaluate("""() => {
      window.P={version:7,squad:[1,2]};window.S={lastQuest:10};
      localStorage.setItem('bf_global_offline_demo_v7','preserved-save');
      window.__saveWrites=0;
      const original=Storage.prototype.setItem;
      Storage.prototype.setItem=function(...args){window.__saveWrites++;return original.apply(this,args);};
    }""")
    page.add_script_tag(content=nav_bootstrap)
    assert page.evaluate("window.BF_homeNav.current") == "home"
    assert page.evaluate(back_js) is False, "Home must fall through to native back"
    for screen in ("quest", "units", "summon", "menu"):
        assert page.evaluate("(route) => window.BF_homeNav.go(route)", screen)
        assert page.evaluate("window.BF_homeNav.current") == screen
        assert page.evaluate(back_js) is True, screen
        assert page.evaluate("window.BF_homeNav.current") == "home"
        assert page.evaluate(back_js) is False, "Home must not re-route on repeated Back"
    assert page.evaluate("document.querySelectorAll('#bf-home').length") == 1
    assert page.evaluate("document.querySelectorAll('.bf-navbar').length") == 1
    assert page.evaluate("JSON.stringify(P)") == '{"version":7,"squad":[1,2]}'
    assert page.evaluate("JSON.stringify(S)") == '{"lastQuest":10}'
    assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')") == "preserved-save"
    assert page.evaluate("window.__saveWrites") == 0
    page.evaluate("delete window.BF_homeNav")
    assert page.evaluate(back_js) is False, "Missing navigation must fail closed"
    browser.close()
print("PASS v225 browser: 4 in-page routes return Home; no duplicated UI or v7 save writes")
