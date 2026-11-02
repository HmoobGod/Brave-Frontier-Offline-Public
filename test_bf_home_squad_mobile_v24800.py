"""v248 original Global Home six-slot squad preview: responsive CSS only."""
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parent
A=ROOT/"app/src/main/assets"
JS=(A/"bf_home_nav.js").read_text("utf8")
CSS=(A/"bf_home_nav.css").read_text("utf8")
WF=(ROOT/".github/workflows/build-debug-apk.yml").read_text("utf8")
PRE=(ROOT/".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
MAN=(ROOT/"app/src/main/AndroidManifest.xml").read_text("utf8")
HOME=JS.split("/* Build #9: original Global home location hub",1)[1].split(
    "/* Build #11 - recovered BF1 Global artwork",1)[0]

assert "/* v248: original six-unit Home squad preview" in CSS
s=CSS.split("/* v248: original six-unit Home squad preview",1)[1]
assert re.search(r"@media\(max-width:412px\)\s*\{",s)
assert re.search(r"\.bf-scene-party\s*\{\s*grid-template-columns:repeat\(3,minmax\(0,1fr\)\)",s)
assert re.search(r"\.bf-scene-member strong\s*\{\s*font-size:11px",s)
assert re.search(r"\.bf-scene-member small\s*\{\s*font-size:10px",s)
assert not any(x in s for x in ("display:none", "visibility:hidden", "pointer-events:none",
                                "localStorage", "#battle", "animation-duration"))
assert "for (let index = 0; index < 6; index++)" in HOME
assert "party.replaceChildren(...nodes);" in HOME
assert "window.BFGlobalHome = {refreshParty};" in HOME
assert WF.count("python3 test_bf_home_squad_mobile_v24800.py") == 1
assert PRE.count("test_bf_home_squad_mobile_v24800.py") == 2
assert len(JS.encode("utf8")) <= 128*1024 and len(CSS.encode("utf8")) <= 128*1024
assert "android.permission.INTERNET" not in MAN
print("PASS v248 source: six-slot Home squad uses three phone columns without state changes")
if "--source-only" in sys.argv:
    raise SystemExit(0)

import shutil
from playwright.sync_api import sync_playwright
chrome=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "Chromium required for v248 browser checks"
marker="\n})();"
bootstrap=marker.join(JS.split(marker)[:2])+marker
html="""<!doctype html><html><head><meta charset="utf-8"></head><body>
<main class="wrap"><section class="progresspanel">Saves</section>
<section class="questpanel">Quests</section><section class="squadsetup">Units</section>
<section class="summonpanel">Summon</section></main></body></html>"""
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=chrome,
        args=["--no-sandbox","--disable-dev-shm-usage"])
    for width in (320,360,393,412,540):
        page=browser.new_page(viewport={"width":width,"height":760})
        errors=[]
        page.on("pageerror",lambda error:errors.append(str(error)))
        page.set_content(html)
        page.add_style_tag(content=CSS)
        page.add_script_tag(content=bootstrap)
        grid=page.locator("#bf-scene-party")
        cards=grid.locator(".bf-scene-member")
        assert cards.count()==6
        sizes=grid.evaluate("""el=>({
            cols:getComputedStyle(el).gridTemplateColumns.split(' ').length,
            scroll:el.scrollWidth,client:el.clientWidth
        })""")
        assert sizes["cols"]==(3 if width<=412 else 6),(width,sizes)
        assert sizes["scroll"] <= sizes["client"]+2,(width,sizes)
        for item in cards.all():
            assert item.get_attribute("aria-label")=="Empty squad slot"
            m=item.evaluate("""el=>({
                size:el.getBoundingClientRect().width,
                minHeight:parseFloat(getComputedStyle(el).minHeight)
            })""")
            assert m["size"] >= 36 and m["minHeight"] >= 90,(width,m)
        page.locator(".bf-scene-squad button[data-bf-goto='units']").click()
        assert page.evaluate("BF_homeNav.current")=="units"
        assert not errors,(width,errors)
        page.close()
    browser.close()
print("PASS v248 browser: six visible squad slots, 3/6 responsive columns and Units route")
