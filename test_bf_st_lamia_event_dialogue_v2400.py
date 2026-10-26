"""v24.00 source-backed original St Lamia dialogues, 350 ambiguity excluded and save v7."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf2400_st_lamia_event_dialogue.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_2022_ST_LAMIA_EVENT_DIALOGUE_V2400 */')==1
assert len(src.encode('utf8'))<65536 and 'localStorage' not in src
assert java.index('readPackagedText("bf2300_morgan_event_dialogue.js")')<java.index('readPackagedText("bf2400_st_lamia_event_dialogue.js")')
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
    'bf2200_original_event_reader.js','bf2300_morgan_event_dialogue.js',
    'bf2400_st_lamia_event_dialogue.js'):
  page.add_script_tag(path=str(A/name))
 assert page.evaluate('BFGlobalOriginalEventsV2200.count')==23
 assert page.evaluate('BFGlobalOriginalEventsV2200.lineCount')==410
 assert page.evaluate('BFStLamiaEventDialogueV2400.lineCount')==117
 assert page.evaluate('BFStLamiaEventDialogueV2400.skippedDungeonId')==350
 assert page.evaluate('BFGlobalOriginalEventsV2200.lookup("dungeon",350)') is None
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",300)') is False
 before=page.evaluate('localStorage.getItem("bf_global_offline_demo_v7")')
 page.evaluate('()=>{for(const q of QUESTS.slice(0,70))P.questClears[q.missionId]=1;renderQuestList()}')
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",300)') is True
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert 'Volcano Eldent' in page.locator('#bf2200-title').inner_text()
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",360)') is False
 page.evaluate('()=>{for(const q of QUESTS)P.questClears[q.missionId]=1;renderQuestList()}')
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",360)') is True
 assert page.evaluate('BFGlobalOriginalEventsV2200.snapshot().lines')==13
 assert page.evaluate('BFGlobalOriginalEventsV2200.lookup("dungeon",340).lines.length')==44
 assert page.evaluate('P.version')==7
 assert page.evaluate('localStorage.getItem("bf_global_offline_demo_v7")')==before
 assert not errors,errors
 browser.close()
print('PASS v24.00 6 St Lamia original scenes 117 frames, strict 350 exclusion and v7 safe')
