"""v421: independent proof of Home phone cold-start + second 2022 source gate.

This adds targeted Chromium assertions to existing merged runtime features only.
No runtime, save, APK or gameplay logic is changed by this test.
"""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/"app/src/main/assets"
HEADER=(ASSETS/"bf054_header_status.js").read_text("utf-8")
READY=(ASSETS/"bf_home_battle_readiness_v420.js").read_text("utf-8")
JAVA=(ROOT/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf-8")

assert "syncNarrowHome();" in HEADER, "phone must reorder on initial module load"
assert "home.insertBefore(sceneExplore,sceneSquad)" in HEADER
assert "if (preview) home.insertBefore(preview,sceneSquad)" in HEADER
assert ".every((v,i)=>v===row[i])" in READY, "v420 must independently compare all source tuple fields"
assert JAVA.index('readPackagedText("bf054_header_status.js")') < JAVA.index(
    'readPackagedText("bf100_grand_gaia_campaign.js")') < JAVA.index(
    'readPackagedText("bf14300_original_quest_energy.js")') < JAVA.index(
    'readPackagedText("bf_home_battle_readiness_v420.js")')

def fresh_page(browser,width):
    page=browser.new_page(viewport={"width":width,"height":844})
    errors=[]
    page.on("pageerror",lambda error:errors.append(str(error)))
    page.evaluate("""() => {
      const db={};
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:k=>db[k]??null,setItem:(k,v)=>{db[k]=String(v)},
        removeItem:k=>{delete db[k]},key:i=>Object.keys(db)[i]??null,
        get length(){return Object.keys(db).length}
      }});
      window.alert=()=>{};window.confirm=()=>true;
      HTMLMediaElement.prototype.load=()=>{};
      HTMLMediaElement.prototype.pause=()=>{};
      HTMLMediaElement.prototype.play=()=>Promise.resolve();
    }""")
    page.set_content((ASSETS/"index.html").read_text("utf-8"),wait_until="load",timeout=90000)
    page.add_style_tag(path=str(ASSETS/"bf_home_nav.css"))
    for name in ("bf_home_nav.js","bf054_header_status.js",
                 "bf080_morgan_map.js","bf090_st_lamia_map.js",
                 "bf100_grand_gaia_campaign.js","bf101_story_continue.js",
                 "bf14300_original_quest_energy.js"):
        page.add_script_tag(path=str(ASSETS/name))
    return page,errors

def state(page):
    return page.evaluate("""() => ({
       player:JSON.stringify(P),mission:QUEST.missionId,
       auto:S.auto,busy:S.busy,round:S.round,wave:S.wave,
       save:localStorage.getItem('bf_global_offline_demo_v7'),
       keys:Object.keys(localStorage).sort().join(',')
    })""")

with sync_playwright() as pw:
    browser=pw.chromium.launch(
        headless=True,
        executable_path=shutil.which("chromium") or
          shutil.which("google-chrome") or shutil.which("google-chrome-stable"),
        args=["--no-sandbox","--disable-dev-shm-usage"])
    try:
        # Cold boot MUST start at the narrow size; simply resizing a wide page
        # cannot prove the mandatory initial syncNarrowHome() call works.
        for width in (320,370):
            page,errors=fresh_page(browser,width)
            try:
                before=state(page)
                geometry=page.evaluate("""() => {
                  const home=document.getElementById('bf-home'),
                    title=home.querySelector('.bf-scene-title'),
                    details=home.querySelector('#bf054-home-details'),
                    explore=home.querySelector('.bf-scene-explore'),
                    squad=home.querySelector('.bf-scene-squad'),
                    story=home.querySelector('.bf-scene-story'),
                    nav=document.querySelector('.bf-navbar').getBoundingClientRect(),
                    tiles=[...explore.querySelectorAll('button.bf-scene-active')];
                  return {
                    adjacent:explore.nextElementSibling===squad,
                    order:title.compareDocumentPosition(explore)&Node.DOCUMENT_POSITION_FOLLOWING,
                    orderOK:!!(title.compareDocumentPosition(explore)&Node.DOCUMENT_POSITION_FOLLOWING)&&
                      !!(explore.compareDocumentPosition(story)&Node.DOCUMENT_POSITION_FOLLOWING),
                    details:details?.parentElement===home,
                    routes:tiles.map(t=>t.dataset.bfGoto),
                    buttons:tiles.map(t=>{
                      const b=t.getBoundingClientRect();
                      return {left:b.left,right:b.right,top:b.top,bottom:b.bottom};
                    }),
                    navTop:nav.top,scroll:document.documentElement.scrollWidth,
                    viewport:innerWidth
                  };
                }""")
                assert geometry["adjacent"] and geometry["orderOK"] and geometry["details"],(width,geometry)
                assert geometry["routes"]==["quest","summon"],(width,geometry)
                assert len(geometry["buttons"])==2,(width,geometry)
                assert all(t["top"]>=0 and t["bottom"]<geometry["navTop"]
                           and t["left"]>=0 and t["right"]<=width for t in geometry["buttons"]),(width,geometry)
                assert geometry["scroll"]<=width,(width,geometry)
                # Late v420 injection must keep the original artwork before
                # the optional preview with no additional location nodes.
                page.add_script_tag(path=str(ASSETS/"bf_home_battle_readiness_v420.js"))
                assert page.evaluate("""() => {
                  const home=document.getElementById('bf-home');
                  const e=home.querySelector('.bf-scene-explore');
                  const p=home.querySelector('#bf420-home-readiness');
                  const squad=home.querySelector('.bf-scene-squad');
                  return e.nextElementSibling===p && p.nextElementSibling===squad &&
                    home.querySelectorAll('.bf-scene-explore').length===1 &&
                    home.querySelectorAll('#bf420-home-readiness').length===1;
                }"""),width
                assert before==state(page),(width,before,state(page))
                assert not errors,errors
            finally:
                page.close()

        # The v420 campaign provider is captured when v420 is injected.
        # Override it BEFORE injection with an immutable source-qualified
        # nextPlayable() result. This bypasses the upstream source-validation
        # gate and independently tests v420's OWN 8-field tuple comparison.
        page,errors=fresh_page(browser,390)
        try:
            original=state(page)
            stub=page.evaluate("""() => {
              const live=window.BFGrandGaiaCampaignV100;
              const pinned=live.nextPlayable();
              if(!pinned||pinned.missionId!==1)return false;
              window.BFGrandGaiaCampaignV100=Object.freeze({
                ...live,nextPlayable:()=>pinned
              });
              return true;
            }""")
            assert stub is True
            page.add_script_tag(path=str(ASSETS/"bf_home_battle_readiness_v420.js"))
            assert page.evaluate("BFHomeBattleReadinessV420.snapshot()?.missionId") == 1
            flags=page.evaluate("""() => {
              const q=QUESTS.find(q=>q.missionId===1);
              const keys=['missionId','dungeonId','requires','battles',
                          'energy','exp','zel','karma'];
              const results={};
              for(const key of keys){
                const old=q[key];
                try{
                  q[key]=old+1;
                  const snapshot=BFHomeBattleReadinessV420.refresh();
                  results[key]=snapshot===null &&
                    document.getElementById('bf420-home-quest').disabled &&
                    document.getElementById('bf420-home-units').disabled &&
                    document.getElementById('bf420-home-mission').textContent.includes('unavailable');
                }finally{
                  q[key]=old;
                }
              }
              BFHomeBattleReadinessV420.refresh();
              return results;
            }""")
            assert len(flags)==8 and all(flags.values()),flags
            assert page.evaluate("BFHomeBattleReadinessV420.snapshot()?.missionId") == 1
            assert original==state(page),(original,state(page))
            assert not errors,errors
        finally:
            page.close()
    finally:
        browser.close()
print("PASS v421: authentic narrow cold boot + independent 8-field v420 source gate; v7 unchanged")
