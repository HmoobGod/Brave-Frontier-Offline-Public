"""B100 Home resume of an already-open source scene, native Chromium only."""
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
 for n in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
   'bf100_grand_gaia_campaign.js','bf101_story_continue.js','bf110_quest_journal.js',
   'bf2000_story_battle_hud.js','bf2100_battle_command_tray.js',
   'bf2200_original_event_reader.js','bf2300_morgan_event_dialogue.js',
   'bf2400_st_lamia_event_dialogue.js','bf2500_story_event_prompt.js'):
  page.add_script_tag(path=str(A/n))
 assert page.locator('#bf-home-resume-scene').is_hidden()
 page.evaluate('()=>{P.questClears[12]=1;renderQuestList()}')
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",20)') is True
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 for _ in range(4):page.locator('#bf2200-next').click()
 assert page.evaluate('BFGlobalOriginalEventsV2200.snapshot().step')==5
 for width in (320,390,540):
  page.set_viewport_size({'width':width,'height':844})
  page.locator('.bf-navbar button[data-bf-goto="home"]').click()
  before=page.evaluate('JSON.stringify({P,S,QUEST,scene:BFGlobalOriginalEventsV2200.snapshot(),save:localStorage.getItem("bf_global_offline_demo_v7")})')
  button=page.locator('#bf-home-resume-scene');assert button.is_visible()
  assert button.bounding_box()['height']>=44
  button.focus();page.keyboard.press('Enter')
  assert page.evaluate('BF_homeNav.current')=='quest'
  assert page.evaluate('document.activeElement.id')=='bf2200-title'
  assert page.evaluate('JSON.stringify({P,S,QUEST,scene:BFGlobalOriginalEventsV2200.snapshot(),save:localStorage.getItem("bf_global_offline_demo_v7")})')==before
 page.evaluate('BF_homeNav.go("home")')
 guarded=page.evaluate('JSON.stringify({P,S,QUEST,save:localStorage.getItem("bf_global_offline_demo_v7")})')
 for mode in ('busy','auto'):
  page.evaluate('(k)=>S[k]=true',mode)
  assert page.evaluate('BFHomeSourceResumeB100.open()') is False
  assert page.evaluate('BF_homeNav.current')=='home'
  page.evaluate('(k)=>S[k]=false',mode)
 for status in (True,None,'false'):
  page.evaluate('(v)=>window.BFGlobalQoLQuestRepeatV9800={statusSnapshot:()=>({active:v})}',status)
  assert page.evaluate('BFHomeSourceResumeB100.open()') is False
 page.evaluate("window.BFGlobalQoLQuestRepeatV9800={statusSnapshot:()=>{throw Error('repeat unavailable')}}")
 assert page.evaluate('BFHomeSourceResumeB100.open()') is False
 page.evaluate('window.BFGlobalQoLQuestRepeatV9800={statusSnapshot:()=>({active:false})}')
 assert page.evaluate('JSON.stringify({P,S,QUEST,save:localStorage.getItem("bf_global_offline_demo_v7")})')==guarded
 assert page.evaluate('BFHomeSourceResumeB100.open()') is True
 assert not errors,errors
 browser.close()
print('PASS B100 Home source-scene resume, three widths, exact page/focus, busy/Auto/Repeat gates, full state/save invariance')
