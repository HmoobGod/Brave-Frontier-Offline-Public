"""v277 Unit Box detail navigation is readable and touch accessible, without data writes."""
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/"app/src/main/assets"
CSS=(ASSETS/"bf_home_nav.css").read_text("utf8")
JS=(ASSETS/"bf_home_nav.js").read_text("utf8")
PRE=(ROOT/".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
BUILD=(ROOT/".github/workflows/build-debug-apk.yml").read_text("utf8")
MAN=(ROOT/"app/src/main/AndroidManifest.xml").read_text("utf8")
MARK="/* v277 Unit Box detail navigation: accessible touch targets, no changed actions. */"
assert CSS.count(MARK)==1
DELTA=CSS.split(MARK,1)[1]
for token in (".bf-owned-box .bf-box-detail .bf-box-manage",
              ".bf-owned-box .bf-box-detail .bf-box-original-profile",
              ".bf-owned-box .bf-box-detail .bf-evo-open",
              "min-height:44px","min-width:44px","overflow-wrap:anywhere",
              ".bf-box-original-profile:focus-visible","outline:3px solid"):
    assert token in DELTA,token
for token in ("display:none","localStorage.","saveProgress(","P.roster","P.gems","fetch("):
    assert token not in DELTA,token
assert "test_bf_unit_box_detail_actions_v27700.py --source-only" in PRE
assert BUILD.count("python3 test_bf_unit_box_detail_actions_v27700.py")==1
assert "android.permission.INTERNET" not in MAN
assert len(JS.encode())<128*1024 and len(CSS.encode())<128*1024
print("PASS v277 source: scoped read-only detail navigation touch targets")
if "--source-only" in sys.argv[1:]:
    raise SystemExit(0)

from playwright.sync_api import sync_playwright
chrome=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome,"Chromium required for v277 UI regression"
HTML=(ASSETS/"index.html").read_text("utf8")
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=chrome,
                               args=["--no-sandbox","--disable-dev-shm-usage"])
    for width in (320,359,393,540):
        context=browser.new_context(viewport={"width":width,"height":800},
                                    reduced_motion="reduce",service_workers="block")
        page=context.new_page()
        errors=[]
        page.on("pageerror",lambda e:errors.append(str(e)))
        page.on("dialog",lambda d:d.dismiss())
        page.route("http://**/*",lambda route:route.abort())
        page.route("https://**/*",lambda route:route.abort())
        page.evaluate("""() => {const m=Object.create(null);window.__v277=m;
          Object.defineProperty(window,"localStorage",{configurable:true,value:{
            getItem:k=>m[k]??null,setItem:(k,v)=>m[k]=String(v),
            removeItem:k=>delete m[k],clear:()=>Object.keys(m).forEach(k=>delete m[k]),
            key:i=>Object.keys(m)[i]??null,get length(){return Object.keys(m).length}
          }});}""")
        page.set_content(HTML,wait_until="load",timeout=120000)
        page.add_style_tag(content=CSS)
        page.add_script_tag(content=JS)
        page.evaluate("BF_homeNav.go('units');BFInnerScreens.setTab('box');BFUnitBox.refresh()")
        state="""() => JSON.stringify({
          roster:P.roster,squad:P.squad,exp:P.unitExp,evolutions:P.evolutions,
          gems:P.gems,zel:P.zel,karma:P.karma,
          save:localStorage.getItem('bf_global_offline_demo_v7'),storage:window.__v277
        })"""
        baseline=page.evaluate(state)
        cards=page.locator("#bf-box-results button[data-bf-unit-id]")
        assert cards.count()==6,(width,"expected six default cards")
        cards.first.click()
        detail=page.locator("#bf-box-detail")
        manage=detail.locator("button.bf-box-manage")
        original=detail.locator("button.bf-box-original-profile")
        assert manage.count()==1 and original.count()==1,(width,"detail buttons")
        # Navigation display only; never activate squad/evolution/profile handlers.
        # Some rosters have no evolvable default unit; check the actual one if present,
        # otherwise add a noninteractive size-only fixture inside the real detail.
        preview=detail.locator("button.bf-evo-open")
        for idx in range(1,cards.count()):
            if preview.count(): break
            cards.nth(idx).click()
        synthetic=False
        if preview.count()==0:
            page.evaluate("""() => {
              const b=document.createElement('button');
              b.type='button';b.className='bf-evo-open';
              b.textContent='OPEN EVOLUTION LAB';
              document.getElementById('bf-box-detail').appendChild(b);
            }""")
            synthetic=True
        page.keyboard.press("Tab")
        for name,locator in (("manage",manage),("original profile",original),
                             ("evolution",preview)):
            assert locator.count()==1 and locator.is_visible(),(width,name)
            bounds=locator.evaluate("""e=>({
              width:e.getBoundingClientRect().width,
              height:e.getBoundingClientRect().height})""")
            assert bounds["width"]>=44 and bounds["height"]>=44,(width,name,bounds)
            locator.focus()
            style=locator.evaluate("""e=>({
              focused:document.activeElement===e,
              width:getComputedStyle(e).outlineWidth,
              style:getComputedStyle(e).outlineStyle})""")
            assert style=={"focused":True,"width":"3px","style":"solid"},(width,name,style)
        assert page.evaluate(state)==baseline,(width,"roster/save changed")
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"),(width,"overflow")
        assert not errors,(width,errors[:3])
        context.close()
        print("PASS v277",width,"three detail navigation targets >=44px;",
              "synthetic evolution button" if synthetic else "real evolution button",
              "unchanged save")
    browser.close()
print("PASS v277 all widths, isolated game/save")
