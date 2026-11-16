"""Native Home Village notice links read archived text only, no gameplay unlocks."""
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
 api='BFHomeVillageNoticesB100'
 page.evaluate("BF_homeNav.go('home');document.querySelector('#bf-home-village-notices').open=true;BFHomeVillageNoticesB100.refresh()")
 assert page.locator('[data-village-notice="10"]').is_disabled()
 page.evaluate('P.questClears[10]=1;BFHomeVillageNoticesB100.refresh()')
 stable=page.evaluate("JSON.stringify({P,S,mission:QUEST.missionId,save:localStorage.getItem('bf_global_offline_demo_v7')})")
 for width in (320,390,540):
  page.set_viewport_size({'width':width,'height':844});page.evaluate("BF_homeNav.go('home');BFHomeVillageNoticesB100.refresh()")
  assert page.locator('[data-village-notice="10"]').bounding_box()['height']>=44
  page.locator('[data-village-notice="10"]').click()
  assert page.evaluate('BFGlobalOriginalEventsV2200.snapshot().chosen')=='clear:10'
  assert page.evaluate('document.activeElement.id')=='bf2200-title'
  assert page.evaluate("JSON.stringify({P,S,mission:QUEST.missionId,save:localStorage.getItem('bf_global_offline_demo_v7')})")==stable
 blocked=page.evaluate("""()=>{BF_homeNav.go('home');const repeat=window.BFGlobalQoLQuestRepeatV9800,api=BFHomeVillageNoticesB100,out=[];
 try{for(const mode of ['busy','auto','active','unknown','throw']){S.busy=mode==='busy';S.auto=mode==='auto';window.BFGlobalQoLQuestRepeatV9800=mode==='busy'||mode==='auto'?repeat:{statusSnapshot:()=>{if(mode==='throw')throw Error('fixture');return mode==='unknown'?null:{active:true}}};api.refresh();out.push(document.querySelector('[data-village-notice="10"]').disabled&&api.open(10)===false&&BF_homeNav.current==='home');}}
 finally{S.busy=false;S.auto=false;window.BFGlobalQoLQuestRepeatV9800=repeat;api.refresh();}return out;}""")
 assert blocked==[True]*5,blocked
 assert 'gameplay remain unavailable' in page.locator('#bf-home-village-notices').text_content()
 assert page.evaluate("JSON.stringify({P,S,mission:QUEST.missionId,save:localStorage.getItem('bf_global_offline_demo_v7')})")==stable
 assert not errors,errors
 browser.close()
print('PASS Home recovered Village notice routing, source identity, clear/idle guards, three widths, focus and v7 invariance')
