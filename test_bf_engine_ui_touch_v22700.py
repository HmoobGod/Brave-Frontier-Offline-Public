"""v227: read-only home UI touch/reduced-motion acceptance for Android-scale screens."""
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent
css = (ROOT / "app/src/main/assets/bf_home_nav.css").read_text("utf-8")
nav = (ROOT / "app/src/main/assets/bf_home_nav.js").read_text("utf-8")
manifest = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf-8")
assert "v227: Home/route touch and focus accessibility" in css
assert "touch-action:manipulation;" in css
assert "min-height:58px;" in css
assert "prefers-reduced-motion:reduce" in css
assert "focus-visible" in css
assert "window.BF_homeNav = {go,get current()" in nav
assert "android.permission.INTERNET" not in manifest
new_css = css[css.index("/* v227: Home/route touch"): ]
for forbidden in ("#battle", "localStorage", "saveProgress", "P.", "S."):
    assert forbidden not in new_css, forbidden
if "--source-only" in sys.argv:
    print("PASS v227 source: navigation-only CSS, focus, touch and reduced-motion; no game/save changes")
    raise SystemExit(0)

from playwright.sync_api import sync_playwright
chrome = shutil.which("google-chrome") or shutil.which("google-chrome-stable") or shutil.which("chromium")
assert chrome, "Install system Chrome/Chromium before running v227 browser regression"
marker = "\n})();"
assert marker in nav
bootstrap = nav.split(marker, 1)[0] + marker
assert "window.BF_homeNav = {go,get current()" in bootstrap

html = """<!doctype html><html><head><meta charset="utf-8"></head>
<body><main class="wrap">
<section class="progresspanel">Save menu</section>
<section class="questpanel">Quest route</section>
<section class="squadsetup">Units route</section>
<section class="summonpanel">Summon route</section>
</main></body></html>"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=chrome,
                                args=["--no-sandbox", "--disable-dev-shm-usage"])
    for width in (320, 360, 412, 540):
        page = browser.new_page(viewport={"width":width,"height":750}, device_scale_factor=2)
        page.route("https://bf-v227-ui.test/", lambda route: route.fulfill(
            status=200,content_type="text/html",body=html))
        page.goto("https://bf-v227-ui.test/")
        page.add_style_tag(content=css)
        page.evaluate("""() => {
          window.P={version:7,squad:[1]};window.S={lastQuest:10};
          localStorage.setItem('bf_global_offline_demo_v7','preserve-v7');
          window.__uiWrites=0;
          const original=Storage.prototype.setItem;
          Storage.prototype.setItem=function(...args){window.__uiWrites++;return original.apply(this,args);};
        }""")
        page.add_script_tag(content=bootstrap)
        assert page.evaluate("BF_homeNav.current") == "home"
        assert page.evaluate("""() => [...document.querySelectorAll('.bf-navbar button')].length""")==5
        bounds=page.evaluate("""() => [...document.querySelectorAll('.bf-navbar button')].map(
          e => {const b=e.getBoundingClientRect();return {w:b.width,h:b.height,left:b.left,right:b.right}}
        )""")
        assert all(b["w"]>=44 and b["h"]>=44 and b["left"]>=0 and b["right"]<=width+1 for b in bounds), (width,bounds)
        assert page.evaluate("""() => getComputedStyle(document.querySelector('.bf-navbar button')).touchAction""")=="manipulation"
        for route in ("units","quest","summon","menu","home"):
            page.locator('.bf-navbar button[data-bf-goto="'+route+'"]').click()
            assert page.evaluate("BF_homeNav.current")==route
            assert page.locator('.bf-navbar button[aria-current="page"]').count()==1
        page.emulate_media(reduced_motion="reduce")
        assert page.evaluate("""() => matchMedia('(prefers-reduced-motion:reduce)').matches""")
        assert page.evaluate("""() => {
          const css=getComputedStyle(document.querySelector('.bf-navbar button'));
          return css.animationDuration.split(',').every(v=>parseFloat(v)<=0.001)
            && css.transitionDuration.split(',').every(v=>parseFloat(v)<=0.001);
        }""")
        assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")=="preserve-v7"
        assert page.evaluate("window.__uiWrites")==0
        assert page.evaluate("JSON.stringify(P)")== '{"version":7,"squad":[1]}'
        assert page.evaluate("JSON.stringify(S)")== '{"lastQuest":10}'
        page.close()
    browser.close()
print("PASS v227 browser: 320/360/412/540px touch routes, reduced motion and v7 save unchanged")
