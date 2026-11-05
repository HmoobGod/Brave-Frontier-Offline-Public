"""v260: mobile-friendly offline battle command layout; presentation only.

Source test runs without generated assets. Browser test injects the v21 tray CSS
*after* the nav CSS to reproduce the actual runtime cascade.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
CSS = (ASSETS / "bf_home_nav.css").read_text("utf8")
JS = (ASSETS / "bf_home_nav.js").read_text("utf8")
TRAY = (ASSETS / "bf2100_battle_command_tray.js").read_text("utf8")
STORY = (ASSETS / "bf2000_story_battle_hud.js").read_text("utf8")
WF = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf8")
PRE = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
MAN = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf8")

MARKER = "/* v260 battle commands mobile touch/readability"
assert CSS.count(MARKER) == 1
PATCH = CSS.split(MARKER, 1)[1]
for required in (
    "body.bf-menu-mode #bf2100-tray #bf2100-buttons",
    "body.bf-menu-mode #bf2100-tray #bf2100-targets button",
    "body.bf-menu-mode #bf2000-actions button",
    "body.bf-menu-mode .squad-panel .actionrow .bf-original-action",
    "min-height:48px", "min-height:50px", "touch-action:manipulation",
    "overflow-wrap:anywhere", ":focus-visible",
    "@media(max-width:359px)", "grid-template-columns:minmax(0,1fr)",
):
    assert required in PATCH, required
for forbidden in (
    "localStorage.", "saveProgress(", "P.gems", "P.questClears",
    "S.party", "S.enemies", "window.", "document.", "fetch(",
    "XMLHttpRequest(", "setInterval(", "onclick=",
):
    assert forbidden not in PATCH, forbidden
assert "'#bf2100-buttons button{padding:8px 5px;min-height:44px" in TRAY
assert "'#bf2100-targets button{padding:6px 8px;background:" in TRAY
assert "'#bf2000-actions button{padding:8px 12px;min-height:42px" in STORY
assert "test_bf_battle_mobile_controls_v26000.py --source-only" in PRE
assert WF.count("python3 test_bf_battle_mobile_controls_v26000.py") == 1
assert "android.permission.INTERNET" not in MAN
assert len(CSS.encode("utf8")) < 128 * 1024
assert len(JS.encode("utf8")) < 128 * 1024
print("PASS v260 source: read-only battle controls styling and CI registration")
if "--source-only" in sys.argv[1:]:
    raise SystemExit(0)

import shutil
from playwright.sync_api import sync_playwright

chrome = shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "Chromium required for battle control mobile tests"
marker = "\n})();"
bootstrap = marker.join(JS.split(marker)[:2]) + marker

# This fixture exercises the actual ID/classes from bf2100 and the original
# three action buttons without building a pretend combat engine or touching v7.
fixture = """<!doctype html><html><head><meta charset="utf-8"></head><body>
<main class="wrap">
<section class="progresspanel">Save controls (menu only)</section>
<section class="squadsetup">Units</section>
<section class="summonpanel">Summon demo</section>
<section class="questpanel"><div id="questlist">Quest list</div>
<div id="bf2000-actions"><button id="bf2000-battle">VIEW BATTLE</button>
<button id="bf2000-next" disabled>NEXT STORY MISSION</button></div>
</section>
<section class="squad-panel"><div id="battle">Demo battle</div>
<div id="bf2100-tray"><h3>SQUAD COMMANDS · DEMO COMBAT</h3>
<div id="bf2100-status">Wave 1 · Round 1 · 0/6 commands ready</div>
<div id="bf2100-targets">
<button id="enemy1" aria-pressed="true">Original Global Enemy Name With Long Wrapping · 100/100 HP</button>
<button id="enemy2" disabled aria-pressed="false">Unavailable enemy · 0/100 HP</button></div>
<div id="bf2100-buttons">
<button id="bf2100-attacks">QUEUE ALL ATTACKS</button>
<button id="bf2100-guards">QUEUE ALL GUARDS</button>
<button id="bf2100-bursts">READY BB + ATTACK</button>
<button id="bf2100-execute" disabled>EXECUTE QUEUED TURN</button>
</div><small id="bf2100-info">Offline demo combat only</small></div>
<div class="actionbar"><div class="actionrow" style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:3px">
<button id="attack" class="bf-original-action">Attack</button>
<button id="guard" class="bf-original-action">Guard</button>
<button id="burst" class="bf-original-action" disabled>BB</button>
</div></div>
<div id="targets"><button class="enemybtn selected">Enemy 1</button></div>
</section></main></body></html>"""

# Match the important post-nav runtime styles injected by the actual two
# scripts, which would otherwise shrink controls back to 37/42/44px.
runtime_css = """
#bf2100-tray{padding:11px;margin:10px 0;border:1px solid #a88b59}
#bf2100-buttons{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}
#bf2100-buttons button{padding:8px 5px;min-height:44px}
#bf2100-targets{display:flex;flex-wrap:wrap;gap:6px}
#bf2100-targets button{padding:6px 8px;min-height:37px}
#bf2000-actions{display:flex;flex-wrap:wrap;gap:7px}
#bf2000-actions button{padding:8px 12px;min-height:42px}
"""

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=chrome,
                                 args=["--no-sandbox", "--disable-dev-shm-usage"])
    for width in (320, 359, 360, 393, 412, 540):
        page = browser.new_page(viewport={"width": width, "height": 760})
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.set_content(fixture)
        page.add_style_tag(content=CSS)
        page.add_script_tag(content=bootstrap)
        page.add_style_tag(content=runtime_css)
        page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
        assert page.locator("#bf2100-tray").is_visible(), width
        buttons = page.locator("#bf2100-buttons button")
        targets = page.locator("#bf2100-targets button")
        story = page.locator("#bf2000-actions button")
        original = page.locator(".squad-panel .actionrow .bf-original-action")
        assert buttons.count() == 4 and targets.count() == 2 and story.count() == 2
        assert original.count() == 3
        assert page.locator("#bf2100-execute").is_disabled()
        assert page.locator("#enemy2").is_disabled()
        assert page.locator("#burst").is_disabled()
        assert page.locator("#enemy1").get_attribute("aria-pressed") == "true"
        for group, minimum in ((buttons, 50), (targets, 48),
                               (story, 48), (original, 50)):
            for item in group.all():
                values = item.evaluate("""e=>{
                  const c=getComputedStyle(e),r=e.getBoundingClientRect();
                  return {height:r.height,minHeight:parseFloat(c.minHeight),
                    left:r.left,right:r.right,wrap:c.overflowWrap,
                    touch:c.touchAction};
                }""")
                assert values["minHeight"] >= minimum, (width, values)
                assert values["height"] >= minimum, (width, values)
                assert values["left"] >= -1 and values["right"] <= width + 1, (width, values)
        assert buttons.first.evaluate("e=>getComputedStyle(e).overflowWrap") == "anywhere"
        assert targets.first.evaluate("e=>getComputedStyle(e).touchAction") == "manipulation"
        cols = page.locator("#bf2100-buttons").evaluate(
            "e=>getComputedStyle(e).gridTemplateColumns.split(/\\s+/).length")
        assert cols == (1 if width <= 359 else 2), (width, cols)
        page.evaluate("window.__battleClicks=0;document.getElementById('bf2100-attacks').addEventListener('click',()=>window.__battleClicks++)")
        page.locator("#bf2100-attacks").click()
        assert page.evaluate("window.__battleClicks") == 1
        page.keyboard.press("Tab")
        page.locator("#bf2100-guards").focus()
        assert page.locator("#bf2100-guards").evaluate("e=>e.matches(':focus-visible')")
        assert page.locator("#bf2100-guards").evaluate(
            "e=>getComputedStyle(e).outlineStyle") != "none"
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth+1"), width
        page.locator('.bf-navbar button[data-bf-goto="home"]').click()
        assert page.locator("#bf2100-tray").is_hidden()
        assert not errors, (width, errors)
        page.close()
    browser.close()
print("PASS v260 browser: original battle and demo tray controls fit 320–540px; touch/disabled/focus preserved")
