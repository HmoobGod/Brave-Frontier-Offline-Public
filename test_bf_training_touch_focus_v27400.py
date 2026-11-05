"""v274: read-only Training touch-target and focus visibility regression.

Packaged offline index and navigation assets, synthetic browser storage only.
"""
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parent
A=ROOT/"app/src/main/assets"
JS=(A/"bf_home_nav.js").read_text("utf8")
CSS=(A/"bf_home_nav.css").read_text("utf8")
SOURCE=(ROOT/".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
BUILD=(ROOT/".github/workflows/build-debug-apk.yml").read_text("utf8")
MANIFEST=(ROOT/"app/src/main/AndroidManifest.xml").read_text("utf8")

patch=CSS.split("/* v274 Training controls: 44px touch targets and visible keyboard focus. */")
assert len(patch)==2
assert "body.bf-menu-mode .training-panel .train-actions button {" in patch[1]
assert "min-height:44px" in patch[1] and "touch-action:manipulation" in patch[1]
assert ".train-actions button:focus-visible {" in patch[1]
assert "outline:3px solid" in patch[1]
assert "display:none" not in patch[1]
assert "test_bf_training_touch_focus_v27400.py --source-only" in SOURCE
assert BUILD.count("python3 test_bf_training_touch_focus_v27400.py")==1
assert "android.permission.INTERNET" not in MANIFEST
assert len(JS.encode())<128*1024 and len(CSS.encode())<128*1024
print("PASS v274 source: 44px Training targets and keyboard focus, offline CI")
if "--source-only" in sys.argv[1:]:
    raise SystemExit(0)

from playwright.sync_api import sync_playwright
HTML=(A/"index.html").read_text("utf8")
assert "P.trainingShards<count" in HTML
assert "P.trainingSpent>100000-count" in HTML
chrome=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome,"Chromium required for v274 browser regression"
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
        page.evaluate("""()=>{const map=Object.create(null);window.__v274=map;
            Object.defineProperty(window,'localStorage',{configurable:true,value:{
              getItem:k=>map[k]??null,setItem:(k,v)=>map[k]=String(v),
              removeItem:k=>delete map[k],clear:()=>Object.keys(map).forEach(k=>delete map[k]),
              key:i=>Object.keys(map)[i]??null,get length(){return Object.keys(map).length}
            }});
        }""")
        page.set_content(HTML,wait_until="load",timeout=120000)
        page.add_style_tag(content=CSS)
        page.add_script_tag(content=JS)
        state="""()=>JSON.stringify({
           roster:P.roster,squad:P.squad,unitExp:P.unitExp,evolutions:P.evolutions,
           gems:P.gems,zel:P.zel,karma:P.karma,trainingShards:P.trainingShards,
           trainingSpent:P.trainingSpent,
           save:localStorage.getItem('bf_global_offline_demo_v7'),map:window.__v274
        })"""
        before=page.evaluate(state)
        page.evaluate("BF_homeNav.go('units');BFInnerScreens.setTab('training')")
        buttons=page.locator(".training-panel .train-actions button")
        assert buttons.count()>=2,(width,"no Training actions")
        rects=buttons.evaluate_all("""els=>els.map(e=>({
          height:e.getBoundingClientRect().height,
          width:e.getBoundingClientRect().width,disabled:e.disabled
        }))""")
        assert all(x["height"]>=44 and x["width"]>=44 for x in rects),(width,rects)
        assert all(x["disabled"] for x in rects),(width,"zero-resource buttons unexpectedly enabled")
        # Temporarily enable one DOM button ONLY to measure keyboard focus.
        # Do not click, submit, spend resources or call the original training function.
        page.evaluate("""()=>document.querySelector('.training-panel .train-actions button').disabled=false""")
        target=buttons.first
        target.focus()
        outline=target.evaluate("""e=>({
          active:document.activeElement===e,style:getComputedStyle(e).outlineStyle,
          width:getComputedStyle(e).outlineWidth
        })""")
        assert outline=={"active":True,"style":"solid","width":"3px"},(width,outline)
        page.evaluate("""()=>document.querySelector('.training-panel .train-actions button').disabled=true""")
        assert all(x["disabled"] for x in buttons.evaluate_all("els=>els.map(e=>({disabled:e.disabled}))"))
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"),(width,"overflow")
        assert before==page.evaluate(state),(width,"state mutation")
        assert not errors,(width,errors[:3])
        ctx.close()
        print("PASS v274",width,"Training targets >=44px, 3px focus, no save writes")
    browser.close()
print("PASS v274 all four phone widths, owner device and save untouched")
