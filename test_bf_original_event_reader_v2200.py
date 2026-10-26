"""v22.00 verified 2022 original source dialogue reader, progression gates, save isolation."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf2200_original_event_reader.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_2022_EVENT_READER_V2200 */')==1
assert len(src.encode('utf8'))<65536
assert 'localStorage' not in src and 'saveProgress(' not in src
assert java.index('readPackagedText("bf2100_battle_command_tray.js")')<java.index('readPackagedText("bf2200_original_event_reader.js")')
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
 assert page.evaluate('P.version')==7
 assert page.evaluate('BFGlobalOriginalEventsV2200.count')==10
 assert page.evaluate('BFGlobalOriginalEventsV2200.lineCount')==128
 assert page.evaluate('BFGlobalOriginalEventsV2200.snapshot().available')==0
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("clear",10)') is False
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",80)') is False
 assert page.locator('#bf2200-reader').is_hidden()
 before=page.evaluate("""()=>({p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.evaluate('()=>{P.questClears[12]=1;renderQuestList()}')
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",20)') is True
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.locator('#bf2200-reader').is_visible()
 assert "It's so hot!" in page.locator('#bf2200-text').inner_text()
 assert page.locator('#bf2200-prev').is_disabled()
 page.locator('#bf2200-next').click()
 assert page.evaluate('BFGlobalOriginalEventsV2200.snapshot().step')==2
 assert 'Summoner' in page.locator('#bf2200-text').inner_text()
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("clear",10)') is False
 page.evaluate('()=>{P.questClears[10]=1;renderQuestList()}')
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("clear",10)') is True
 assert 'Farm' in page.locator('#bf2200-text').inner_text()
 assert page.evaluate('BFGlobalOriginalEventsV2200.snapshot().lines')==1
 assert page.locator('#bf2200-next').is_disabled()
 # All dialogue keys unlock only via existing quest requirements; no bypass.
 page.evaluate('()=>{for(const q of QUESTS.slice(0,34))P.questClears[q.missionId]=1;renderQuestList()}')
 assert page.evaluate('BFGlobalOriginalEventsV2200.snapshot().available')==10
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",80)') is True
 assert 'Tower of Mistral' in page.locator('#bf2200-title').inner_text()
 assert page.evaluate('BFGlobalOriginalEventsV2200.lookup("dungeon",80).lines.length')==10
 assert page.evaluate('BFGlobalOriginalEventsV2200.read("dungeon",999)') is False
 assert page.evaluate('P.version')==7
 saved=page.evaluate('localStorage.getItem("bf_global_offline_demo_v7")')
 assert saved==before['save'],'Reader must never auto-save or grant rewards'
 assert not errors,errors
 browser.close()
print('PASS v22.00 10 original 2022 event scripts, 128 text frames, Mistral unlocks and no save writes')
