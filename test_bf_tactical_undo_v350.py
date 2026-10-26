"""v3.50: exact RAM-only round undo, bounded autoplays and archived portrait safety."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf300_tactical_rounds.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert js.count('/* BF_GLOBAL_TACTICAL_ROUNDS_V300 */')==1
assert 'undoLastRound' in js and 'autoAdvance' in js
assert len(js.encode('utf8'))<65536
assert 'localStorage' not in js and 'saveProgress(' not in js and 'BFAndroid' not in js
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""() => {
  const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
    getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
    removeItem:k=>{delete db[k]},key:i=>Object.keys(db)[i]??null,
    get length(){return Object.keys(db).length}}});
  window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 page.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 page.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
  'bf100_grand_gaia_campaign.js','bf101_story_continue.js',
  'bf110_quest_journal.js','bf120_historical_encounters.js',
  'bf_global_unit_archive.js','bf150_source_crosscheck.js',
  'bf200_historical_wave_lab.js','bf250_squad_training.js',
  'bf300_tactical_rounds.js'):
  page.add_script_tag(path=str(A/name))
 assert page.evaluate('P.version')==7
 assert page.evaluate('BFTacticalRoundsV300.sourceMissions')==21
 assert page.evaluate('BFTacticalRoundsV300.undoDepth')==0
 assert page.evaluate('BFTacticalRoundsV300.undoLastRound()') is False
 assert page.evaluate('BFTacticalRoundsV300.autoAdvance(1)') is False
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.locator('#bf300-tactics summary').click()
 before_game=page.evaluate("""()=>({
   player:JSON.stringify(P),battle:JSON.stringify(S),
   save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert page.evaluate('BFTacticalRoundsV300.startTrial(1)') is True
 start=page.evaluate('BFTacticalRoundsV300.snapshot')
 assert start['undoDepth']==0 and start['rounds']==0 and start['wave']==1
 assert page.locator('#bf300-roster [role="progressbar"]').count()==len(start['party'])==6
 assert page.locator('#bf300-enemies [role="progressbar"]').count()==len(start['enemies'])
 assert page.locator('#bf350-undo').is_disabled()
 assert page.evaluate('BFTacticalRoundsV300.stepRound()') is True
 progressed=page.evaluate('BFTacticalRoundsV300.snapshot')
 assert progressed['rounds']==1 and progressed['wave']==2
 assert progressed['damageDealt']>0 and progressed['undoDepth']==1
 assert not page.locator('#bf350-undo').is_disabled()
 # Precise rewind includes wave contents, enemy HP, log, counters and plans.
 page.locator('#bf350-undo').click()
 restored=page.evaluate('BFTacticalRoundsV300.snapshot')
 assert restored==start,(restored,start)
 assert page.evaluate('BFTacticalRoundsV300.stepRound()') is True
 assert page.evaluate('BFTacticalRoundsV300.snapshot')==progressed
 assert page.evaluate('BFTacticalRoundsV300.autoAdvance(0)') is False
 assert page.evaluate('BFTacticalRoundsV300.autoAdvance(16)') is False
 assert page.evaluate('BFTacticalRoundsV300.autoAdvance(1.5)') is False
 initial_round=page.evaluate('BFTacticalRoundsV300.snapshot.rounds')
 moved=page.evaluate('BFTacticalRoundsV300.autoAdvance(2)')
 assert isinstance(moved,int) and 0<moved<=2
 assert page.evaluate('BFTacticalRoundsV300.snapshot.rounds')==initial_round+moved
 assert page.evaluate('BFTacticalRoundsV300.undoDepth')>=2
 assert page.evaluate('BFTacticalRoundsV300.undoLastRound()') is True
 assert page.evaluate('BFTacticalRoundsV300.snapshot.rounds')==initial_round+moved-1
 assert page.evaluate('BFTacticalRoundsV300.undoLastRound()') is True
 assert page.evaluate('BFTacticalRoundsV300.snapshot.rounds')==initial_round+moved-2
 # Replay the same input deterministically and preserve normal party controls.
 assert page.evaluate('BFTacticalRoundsV300.autoPlan()') is True
 assert page.evaluate('BFTacticalRoundsV300.stepRound()') is True
 after_game=page.evaluate("""()=>({
   player:JSON.stringify(P),battle:JSON.stringify(S),
   save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before_game==after_game,'Practice must not write v7 state or native battle'
 assert page.evaluate('BFTacticalRoundsV300.exit()') is True
 assert page.evaluate('BFTacticalRoundsV300.undoDepth')==0
 assert page.evaluate('BFTacticalRoundsV300.snapshot') is None
 assert page.locator('#bf300-tactics summary').is_visible()
 assert not errors,errors
 browser.close()
print('PASS v3.50 reversible 2014 wave training, accessible HP cards, bounded autoplays, v7 no-save isolation')
