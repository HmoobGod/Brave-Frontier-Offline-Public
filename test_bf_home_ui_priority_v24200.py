"""v242: visible original-asset Home prioritization, browser + source regressions.

No reward, game-state, save, unit, or network semantics are changed by v242.
"""
from pathlib import Path
import re
import sys

R=Path(__file__).resolve().parent
A=R/"app/src/main/assets"
J=(A/"bf_home_nav.js").read_text("utf8")
C=(A/"bf_home_nav.css").read_text("utf8")
W=(R/".github/workflows/build-debug-apk.yml").read_text("utf8")
PRE=(R/".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
M=(R/"app/src/main/AndroidManifest.xml").read_text("utf8")

start=J.index("/* Build #9: original Global home location hub")
end=J.index("/* Build #11 - recovered BF1 Global artwork")
home=J[start:end]
available="bf-scene-available-label"
archived="bf-scene-archive-label"
assert home.count(available)==1 and home.count(archived)==1
assert home.count('class="bf-scene-place bf-scene-active bf-scene-featured"')==2
assert home.count('class="bf-scene-place bf-scene-locked"')==4
assert home.index("AVAILABLE OFFLINE") < home.index('data-bf-goto="quest"') < home.index('data-bf-goto="summon"') < home.index("RECOVERED GLOBAL LOCATIONS") < home.index("Vortex Gate not implemented")
for path in ("home_win_quest.png","home_win_akras_smn_hall.png",
             "home_win_gate.png","home_win_arena.png",
             "home_win_raid_open.png","home_win_randall.png"):
    assert path in home
    assert (A/"content/home"/path).is_file(), path
assert "window.BFGlobalHome = {refreshParty};" in home
assert 'data-bf-goto="menu"' in home
assert "window.BF_homeNav = {go,get current()" in J
assert "/* v242: visual-first Home hierarchy" in C
sty=C.split("/* v242: visual-first Home hierarchy",1)[1]
for selector in (".bf-scene-places button.bf-scene-featured",
                 ".bf-scene-places .bf-scene-locked",
                 ".bf-scene-available-label",
                 ".bf-scene-archive-label",
                 "max-width:359px"):
    assert selector in sty
for forbidden in ("localStorage","saveProgress(","awardDemoRewards(",
                  "P.","S.","#battle", "animation-duration"):
    assert forbidden not in sty
for forbidden in ("localStorage.setItem(","saveProgress(","P.squad =",
                  "P.questClears =","awardDemoRewards("):
    assert forbidden not in home, forbidden
assert "android.permission.INTERNET" not in M
assert W.count("test_bf_home_ui_priority_v24200.py")==1
assert PRE.count("test_bf_home_ui_priority_v24200.py")==2
assert len(J.encode("utf8"))<128*1024 and len(C.encode("utf8"))<128*1024
print("PASS v242 source: active Home destinations first, original art intact, no game/save changes")
if "--source-only" in sys.argv:
    raise SystemExit(0)

import shutil
from playwright.sync_api import sync_playwright
chrome=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "Chromium required by full visual UI regression"
marker="\n})();"
assert J.count(marker)>=2
pilot=marker.join(J.split(marker)[:2])+marker
html='''<!doctype html><html><head><meta charset="utf-8"></head><body>
<main class="wrap">
<section class="progresspanel">Save menu</section>
<section class="questpanel">Quest route</section>
<section class="squadsetup">Units route</section>
<section class="summonpanel">Summon route</section>
</main></body></html>'''
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=chrome,
                               args=["--no-sandbox","--disable-dev-shm-usage"])
    for width in (320,360,393,412,540):
        page=browser.new_page(viewport={"width":width,"height":750},device_scale_factor=2)
        errors=[]
        page.on("pageerror",lambda error:errors.append(str(error)))
        page.set_content(html)
        page.add_style_tag(content=C)
        page.add_script_tag(content=pilot)
        assert page.locator(".bf-scene-featured").count()==2
        assert page.locator(".bf-scene-locked").count()==4
        assert page.locator(".bf-scene-places > :first-child").get_attribute("class")==available
        positions=page.locator(".bf-scene-places").evaluate(
            "(root)=>Array.from(root.children).map(el=>el.className)")
        assert positions[:4]==[available,"bf-scene-place bf-scene-active bf-scene-featured",
                               "bf-scene-place bf-scene-active bf-scene-featured",archived],positions
        bounds=page.locator(".bf-scene-places").evaluate(
            "(el)=>({scroll:el.scrollWidth,client:el.clientWidth})")
        assert bounds["scroll"] <= bounds["client"]+2,(width,bounds)
        assert page.locator(".bf-scene-featured").first.evaluate(
            "(el)=>getComputedStyle(el).minHeight") != "0px"
        page.locator('.bf-scene-featured[data-bf-goto="summon"]').click()
        assert page.evaluate("BF_homeNav.current")=="summon"
        page.locator('.bf-navbar [data-bf-goto="home"]').click()
        page.locator('.bf-scene-featured[data-bf-goto="quest"]').click()
        assert page.evaluate("BF_homeNav.current")=="quest"
        page.locator('.bf-navbar [data-bf-goto="home"]').click()
        page.locator('.bf-scene-toolrow [data-bf-goto="menu"]').click()
        assert page.evaluate("BF_homeNav.current")=="menu"
        assert not errors,(width,errors)
        page.close()
    browser.close()
print("PASS v242 browser: 320/360/393/412/540px usable Quest, Summon and Saves UI")
