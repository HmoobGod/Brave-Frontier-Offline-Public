"""v23.00 Morgan original 2022 event texts, ordered unlocked quest reader and v7 safety."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
source=(A/'bf2300_morgan_event_dialogue.js').read_text('utf8')
reader=(A/'bf2200_original_event_reader.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert source.count('/* BF_GLOBAL_2022_MORGAN_EVENT_DIALOGUE_V2300 */')==1
assert len(source.encode('utf8'))<65536 and 'localStorage' not in source
assert 'registerSupplemental(s)' in reader
assert java.index('readPackagedText("bf2200_original_event_reader.js")')<java.index('readPackagedText("bf2300_morgan_event_dialogue.js")')
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
    'bf100_grand_gaia_campaign.js','bf101_story_continue.js','bf110_quest_journal.js',
    'bf2000_story_battle_hud.js','bf2100_battle_command_tray.js',
    'bf2200_original_event_reader.js','bf2300_morgan_event_dialogue.js'):
  page.add_script_tag(path=str(A/name))
 assert page.evaluate('BFGlobalOriginalEventsV2200.count')==17
 assert page.evaluate('BFMorganEventDialogueV2300.lineCount')==165
 assert page.evaluate('BFGlobalOriginalEventsV2200.lineCount')==293
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",200)') is False
 assert page.evaluate("""()=>BFGlobalOriginalEventsV2200.registerSupplemental({
   kind:'dungeon',id:200,title:'Duplicate',name:'map2-dungeon1.txt',lines:['x']})""") is False
 assert page.evaluate("""()=>BFGlobalOriginalEventsV2200.registerSupplemental({
   kind:'dungeon',id:270,title:'Unknown',name:'map2-dungeon8.txt',lines:['x']})""") is False
 before=page.evaluate('localStorage.getItem("bf_global_offline_demo_v7")')
 page.evaluate('()=>{for(const q of QUESTS.slice(0,34))P.questClears[q.missionId]=1;renderQuestList()}')
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",200)') is True
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert 'Kagan Desert' in page.locator('#bf2200-title').inner_text()
 assert 'Summoner' in page.locator('#bf2200-text').inner_text()
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",260)') is False
 page.evaluate('()=>{for(const q of QUESTS.slice(0,70))P.questClears[q.missionId]=1;renderQuestList()}')
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",260)') is True
 assert page.evaluate('BFGlobalOriginalEventsV2200.snapshot().lines')==49
 assert page.evaluate('BFGlobalOriginalEventsV2200.lookup("dungeon",240).lines.length')==31
 assert page.evaluate('P.version')==7
 assert page.evaluate('localStorage.getItem("bf_global_offline_demo_v7")')==before
 assert not errors,errors
 browser.close()
print('PASS v23.00 Morgan 7 originals, 165 frames, unlocks and v7 isolation')
