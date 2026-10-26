"""v27.00 - exact 2022 source event JPG joins, actual archived scene reader, save isolation."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf2700_original_event_stage.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_ORIGINAL_EVENT_STAGE_V2700 */')==1
assert len(src.encode('utf8'))<65536
assert 'localStorage' not in src and 'saveProgress(' not in src
assert java.index('readPackagedText("bf2600_original_event_portraits.js")')<java.index('readPackagedText("bf2700_original_event_stage.js")')
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
  'bf2600_original_event_portraits.js','bf2700_original_event_stage.js'):
   page.add_script_tag(path=str(A/n))
 assert page.evaluate('BFOriginalEventStageV2700.snapshot().count')==20
 assert page.locator('#bf2700-stage').is_hidden()
 assert page.evaluate('BFOriginalEventStageV2700.backgroundFor("map3-dungeon6.txt")') is None
 assert page.evaluate('BFOriginalEventStageV2700.backgroundFor("../evil")') is None
 # Script filenames link to the original archived backgrounds for every region.
 for name,background in (
   ('map1-dungeon1.txt','dungeon_battle_10200.jpg'),
   ('map1-dungeon7.txt','dungeon_battle_10800.jpg'),
   ('map2-dungeon1.txt','dungeon_battle_20100.jpg'),
   ('map2-dungeon7.txt','dungeon_battle_20700.jpg'),
   ('map3-dungeon1.txt','dungeon_battle_30100.jpg'),
   ('map3-dungeon7.txt','dungeon_battle_30700.jpg')):
  assert page.evaluate('(s)=>BFOriginalEventStageV2700.backgroundFor(s)',name)==background
 before=page.evaluate('localStorage.getItem("bf_global_offline_demo_v7")')
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.evaluate('()=>{P.questClears[12]=1;renderQuestList()}')
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",20)') is True
 assert page.evaluate('BFOriginalEventStageV2700.refresh().background')=='dungeon_battle_10200.jpg'
 assert page.locator('#bf2700-art').get_attribute('src')=='content/dungeon/dungeon_battle_10200.jpg'
 assert page.locator('#bf2700-stage').is_visible()
 page.evaluate('()=>{P.questClears[23]=1;renderQuestList()}')
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",30)') is True
 assert page.evaluate('BFOriginalEventStageV2700.refresh().background')=='dungeon_battle_10300.jpg'
 assert page.locator('#bf2700-art').get_attribute('src')=='content/dungeon/dungeon_battle_10300.jpg'
 assert page.locator('#bf2700-stage').is_visible()
 page.locator('#bf2200-next').click()
 assert page.evaluate('BFOriginalEventStageV2700.snapshot().step')==2
 assert page.locator('#bf2700-stage-caption').inner_text().endswith('Frame 2')
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("clear",10)') is False
 page.evaluate('()=>{for(const q of QUESTS)P.questClears[q.missionId]=1;renderQuestList()}')
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",200)') is True
 assert page.evaluate('BFOriginalEventStageV2700.refresh().background')=='dungeon_battle_20100.jpg'
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",360)') is True
 assert page.evaluate('BFOriginalEventStageV2700.refresh().background')=='dungeon_battle_30700.jpg'
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("clear",10)') is True
 assert page.evaluate('BFOriginalEventStageV2700.refresh().available') is False
 assert page.locator('#bf2700-stage').is_hidden()
 assert page.evaluate('P.version')==7
 assert page.evaluate('localStorage.getItem("bf_global_offline_demo_v7")')==before
 assert not errors,errors
 browser.close()
print('PASS v27.00 exact source event background joins 20/20, read-only reader, three regions, v7 save unchanged')
