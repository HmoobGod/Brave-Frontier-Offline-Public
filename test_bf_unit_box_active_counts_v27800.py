"""v278: preserve archived Unit Box truthful active count and no-profile copy.

Presentation-only checks; synthetic in-memory player state, no owner saves or APK installs.
"""
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parent
A=ROOT/"app/src/main/assets"
H=(A/"index.html").read_text("utf8")
J=(A/"bf_home_nav.js").read_text("utf8")
CSS=(A/"bf_home_nav.css").read_text("utf8")
PRE=(ROOT/".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
BUILD=(ROOT/".github/workflows/build-debug-apk.yml").read_text("utf8")
MAN=(ROOT/"app/src/main/AndroidManifest.xml").read_text("utf8")

assert "function showDetail(id, noAvailableProfiles = false)" in J
assert "const resolvedIds = new Set(owned.map(row => row.id));" in J
assert "const activeSquad = P.squad.filter(id => resolvedIds.has(id)).length;" in J
assert "const missingSquad = P.squad.length - activeSquad;" in J
assert "squad profile" in J and "unavailable" in J
assert "Saved unit profiles are unavailable in this offline archive; there is no unit to select." in J
assert "else showDetail(null, !owned.length && unresolved.length>0);" in J
assert "role=\"note\" hidden" in J
assert "test_bf_unit_box_active_counts_v27800.py --source-only" in PRE
assert BUILD.count("python3 test_bf_unit_box_active_counts_v27800.py")==1
assert "android.permission.INTERNET" not in MAN
assert len(J.encode())<128*1024 and len(CSS.encode())<128*1024
print("PASS v278 source: resolved active count, unavailable note, safe registrations")
if "--source-only" in sys.argv[1:]:
    raise SystemExit(0)

from playwright.sync_api import sync_playwright
chrome=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "Chromium required for v278 browser test"

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=chrome,args=["--no-sandbox","--disable-dev-shm-usage"])
    for width in (320,359,393,540):
        ctx=browser.new_context(viewport={"width":width,"height":800},
                                reduced_motion="reduce",service_workers="block")
        page=ctx.new_page()
        errors=[]
        page.on("pageerror",lambda error:errors.append(str(error)))
        page.on("dialog",lambda dialog:dialog.dismiss())
        page.route("http://**/*",lambda route:route.abort())
        page.route("https://**/*",lambda route:route.abort())
        page.evaluate("""() => {
          const map=Object.create(null);window.__v278=map;
          Object.defineProperty(window,'localStorage',{configurable:true,value:{
            getItem:k=>map[k]??null,setItem:(k,v)=>{map[k]=String(v)},
            removeItem:k=>delete map[k],clear:()=>Object.keys(map).forEach(k=>delete map[k]),
            key:i=>Object.keys(map)[i]??null,get length(){return Object.keys(map).length}
          }});
        }""")
        page.set_content(H,wait_until="load",timeout=120000)
        page.add_style_tag(content=CSS)
        page.add_script_tag(content=J)
        page.evaluate("BF_homeNav.go('units');BFInnerScreens.setTab('box');BFUnitBox.refresh()")
        count=page.locator("#bf-box-count")
        detail=page.locator("#bf-box-detail")
        results=page.locator("#bf-box-results")
        state="""() => JSON.stringify({
          roster:P.roster,squad:P.squad,exp:P.unitExp,evolutions:P.evolutions,
          gems:P.gems,zel:P.zel,karma:P.karma,
          save:localStorage.getItem('bf_global_offline_demo_v7'),storage:window.__v278
        })"""
        assert count.inner_text().endswith("6 active"),(width,"normal roster",count.inner_text())
        assert results.locator(".bf-box-card").count()==6
        assert count.get_attribute("aria-live")=="polite"
        assert page.locator("#bf-box-unresolved").get_attribute("role")=="note"
        # Browser-only synthetic IDs, never a real save.
        page.evaluate("() => {const known=P.roster[0];P.roster.push(999999997);P.squad=[known,999999997];BFUnitBox.refresh()}")
        before=page.evaluate(state)
        assert "1 active · 1 squad profile unavailable" in count.inner_text(),(width,count.inner_text())
        assert count.inner_text().endswith("1 unresolved")
        assert results.locator(".bf-box-card").count()==6
        page.locator("#bf-box-search").fill("no_such_unit_v278")
        assert results.locator(".bf-box-clear-filters").count()==1
        results.locator(".bf-box-clear-filters").click()
        assert before==page.evaluate(state),(width,"mixed case mutated player data")
        page.evaluate("() => {P.roster=[999999997,999999998];P.squad=[999999998];BFUnitBox.refresh()}")
        before=page.evaluate(state)
        assert "0 active · 1 squad profile unavailable" in count.inner_text(),(width,count.inner_text())
        assert count.inner_text().endswith("2 unresolved")
        assert detail.inner_text()=="Saved unit profiles are unavailable in this offline archive; there is no unit to select."
        assert results.locator(".bf-box-card").count()==0
        assert results.locator(".bf-box-clear-filters").count()==0
        page.evaluate("BFUnitBox.refresh()")
        assert before==page.evaluate(state),(width,"unresolved refresh mutated player data")
        page.evaluate("() => {P.roster=[];P.squad=[];BFUnitBox.refresh()}")
        assert count.inner_text()=="0 shown / 0 owned · 0 active"
        assert detail.inner_text()=="Select an owned unit to view its archived base statistics."
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"),(width,"horizontal overflow")
        assert not errors,(width,errors[:3])
        ctx.close()
        print("PASS v278",width,"normal/mixed/all-unresolved/empty, no saves or network")
    browser.close()
print("PASS v278 4-width genuine packaged-HTML browser regression")
