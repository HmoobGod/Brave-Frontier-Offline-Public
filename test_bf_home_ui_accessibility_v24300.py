"""v243 source and browser: Menu icon responsive fix, original-art Home semantics.

No game logic, v7 save, rewards, AI, or original image bytes are changed.
"""
from pathlib import Path
import re, sys

R=Path(__file__).resolve().parent
A=R/"app/src/main/assets"
C=(A/"bf_home_nav.css").read_text("utf8")
J=(A/"bf_home_nav.js").read_text("utf8")
PRE=(R/".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
WF=(R/".github/workflows/build-debug-apk.yml").read_text("utf8")
MAN=(R/"app/src/main/AndroidManifest.xml").read_text("utf8")
head=J.split("/* Build #9: original Global home location hub",1)[1].split("/* Build #11 - recovered BF1 Global artwork",1)[0]
assert head.count('role="heading" aria-level="3"')==2
assert 'class="bf-scene-available-label" role="heading" aria-level="3"' in head
assert 'class="bf-scene-archive-label" role="heading" aria-level="3"' in head
for name in ("Vortex Gate", "Arena", "Raid Battle", "Capital Randall"):
    assert f'role="group" aria-label="{name} not implemented"' in head
assert head.count('class="bf-scene-place bf-scene-locked" role="group"')==4
assert head.count('class="bf-scene-place bf-scene-active bf-scene-featured"')==2
narrow=C.split("@media(max-width:360px){",1)[1].split("}",1)[0]
# This media query contains rule closing braces: check through last nav-art rule.
narrow=C.split("@media(max-width:360px){",1)[1].split("/* Build #9: Global-art hub",1)[0]
assert re.search(r'\.bf-nav-art-menu\s*\{\s*background-size:contain;\s*background-position:center\s*\}',narrow)
styles=C.split("/* v242: visual-first Home hierarchy",1)[1]
assert re.search(r'\.bf-scene-places\s+\.bf-scene-locked\s*\{[^}]*opacity:\.76',styles)
assert re.search(r'\.bf-scene-places\s+\.bf-scene-locked\s+\.bf-scene-status\s*\{[^}]*font-size:10px',styles)
assert WF.count("test_bf_home_ui_accessibility_v24300.py")==1
assert PRE.count("test_bf_home_ui_accessibility_v24300.py")==2
assert "android.permission.INTERNET" not in MAN
assert not any(term in head for term in ("saveProgress(", "localStorage.setItem(", "awardDemoRewards(", "P.questClears=", "P.squad="))
assert len(C.encode("utf8"))<128*1024 and len(J.encode("utf8"))<128*1024
print("PASS v243 source: Menu original art at <=360px, accessible locked cards, 10px labels, unchanged save")
if "--source-only" in sys.argv:
    raise SystemExit(0)

import shutil
from playwright.sync_api import sync_playwright
chrome=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "Chromium required for v243 UI browser checks"
marker="\n})();"
bootstrap=marker.join(J.split(marker)[:2])+marker
html="""<!doctype html><html><head><meta charset="utf-8"></head><body><main class="wrap">
<section class="progresspanel">Saves</section><section class="questpanel">Quests</section>
<section class="squadsetup">Units</section><section class="summonpanel">Summon</section>
</main></body></html>"""
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True,executable_path=chrome,
                         args=["--no-sandbox","--disable-dev-shm-usage"])
    for width in (320,360,393,412,540):
        page=b.new_page(viewport={"width":width,"height":760},device_scale_factor=2)
        errors=[]
        page.on("pageerror",lambda err:errors.append(str(err)))
        page.set_content(html)
        page.add_style_tag(content=C)
        page.add_script_tag(content=bootstrap)
        art=page.locator(".bf-nav-art-menu").evaluate(
            "(el)=>({size:getComputedStyle(el).backgroundSize,image:getComputedStyle(el).backgroundImage})")
        assert art["size"]=="contain",(width,art)
        assert "home_new_btn_menu1.png" in art["image"],(width,art)
        locked=page.locator(".bf-scene-places .bf-scene-locked")
        assert locked.count()==4
        for ix,name in enumerate(("Vortex Gate","Arena","Raid Battle","Capital Randall")):
            el=locked.nth(ix)
            assert el.get_attribute("role")=="group"
            assert el.get_attribute("aria-label")==name+" not implemented"
            computed=el.evaluate("""el=>({
              size:parseFloat(getComputedStyle(el.querySelector('.bf-scene-status')).fontSize),
              fit:getComputedStyle(el.querySelector('img')).objectFit
            })""")
            assert computed["size"]>=10,(width,name,computed)
            assert computed["fit"]=="contain",(width,name,computed)
        assert page.locator(".bf-scene-places [role=heading]").count()==2
        assert page.locator(".bf-scene-places button").count()==2
        page.locator('.bf-navbar button[data-bf-goto="menu"]').click()
        assert page.evaluate("BF_homeNav.current")=="menu"
        page.locator('.bf-navbar button[data-bf-goto="home"]').click()
        page.locator('.bf-scene-featured[data-bf-goto="quest"]').click()
        assert page.evaluate("BF_homeNav.current")=="quest"
        assert not errors,(width,errors)
        page.close()
    b.close()
print("PASS v243 browser: Menu sprite, headings/groups, readable art-only labels, routing at five widths")
