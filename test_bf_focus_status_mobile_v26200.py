"""v262 read-only mobile tactical focus and ailment disclosure regressions.

Checks that late-injected v31/v78 styles cannot shrink the effective touch targets.
The browser fixture is isolated: it is not a combat-engine or saved-game test.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
A = ROOT / "app/src/main/assets"
CSS = (A / "bf_home_nav.css").read_text("utf8")
NAV = (A / "bf_home_nav.js").read_text("utf8")
FOCUS = (A / "bf3100_battle_focus.js").read_text("utf8")
STATUS = (A / "bf7800_live_battle_status.js").read_text("utf8")
PRE = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
WF = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf8")
MAN = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf8")

MARKER = "/* v262 battle tactical focus/status mobile controls"
assert CSS.count(MARKER) == 1
PATCH = CSS.split(MARKER, 1)[1]
for token in (
    "#bf2100-tray #bf3100-options",
    "#bf2100-tray #bf3100-focus button",
    "#bf2100-tray #bf3100-status",
    "min-height:50px",
    "#bf7800-status[hidden]",
    "#bf7800-status #bf7800-heading",
    "#bf7800-status .bf7800-chip",
    "min-height:48px",
    "display:none!important",
    "overflow-wrap:anywhere",
    "touch-action:manipulation",
    ":focus-visible",
    "@media(max-width:359px)",
    "grid-template-columns:minmax(0,1fr)",
    "grid-template-columns:repeat(2,minmax(0,1fr))",
):
    assert token in PATCH, token
for forbidden in (
    "localStorage.", "saveProgress(", "P.gems", "P.questClears",
    "S.party", "S.enemies", "window.", "document.", "fetch(",
    "XMLHttpRequest(", "setInterval(", "onclick=",
):
    assert forbidden not in PATCH, forbidden
assert "'#bf3100-focus button{background:#35516b" in FOCUS
assert "#bf7800-status summary{cursor:pointer;min-height:34px" in STATUS
for token in ("LOWEST HP", "HIGHEST ATK", "LOWEST DEF", "FOCUS + BB IF READY"):
    assert token in FOCUS
for token in ("Poison", "Curse", "Paralysis", "DEMO round"):
    assert token in STATUS
assert "test_bf_focus_status_mobile_v26200.py --source-only" in PRE
assert WF.count("python3 test_bf_focus_status_mobile_v26200.py") == 1
assert "android.permission.INTERNET" not in MAN
assert len(CSS.encode("utf8")) < 128 * 1024
assert len(NAV.encode("utf8")) < 128 * 1024
print("PASS v262 source: scoped focus/status UI only, existing DEMO engine and save intact")
if "--source-only" in sys.argv[1:]:
    raise SystemExit(0)

import shutil
from playwright.sync_api import sync_playwright

chrome = (shutil.which("chromium") or shutil.which("google-chrome") or
          shutil.which("google-chrome-stable"))
assert chrome, "Chromium is required for v262 responsive test"
marker = "\n})();"
bootstrap = marker.join(NAV.split(marker)[:2]) + marker
fixture = """<!doctype html><html><head><meta charset="utf-8"></head><body>
<main class="wrap">
<section class="progresspanel">Save</section>
<section class="squadsetup">Units</section>
<section class="summonpanel">Summon</section>
<section class="questpanel">
<div id="questlist">Quests</div>
<details id="bf7800-status" aria-label="Live ally battle statuses and supported protection">
<summary id="bf7800-heading">BATTLE STATUS · 2 AFFECTED ALLIES</summary>
<div id="bf7800-rows">
<div class="bf7800-row"><strong class="bf7800-unit">1. Very Long Archived Original Global Ally Name</strong>
<span class="bf7800-chip">Poison · DEMO HP loss each tick</span>
<span class="bf7800-chip bf7800-protection">Nullifier · 3 DEMO rounds left</span></div></div>
<small>Archived 2022 ailments; round timing remains DEMO.</small></details>
</section>
<section class="squad-panel">
<div id="bf2100-tray"><section id="bf3100-focus">
<h3>TACTICAL FOCUS · DEMO</h3>
<div id="bf3100-options">
<button id="focus-low">LOWEST HP + ATTACK</button>
<button id="focus-high">HIGHEST ATK + ATTACK</button>
<button id="focus-def">LOWEST DEF + ATTACK</button>
<button id="focus-burst" disabled>FOCUS + BB IF READY</button>
</div>
<p id="bf3100-status">Focus Very Long Archived DEMO Enemy Name · lowest HP · 999999 HP</p>
<small>Optional simulated enemy targeting; original 2022 combat AI not claimed.</small>
</section></div></section></main></body></html>"""
# Real scripts insert their own CSS *after* the Home navigation stylesheet.
runtime_css = """
#bf3100-focus{margin-top:12px;padding:10px 0;border-top:1px solid #a48d6b}
#bf3100-options{display:grid;grid-template-columns:repeat(auto-fit,minmax(105px,1fr));gap:7px}
#bf3100-focus button{min-height:42px;padding:7px;font-weight:bold}
#bf3100-focus button:disabled{opacity:.4}
#bf3100-status{margin:9px 0}
#bf7800-status{margin:9px 11px;padding:8px;border:1px solid #978fba}
#bf7800-status[hidden]{display:none!important}
#bf7800-status summary{cursor:pointer;min-height:34px;font-weight:800}
#bf7800-status .bf7800-row{padding:6px 0}
#bf7800-status .bf7800-chip{display:inline-block;margin:2px 5px 2px 0;padding:3px 6px}
"""
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=chrome,
                                 args=["--no-sandbox", "--disable-dev-shm-usage"])
    for width in (320, 359, 360, 393, 412, 540):
        page = browser.new_page(viewport={"width":width,"height":760})
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.set_content(fixture)
        page.add_style_tag(content=CSS)
        page.add_script_tag(content=bootstrap)
        page.add_style_tag(content=runtime_css)
        page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
        assert page.locator("#bf3100-focus").is_visible(), width
        grid = page.locator("#bf3100-options")
        cols = grid.evaluate("e=>getComputedStyle(e).gridTemplateColumns.trim().split(/\\s+/).length")
        assert cols == (1 if width<=359 else 2), (width, cols)
        choices = grid.locator("button")
        assert choices.count() == 4, width
        assert page.locator("#focus-burst").is_disabled(), width
        for item in choices.all():
            v = item.evaluate("""e=>{
              const c=getComputedStyle(e),r=e.getBoundingClientRect();
              return {height:r.height,minHeight:parseFloat(c.minHeight),
                left:r.left,right:r.right,wrap:c.overflowWrap,touch:c.touchAction}
            }""")
            assert v["height"]>=50 and v["minHeight"]>=50,(width,v)
            assert v["left"]>=-1 and v["right"]<=width+1,(width,v)
            assert v["wrap"]=="anywhere" and v["touch"]=="manipulation",(width,v)
        details = page.locator("#bf7800-status")
        summary = page.locator("#bf7800-heading")
        assert details.is_visible() and summary.is_visible(), width
        v = summary.evaluate("""e=>{
          const c=getComputedStyle(e),r=e.getBoundingClientRect();
          return {height:r.height,minHeight:parseFloat(c.minHeight),
            left:r.left,right:r.right,touch:c.touchAction}
        }""")
        assert v["height"]>=48 and v["minHeight"]>=48,(width,v)
        assert v["left"]>=-1 and v["right"]<=width+1,(width,v)
        assert v["touch"]=="manipulation",(width,v)
        assert details.get_attribute("open") is None, width
        summary.click()
        assert details.get_attribute("open") is not None, width
        chip=page.locator(".bf7800-chip").first
        assert chip.is_visible(), width
        assert chip.evaluate("e=>getComputedStyle(e).overflowWrap")=="anywhere", width
        assert page.locator(".bf7800-unit").evaluate(
            "e=>getComputedStyle(e).overflowWrap")=="anywhere",width
        page.evaluate("window.__focusClicks=0;document.getElementById('focus-low').addEventListener('click',()=>window.__focusClicks++)")
        page.locator("#focus-low").click()
        assert page.evaluate("window.__focusClicks")==1,width
        page.keyboard.press("Tab")
        page.locator("#focus-low").focus()
        assert page.locator("#focus-low").evaluate("e=>e.matches(':focus-visible')"),width
        assert page.locator("#focus-low").evaluate(
            "e=>getComputedStyle(e).outlineStyle")!="none",width
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"),width
        details.evaluate("e=>e.hidden=true")
        assert details.is_hidden(),width
        page.locator('.bf-navbar button[data-bf-goto="home"]').click()
        assert page.locator("#bf3100-focus").is_hidden(),width
        assert not errors,(width,errors)
        page.close()
    browser.close()
print("PASS v262 Chromium: tactical focus/status responsive touch, wrap, disclosure and route safety")
