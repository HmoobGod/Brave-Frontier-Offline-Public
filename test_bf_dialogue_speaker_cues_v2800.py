"""v28.00 original 2022 per-line speakers automatically set source-art portrait."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf2800_dialogue_speaker_cues.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_SOURCE_SPEAKER_CUES_V2800 */')==1
assert len(src.encode('utf8'))<65536
assert 'localStorage' not in src and 'saveProgress(' not in src
assert java.index('readPackagedText("bf2700_original_event_stage.js")')<java.index('readPackagedText("bf2800_dialogue_speaker_cues.js")')
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
  'bf2800_dialogue_speaker_cues.js'):
  page.add_script_tag(path=str(A/n))
 assert page.evaluate('BFGlobalDialogueSpeakerV2800.snapshot().supportedScenes')==20
 assert page.evaluate('BFGlobalDialogueSpeakerV2800.lookup("map3-dungeon6.txt",1)') is None
 assert page.evaluate('BFGlobalDialogueSpeakerV2800.lookup("../foo",1)') is None
 before=page.evaluate('localStorage.getItem("bf_global_offline_demo_v7")')
 page.evaluate('()=>{for(const q of QUESTS.slice(0,70))P.questClears[q.missionId]=1;renderQuestList()}')
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",240)') is True
 assert page.evaluate('BFGlobalDialogueSpeakerV2800.refresh().character')=='Karl'
 assert page.evaluate('BFGlobalOriginalEventPortraitsV2600.snapshot.character')=='Karl'
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 for _ in range(8):page.locator('#bf2200-next').click()
 assert page.evaluate('BFGlobalDialogueSpeakerV2800.snapshot().step')==9
 assert page.evaluate('BFGlobalDialogueSpeakerV2800.refresh().character')=='Seria'
 assert page.evaluate('BFGlobalOriginalEventPortraitsV2600.snapshot.character')=='Seria'
 for _ in range(3):page.locator('#bf2200-next').click()
 assert page.evaluate('BFGlobalDialogueSpeakerV2800.snapshot().step')==12
 assert page.evaluate('BFGlobalDialogueSpeakerV2800.refresh().character')=='Karl'
 assert page.evaluate('BFGlobalOriginalEventPortraitsV2600.snapshot.character')=='Karl'
 page.evaluate('()=>{for(const q of QUESTS)P.questClears[q.missionId]=1;renderQuestList()}')
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",340)') is True
 assert page.evaluate('BFGlobalDialogueSpeakerV2800.refresh().character')=='Tilith'
 for _ in range(17):page.locator('#bf2200-next').click()
 assert page.evaluate('BFGlobalDialogueSpeakerV2800.snapshot().step')==18
 assert page.evaluate('BFGlobalDialogueSpeakerV2800.refresh().character')=='Seria'
 assert page.evaluate('BFGlobalOriginalEventPortraitsV2600.snapshot.character')=='Seria'
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("clear",10)') is True
 assert page.evaluate('BFGlobalDialogueSpeakerV2800.refresh().character') is None
 assert page.evaluate('localStorage.getItem("bf_global_offline_demo_v7")')==before
 assert page.evaluate('P.version')==7
 assert not errors,errors
 browser.close()
print('PASS v28.00 20 source-verified dialogues, automatic native speaker portraits at exact dialogue lines, save v7')
