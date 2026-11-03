"""v271: missing archived profiles remain visible as saved roster metadata, never edited.

Real index.html + current navigation JS/CSS, disposable synthetic storage only.
"""
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parent
A=ROOT/"app/src/main/assets"
H=(A/"index.html").read_text("utf8")
J=(A/"bf_home_nav.js").read_text("utf8")
C=(A/"bf_home_nav.css").read_text("utf8")
PRE=(ROOT/".github/workflows/android-back-ui-source-preflight.yml").read_text()
BUILD=(ROOT/".github/workflows/build-debug-apk.yml").read_text()
MAN=(ROOT/"app/src/main/AndroidManifest.xml").read_text()
assert 'id="bf-box-unresolved" class="bf-box-unresolved" role="note" hidden' in J
assert "const unresolved = rows.filter(row => !row.unit);" in J
assert "unresolvedNote.textContent = unresolved.length ?" in J
assert "Your roster is unchanged." in J
assert "Saved units are present, but their archived profiles are unavailable." in J
assert "No owned units are available in this offline save." in J
assert ".bf-box-unresolved[hidden]{display:none!important}" in C
assert "test_bf_unit_box_unresolved_v27100.py --source-only" in PRE
assert BUILD.count("python3 test_bf_unit_box_unresolved_v27100.py")==1
assert "android.permission.INTERNET" not in MAN
assert len(J.encode("utf8"))<128*1024 and len(C.encode("utf8"))<128*1024
print("PASS v271 source: unresolved roster display only, no added permission, CI wired")
if "--source-only" in sys.argv[1:]:
    raise SystemExit(0)

from playwright.sync_api import sync_playwright
chrome=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "Chromium is required for full v271 UI regression"
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
        page.evaluate("""() => { const m=Object.create(null);window.__v271=m;
          Object.defineProperty(window,'localStorage',{configurable:true,value:{
            getItem:k=>m[k]??null,setItem:(k,v)=>m[k]=String(v),
            removeItem:k=>delete m[k],clear:()=>Object.keys(m).forEach(k=>delete m[k]),
            key:i=>Object.keys(m)[i]??null,get length(){return Object.keys(m).length}
          }}); }""")
        page.set_content(H,wait_until="load",timeout=120000)
        page.add_style_tag(content=C)
        page.add_script_tag(content=J)
        page.evaluate("BF_homeNav.go('units');BFInnerScreens.setTab('box');BFUnitBox.refresh()")
        state="""()=>JSON.stringify({roster:P.roster,squad:P.squad,exp:P.unitExp,
          evolutions:P.evolutions,gems:P.gems,zel:P.zel,karma:P.karma,
          save:localStorage.getItem('bf_global_offline_demo_v7'),storage:window.__v271})"""
        results=page.locator("#bf-box-results")
        count=page.locator("#bf-box-count")
        note=page.locator("#bf-box-unresolved")
        assert results.locator(".bf-box-card").count()==6,(width,"default cards")
        assert note.is_hidden(),(width,"unexpected note")
        assert count.inner_text().endswith("6 active")
        assert count.get_attribute("aria-live")=="polite"
        # Disposable synthetic state only. Unknown IDs are never written to disk.
        page.evaluate("()=>{P.roster.push(999999997);BFUnitBox.refresh()}")
        before=page.evaluate(state)
        assert results.locator(".bf-box-card").count()==6,(width,"mixed cards")
        assert note.is_visible() and note.get_attribute("role")=="note"
        assert note.inner_text()=="1 saved unit ID cannot be displayed from this offline archive. Your roster is unchanged."
        assert count.inner_text().endswith("1 unresolved")
        page.locator("#bf-box-search").fill("not_a_real_unit_999_v271")
        assert results.locator(".bf-box-card").count()==0
        assert results.locator(".bf-box-empty p").inner_text()=="No owned units match the current filters."
        results.locator("button.bf-box-clear-filters").click()
        assert results.locator(".bf-box-card").count()==6
        assert page.locator("#bf-box-search").input_value()==""
        assert before==page.evaluate(state),(width,"filter mutated player state")
        page.evaluate("()=>{P.roster=[999999997,999999998];P.squad=[];BFUnitBox.refresh()}")
        all_unresolved=page.evaluate(state)
        assert results.locator(".bf-box-card").count()==0
        assert note.inner_text()=="2 saved unit IDs cannot be displayed from this offline archive. Your roster is unchanged."
        assert results.locator(".bf-box-empty p").inner_text()=="Saved units are present, but their archived profiles are unavailable."
        assert results.locator(".bf-box-clear-filters").count()==0
        assert count.inner_text().endswith("2 unresolved")
        page.evaluate("BFUnitBox.refresh()")
        assert all_unresolved==page.evaluate(state),(width,"unresolved render changed roster")
        page.evaluate("()=>{P.roster=[];P.squad=[];BFUnitBox.refresh()}")
        empty=page.evaluate(state)
        assert note.is_hidden()
        assert count.inner_text()=="0 shown / 0 owned · 0 active"
        assert results.locator(".bf-box-empty p").inner_text()=="No owned units are available in this offline save."
        assert results.locator("button").count()==0
        page.evaluate("BFUnitBox.refresh()")
        assert empty==page.evaluate(state),(width,"empty render changed player state")
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"),(width,"overflow")
        assert not errors,(width,errors[:3])
        ctx.close()
        print("PASS v271",width,"normal, mixed, all unresolved, empty, filter and save")
    browser.close()
print("PASS v271 four portrait viewports")
