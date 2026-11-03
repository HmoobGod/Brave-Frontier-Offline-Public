"""v269: read-only Unit Box no-owned vs filtered-out UI at phone widths."""
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parent
A=ROOT/"app/src/main/assets"
H=(A/"index.html").read_text("utf8")
C=(A/"bf_home_nav.css").read_text("utf8")
J=(A/"bf_home_nav.js").read_text("utf8")
PRE=(ROOT/".github/workflows/android-back-ui-source-preflight.yml").read_text()
BUILD=(ROOT/".github/workflows/build-debug-apk.yml").read_text()
MAN=(ROOT/"app/src/main/AndroidManifest.xml").read_text()
assert 'No owned units match the current filters.' in J
assert 'No owned units are available in this offline save.' in J
assert 'clear.textContent='+"'CLEAR FILTERS'"+'' in J
assert 'role="status" aria-live="polite"' in J
assert "clear.addEventListener('click'" in J
assert "/* v269 read-only Unit Box" in C and ".bf-box-clear-filters:focus-visible" in C
assert "test_bf_unit_box_empty_state_v26900.py --source-only" in PRE
assert BUILD.count("python3 test_bf_unit_box_empty_state_v26900.py")==1
assert "android.permission.INTERNET" not in MAN
assert len(J.encode())<128*1024 and len(C.encode())<128*1024
print("PASS v269 source: accessible no-results states, CI and offline guard")
if "--source-only" in sys.argv[1:]:raise SystemExit(0)

from playwright.sync_api import sync_playwright
chrome=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "Chromium is required for full v269 browser test"
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=chrome,
                             args=["--no-sandbox","--disable-dev-shm-usage"])
 for width in (320,359,393,540):
  context=browser.new_context(viewport={"width":width,"height":790},service_workers="block",reduced_motion="reduce")
  page=context.new_page()
  errors=[]
  page.on("pageerror",lambda e:errors.append(str(e)))
  page.on("dialog",lambda d:d.dismiss())
  page.route("http://**/*",lambda route:route.abort())
  page.route("https://**/*",lambda route:route.abort())
  page.evaluate("""() => {const s=Object.create(null);window.__v269=s;
    Object.defineProperty(window,"localStorage",{configurable:true,value:{
      getItem:k=>s[k]??null,setItem:(k,v)=>s[k]=String(v),
      removeItem:k=>delete s[k],clear:()=>Object.keys(s).forEach(k=>delete s[k]),
      key:i=>Object.keys(s)[i]??null,get length(){return Object.keys(s).length}
    }});
  }""")
  page.set_content(H,wait_until="load",timeout=120000)
  page.add_style_tag(content=C)
  page.add_script_tag(content=J)
  page.evaluate("BF_homeNav.go('units');BFInnerScreens.setTab('box');BFUnitBox.refresh()")
  state="""()=>JSON.stringify({
    roster:P.roster,squad:P.squad,unitExp:P.unitExp,e:P.evolutions,
    gems:P.gems,zel:P.zel,karma:P.karma,
    save:localStorage.getItem('bf_global_offline_demo_v7'),storage:window.__v269
  })"""
  before=page.evaluate(state)
  assert page.locator("#bf-box-results .bf-box-card").count()==6,(width,"owned")
  assert page.locator("#bf-box-count").get_attribute("aria-live")=="polite"
  page.locator("#bf-box-sort").select_option("rarity")
  page.locator("#bf-box-search").fill("does_not_match_any_unit_777")
  empty=page.locator("#bf-box-results .bf-box-empty")
  assert empty.is_visible() and empty.get_attribute("role")=="status"
  assert empty.locator("p").inner_text()=="No owned units match the current filters."
  clear=empty.locator("button.bf-box-clear-filters")
  assert clear.is_visible() and clear.inner_text()=="CLEAR FILTERS"
  assert clear.evaluate("e=>e.getBoundingClientRect().height")>=44
  clear.click()
  assert page.locator("#bf-box-search").input_value()==""
  assert page.locator("#bf-box-sort").input_value()=="rarity",(width,"sort incorrectly reset")
  assert page.locator("#bf-box-results .bf-box-card").count()==6
  assert page.evaluate("document.activeElement.id")=="bf-box-search"
  page.locator("#bf-box-filter").select_option("reserve")
  assert page.locator("#bf-box-results .bf-box-card").count()==0
  page.locator("#bf-box-results .bf-box-clear-filters").click()
  assert page.locator("#bf-box-filter").input_value()=="all"
  assert page.locator("#bf-box-results .bf-box-card").count()==6
  assert before==page.evaluate(state),(width,"unintended player/save mutation")
  # Empty collection simulated in-memory; this is not the owner's real save.
  page.evaluate("()=>{P.roster=[];P.squad=[];BFUnitBox.refresh()}")
  emptyBefore=page.evaluate(state)
  empty=page.locator("#bf-box-results .bf-box-empty")
  assert empty.is_visible()
  assert empty.locator("p").inner_text()=="No owned units are available in this offline save."
  assert empty.locator("button").count()==0
  assert page.locator("#bf-box-results .bf-box-card").count()==0
  assert page.locator("#bf-box-count").inner_text().startswith("0 shown / 0 owned")
  assert emptyBefore==page.evaluate(state),(width,"empty collection write")
  assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"),(width,"overflow")
  assert not errors,(width,errors[:3])
  context.close()
  print("PASS v269",width,"empty owned, filtered out, reset, accessibility, no writes")
 browser.close()
print("PASS v269 four phone widths; owner save never accessed")
