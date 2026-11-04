"""v275 — Training search/filter minimum touch targets, focus and save isolation."""
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/"app/src/main/assets"
CSS=(ASSETS/"bf_home_nav.css").read_text("utf8")
JS=(ASSETS/"bf_home_nav.js").read_text("utf8")
PRE=(ROOT/".github/workflows/android-back-ui-source-preflight.yml").read_text()
BUILD=(ROOT/".github/workflows/build-debug-apk.yml").read_text()
MAN=(ROOT/"app/src/main/AndroidManifest.xml").read_text()

MARK="/* v275 Training search and filters: 44px mobile hit targets and keyboard focus. */"
assert CSS.count(MARK)==1
block=CSS.split(MARK,1)[1]
assert "training-panel .training-toolbar input" in block
assert "training-panel .training-toolbar select" in block
assert "min-height:44px" in block and ":focus-visible" in block
assert "outline:3px solid" in block and "display:none" not in block
assert "/* v274 Training controls: 44px touch targets" in CSS
assert "test_bf_training_form_targets_v27500.py --source-only" in PRE
assert BUILD.count("python3 test_bf_training_form_targets_v27500.py")==1
assert "android.permission.INTERNET" not in MAN
assert len(JS.encode())<128*1024 and len(CSS.encode())<128*1024
print("PASS v275 source: 44px Training toolbar, focus and exact CI gate")
if "--source-only" in sys.argv[1:]:
    raise SystemExit(0)

from playwright.sync_api import sync_playwright
HTML=(ASSETS/"index.html").read_text("utf8")
chrome=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome,"Chromium required for v275 packaged browser test"

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=chrome,
                               args=["--no-sandbox","--disable-dev-shm-usage"])
    for width in (320,359,393,540):
        ctx=browser.new_context(viewport={"width":width,"height":790},
                                service_workers="block",reduced_motion="reduce")
        page=ctx.new_page();errors=[]
        page.on("pageerror",lambda e:errors.append(str(e)))
        page.on("dialog",lambda d:d.dismiss())
        page.route("http://**/*",lambda route:route.abort())
        page.route("https://**/*",lambda route:route.abort())
        page.evaluate("""()=>{const m=Object.create(null);window.__v275=m;
          Object.defineProperty(window,'localStorage',{configurable:true,value:{
            getItem:k=>m[k]??null,setItem:(k,v)=>m[k]=String(v),
            removeItem:k=>delete m[k],clear:()=>Object.keys(m).forEach(k=>delete m[k]),
            key:i=>Object.keys(m)[i]??null,get length(){return Object.keys(m).length}
          }});}""")
        page.set_content(HTML,wait_until="load",timeout=120000)
        page.add_style_tag(content=CSS)
        page.add_script_tag(content=JS)
        state="""()=>JSON.stringify({
          roster:P.roster,squad:P.squad,unitExp:P.unitExp,
          evolutions:P.evolutions,trainingShards:P.trainingShards,
          trainingSpent:P.trainingSpent,gems:P.gems,zel:P.zel,karma:P.karma,
          save:localStorage.getItem('bf_global_offline_demo_v7'),
          storage:window.__v275
        })"""
        before=page.evaluate(state)
        page.evaluate("BF_homeNav.go('units');BFInnerScreens.setTab('training')")
        fields=page.locator(".training-panel .training-toolbar input, .training-panel .training-toolbar select")
        buttons=page.locator(".training-panel .train-actions button")
        assert fields.count()==3,(width,"Training search/filter/sort count")
        assert buttons.count()==12,(width,"v274 Training buttons")
        for label,items in (("forms",fields),("actions",buttons)):
            for i in range(items.count()):
                size=items.nth(i).evaluate("""e=>({
                  w:e.getBoundingClientRect().width,
                  h:e.getBoundingClientRect().height,
                  visible:getComputedStyle(e).visibility})""")
                assert size["w"]>=44 and size["h"]>=44 and size["visible"]=="visible",(width,label,i,size)
        for i in range(fields.count()):
            fields.nth(i).focus()
            outline=fields.nth(i).evaluate("""e=>({
              active:document.activeElement===e,
              width:getComputedStyle(e).outlineWidth,
              style:getComputedStyle(e).outlineStyle})""")
            assert outline=={"active":True,"width":"3px","style":"solid"},(width,i,outline)
        assert buttons.first.is_disabled() and buttons.nth(1).is_disabled()
        status=page.locator(".training-panel .bf-training-cost-note")
        assert status.count()==1 and "Training unavailable" in status.inner_text()
        page.evaluate("BFInnerScreens.setTab('training')")
        assert status.count()==1
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"),(width,"overflow")
        assert before==page.evaluate(state),(width,"synthetic saved state changed")
        assert not errors,(width,errors[:3])
        ctx.close()
        print("PASS v275",width,"three form fields and 12 actions >=44px; focus and save preserved")
    browser.close()
print("PASS v275 four widths; no owner save or device access")
