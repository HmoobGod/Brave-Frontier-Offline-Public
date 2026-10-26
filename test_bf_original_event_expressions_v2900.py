"""v29.00 source-native original facial expressions at exact 2022 MSGDRAW frames."""
from pathlib import Path
import shutil,subprocess,sys
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
subprocess.run([sys.executable,str(R/'prepare_original_event_expressions_v2900.py')],check=True)
source=(A/'bf2900_original_event_expressions.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert source.count('/* BF_GLOBAL_ORIGINAL_DIALOGUE_EXPRESSIONS_V2900 */')==1
assert len(source.encode())<65536 and 'BF2900_DATA_PLACEHOLDER' not in source
assert 'localStorage' not in source and 'saveProgress(' not in source
assert java.index('readPackagedText("bf2800_dialogue_speaker_cues.js")')<java.index('readPackagedText("bf2900_original_event_expressions.js")')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
  getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
  removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
  get length(){return Object.keys(db).length}}});
  window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 page.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 page.add_style_tag(path=str(A/'bf_home_nav.css'))
 for n in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
   'bf100_grand_gaia_campaign.js','bf101_story_continue.js','bf110_quest_journal.js',
   'bf2000_story_battle_hud.js','bf2100_battle_command_tray.js',
   'bf2200_original_event_reader.js','bf2300_morgan_event_dialogue.js',
   'bf2400_st_lamia_event_dialogue.js','bf2500_story_event_prompt.js',
   'bf2600_original_event_portraits.js','bf2700_original_event_stage.js',
   'bf2800_dialogue_speaker_cues.js','bf2900_original_event_expressions.js'):
  page.add_script_tag(path=str(A/n))
 assert page.evaluate('BFGlobalEventExpressionsV2900.snapshot().frames')==405
 assert page.evaluate('BFGlobalEventExpressionsV2900.snapshot().scenes')==20
 assert page.evaluate('BFGlobalEventExpressionsV2900.snapshot().sprites')==19
 assert page.evaluate('BFGlobalEventExpressionsV2900.lookup("../evil",1)') is None
 assert page.evaluate('BFGlobalEventExpressionsV2900.lookup("map3-dungeon6.txt",1)') is None
 assert page.locator('#bf2900-expression-note').is_hidden()
 before=page.evaluate('localStorage.getItem("bf_global_offline_demo_v7")')
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.evaluate('()=>{for(const q of QUESTS)P.questClears[q.missionId]=1;renderQuestList()}')
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",20)') is True
 assert page.evaluate('BFGlobalEventExpressionsV2900.refresh().image')=='navi_chara1_4.png'
 assert page.locator('#bf2600-portrait').get_attribute('src')=='content/event/navi_chara1_4.png'
 page.locator('#bf2200-next').click()
 assert page.evaluate('BFGlobalEventExpressionsV2900.refresh().image')=='navi_chara1_3.png'
 assert page.locator('#bf2600-portrait').get_attribute('src')=='content/event/navi_chara1_3.png'
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",240)') is True
 assert page.evaluate('BFGlobalEventExpressionsV2900.refresh().image')=='navi_chara2_2.png'
 for _ in range(8):page.locator('#bf2200-next').click()
 assert page.evaluate('BFGlobalEventExpressionsV2900.refresh().character')=='Seria'
 assert page.locator('#bf2600-portrait').get_attribute('src')=='content/event/navi_chara3_2.png'
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",340)') is True
 assert page.evaluate('BFGlobalEventExpressionsV2900.refresh().image')=='navi_chara1_6.png'
 for _ in range(17):page.locator('#bf2200-next').click()
 assert page.evaluate('BFGlobalEventExpressionsV2900.refresh().image')=='navi_chara3_0.png'
 assert page.locator('#bf2600-portrait').get_attribute('src')=='content/event/navi_chara3_0.png'
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("clear",10)') is True
 assert page.evaluate('BFGlobalEventExpressionsV2900.refresh().image') is None
 assert page.locator('#bf2900-expression-note').is_hidden()
 assert page.evaluate('P.version')==7
 assert page.evaluate('localStorage.getItem("bf_global_offline_demo_v7")')==before
 assert not errors,errors
 browser.close()
print('PASS v29.00 405 source-expression frames, 20 scenes, 19 actual PNG assets, three-region transitions, save isolation')
