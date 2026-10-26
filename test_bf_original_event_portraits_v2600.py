"""v26.00 source-verified original Tilith, Karl and Seria art in original story dialogue reader."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
source=(A/'bf2600_original_event_portraits.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert source.count('/* BF_GLOBAL_ORIGINAL_EVENT_PORTRAITS_V2600 */')==1
assert len(source.encode('utf8'))<65536 and 'saveProgress(' not in source and 'localStorage' not in source
assert java.index('readPackagedText("bf2500_story_event_prompt.js")')<java.index('readPackagedText("bf2600_original_event_portraits.js")')
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
    'bf2400_st_lamia_event_dialogue.js','bf2500_story_event_prompt.js',
    'bf2600_original_event_portraits.js'):
  page.add_script_tag(path=str(A/n))
 assert page.evaluate('BFGlobalOriginalEventPortraitsV2600.snapshot.visible') is False
 before=page.evaluate('localStorage.getItem("bf_global_offline_demo_v7")')
 page.evaluate('()=>{for(const q of QUESTS.slice(0,34))P.questClears[q.missionId]=1;renderQuestList()}')
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",20)') is True
 s=page.evaluate('BFGlobalOriginalEventPortraitsV2600.snapshot')
 assert s['character']=='Tilith' and s['options']==['Tilith']
 assert page.locator('#bf2600-portrait').get_attribute('src')=='content/event/navi_chara1_0.png'
 page.evaluate('()=>{for(const q of QUESTS.slice(0,70))P.questClears[q.missionId]=1;renderQuestList()}')
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",240)') is True
 s=page.evaluate('BFGlobalOriginalEventPortraitsV2600.snapshot')
 assert s['character']=='Karl' and s['options']==['Karl','Seria']
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.locator('#bf2600-portrait-controls button').nth(1).click()
 assert page.evaluate('BFGlobalOriginalEventPortraitsV2600.snapshot.character')=='Seria'
 assert page.locator('#bf2600-portrait').get_attribute('src')=='content/event/navi_chara3_0.png'
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("clear",10)') is True
 assert page.evaluate('BFGlobalOriginalEventPortraitsV2600.snapshot.visible') is False
 assert page.evaluate('localStorage.getItem("bf_global_offline_demo_v7")')==before
 assert page.evaluate('P.version')==7
 assert not errors,errors
 browser.close()
print('PASS v26.00 original 2022 event art mapping, speaker switch, v7 save untouched')
