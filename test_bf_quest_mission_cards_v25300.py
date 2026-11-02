"""v253 — Quest card visual/accessibility smoke tests; no quest logic changes."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
CSS = (ASSETS / "bf_home_nav.css").read_text("utf8")
JS = (ASSETS / "bf_home_nav.js").read_text("utf8")
WF = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf8")
PRE = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
MAN = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf8")
START = CSS.index("/* v253 UI-only:")
PATCH = CSS[START:]
assert "content/mission_select/mission_frame_off.png" in PATCH
assert "button.questcard:disabled" in PATCH
assert "button.questcard:focus-visible" in PATCH
assert "button.questcard:active:not(:disabled)" in PATCH
assert "touch-action:manipulation" in PATCH
assert "overflow-wrap:anywhere" in PATCH
assert "max-width:100%" in PATCH
assert "min-height:68px" in PATCH
assert "min-height:76px" in PATCH
assert "test_bf_quest_mission_cards_v25300.py --source-only" in PRE
assert WF.count("python3 test_bf_quest_mission_cards_v25300.py") == 1
assert "android.permission.INTERNET" not in MAN
assert len(CSS.encode("utf8")) < 128*1024
assert len(JS.encode("utf8")) < 128*1024
for forbidden in ("localStorage.", "saveProgress(", "P.questClears",
                  "P.gems", "QUEST=", "fetch(", "XMLHttpRequest("):
    assert forbidden not in PATCH, forbidden
print("PASS v253 source: mission-list touch, disabled/focus styles, read-only original art and unchanged save")
if "--source-only" in sys.argv[1:]:
    raise SystemExit(0)

import shutil
from playwright.sync_api import sync_playwright
chrome = shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "Chromium is required for v253 UI acceptance"
marker = "\n})();"
bootstrap = marker.join(JS.split(marker)[:2]) + marker
fixture = """<!doctype html><html><head><meta charset="utf-8"></head><body>
<main class="wrap">
<section class="progresspanel">Save controls</section>
<section class="squadsetup">Unit controls</section>
<section class="summonpanel">Summon controls</section>
<section class="questpanel"><div id="questlist">
<button type="button" class="questcard" id="q1"><strong>Mission 12 — Recovery of Grand Gaia and Original Global Progression</strong><small>Playable offline demo mission</small></button>
<button type="button" class="questcard" id="q2" disabled><strong>Locked mission</strong><small>Unlock progression required</small></button>
<button type="button" class="questcard" id="q3" hidden><strong>Hidden filtered mission</strong></button>
</div></section></main></body></html>"""
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=chrome,
                                 args=["--no-sandbox","--disable-dev-shm-usage"])
    for width in (320,360,393,412,540):
        page = browser.new_page(viewport={"width":width,"height":760})
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.set_content(fixture)
        page.add_style_tag(content=CSS)
        page.add_script_tag(content=bootstrap)
        page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
        active = page.locator("#q1")
        locked = page.locator("#q2")
        hidden = page.locator("#q3")
        assert active.is_visible() and locked.is_visible(), width
        assert hidden.is_hidden(), width
        assert locked.is_disabled(), width
        for button in (active,locked):
            values = button.evaluate("""e=>{
               const c=getComputedStyle(e),r=e.getBoundingClientRect();
               return {height:r.height,left:r.left,right:r.right,
                 minHeight:parseFloat(c.minHeight),font:parseFloat(getComputedStyle(e.querySelector('strong')).fontSize),
                 art:c.backgroundImage.includes('mission_frame_off.png'),
                 wrap:getComputedStyle(e.querySelector('strong')).overflowWrap}
            }""")
            assert values["minHeight"] >= 68, (width,values)
            assert values["height"] >= 68, (width,values)
            assert values["art"] and values["wrap"]=="anywhere", (width,values)
            assert values["left"] >= -1 and values["right"] <= width+1, (width,values)
        assert float(locked.evaluate("e=>getComputedStyle(e).opacity")) < .8
        active.focus()
        assert active.evaluate("e=>getComputedStyle(e).outlineStyle") != "none"
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth+1"), width
        page.locator('.bf-navbar button[data-bf-goto="home"]').click()
        assert active.is_hidden() and page.locator("#bf-home").is_visible(), width
        assert not errors, (width,errors)
        page.close()
    browser.close()
print("PASS v253 browser: Quest cards readable/touch-safe with disabled, hidden, focus and route state at five widths")
