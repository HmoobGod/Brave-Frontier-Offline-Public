"""v276 — Unit Box toolbar touch size/focus; source and network-blocked browser evidence.

No owner phone or persistent game save is accessed; all browser state is disposable.
"""
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
MARK="/* v276 Unit Box toolbar: five 44px phone controls without changing filter logic. */"
assert CSS.count(MARK)==1
DELTA=CSS.split(MARK,1)[1]
assert "body.bf-menu-mode .bf-owned-box .bf-box-filters input" in DELTA
assert "body.bf-menu-mode .bf-owned-box .bf-box-filters select" in DELTA
assert "min-height:44px" in DELTA and "display:none" not in DELTA
assert ".bf-box-filters input:focus-visible,.bf-box-filters select:focus-visible" in CSS
assert "test_bf_unit_box_toolbar_targets_v27600.py --source-only" in PRE
assert BUILD.count("python3 test_bf_unit_box_toolbar_targets_v27600.py")==1
assert "android.permission.INTERNET" not in MAN
assert len(CSS.encode())<128*1024 and len(JS.encode())<128*1024
print("PASS v276 source: Unit Box 44px toolbar, inherited keyboard focus, no network permission")
if "--source-only" in sys.argv:
    raise SystemExit(0)

from playwright.sync_api import sync_playwright
chrome=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "Chromium is required for full v276 browser regression"
HTML=(ASSETS/"index.html").read_text("utf8")
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=chrome,
                               args=["--no-sandbox","--disable-dev-shm-usage"])
    for width in (320,359,393,540):
        ctx=browser.new_context(viewport={"width":width,"height":800},
                                reduced_motion="reduce",service_workers="block")
        page=ctx.new_page()
        errors=[]
        page.on("pageerror",lambda e:errors.append(str(e)))
        page.on("dialog",lambda d:d.dismiss())
        page.route("http://**/*",lambda route:route.abort())
        page.route("https://**/*",lambda route:route.abort())
        page.evaluate("""() => {const m=Object.create(null);window.__v276=m;
          Object.defineProperty(window,"localStorage",{configurable:true,value:{
            getItem:k=>m[k]??null,setItem:(k,v)=>m[k]=String(v),
            removeItem:k=>delete m[k],clear:()=>Object.keys(m).forEach(k=>delete m[k]),
            key:i=>Object.keys(m)[i]??null,get length(){return Object.keys(m).length}
          }});}""")
        page.set_content(HTML,wait_until="load",timeout=120000)
        page.add_style_tag(content=CSS)
        page.add_script_tag(content=JS)
        page.evaluate("BF_homeNav.go('units');BFInnerScreens.setTab('box');BFUnitBox.refresh()")
        assert page.locator("#bf-box-results .bf-box-card").count()==6
        state="""() => JSON.stringify({
          roster:P.roster,squad:P.squad,exp:P.unitExp,evolutions:P.evolutions,
          gems:P.gems,zel:P.zel,karma:P.karma,
          save:localStorage.getItem('bf_global_offline_demo_v7'),storage:window.__v276
        })"""
        before=page.evaluate(state)
        ids=("#bf-box-search","#bf-box-filter","#bf-box-element",
             "#bf-box-rarity","#bf-box-sort")
        for field_id in ids:
            field=page.locator(field_id)
            assert field.is_visible(),(width,field_id,"missing")
            size=field.evaluate("""e=>({
              w:e.getBoundingClientRect().width,
              h:e.getBoundingClientRect().height})""")
            assert size["w"]>=44 and size["h"]>=44,(width,field_id,size)
            field.focus()
            outline=field.evaluate("""e=>({
              active:document.activeElement===e,
              width:getComputedStyle(e).outlineWidth,
              style:getComputedStyle(e).outlineStyle})""")
            assert outline=={"active":True,"width":"3px","style":"solid"},(width,field_id,outline)
        page.locator("#bf-box-search").fill("no_matching_unit_v276")
        assert page.locator("#bf-box-results .bf-box-card").count()==0
        page.locator(".bf-box-clear-filters").click()
        assert page.locator("#bf-box-results .bf-box-card").count()==6
        assert page.locator("#bf-box-search").input_value()==""
        assert page.evaluate(state)==before,(width,"unintended player or save mutation")
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"),(width,"overflow")
        assert not errors,(width,errors[:3])
        ctx.close()
        print("PASS v276",width,"five toolbar fields >=44px; focus and saved state unchanged")
    browser.close()
print("PASS v276 all four mobile widths; no owner save or device access")
