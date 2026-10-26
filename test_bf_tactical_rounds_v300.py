"""v3.00: six allied actions per planned round, source waves and strict no-save isolation."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf300_tactical_rounds.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert len(js.encode('utf8'))<65536
assert js.count('/* BF_GLOBAL_TACTICAL_ROUNDS_V300 */')==1
assert 'localStorage' not in js and 'saveProgress(' not in js and 'BFAndroid' not in js
assert java.index('readPackagedText("bf250_squad_training.js")')<java.index('readPackagedText("bf300_tactical_rounds.js")')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
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
 assert page.evaluate('QUESTS.length')==106
 assert page.evaluate('BFTacticalRoundsV300.sourceMissions')==21
 assert len(page.evaluate('BFTacticalRoundsV300.clonedSquad'))==6
 assert page.evaluate('BFTacticalRoundsV300.startTrial(200)') is False
 assert page.evaluate('BFTacticalRoundsV300.canStart(1)') is True
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.locator('#bf300-tactics summary').click()
 before=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert page.evaluate('BFTacticalRoundsV300.startTrial(1)') is True
 assert page.locator('#bf300-arena').is_visible()
 state=page.evaluate('BFTacticalRoundsV300.snapshot')
 assert state['phase']=='running'
 assert state['wave']==1 and len(state['party'])==6
 assert len(state['plans'])==6
 assert page.evaluate('BFTacticalRoundsV300.startTrial(1)') is False
 # First wave is just one Mossy and is cleared by six simulated ally actions.
 assert page.evaluate('BFTacticalRoundsV300.stepRound()') is True
 phase=page.evaluate('BFTacticalRoundsV300.snapshot')
 assert phase['rounds']==1
 assert phase['wave']==2
 assert phase['damageDealt']>0 and phase['kills']>=1
 assert page.evaluate('BFTacticalRoundsV300.plan(123456,"attack",0,10011)') is False
 assert page.evaluate('BFTacticalRoundsV300.plan(10011,"cheat",0,10011)') is False
 assert page.evaluate('BFTacticalRoundsV300.plan(10011,"attack",999,10011)') is False
 assert page.evaluate('BFTacticalRoundsV300.plan(10011,"burst",0,10011)') is False
 assert page.evaluate('BFTacticalRoundsV300.autoPlan()') is True
 assert page.evaluate('BFTacticalRoundsV300.snapshot.plans.length')==6
 assert page.locator('#bf300-planner .bf300-planner').count()==6
 assert page.evaluate('BFTacticalRoundsV300.stepRound()') is True
 assert page.evaluate('BFTacticalRoundsV300.snapshot.rounds')==2
 after=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'Tactical turns must never edit P, S, or v7 save'
 # An older isolated training session blocks starting a new tactical trial.
 assert page.evaluate('BFTacticalRoundsV300.exit()') is True
 assert page.evaluate('BFTacticalRoundsV300.snapshot') is None
 assert page.evaluate('BFSquadTrainingV250.start(1)') is True
 assert page.evaluate('BFTacticalRoundsV300.canStart(1)') is False
 page.evaluate('BFSquadTrainingV250.reset()')
 assert page.evaluate('BFTacticalRoundsV300.startTrial(1)') is True
 assert page.evaluate('BFTacticalRoundsV300.exit()') is True
 assert page.locator('#bf300-roster').count()==1
 assert page.evaluate('P.version')==7
 assert not errs,errs
 browser.close()
print('PASS v3.00: 6 allied queued actions, two historical waves, auto plan, source validation and no save writes')
