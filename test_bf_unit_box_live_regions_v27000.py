"""v270: Unit Box live announcements and keyboard filter-reset regression.

Runs against the actual packaged index.html in disposable, network-blocked
Chromium with synthetic in-memory storage. Never opens an owner's saved game.
"""
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/"app/src/main/assets"
HTML=(ASSETS/"index.html").read_text("utf8")
JS=(ASSETS/"bf_home_nav.js").read_text("utf8")
CSS=(ASSETS/"bf_home_nav.css").read_text("utf8")
SRC=(ROOT/".github/workflows/android-back-ui-source-preflight.yml").read_text()
BUILD=(ROOT/".github/workflows/build-debug-apk.yml").read_text()
MAN=(ROOT/"app/src/main/AndroidManifest.xml").read_text()

assert '<div id="bf-box-results" class="bf-box-results"></div>' in JS
assert '<div id="bf-box-results" class="bf-box-results" aria-live=' not in JS
assert 'id="bf-box-count" role="status" aria-live="polite"' in JS
assert JS.count("empty.setAttribute('role','status')")==1
assert "clear.addEventListener('click'" in JS
assert "test_bf_unit_box_live_regions_v27000.py --source-only" in SRC
assert BUILD.count("python3 test_bf_unit_box_live_regions_v27000.py")==1
assert "android.permission.INTERNET" not in MAN
assert len(JS.encode("utf8"))<128*1024 and len(CSS.encode("utf8"))<128*1024
print("PASS v270 source: sibling status regions, original filter behavior and CI")
if "--source-only" in sys.argv[1:]:
    raise SystemExit(0)

from playwright.sync_api import sync_playwright
chrome=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "Chromium needed for v270 real-page browser test"
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=chrome,
                               args=["--no-sandbox","--disable-dev-shm-usage"])
    for width in (320,359,393,540):
        ctx=browser.new_context(viewport={"width":width,"height":790},
                                reduced_motion="reduce",service_workers="block")
        page=ctx.new_page()
        errors=[]
        page.on("pageerror",lambda e:errors.append(str(e)))
        page.on("dialog",lambda d:d.dismiss())
        page.route("http://**/*",lambda route:route.abort())
        page.route("https://**/*",lambda route:route.abort())
        page.evaluate("""() => {const data=Object.create(null);window.__v270=data;
          Object.defineProperty(window,"localStorage",{configurable:true,value:{
            getItem:k=>data[k]??null,setItem:(k,v)=>data[k]=String(v),
            removeItem:k=>delete data[k],clear:()=>Object.keys(data).forEach(k=>delete data[k]),
            key:n=>Object.keys(data)[n]??null,get length(){return Object.keys(data).length}
          }});
        }""")
        page.set_content(HTML,wait_until="load",timeout=120000)
        page.add_style_tag(content=CSS)
        page.add_script_tag(content=JS)
        page.evaluate("BF_homeNav.go('units');BFInnerScreens.setTab('box');BFUnitBox.refresh()")
        snapshot="""()=>JSON.stringify({r:P.roster,s:P.squad,x:P.unitExp,e:P.evolutions,
          g:P.gems,z:P.zel,k:P.karma,save:localStorage.getItem('bf_global_offline_demo_v7'),
          store:window.__v270})"""
        before=page.evaluate(snapshot)
        results=page.locator("#bf-box-results")
        count=page.locator("#bf-box-count")
        assert results.get_attribute("aria-live") is None,(width,"nested live results")
        assert results.get_attribute("role") is None,(width,"unexpected results role")
        assert count.get_attribute("role")=="status"
        assert count.get_attribute("aria-live")=="polite"
        assert results.locator("button.bf-box-card").count()==6
        page.locator("#bf-box-sort").select_option("level")
        page.locator("#bf-box-filter").select_option("reserve")
        element=page.locator("#bf-box-element option").all()
        rarity=page.locator("#bf-box-rarity option").all()
        assert len(element)>1 and len(rarity)>1
        page.locator("#bf-box-element").select_option(element[1].get_attribute("value"))
        page.locator("#bf-box-rarity").select_option(rarity[1].get_attribute("value"))
        missing=results.locator(".bf-box-empty")
        assert missing.is_visible() and missing.get_attribute("role")=="status"
        assert missing.locator("p").inner_text()=="No owned units match the current filters."
        clear=missing.locator("button.bf-box-clear-filters")
        assert clear.is_visible()
        assert clear.evaluate("e=>e.getBoundingClientRect().height")>=44
        clear.focus()
        assert clear.evaluate("e=>getComputedStyle(e).outlineStyle")!="none"
        clear.press("Enter")
        for name in ("#bf-box-search","#bf-box-filter","#bf-box-element","#bf-box-rarity"):
            assert page.locator(name).input_value() in ("","all"),(width,name)
        assert page.locator("#bf-box-sort").input_value()=="level"
        assert results.locator("button.bf-box-card").count()==6
        assert page.evaluate("document.activeElement.id")=="bf-box-search"
        page.locator("#bf-box-search").fill("no_matching_unit_v270")
        clear=results.locator("button.bf-box-clear-filters")
        clear.focus()
        clear.press("Space")
        assert results.locator("button.bf-box-card").count()==6
        assert page.locator("#bf-box-search").input_value()==""
        assert page.evaluate("document.activeElement.id")=="bf-box-search"
        assert before==page.evaluate(snapshot),(width,"UI modified player/save")
        # Simulate a new empty-roster save only in this throwaway browser.
        page.evaluate("()=>{P.roster=[];P.squad=[];BFUnitBox.refresh()}")
        empty_before=page.evaluate(snapshot)
        empty=results.locator(".bf-box-empty")
        assert empty.is_visible() and empty.get_attribute("role")=="status"
        assert empty.locator("p").inner_text()=="No owned units are available in this offline save."
        assert empty.locator("button").count()==0
        assert count.inner_text().startswith("0 shown / 0 owned")
        assert empty_before==page.evaluate(snapshot)
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"),width
        assert not errors,(width,errors[:3])
        ctx.close()
        print("PASS v270",width,"status regions, Enter/Space, four filters and unchanged save")
    browser.close()
print("PASS v270: 4 original-page mobile widths")
