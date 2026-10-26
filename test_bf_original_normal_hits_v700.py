"""v7.00 original 2022 attack-hit timing/weight reference with synthetic hit breakdown."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,shutil
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
evidence=(A/'bf700_original_normal_hits.js').read_text('utf8')
trial=(A/'bf300_tactical_rounds.js').read_text('utf8')
assert len(evidence.encode())<65536 and len(trial.encode())<65536
assert 'localStorage' not in evidence+trial and 'saveProgress(' not in evidence+trial
assert 'BFOriginalHitSequenceV700' in evidence and 'hitEvents' in trial
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf700_original_normal_hits.js")')<java.index('readPackagedText("bf300_tactical_rounds.js")')
source=json.loads((R/'source_data/bf_global_playable_attack_frames_v061.json').read_text('utf8'))
assert len(source['rows'])==72
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
   'bf500_source_bb_evidence.js','bf700_original_normal_hits.js',
   'bf300_tactical_rounds.js','bf400_original_battle_dossier.js'):
  page.add_script_tag(path=str(A/name))
 assert page.evaluate('P.version')==7 and page.evaluate('QUESTS.length')==106
 assert page.evaluate('BFOriginalHitSequenceV700.sourceRows')==72
 assert page.evaluate('BFOriginalHitSequenceV700.eligible')==71
 assert page.evaluate('BFOriginalHitSequenceV700.excluded')==1
 assert page.evaluate('BFOriginalHitSequenceV700.get(10023)') is None
 assert page.evaluate('BFOriginalHitSequenceV700.get(999999)') is None
 for rec in source['rows']:
  pairs=[[int(x) for x in seg.split(':')[:2]] for seg in rec['damageFrames'].split(',')]
  actual=page.evaluate('(id)=>BFOriginalHitSequenceV700.get(id)',rec['unitId'])
  if rec['unitId']==10023:
   assert sum(p[1] for p in pairs)==130 and actual is None
  else:
   assert sum(p[1] for p in pairs)==100 and actual==pairs,rec['unitId']
 page.evaluate('BFOriginalHitSequenceV700.get(10011)[0][1]=999')
 assert page.evaluate('BFOriginalHitSequenceV700.get(10011)[0][1]')==50
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.locator('#bf300-tactics > summary').click()
 before=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert page.evaluate('BFTacticalRoundsV300.startTrial(1)') is True
 initial=page.evaluate('BFTacticalRoundsV300.snapshot')
 assert initial['sourceHitCoverage']==71 and initial['hitEvents']==[]
 for u in initial['party'][1:]:
  assert page.evaluate('(id)=>BFTacticalRoundsV300.plan(id,"guard",0,id)',u['sourceId'])
 planned=page.evaluate('BFTacticalRoundsV300.snapshot')
 assert page.evaluate('BFTacticalRoundsV300.stepRound()') is True
 progressed=page.evaluate('BFTacticalRoundsV300.snapshot')
 assert len(progressed['hitEvents'])==1
 hit=progressed['hitEvents'][0]
 assert hit['sourceId']==10011 and hit['unitId']==10011
 assert [(v['frame'],v['weight']) for v in hit['events']]==[(26,50),(44,30),(62,20)]
 assert sum(v['damage'] for v in hit['events'])==hit['total']==300
 assert progressed['damageDealt']>=300
 assert page.locator('#bf700-hit-report .bf700-hit-cell').count()==3
 assert 'Frame 26' in page.locator('#bf700-hit-report').inner_text()
 assert page.evaluate('BFTacticalRoundsV300.undoLastRound()') is True
 assert page.evaluate('BFTacticalRoundsV300.snapshot')==planned
 assert page.locator('#bf700-hit-report .bf700-hit-cell').count()==0
 assert page.evaluate('BFTacticalRoundsV300.stepRound()') is True
 assert page.evaluate('BFTacticalRoundsV300.snapshot')==progressed
 after=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'2022 attack evidence is only a read-only practice overlay'
 assert page.evaluate('BFTacticalRoundsV300.exit()') is True
 assert not errors,errors
 browser.close()
print('PASS v7.00 source-exact 71 hit sequences, malformed weight excluded, live timeline and undo and save isolation')
