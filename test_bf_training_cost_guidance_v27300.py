"""v273: current Training affordability feedback without gameplay/save writes."""
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parent
A=ROOT/"app/src/main/assets"
J=(A/"bf_home_nav.js").read_text("utf8")
C=(A/"bf_home_nav.css").read_text("utf8")
PRE=(ROOT/".github/workflows/android-back-ui-source-preflight.yml").read_text()
BUILD=(ROOT/".github/workflows/build-debug-apk.yml").read_text()
MAN=(ROOT/"app/src/main/AndroidManifest.xml").read_text()
assert J.count("const trainingToolbar = training.querySelector('.training-toolbar');")==1
assert J.count("trainingBalance.after(note);")==1
assert J.count("training.querySelector('.bf-training-cost-note')")==1
assert "note.setAttribute('role', 'status');" in J
assert "new MutationObserver(refreshTrainingAffordability)" in J
assert "'1 Training Shard'" in J and "'150 Zel'" in J
assert "Resources support +10 EXP" in J and "Resources support +10 or +50 EXP" in J
assert "/* v273 read-only Training current-affordability feedback" in C
assert "display:none" not in C.split("/* v273 read-only Training current-affordability feedback",1)[1]
assert "test_bf_training_cost_guidance_v27300.py --source-only" in PRE
assert BUILD.count("python3 test_bf_training_cost_guidance_v27300.py")==1
assert "android.permission.INTERNET" not in MAN
assert len(J.encode())<128*1024 and len(C.encode())<128*1024
print("PASS v273 source: conditional resource status, no gameplay or permission changes")
if "--source-only" in sys.argv[1:]:raise SystemExit(0)

from playwright.sync_api import sync_playwright
HTML=(A/"index.html").read_text("utf8")
assert "Spend $"+"{count} training shard" in HTML
assert "150*count" in HTML and "P.trainingShards<count" in HTML
chrome=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome,"Chromium required for v273 browser regression"
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=chrome,args=["--no-sandbox","--disable-dev-shm-usage"])
 for width in (320,359,393,540):
  ctx=browser.new_context(viewport={"width":width,"height":790},service_workers="block",reduced_motion="reduce")
  page=ctx.new_page()
  errors=[]
  page.on("pageerror",lambda e:errors.append(str(e)))
  page.on("dialog",lambda d:d.dismiss())
  page.route("http://**/*",lambda route:route.abort())
  page.route("https://**/*",lambda route:route.abort())
  page.evaluate("""()=>{const m=Object.create(null);window.__v273=m;
   Object.defineProperty(window,'localStorage',{configurable:true,value:{
    getItem:k=>m[k]??null,setItem:(k,v)=>m[k]=String(v),
    removeItem:k=>delete m[k],clear:()=>Object.keys(m).forEach(k=>delete m[k]),
    key:i=>Object.keys(m)[i]??null,get length(){return Object.keys(m).length}
   }});}""")
  page.set_content(HTML,wait_until="load",timeout=120000)
  page.add_style_tag(content=C)
  page.add_script_tag(content=J)
  state="""()=>JSON.stringify({roster:P.roster,squad:P.squad,
   shards:P.trainingShards,spent:P.trainingSpent,exp:P.unitExp,
   evolutions:P.evolutions,gems:P.gems,zel:P.zel,karma:P.karma,
   save:localStorage.getItem('bf_global_offline_demo_v7'),storage:window.__v273})"""
  before=page.evaluate(state)
  page.evaluate("BF_homeNav.go('units');BFInnerScreens.setTab('training')")
  note=page.locator(".training-panel .bf-training-cost-note")
  assert note.count()==1,(width,"duplicate note")
  note.wait_for(state="visible")
  assert note.get_attribute("role")=="status"
  assert note.get_attribute("aria-live")=="polite"
  assert note.inner_text()=="Training unavailable with current resources: need at least 1 Training Shard and 150 Zel."
  buttons=page.locator(".training-panel .train-actions button")
  assert buttons.count()>=2
  assert buttons.nth(0).is_disabled() and buttons.nth(1).is_disabled()
  assert page.evaluate("getComputedStyle(document.querySelector('.bf-training-cost-note')).fontSize")=="12px"
  assert note.evaluate("e=>e.getBoundingClientRect().right<=innerWidth+1")
  assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"),width
  page.evaluate("""()=>{P.trainingShards=1;P.zel=150;document.getElementById("trainingbalance").textContent="Training Shards: 1 · Used: 0 · Zel: 150"}""")
  page.wait_for_function("document.querySelector('.bf-training-cost-note').textContent.includes('Resources support +10 EXP')")
  page.evaluate("""()=>{P.trainingShards=5;P.zel=750;document.getElementById("trainingbalance").textContent="Training Shards: 5 · Used: 0 · Zel: 750"}""")
  page.wait_for_function("document.querySelector('.bf-training-cost-note').textContent.includes('Resources support +10 or +50')")
  page.evaluate("""()=>{P.trainingShards=0;P.zel=0;document.getElementById("trainingbalance").textContent="Training Shards: 0 · Used: 0 · Zel: 0"}""")
  page.wait_for_function("document.querySelector('.bf-training-cost-note').textContent.includes('Training unavailable')")
  page.evaluate("BFInnerScreens.setTab('training')")
  assert note.count()==1
  assert before==page.evaluate(state),(width,"player/save mutation")
  assert not errors,(width,errors[:3])
  ctx.close()
  print("PASS v273",width,"unavailable/1x/5x affordability updates, no save mutation")
 browser.close()
print("PASS v273 four phone widths; owner save never accessed")
