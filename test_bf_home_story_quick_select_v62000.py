"""v620: Home selects the next source-verified DEMO story mission via native v101.

Real index.html, real Home and Grand Gaia modules, disposable browser-only state.
Never loads an owner save. Selecting a mission is deliberately NOT Auto Battle.
"""
from pathlib import Path
import shutil
import sys

R = Path(__file__).resolve().parent
A = R / "app/src/main/assets"
HOME = (A / "bf_home_nav.js").read_text("utf-8")
CONTINUE = (A / "bf101_story_continue.js").read_text("utf-8")
WORKFLOW = (R / ".github/workflows/build-debug-apk.yml").read_text("utf-8")
PREFLIGHT = (R / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf-8")
MANIFEST = (R / "app/src/main/AndroidManifest.xml").read_text("utf-8")
TEST = "test_bf_home_story_quick_select_v62000.py"

assert WORKFLOW.count("python3 " + TEST) == 1
assert PREFLIGHT.count(TEST) == 2  # path trigger + --source-only
assert "android.permission.INTERNET" not in MANIFEST
assert len(HOME.encode("utf-8")) < 128 * 1024
assert HOME.count("function safeNextStoryMission()") == 1
assert "S?.auto!==false" in HOME and "S?.mode!=='archive'" in HOME
assert "S.party.some(p=>!!p?.action)" in HOME
assert "api.canNavigate()!==true" in HOME
assert "source?.missionId!==mission" in HOME
assert "document.getElementById('bf101-continue')?.click()" in HOME
assert "SELECT NEXT STORY" in HOME and "VIEW QUESTS" in HOME
assert "BFQuestAreas.choose(q)" in CONTINUE and "questUnlocked(q)" in CONTINUE
quick = HOME.split("function safeNextStoryMission()", 1)[1].split("  function refreshStory()", 1)[0]
assert "localStorage" not in quick and "saveProgress(" not in quick
assert "awardDemoRewards(" not in quick and "auto.click()" not in quick
print("PASS v620 source: native v101 source next-mission route, manual only, no writes")
if "--source-only" in sys.argv:
    raise SystemExit(0)

from playwright.sync_api import sync_playwright

chrome = (shutil.which("chromium") or shutil.which("google-chrome")
          or shutil.which("google-chrome-stable"))
assert chrome, "Chromium required for real Home+story regression"
mods = (
    "bf_home_nav.js", "bf080_morgan_map.js", "bf090_st_lamia_map.js",
    "bf100_grand_gaia_campaign.js", "bf101_story_continue.js",
    "bf14300_original_quest_energy.js",
)
with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=True, executable_path=chrome,
        args=["--no-sandbox", "--disable-dev-shm-usage"])
    page = browser.new_page(viewport={"width": 390, "height": 844})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    try:
        page.evaluate("""() => {
          const db={};
          Object.defineProperty(window,'localStorage',{configurable:true,value:{
            getItem:k=>db[k]??null,
            setItem:(k,v)=>{db[k]=String(v)},
            removeItem:k=>{delete db[k]},
            key:i=>Object.keys(db)[i]??null,
            get length(){return Object.keys(db).length}
          }});
          window.alert=()=>{};window.confirm=()=>true;
          HTMLMediaElement.prototype.load=()=>{};
          HTMLMediaElement.prototype.pause=()=>{};
          HTMLMediaElement.prototype.play=()=>Promise.resolve();
        }""")
        page.set_content((A / "index.html").read_text("utf-8"),
                         wait_until="load", timeout=90000)
        page.add_style_tag(path=str(A / "bf_home_nav.css"))
        for mod in mods:
            page.add_script_tag(path=str(A / mod))
        assert page.evaluate("P.version") == 7
        assert page.evaluate("QUESTS.length") == 106
        assert page.evaluate("BF_homeNav.current") == "home"
        assert page.evaluate("BFGrandGaiaContinueV101.nextMission") == 1

        # A clean, disposable archive-mode manual session. Source and native
        # Continue Story remain actual production implementations.
        page.evaluate("""() => {
          S.mode='archive';S.busy=false;S.over=false;S.auto=false;
          if(Array.isArray(S.party))for(const p of S.party)if(p)p.action=null;
          BFGrandGaiaContinueV101.refresh();
          BFGlobalHome.refreshStory();
          window.__nativeContinueClicks=0;
          document.getElementById('bf101-continue').addEventListener(
            'click',()=>{__nativeContinueClicks++});
        }""")
        label = page.locator("#bf-home-story-open")
        assert label.inner_text() == "SELECT NEXT STORY ›"
        for width in (320, 360, 393, 412, 540):
            page.set_viewport_size({"width": width, "height": 844})
            bounds=label.evaluate("""el=>({
              left:el.getBoundingClientRect().left,
              right:el.getBoundingClientRect().right,
              viewport:innerWidth,
              height:el.getBoundingClientRect().height
            })""")
            assert bounds["left"] >= 0 and bounds["right"] <= width+1, (width,bounds)
            assert bounds["height"] >= 44, (width,bounds)

        before=page.evaluate("""()=>({
          player:JSON.stringify(P),save:localStorage.getItem(
            'bf_global_offline_demo_v7'),auto:S.auto,
          clears:JSON.stringify(P.questClears),
          storageKeys:Array.from({length:localStorage.length},(_,i)=>localStorage.key(i)).sort()
        })""")
        label.click()
        result=page.evaluate("""()=>{
          const raw=localStorage.getItem('bf_global_offline_demo_v7');
          const stored=raw?JSON.parse(raw):null;
          return {
            route:BF_homeNav.current,mission:QUEST.missionId,
            nativeClicks:__nativeContinueClicks,auto:S.auto,
            player:JSON.stringify(P),save:raw,
            storedVersion:stored?.version??null,
            storedClears:JSON.stringify(stored?.questClears??null),
            storageKeys:Array.from({length:localStorage.length},(_,i)=>localStorage.key(i)).sort()
          };
        }""")
        assert result["route"]=="quest" and result["mission"]==1, result
        assert result["nativeClicks"]==1 and result["auto"] is False, result
        assert result["player"]==before["player"], "mission selection altered player progress"
        # Native BFQuestAreas.choose(q) may persist the selected lastMission.
        # Unlike a passive Home preview, an explicit Quest selection can write
        # a VALID v7 save; source v101 tests already document this behavior.
        # Reject an invalid schema, changed clear ledger or extra storage keys.
        # The disposable localStorage stub's keys live in its backing db; use
        # the Web Storage length/key(i) contract, not Object.keys(methods).
        assert result["save"] and result["storedVersion"]==7, result
        assert result["storedClears"]==before["clears"], "selection changed saved clears"
        assert set(result["storageKeys"])==(
          set(before["storageKeys"])|{"bf_global_offline_demo_v7"}), result

        home=page.locator('.bf-navbar [data-bf-goto="home"]')
        home.click()
        assert page.evaluate("BF_homeNav.current")=="home"
        # Unattended/corrupted states must ONLY show the legacy View Quests
        # route. They must never click the native Continue button.
        def probe(expr,restore):
            page.evaluate(expr)
            page.evaluate("BFGlobalHome.refreshStory()")
            assert label.inner_text()=="VIEW QUESTS ›"
            count=page.evaluate("__nativeContinueClicks")
            storage=page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
            label.click()
            assert page.evaluate("BF_homeNav.current")=="quest"
            assert page.evaluate("__nativeContinueClicks")==count
            assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==storage
            page.evaluate(restore)
            home.click()
            assert page.evaluate("BF_homeNav.current")=="home"

        probe("S.auto=1", "S.auto=false")
        probe("S.busy=true", "S.busy=false")
        # Deliberate v620 scope limit: a completed victory stays on VIEW QUESTS
        # until a future independently reviewed canonical-receipt shortcut.
        probe("S.over=true", "S.over=false")
        probe("S.mode='training'", "S.mode='archive'")
        probe("P.questClears[365]=-1", "delete P.questClears[365]")
        probe("window.__savedContinue=window.BFGrandGaiaContinueV101;"
              "delete window.BFGrandGaiaContinueV101",
              "window.BFGrandGaiaContinueV101=window.__savedContinue;"
              "delete window.__savedContinue")
        page.evaluate("BFGrandGaiaContinueV101.refresh();BFGlobalHome.refreshStory()")
        assert label.inner_text()=="SELECT NEXT STORY ›"
        assert page.evaluate("S.auto") is False
        assert not errors,errors
        print("PASS v620 browser: one-tap native source-next manual selection; "
              "320–540 layouts, six blocked fallbacks, valid v7, no rewards")
    finally:
        page.close()
        browser.close()
