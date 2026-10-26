"""v2.50 safe, unit-based six-member squad training (never writes original game)."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf250_squad_training.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert js.count('/* BF_GLOBAL_SQUAD_TRAINING_V250 */')==1
assert len(js.encode('utf8'))<65536
assert 'localStorage' not in js and 'saveProgress(' not in js and 'BFAndroid' not in js
assert java.index('readPackagedText("bf200_historical_wave_lab.js")')<java.index('readPackagedText("bf250_squad_training.js")')
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
 for n in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
   'bf100_grand_gaia_campaign.js','bf101_story_continue.js',
   'bf110_quest_journal.js','bf120_historical_encounters.js',
   'bf_global_unit_archive.js','bf150_source_crosscheck.js',
   'bf200_historical_wave_lab.js','bf250_squad_training.js'):
  page.add_script_tag(path=str(A/n))
 assert page.evaluate('P.version')==7
 assert page.evaluate('QUESTS.length')==106
 assert page.evaluate('BFSquadTrainingV250.sourceQuests')==21
 snap=page.evaluate('BFSquadTrainingV250.squadSnapshot')
 assert len(snap)==6
 assert [u['sourceId'] for u in snap]==page.evaluate('P.squad')
 assert all(u['baseHp']>0 and u['atk']>0 and u['rec']>0 for u in snap)
 assert page.evaluate('BFSquadTrainingV250.canStart(200)') is False
 assert page.evaluate('BFSquadTrainingV250.start(200)') is False
 # Open the actual Quest screen and the collapsible squad lab before
 # selecting an acting unit through a real visible Playwright control.
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.locator('#bf250-squad summary').click()
 before=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert page.evaluate('BFSquadTrainingV250.start(1)') is True
 assert page.locator('#bf250-actor').is_visible()
 training=page.evaluate('BFSquadTrainingV250.training')
 assert len(training['party'])==6
 assert training['wave']==1 and training['missionId']==1
 assert page.evaluate('BFSquadTrainingV250.action("burst")') is False
 # User-selected actor must remain selected after a controls refresh.
 page.locator('#bf250-actor').select_option('20011')
 assert page.locator('#bf250-actor').input_value()=='20011'
 assert page.evaluate('BFSquadTrainingV250.action("attack")') is True
 assert page.evaluate("""()=>BFSquadTrainingV250.training.party.find(
    u=>u.sourceId===20011).burst""")==1
 assert page.evaluate('BFSquadTrainingV250.training.turns')==1
 assert page.evaluate('BFSquadTrainingV250.autoTurn()') is True
 # Duplicate IDs must have distinct wave indices in target selector.
 page.evaluate('BFSquadTrainingV250.reset()')
 assert page.evaluate('BFSquadTrainingV250.start(1)') is True
 page.evaluate("""() => {for(let i=0;i<8 && BFSquadTrainingV250.training.wave<2;i++)
    BFSquadTrainingV250.action('attack');}""")
 assert page.evaluate('BFSquadTrainingV250.training.wave')>=2
 assert page.locator('#bf250-enemy option').count()>=1
 after=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'Training cannot modify original battle, save or roster'
 # Mutation of real squad externally cannot mutate existing practice clone.
 retained=page.evaluate('BFSquadTrainingV250.training.party.map(x=>x.sourceId)')
 page.evaluate('()=>{P.squad=[10011];P.roster=[10011];}')
 assert page.evaluate('BFSquadTrainingV250.training.party.map(x=>x.sourceId)')==retained
 assert page.evaluate('BFSquadTrainingV250.reset()') is True
 assert page.evaluate('BFSquadTrainingV250.training') is None
 assert len(page.evaluate('BFSquadTrainingV250.squadSnapshot'))==1
 page.evaluate("""() => {P.squad=[10011,20011,30011,40011,50011,60011];
 P.roster=[10011,20011,30011,40011,50011,60011];}""")
 # Test directly changed P without passing through normal Units navigation,
 # so explicitly redraw the read-only snapshot before inspecting its cards.
 page.evaluate('BFSquadTrainingV250.refresh()')
 assert page.locator('#bf250-squad').is_visible()
 assert page.locator('#bf250-mission option').count()==21
 assert page.locator('#bf250-copied .bf250-member').count()==6
 page.locator('#bf250-mission').select_option('200')
 assert page.locator('#bf250-start').is_disabled()
 assert page.evaluate('P.version')==7
 assert not errs,errs
 browser.close()
print('PASS v2.50: six owned archived source units, practice UI and no original game/save mutation')
