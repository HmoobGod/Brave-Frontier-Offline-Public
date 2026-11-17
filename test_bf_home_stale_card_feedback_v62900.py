"""v629: real packaged Home refreshes a valid stale owned-card form before navigation.

Runs on disposable in-memory v7 state only. Does not read the installed APK,
owner save, original screenshots, or enable automatic gameplay.
"""
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
NAME = "test_bf_home_stale_card_feedback_v62900.py"
HOME = (ASSETS / "bf_home_nav.js").read_text("utf-8")
BUILD = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf-8")
PREFLIGHT = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf-8")
MANIFEST = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf-8")
assert HOME.count("// v629: stale displayed form") == 1
assert HOME.count("refreshParty();") >= 2
assert "partyReview.textContent =" in HOME
assert "liveUnit.id !== displayedFormId" in HOME
assert "liveUnit.name !== displayedFormName" in HOME
assert BUILD.count("python3 " + NAME) == 1
assert PREFLIGHT.count(NAME) == 2
assert "android.permission.INTERNET" not in MANIFEST
assert len(HOME.encode("utf-8")) < 128 * 1024
print("PASS v629 source: manual stale-card refresh, polite status and signed test wiring")
if "--source-only" in sys.argv:
    raise SystemExit(0)

from playwright.sync_api import sync_playwright

browser_bin = (shutil.which("chromium") or shutil.which("google-chrome") or
               shutil.which("google-chrome-stable"))
assert browser_bin, "Real Chromium required for Home interaction proof"

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=browser_bin,
                                 args=["--no-sandbox", "--disable-dev-shm-usage"])
    try:
        for width in (320, 359, 393, 412, 540):
            for mode in ("stale-form-id", "stale-form-name", "baseline"):
                page = browser.new_page(viewport={"width": width, "height": 844})
                errors = []
                page.on("pageerror", lambda exc: errors.append(str(exc)))
                try:
                    page.evaluate("""() => {
                      const db={}; let writes=0;
                      Object.defineProperty(window,"localStorage",{configurable:true,value:{
                        getItem:k=>Object.hasOwn(db,k)?db[k]:null,
                        setItem:(k,v)=>{writes++;db[k]=String(v)},
                        removeItem:k=>{writes++;delete db[k]},
                        key:i=>Object.keys(db)[i]??null,
                        get length(){return Object.keys(db).length}
                      }});
                      window.__v629Writes=()=>writes;
                      window.alert=()=>{};window.confirm=()=>true;
                      HTMLMediaElement.prototype.load=()=>{};
                      HTMLMediaElement.prototype.pause=()=>{};
                      HTMLMediaElement.prototype.play=()=>Promise.resolve();
                    }""")
                    page.set_content((ASSETS/"index.html").read_text("utf-8"),
                                     wait_until="load", timeout=90000)
                    page.add_style_tag(path=str(ASSETS/"bf_home_nav.css"))
                    page.add_script_tag(path=str(ASSETS/"bf_home_nav.js"))
                    assert page.evaluate("P.version") == 7, width
                    assert page.evaluate("BF_homeNav.current") == "home", width
                    assert page.locator("#bf-scene-party button.bf-scene-member").count() == 6, width
                    result = page.evaluate("""mode => {
                      const nav=BF_homeNav, box=BFUnitBox;
                      const originalEffective=window.effectiveUnit;
                      const originalShow=box.showDetail, calls=[];
                      const button=document.querySelector("#bf-scene-party button.bf-scene-member");
                      const first=P.squad[0];
                      const observedName=button.querySelector("strong").textContent;
                      const observedLabel=button.getAttribute("aria-label");
                      const snapshot=()=>JSON.stringify({
                        p:P,s:S,quest:QUEST.missionId,writes:window.__v629Writes(),
                        storage:Array.from({length:localStorage.length},(_,i)=>{
                          const key=localStorage.key(i);
                          return [key,localStorage.getItem(key)];
                        }).sort((a,b)=>a[0].localeCompare(b[0]))
                      });
                      const before=snapshot();
                      if(mode==="stale-form-id"){
                        window.effectiveUnit=id=>{
                          const u=originalEffective(id);
                          return id===first&&u?{...u,id:u.id+1000000}:u;
                        };
                      }else if(mode==="stale-form-name"){
                        window.effectiveUnit=id=>{
                          const u=originalEffective(id);
                          return id===first&&u?{...u,name:u.name+" Evolved Guardian"}:u;
                        };
                      }else if(mode!=="baseline")throw Error("Invalid mode "+mode);
                      box.showDetail=function(id){calls.push(id);return originalShow.call(this,id);};
                      try {
                        button.focus();
                        button.click();
                        const refreshed=document.querySelector("#bf-scene-party button.bf-scene-member");
                        const review=document.getElementById("bf-scene-party-review");
                        return {
                          mode,route:nav.current,
                          tab:BFInnerScreens.unitTab,
                          calls,oldName:observedName,
                          newName:refreshed?.querySelector("strong")?.textContent??"",
                          oldLabel:observedLabel,
                          newLabel:refreshed?.getAttribute("aria-label")??"",
                          changedNode:refreshed!==button,
                          refreshedFocused:document.activeElement===refreshed,
                          reviewVisible:review?.hidden===false,
                          reviewRole:review?.getAttribute("role"),
                          reviewText:review?.textContent??"",
                          unchanged:snapshot()===before,
                          screenOverflow:document.documentElement.scrollWidth>innerWidth+1
                        };
                      } finally {
                        window.effectiveUnit=originalEffective;
                        box.showDetail=originalShow;
                      }
                    }""", mode)
                    assert result["unchanged"], (width, mode, "v7 state or storage write", result)
                    assert not result["screenOverflow"], (width, mode, "horizontal overflow", result)
                    if mode == "baseline":
                        assert result["route"] == "units", (width, mode, result)
                        assert result["calls"] == [page.evaluate("P.squad[0]")], (width, mode, result)
                    else:
                        assert result["route"] == "home", (width, mode, result)
                        assert result["calls"] == [], (width, mode, result)
                        assert result["changedNode"] and result["refreshedFocused"], (width, mode, result)
                        assert result["reviewVisible"] and result["reviewRole"] == "status", (width, mode, result)
                        assert "Squad unit changed" in result["reviewText"], (width, mode, result)
                        assert result["newLabel"].startswith("Inspect "), (width, mode, result)
                        if mode == "stale-form-name":
                            assert result["newName"] == result["oldName"]+" Evolved Guardian", (width, result)
                            assert result["newName"] in result["newLabel"], (width, result)
                        else:
                            assert result["newName"] == result["oldName"], (width, result)
                    assert not errors, (width, mode, errors[:3])
                    print("PASS v629 actual Home", width, mode)
                finally:
                    page.close()
    finally:
        browser.close()
print("PASS v629 Home stale-card feedback: 5 widths, 15 live cases, zero owner writes")
