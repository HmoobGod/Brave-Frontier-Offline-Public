"""v273: read-only Training resource affordability, four phone widths and save isolation.

Uses a disposable browser with synthetic in-memory storage; never opens owner's
working app or save. This is demo enhancement info, not original 2022 Fusion.
"""
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/"app/src/main/assets"
HTML=(ASSETS/"index.html").read_text("utf8")
JS=(ASSETS/"bf_home_nav.js").read_text("utf8")
CSS=(ASSETS/"bf_home_nav.css").read_text("utf8")
PRE=(ROOT/".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
BUILD=(ROOT/".github/workflows/build-debug-apk.yml").read_text("utf8")
MAN=(ROOT/"app/src/main/AndroidManifest.xml").read_text("utf8")
assert "v273: read-only demo training affordability status" in JS
assert "new MutationObserver(refreshTrainingAffordability)" in JS
assert "if (next === 'training') refreshTrainingAffordability();" in JS
assert "const trainingBalance = training.querySelector('.training-toolbar #trainingbalance');" in JS
assert "Demo Training spending limit reached." in JS
assert "Resources support +10 or +50 EXP training." in JS
assert "v273 read-only Demo Training current-affordability status" in CSS
assert "display:none" not in CSS.split("/* v273 read-only Demo Training current-affordability status. */",1)[1]
assert "test_bf_training_affordability_v27300.py --source-only" in PRE
assert BUILD.count("python3 test_bf_training_affordability_v27300.py")==1
assert len(JS.encode("utf8"))<128*1024
assert len(CSS.encode("utf8"))<128*1024
assert "android.permission.INTERNET" not in MAN
print("PASS v273 source: read-only Training affordability and CI registration")
if "--source-only" in sys.argv[1:]:
    raise SystemExit(0)

from playwright.sync_api import sync_playwright
chrome=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "Chromium required for full v273 UI test"
cases=[
    (0,0,0,"1 Training Shard and 150 Zel"),
    (0,500,0,"1 Training Shard"),
    (3,50,0,"150 Zel"),
    (1,150,0,"Resources support +10 EXP."),
    (4,1000,0,"Resources support +10 EXP."),
    (5,750,0,"Resources support +10 or +50 EXP training."),
    (7,999,99996,"Resources support +10 EXP."),
    (5,750,99999,"Resources support +10 EXP."),
    (5,750,100000,"Demo Training spending limit reached."),
]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=chrome,
        args=["--no-sandbox","--disable-dev-shm-usage"])
    for width,height in ((320,740),(359,760),(393,852),(540,900)):
        context=browser.new_context(viewport={"width":width,"height":height},
            service_workers="block",reduced_motion="reduce")
        page=context.new_page()
        errors=[]
        page.on("pageerror",lambda e:errors.append(str(e)))
        page.on("dialog",lambda d:d.dismiss())
        page.route("http://**/*",lambda route:route.abort())
        page.route("https://**/*",lambda route:route.abort())
        page.evaluate("""() => {const s=Object.create(null);window.__v273storage=s;
          Object.defineProperty(window,"localStorage",{configurable:true,value:{
            getItem:k=>s[k]??null,setItem:(k,v)=>s[k]=String(v),
            removeItem:k=>delete s[k],clear:()=>Object.keys(s).forEach(k=>delete s[k]),
            key:i=>Object.keys(s)[i]??null,get length(){return Object.keys(s).length}
          }}); }""")
        page.set_content(HTML,wait_until="load",timeout=120000)
        page.add_style_tag(content=CSS)
        page.add_script_tag(content=JS)
        page.evaluate("BF_homeNav.go('units');BFInnerScreens.setTab('training')")
        note=page.locator(".training-panel .bf-training-cost-note")
        assert note.count()==1 and note.is_visible(),width
        assert note.get_attribute("role")=="status"
        assert note.get_attribute("aria-live")=="polite"
        assert note.get_attribute("aria-atomic")=="true"
        state="""() => JSON.stringify({
          r:P.roster,s:P.squad,x:P.unitExp,e:P.evolutions,
          sh:P.trainingShards,spent:P.trainingSpent,z:P.zel,g:P.gems,k:P.karma,
          save:localStorage.getItem('bf_global_offline_demo_v7'),storage:window.__v273storage
        })"""
        for shards,zel,spent,expected in cases:
            # These assignments modify ONLY this disposable synthetic browser.
            page.evaluate("(x)=>{P.trainingShards=x[0];P.zel=x[1];P.trainingSpent=x[2]}",[shards,zel,spent])
            baseline=page.evaluate(state)
            page.evaluate("BFInnerScreens.setTab('box');BFInnerScreens.setTab('training')")
            assert expected in note.inner_text(),(width,shards,zel,spent,note.inner_text())
            assert page.evaluate(state)==baseline,(width,"tab/navigation changed player state")
        # Original app updates the balance text on render; observer refreshes note.
        page.evaluate("()=>{P.trainingShards=0;P.zel=0;P.trainingSpent=0}")
        before=page.evaluate(state)
        page.locator("#trainingbalance").evaluate("(e)=>e.textContent='Training Shards: 0 · Used: 0 · Zel: 0'")
        note.get_by_text("Training unavailable with current resources").wait_for(timeout=2000)
        assert "1 Training Shard and 150 Zel" in note.inner_text()
        assert before==page.evaluate(state),(width,"balance status mutated save")
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"),(width,"overflow")
        assert note.evaluate("e=>e.getBoundingClientRect().height")>=24
        assert not errors,(width,errors[:3])
        context.close()
        print("PASS v273",width,"nine affordability states, mutation observer, unchanged state")
    browser.close()
print("PASS v273 all four phone widths; not owner device or original Fusion")
