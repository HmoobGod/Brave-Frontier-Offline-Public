"""v34.00 source x/y stage metadata across Karl, Seria, Tilith and the native expression reader."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf3400_source_scene_placement.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_SOURCE_SCENE_PLACEMENT_V3400 */')==1
assert len(src.encode('utf8'))<65536 and 'localStorage' not in src and 'saveProgress(' not in src
assert java.index('readPackagedText("bf3300_story_playback.js")')<java.index('readPackagedText("bf3400_source_scene_placement.js")')
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
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
 'bf100_grand_gaia_campaign.js','bf101_story_continue.js','bf110_quest_journal.js',
 'bf2000_story_battle_hud.js','bf2100_battle_command_tray.js',
 'bf2200_original_event_reader.js','bf2300_morgan_event_dialogue.js',
 'bf2400_st_lamia_event_dialogue.js','bf2500_story_event_prompt.js',
 'bf2600_original_event_portraits.js','bf2700_original_event_stage.js',
 'bf2800_dialogue_speaker_cues.js','bf2900_original_event_expressions.js',
 'bf3000_battle_results.js','bf3100_battle_focus.js',
 'bf3200_combat_journal.js','bf3300_story_playback.js',
 'bf3400_source_scene_placement.js'):
  page.add_script_tag(path=str(A/name))
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.evaluate('BFGlobalScenePlacementV3400.snapshot().speaker') is None
 assert page.evaluate('BFGlobalScenePlacementV3400.lookup("Karl").x')==-110
 assert page.evaluate('BFGlobalScenePlacementV3400.lookup("Seria").y')==20
 assert page.evaluate('BFGlobalScenePlacementV3400.lookup("Tilith").x')==60
 assert page.evaluate('BFGlobalScenePlacementV3400.lookup("unknown")') is None
 before=page.evaluate('localStorage.getItem("bf_global_offline_demo_v7")')
 page.evaluate('()=>{P.questClears[12]=1;renderQuestList()}')
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",20)') is True
 a=page.evaluate('BFGlobalScenePlacementV3400.refresh()')
 assert (a['speaker'],a['x'],a['y'],a['side'])==('Tilith',60,30,'right'),a
 assert page.locator('#bf2600-portrait').evaluate('(el)=>el.style.gridColumn')=='2'
 page.evaluate('()=>{for(const q of QUESTS.slice(0,70))P.questClears[q.missionId]=1;renderQuestList()}')
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",240)') is True
 a=page.evaluate('BFGlobalScenePlacementV3400.refresh()')
 assert (a['speaker'],a['x'],a['y'],a['side'])==('Karl',-110,-40,'left'),a
 assert page.locator('#bf2600-portrait').evaluate('(el)=>el.style.gridColumn')=='1'
 for _ in range(8):page.locator('#bf2200-next').click()
 a=page.evaluate('BFGlobalScenePlacementV3400.refresh()')
 assert (a['speaker'],a['x'],a['y'])==('Seria',-50,20),a
 assert 'responsive approximation' in page.locator('#bf3400-position').inner_text()
 assert page.evaluate('localStorage.getItem("bf_global_offline_demo_v7")')==before
 assert not errors,errors
 browser.close()
print('PASS v34.00 source 2022 sprite x/y metadata, correct actor-responsive staging, no saves')
