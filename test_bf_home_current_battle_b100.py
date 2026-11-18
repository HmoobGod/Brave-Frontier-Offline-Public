"""Home returns to an existing native battle without selecting/resetting it."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
  getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
  removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
  get length(){return Object.keys(db).length}}});window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 page.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 page.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
              'bf100_grand_gaia_campaign.js','bf101_story_continue.js',
              'bf110_quest_journal.js','bf2000_story_battle_hud.js',
              'bf2100_battle_command_tray.js','bf2200_original_event_reader.js'):
  page.add_script_tag(path=str(A/name))
 page.evaluate("BF_homeNav.go('home');BFHomeCurrentBattleB100.refresh()")
 assert page.evaluate('BFHomeCurrentBattleB100.snapshot().missionId')==page.evaluate('QUEST.missionId')
 assert page.locator('#bf-home-current-battle').is_visible()
 assert page.evaluate("""()=>{
   const button=document.getElementById('bf-home-current-battle').getBoundingClientRect();
   const story=document.querySelector('.bf-scene-story').getBoundingClientRect();
   return button.width >= story.width-40;
 }""")
 stable=page.evaluate("JSON.stringify({P,S,quest:QUEST.missionId,save:localStorage.getItem('bf_global_offline_demo_v7')})")
 page.locator('#bf-home-current-battle').click()
 assert page.evaluate('BF_homeNav.current')=='quest'
 assert page.evaluate("document.activeElement.matches('#bf2100-tray h3')")
 assert page.evaluate("JSON.stringify({P,S,quest:QUEST.missionId,save:localStorage.getItem('bf_global_offline_demo_v7')})")==stable
 proof=page.evaluate("""()=>{BF_homeNav.go('home');const api=BFHomeCurrentBattleB100,old=S,repeat=window.BFGlobalQoLQuestRepeatV9800;const out=[];try{api.refresh();S={...S};out.push(api.open()===false);S=old;
 for(const mode of ['busy','auto','repeat']){S.busy=mode==='busy';S.auto=mode==='auto';if(mode==='repeat')window.BFGlobalQoLQuestRepeatV9800={statusSnapshot:()=>null};api.refresh();out.push(document.querySelector('#bf-home-current-battle').disabled&&api.open()===false);}}
 finally{S=old;S.busy=false;S.auto=false;window.BFGlobalQoLQuestRepeatV9800=repeat;api.refresh();}return out;}""")
 assert proof==[True]*4,proof
 page.evaluate('S.over=true;BFHomeCurrentBattleB100.refresh()')
 assert page.locator('#bf-home-current-battle').is_hidden()
 page.evaluate('S.over=false;BFHomeCurrentBattleB100.refresh()')
 assert page.locator('#bf-home-current-battle').is_visible()
 assert page.evaluate("JSON.stringify({P,S,quest:QUEST.missionId,save:localStorage.getItem('bf_global_offline_demo_v7')})")==stable
 assert not errors,errors
 browser.close()
print('PASS Home existing-battle return, source mission/focus, stale identity and manual guards, full state invariance')
