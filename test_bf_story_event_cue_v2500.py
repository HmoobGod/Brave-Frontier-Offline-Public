"""v25.00 source-aware original story cue on real demo mission completion, non-mutating."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf2500_story_event_prompt.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_STORY_EVENT_CUE_V2500 */')==1
assert len(src.encode('utf8'))<65536
assert 'saveProgress(' not in src and 'localStorage' not in src
assert java.index('readPackagedText("bf2400_st_lamia_event_dialogue.js")')<java.index('readPackagedText("bf2500_story_event_prompt.js")')
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
 assert page.evaluate('BFGlobalStoryEventCueV2500.snapshot()') is None
 assert page.locator('#bf2500-cue').is_hidden()
 assert page.evaluate('BFGlobalStoryEventCueV2500.open()') is False
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 # Original actual quest selection handler and source-dungeon authorization.
 page.evaluate('()=>{P.questClears[12]=1;renderQuestList()}')
 assert page.evaluate('BFQuestAreas.choose(QUESTS.find(q=>q.missionId===20))') is True
 s=page.evaluate('BFGlobalStoryEventCueV2500.refresh()')
 assert s['kind']=='dungeon' and s['id']==20,s
 assert page.locator('#bf2500-cue').is_visible()
 before=page.evaluate('localStorage.getItem("bf_global_offline_demo_v7")')
 page.locator('#bf2500-read').click()
 assert page.evaluate('BFGlobalOriginalEventsV2200.snapshot().chosen')=='dungeon:20'
 assert page.evaluate('localStorage.getItem("bf_global_offline_demo_v7")')==before
 assert page.evaluate('BFGlobalStoryEventCueV2500.dismiss()') is True
 assert page.locator('#bf2500-cue').is_hidden()
 # A completed original quest-clear ID surfaces its exact archived event message.
 page.evaluate("""()=>{P.questClears[2]=1;renderQuestList();S.busy=false;if(!BFQuestAreas.choose(QUESTS.find(q=>q.missionId===10)))throw Error("Mission 10 not selected");P.questClears[10]=1;S.over=true;S.phase="Victory";renderQuestList()}""")
 s=page.evaluate('BFGlobalStoryEventCueV2500.refresh()')
 assert s['kind']=='clear' and s['id']==10,s
 clear_saved=page.evaluate('localStorage.getItem("bf_global_offline_demo_v7")')
 assert page.evaluate('BFGlobalStoryEventCueV2500.open()') is True
 assert 'Farm' in page.locator('#bf2200-text').inner_text()
 assert page.evaluate('localStorage.getItem("bf_global_offline_demo_v7")')==clear_saved
 page.locator('#mode').select_option('training')
 assert page.evaluate('BFGlobalStoryEventCueV2500.refresh()') is None
 assert page.evaluate('P.version')==7
 assert not errors,errors
 browser.close()
print('PASS v25.00 source-backed original clear/dungeon prompts, no save mutation')
