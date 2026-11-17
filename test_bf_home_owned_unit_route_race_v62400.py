"""v624: real Home owned-unit card fails closed after synchronous route/tab races.

Loads the packaged index.html and real Home module under disposable browser-only v7.
No owner APK, player save or screenshot is read. No battle/Auto is triggered.
"""
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent
A = ROOT / "app/src/main/assets"
HOME = (A / "bf_home_nav.js").read_text("utf8")
BUILD = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf8")
PREFLIGHT = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
MANIFEST = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf8")
TEST = "test_bf_home_owned_unit_route_race_v62400.py"
assert HOME.count("function stillSafeToInspect()") == 1
assert HOME.count("!stillSafeToInspect()") == 2
assert "replay.statusSnapshot()?.active === false" in HOME
assert "window.BFUnitBox.showDetail(baseId);" in HOME
assert BUILD.count("python3 " + TEST) == 1
assert PREFLIGHT.count(TEST) == 2  # path trigger and --source-only
assert "android.permission.INTERNET" not in MANIFEST
assert len(HOME.encode("utf8")) < 128 * 1024
print("PASS v624 source: two post-handoff identity/Auto/Repeat checks, signed CI registered")
if "--source-only" in sys.argv:
    raise SystemExit(0)

from playwright.sync_api import sync_playwright

chrome = shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "A real Chromium browser is required for this regression"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=chrome,
                               args=["--no-sandbox", "--disable-dev-shm-usage"])
    try:
        for width in (320, 390, 540):
            page = browser.new_page(viewport={"width": width, "height": 844})
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            try:
                page.evaluate("""() => {
                  const db = {}; let writes = 0;
                  Object.defineProperty(window, "localStorage", {configurable:true,value:{
                    getItem:k=>db[k]??null,
                    setItem:(k,v)=>{writes++;db[k]=String(v)},
                    removeItem:k=>{writes++;delete db[k]},
                    key:i=>Object.keys(db)[i]??null,
                    get length(){return Object.keys(db).length}
                  }});
                  window.__v624Writes=()=>writes;
                  window.alert=()=>{};window.confirm=()=>true;
                  HTMLMediaElement.prototype.load=()=>{};
                  HTMLMediaElement.prototype.pause=()=>{};
                  HTMLMediaElement.prototype.play=()=>Promise.resolve();
                }""")
                page.set_content((A/"index.html").read_text("utf8"),
                                 wait_until="load", timeout=90000)
                page.add_style_tag(path=str(A/"bf_home_nav.css"))
                page.add_script_tag(path=str(A/"bf_home_nav.js"))
                assert page.evaluate("P.version") == 7
                assert page.evaluate("BF_homeNav.current") == "home"
                assert page.locator("#bf-scene-party button.bf-scene-member").count() == 6

                for mode in (
                    "baseline", "route-auto", "route-busy", "route-repeat-active",
                    "route-repeat-null", "route-repeat-throw", "route-squad",
                    "route-roster", "tab-auto", "tab-busy", "tab-repeat-active",
                    "tab-squad", "tab-route"
                ):
                    result = page.evaluate("""mode => {
                      const nav=BF_homeNav, box=BFUnitBox, tabs=BFInnerScreens;
                      const originalShow=box.showDetail, originalTab=tabs.setTab;
                      const originalRepeat=window.BFGlobalQoLQuestRepeatV9800;
                      const originalSquad=P.squad.slice(),originalRoster=P.roster.slice();
                      const originalAuto=S.auto,originalBusy=S.busy;
                      const calls=[];
                      const injected=[];
                      let handler=null, result=null, before=null;
                      const snap=()=>JSON.stringify({
                        p:P,s:S,quest:QUEST.missionId,writes:__v624Writes(),
                        storage:Array.from({length:localStorage.length},(_,i)=>{
                          const k=localStorage.key(i);return [k,localStorage.getItem(k)]
                        }).sort((a,b)=>a[0].localeCompare(b[0]))
                      });
                      try {
                        S.auto=false; S.busy=false;
                        nav.go('home');BFGlobalHome.refreshParty();
                        const first=P.squad[0],second=P.squad[1];
                        const button=document.querySelector('#bf-scene-party button.bf-scene-member');
                        if(button?.dataset.bfHomeUnitId!==String(first))throw Error('Missing genuine owned first slot');
                        before=snap();
                        box.showDetail=id=>{calls.push(id);return true;};
                        const apply=(point)=>{
                          const [when, ...words]=mode.split('-'); const action=words.join('-');
                          if(when!==point)return;
                          if(action==='auto')S.auto=true;
                          else if(action==='busy')S.busy=true;
                          else if(action==='repeat-active')window.BFGlobalQoLQuestRepeatV9800={statusSnapshot:()=>({active:true})};
                          else if(action==='repeat-null')window.BFGlobalQoLQuestRepeatV9800={statusSnapshot:()=>null};
                          else if(action==='repeat-throw')window.BFGlobalQoLQuestRepeatV9800={statusSnapshot:()=>{throw Error('repeat unavailable')}};
                          else if(action==='squad')P.squad[0]=second;
                          else if(action==='roster')P.roster=P.roster.filter(id=>id!==first);
                          else if(action==='route')nav.go('home');
                          else throw Error('Unknown race injection: '+mode);
                          injected.push(action);
                        };
                        if(mode.startsWith('route-')){
                          handler=e=>{
                            if(e.detail?.route!=='units')return;
                            window.removeEventListener('bf-route-change',handler);
                            apply('route');
                          };
                          window.addEventListener('bf-route-change',handler);
                        } else if(mode.startsWith('tab-')){
                          tabs.setTab=function(tab){
                            const ok=originalTab.call(this,tab);
                            if(tab==='box')apply('tab');
                            return ok;
                          };
                        }
                        button.click();
                        result={
                          mode,base:first,calls:[...calls],route:nav.current,
                          tab:tabs.unitTab,changed:snap()!==before,
                          written:__v624Writes(),injected:[...injected]
                        };
                      } finally {
                        if(handler)window.removeEventListener('bf-route-change',handler);
                        box.showDetail=originalShow;tabs.setTab=originalTab;
                        window.BFGlobalQoLQuestRepeatV9800=originalRepeat;
                        P.squad=originalSquad;P.roster=originalRoster;
                        S.auto=originalAuto;S.busy=originalBusy;
                        nav.go('home');BFGlobalHome.refreshParty();
                        result={...result,restored:snap()===before};
                      }
                      return result;
                    }""", mode)
                    if mode == "baseline":
                        assert result["calls"] == [result["base"]], (width, result)
                        assert result["injected"] == [], (width, mode, "unexpected injection")
                    else:
                        assert result["injected"] == [mode.split("-", 1)[1]], (width, mode, "race injection not exercised")
                        assert result["calls"] == [], (width, result)
                    assert result["restored"], (width, mode, "fixture leaked v7 or storage")
                    assert not errors, (width, mode, errors)
                assert page.evaluate("document.documentElement.scrollWidth<=innerWidth"), width
                print("PASS v624 real Home", width, "px, normal Unit Box and 12 route/tab race refusals")
            finally:
                page.close()
    finally:
        browser.close()
print("PASS v624 real Home route+tab race gates; player v7 and manual Auto unchanged")
