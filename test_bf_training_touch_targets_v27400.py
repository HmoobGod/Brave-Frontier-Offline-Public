"""v274: read-only Training control hit-target and focus visibility regression."""
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parent
A=ROOT/"app/src/main/assets"
CSS=(A/"bf_home_nav.css").read_text("utf8")
JS=(A/"bf_home_nav.js").read_text("utf8")
MAN=(ROOT/"app/src/main/AndroidManifest.xml").read_text()
PRE=(ROOT/".github/workflows/android-back-ui-source-preflight.yml").read_text()
BUILD=(ROOT/".github/workflows/build-debug-apk.yml").read_text()

MARK="/* v274 — phone-friendly Training controls, presentation only. */"
assert CSS.count(MARK)==1
section=CSS.split(MARK,1)[1]
assert "training-panel .train-actions button" in section
assert "training-panel .training-toolbar input" in section
assert "training-panel .training-toolbar select" in section
assert "min-height:44px" in section
assert ":focus-visible" in section and "outline:3px solid" in section
assert "display:none" not in section
assert "window.BFInnerScreens" in JS and "#trainingbalance" in JS
assert "test_bf_training_touch_targets_v27400.py --source-only" in PRE
assert BUILD.count("python3 test_bf_training_touch_targets_v27400.py")==1
assert "android.permission.INTERNET" not in MAN
assert len(JS.encode())<128*1024 and len(CSS.encode())<128*1024
print("PASS v274 source: 44px Training controls, keyboard focus, no engine changes")
if "--source-only" in sys.argv[1:]:
    raise SystemExit(0)

from playwright.sync_api import sync_playwright
HTML=(A/"index.html").read_text("utf8")
chrome=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome,"Chromium required for v274 full browser regression"

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=chrome,
                               args=["--no-sandbox","--disable-dev-shm-usage"])
    for width in (320,359,393,540):
        ctx=browser.new_context(viewport={"width":width,"height":790},
                                service_workers="block",reduced_motion="reduce")
        page=ctx.new_page()
        errors=[]
        page.on("pageerror",lambda e:errors.append(str(e)))
        page.on("dialog",lambda d:d.dismiss())
        page.route("http://**/*",lambda route:route.abort())
        page.route("https://**/*",lambda route:route.abort())
        page.evaluate("""()=>{const m=Object.create(null);window.__v274=m;
          Object.defineProperty(window,"localStorage",{configurable:true,value:{
            getItem:k=>m[k]??null,setItem:(k,v)=>m[k]=String(v),
            removeItem:k=>delete m[k],clear:()=>Object.keys(m).forEach(k=>delete m[k]),
            key:i=>Object.keys(m)[i]??null,get length(){return Object.keys(m).length}
          }});}""")
        page.set_content(HTML,wait_until="load",timeout=120000)
        page.add_style_tag(content=CSS)
        page.add_script_tag(content=JS)
        state="""()=>JSON.stringify({roster:P.roster,squad:P.squad,
          unitExp:P.unitExp,evolutions:P.evolutions,
          trainingShards:P.trainingShards,trainingSpent:P.trainingSpent,
          gems:P.gems,zel:P.zel,karma:P.karma,
          save:localStorage.getItem('bf_global_offline_demo_v7'),
          storage:window.__v274})"""
        before=page.evaluate(state)
        page.evaluate("BF_homeNav.go('units');BFInnerScreens.setTab('training')")
        buttons=page.locator(".training-panel .train-actions button")
        inputs=page.locator(".training-panel .training-toolbar input")
        selects=page.locator(".training-panel .training-toolbar select")
        assert buttons.count()==12,(width,"training actions")
        assert inputs.count()==1 and selects.count()==2,(width,"training search/filter/sort")
        for group,loc in (("actions",buttons),("search",inputs),("filters",selects)):
            for i in range(loc.count()):
                rect=loc.nth(i).evaluate("""e=>({
                  w:e.getBoundingClientRect().width,
                  h:e.getBoundingClientRect().height,
                  visibility:getComputedStyle(e).visibility})""")
                assert rect["h"]>=44 and rect["w"]>=44,(width,group,i,rect)
                assert rect["visibility"]=="visible",(width,group,i)
        assert buttons.first.is_disabled() and buttons.nth(1).is_disabled()
        note=page.locator(".training-panel .bf-training-cost-note")
        assert note.count()==1 and "Training unavailable" in note.inner_text()
        inputs.first.focus()
        assert inputs.first.evaluate("e=>getComputedStyle(e).outlineWidth")=="3px",(width,"focus")
        page.evaluate("BFInnerScreens.setTab('training')")
        assert note.count()==1
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"),(width,"overflow")
        assert before==page.evaluate(state),(width,"synthetic player/save changed")
        assert not errors,(width,errors[:3])
        ctx.close()
        print("PASS v274",width,"15 touch targets >=44px, focus, no state writes")
    browser.close()
print("PASS v274 four phone widths; owner save never accessed")
