"""v420 read-only original 2022 Home next-adventure and squad-slot preview."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/"app/src/main/assets"
JS=(ASSETS/"bf_home_battle_readiness_v420.js").read_text("utf8")
JAVA=(ROOT/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
assert JS.count("/* BF_HOME_BATTLE_READINESS_V420 */")==1
assert len(JS.encode("utf8"))<16384
assert all(k not in JS for k in ("localStorage", "saveGame(", "saveProgress(", "BFQuestAreas.choose(", "S.auto="))
assert JAVA.index('readPackagedText("bf100_grand_gaia_campaign.js")') < JAVA.index(
    'readPackagedText("bf14300_original_quest_energy.js")') < JAVA.index(
    'readPackagedText("bf_home_battle_readiness_v420.js")')
assert "2022 archived" in JS and "Enemy formations" in JS
assert 'bf420-home-hint' in JS and "aria-live','polite" in JS
assert 'AUTO BATTLE ACTIVE' in JS and 'AUTO REPEAT ACTIVE' in JS
assert 'REPEAT STATUS UNAVAILABLE' in JS
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
        executable_path=shutil.which("chromium") or
          shutil.which("google-chrome") or shutil.which("google-chrome-stable"),
        args=["--no-sandbox","--disable-dev-shm-usage"])
    try:
        page=browser.new_page(viewport={"width":390,"height":844})
        errors=[]
        page.on("pageerror",lambda e:errors.append(str(e)))
        page.evaluate("""() => {
          const db={};
          Object.defineProperty(window,'localStorage',{configurable:true,value:{
             getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
             removeItem:k=>{delete db[k]},key:i=>Object.keys(db)[i]??null,
             get length(){return Object.keys(db).length}
          }});
          window.alert=()=>{};window.confirm=()=>true;
          HTMLMediaElement.prototype.load=()=>{};
          HTMLMediaElement.prototype.pause=()=>{};
          HTMLMediaElement.prototype.play=()=>Promise.resolve();
        }""")
        page.set_content((ASSETS/"index.html").read_text("utf8"),wait_until="load",timeout=90000)
        page.add_style_tag(path=str(ASSETS/"bf_home_nav.css"))
        for name in ("bf_home_nav.js","bf080_morgan_map.js","bf090_st_lamia_map.js",
                     "bf100_grand_gaia_campaign.js","bf101_story_continue.js",
                     "bf14300_original_quest_energy.js"):
            page.add_script_tag(path=str(ASSETS/name))
        # Capture original playable tile positions BEFORE the optional card.
        # v420 must NOT push them further down the small-phone viewport.
        baseline={}
        for width in (320,390):
            page.set_viewport_size({"width":width,"height":844})
            baseline[width]=page.evaluate("""() => {
              const explore=document.querySelector('.bf-scene-explore');
              return {
                explore:explore.getBoundingClientRect().top,
                quest:explore.querySelector('button[data-bf-goto="quest"]').getBoundingClientRect().top,
                summon:explore.querySelector('button[data-bf-goto="summon"]').getBoundingClientRect().top
              };
            }""")
        page.add_script_tag(path=str(ASSETS/"bf_home_battle_readiness_v420.js"))
        for width in (320,390):
            page.set_viewport_size({"width":width,"height":844})
            geometry=page.evaluate("""() => {
              const explore=document.querySelector('.bf-scene-explore');
              const preview=document.getElementById('bf420-home-readiness');
              return {
                followsAdventure:explore.nextElementSibling===preview,
                explore:explore.getBoundingClientRect().top,
                quest:explore.querySelector('button[data-bf-goto="quest"]').getBoundingClientRect().top,
                summon:explore.querySelector('button[data-bf-goto="summon"]').getBoundingClientRect().top
              };
            }""")
            assert geometry["followsAdventure"],(width,geometry)
            for key in ("explore","quest","summon"):
                assert abs(geometry[key]-baseline[width][key])<=1,(width,key,baseline[width],geometry)
        page.set_viewport_size({"width":390,"height":844})
        assert page.evaluate("P.version")==7
        assert page.evaluate("BF_homeNav.current")=="home"
        panel=page.locator("#bf420-home-readiness")
        assert panel.count()==1 and panel.is_visible()
        assert page.locator('#bf420-home-hint').get_attribute('role')=='status'
        assert page.locator('#bf420-home-hint').is_hidden()
        assert page.locator("#bf420-home-mission").count()==1
        snap=page.evaluate("BFHomeBattleReadinessV420.snapshot()")
        assert snap["missionId"]==1 and snap["waves"]==3 and snap["energy"]==0,snap
        assert "2022 original 3 waves" in page.locator("#bf420-home-mission").inner_text()
        assert "reference only" in page.locator("#bf420-home-mission").inner_text()
        filled=page.evaluate("""() => P.squad.filter(id=>Number.isSafeInteger(id) &&
          id>=0 && typeof effectiveUnit==='function' && !!effectiveUnit(id)).length""")
        assert snap["filled"]==filled,snap
        assert f"{filled}/6 filled slots" in page.locator("#bf420-home-party").inner_text()
        # v425: invalid/duplicate/unowned entries cannot inflate the Home count.
        # All negative fixtures are temporary memory edits, not save writes.
        ownership=page.evaluate("""() => {
          const originalSquad=P.squad, originalRoster=P.roster;
          const before=JSON.stringify(P), beforeS=JSON.stringify(S);
          const save=localStorage.getItem('bf_global_offline_demo_v7');
          let result={};
          try {
            const owned=P.roster.find(id=>Number.isSafeInteger(id)&&id>0&&effectiveUnit(id));
            const unowned=[10012,20012,30012,40012,50012,60012,
                           10013,20013,30013,40013,50013,60013]
              .find(id=>!P.roster.includes(id)&&effectiveUnit(id));
            if(owned===undefined || unowned===undefined)
              return {fixture:false};
            P.squad=[owned,unowned,owned,-1,{},null];
            const record=BFHomeBattleReadinessV420.refresh();
            result={fixture:true,filled:record?.filled,
              countText:document.getElementById('bf420-home-party').textContent,
              questEnabled:!document.getElementById('bf420-home-quest').disabled};
            P.roster=null;
            result.missingRoster=BFHomeBattleReadinessV420.snapshot()===null;
            BFHomeBattleReadinessV420.refresh();
            result.missingText=document.getElementById('bf420-home-party').textContent;
          } finally {
            P.squad=originalSquad;P.roster=originalRoster;
            BFHomeBattleReadinessV420.refresh();
          }
          return {...result,unchanged:JSON.stringify(P)===before&&
            JSON.stringify(S)===beforeS&&
            localStorage.getItem('bf_global_offline_demo_v7')===save};
        }""")
        assert ownership["fixture"] and ownership["filled"]==1,ownership
        assert "1/6 filled slots" in ownership["countText"],ownership
        assert ownership["questEnabled"],ownership
        assert ownership["missingRoster"] and "unavailable" in ownership["missingText"],ownership
        assert ownership["unchanged"],ownership
        # A visible missing-party explanation never auto-selects or starts.
        zero=page.evaluate("""()=>{
          const old=P.squad,save=localStorage.getItem('bf_global_offline_demo_v7');
          try{
            P.squad=[];BFHomeBattleReadinessV420.refresh();
            return {text:document.getElementById('bf420-home-hint').textContent,
              visible:!document.getElementById('bf420-home-hint').hidden,
              questEnabled:!document.getElementById('bf420-home-quest').disabled,
              saveUnchanged:localStorage.getItem('bf_global_offline_demo_v7')===save};
          }finally{P.squad=old;BFHomeBattleReadinessV420.refresh();}
        }""")
        assert zero['visible'] and 'NO VALID SQUAD' in zero['text'],zero
        assert zero['questEnabled'] and zero['saveUnchanged'],zero
        before=page.evaluate("""() => ({
           p:JSON.stringify(P),quest:QUEST.missionId,auto:S.auto,
           save:localStorage.getItem('bf_global_offline_demo_v7'),
           keys:Object.keys(localStorage).sort().join(',')
        })""")
        for width in (320,340,370,390,540):
            page.set_viewport_size({"width":width,"height":844})
            geometry=page.evaluate("""() => {
              const root=document.getElementById('bf420-home-readiness');
              const panel=root.getBoundingClientRect();
              return {
                panelLeft:panel.left,panelRight:panel.right,
                buttons:[...root.querySelectorAll('button')].map(b=>{
                  const r=b.getBoundingClientRect();
                  return {height:r.height,left:r.left,right:r.right};
                }),
                scrollWidth:document.documentElement.scrollWidth,
                viewport:innerWidth
              };
            }""")
            assert geometry["panelLeft"]>=-1 and geometry["panelRight"]<=width+1,(width,geometry)
            assert geometry["scrollWidth"]<=width,(width,geometry)
            for button in geometry["buttons"]:
                assert button["height"]>=44,(width,button)
                assert button["left"]>=-1 and button["right"]<=width+1,(width,button)
        page.set_viewport_size({"width":390,"height":844})
        # A live automatic action must disable even read-only route shortcuts.
        page.evaluate("S.auto=true;BFHomeBattleReadinessV420.refresh()")
        assert 'AUTO BATTLE ACTIVE' in page.locator('#bf420-home-hint').inner_text()
        assert page.locator("#bf420-home-quest").is_disabled()
        assert page.locator("#bf420-home-units").is_disabled()
        page.evaluate("""() => document.getElementById('bf420-home-quest').dispatchEvent(
           new MouseEvent('click',{bubbles:true}))""")
        assert page.evaluate("BF_homeNav.current")=="home"
        page.evaluate("S.auto=false;S.busy=true;BFHomeBattleReadinessV420.refresh()")
        assert 'TURN IN PROGRESS' in page.locator('#bf420-home-hint').inner_text()
        assert page.locator("#bf420-home-quest").is_disabled()
        page.evaluate("S.busy=false;BFHomeBattleReadinessV420.refresh()")
        assert page.locator('#bf420-home-hint').is_hidden()
        assert page.locator("#bf420-home-quest").is_enabled()
        # A broken or active optional repeat provider must fail closed.
        repeat_guards=page.evaluate("""() => {
          const previous=window.BFGlobalQoLQuestRepeatV9800;
          const read=()=>({
            quest:document.getElementById('bf420-home-quest').disabled,
            units:document.getElementById('bf420-home-units').disabled,
            hint:document.getElementById('bf420-home-hint').textContent
          });
          try{
            window.BFGlobalQoLQuestRepeatV9800={statusSnapshot:()=>({active:true})};
            BFHomeBattleReadinessV420.refresh();
            const active=read();
            window.BFGlobalQoLQuestRepeatV9800={statusSnapshot:()=>{throw Error('bad repeat provider');}};
            BFHomeBattleReadinessV420.refresh();
            const throwing=read();
            window.BFGlobalQoLQuestRepeatV9800={};
            BFHomeBattleReadinessV420.refresh();
            const missing=read();
            return {active,throwing,missing,
              activeHint:active.hint,throwingHint:throwing.hint,missingHint:missing.hint};
          }finally{
            if(previous===undefined)delete window.BFGlobalQoLQuestRepeatV9800;
            else window.BFGlobalQoLQuestRepeatV9800=previous;
            BFHomeBattleReadinessV420.refresh();
          }
        }""")
        assert all(v['quest'] and v['units'] for k,v in repeat_guards.items() if k in ('active','throwing','missing')),repeat_guards
        assert 'AUTO REPEAT ACTIVE' in repeat_guards['activeHint'],repeat_guards
        assert 'REPEAT STATUS UNAVAILABLE' in repeat_guards['throwingHint'],repeat_guards
        assert 'REPEAT STATUS UNAVAILABLE' in repeat_guards['missingHint'],repeat_guards
        assert page.locator("#bf420-home-quest").is_enabled()
        # Every archived quest field must remain source-qualified.
        field_gates=page.evaluate("""() => {
          const q=QUESTS.find(x=>x.missionId===1),result={};
          for(const key of ['dungeonId','requires','battles','energy','exp','zel','karma']){
            const original=q[key];
            try{
              q[key]=original+1;
              result[key]=BFHomeBattleReadinessV420.snapshot()===null;
            }finally{q[key]=original;}
          }
          BFHomeBattleReadinessV420.refresh();
          return result;
        }""")
        assert all(field_gates.values()),field_gates
        # Corrupted live quest metadata must NOT yield a fabricated '2022' preview.
        tamper=page.evaluate("""() => {
          const q=QUESTS.find(x=>x.missionId===1),old=q.battles;
          try{q.battles=old+1;return {
             record:BFHomeBattleReadinessV420.refresh(),
             text:document.getElementById('bf420-home-mission').textContent,
             disabled:document.getElementById('bf420-home-quest').disabled
          };}finally{q.battles=old;BFHomeBattleReadinessV420.refresh();}
        }""")
        assert tamper['record'] is None and tamper['disabled'],tamper
        assert 'unavailable' in tamper['text'],tamper
        # Source mismatch must still be fail-closed; the fixture restores the UI.
        # Both actions only navigate; original profile, mission and storage stay unchanged.
        page.locator("#bf420-home-units").click()
        assert page.evaluate("BF_homeNav.current")=="units"
        page.evaluate("BF_homeNav.go('home')")
        assert page.locator("#bf420-home-quest").is_enabled()
        page.locator("#bf420-home-quest").click()
        assert page.evaluate("BF_homeNav.current")=="quest"
        after=page.evaluate("""() => ({
           p:JSON.stringify(P),quest:QUEST.missionId,auto:S.auto,
           save:localStorage.getItem('bf_global_offline_demo_v7'),
           keys:Object.keys(localStorage).sort().join(',')
        })""")
        assert before==after,(before,after)
        page.evaluate("BF_homeNav.go('home')")
        assert page.locator("#bf420-home-readiness").is_visible()
        # Test-only memory-only complete clears, never an owner save write.
        page.evaluate("""() => {
          for(const q of QUESTS)P.questClears[q.missionId]=1;
          BFHomeBattleReadinessV420.refresh();
        }""")
        final=page.evaluate("BFHomeBattleReadinessV420.snapshot()")
        assert final["complete"] is True and final["missionId"] is None,final
        assert "All 106 archived missions cleared" in page.locator("#bf420-home-mission").inner_text()
        assert 'STORY COMPLETE' in page.locator('#bf420-home-hint').inner_text()
        assert page.locator("#bf420-home-quest").is_disabled()
        assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')") is None
        assert not errors,errors
    finally:
        browser.close()
print("PASS v420 original 2022 Home next-quest preview, manual only, 320-540px, no v7 writes")
