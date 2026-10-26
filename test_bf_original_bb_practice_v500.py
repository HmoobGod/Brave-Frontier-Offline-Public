"""v5.00: recovered original Global Brave Burst trial and save isolation."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,shutil
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
s=(A/'bf500_source_bb_evidence.js').read_text('utf8')
t=(A/'bf300_tactical_rounds.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert len(s.encode())<65536 and len(t.encode())<65536
assert s.count('/* BF_GLOBAL_SOURCE_BB_EVIDENCE_V500 */')==1
assert 'localStorage' not in s+t and 'saveProgress(' not in s+t
assert java.index('readPackagedText("bf500_source_bb_evidence.js")')<java.index('readPackagedText("bf300_tactical_rounds.js")')
power=json.loads((R/'source_data/bf_global_original_bb_power_v030.json').read_text('utf8'))
support=json.loads((R/'source_data/bf_global_original_bb_support_v029.json').read_text('utf8'))
assert len(power['skills'])==24 and len(support['skills'])==6
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
 for n in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
  'bf100_grand_gaia_campaign.js','bf101_story_continue.js',
  'bf110_quest_journal.js','bf120_historical_encounters.js',
  'bf_global_unit_archive.js','bf150_source_crosscheck.js',
  'bf200_historical_wave_lab.js','bf250_squad_training.js',
  'bf500_source_bb_evidence.js','bf300_tactical_rounds.js',
  'bf400_original_battle_dossier.js'):
  page.add_script_tag(path=str(A/n))
 assert page.evaluate('P.version')==7
 assert page.evaluate('BFOriginalBBV500.count')==30
 assert page.evaluate('BFOriginalBBV500.offensiveCount')==24
 assert page.evaluate('BFOriginalBBV500.supportCount')==6
 assert page.evaluate('BFTacticalRoundsV300.sourceMissions')==21
 for id,item in power['skills'].items():
  observed=page.evaluate('(id)=>BFOriginalBBV500.get(id)',int(id))
  assert observed['name']==item['name'],id
  assert observed['target']==item['target'],id
  assert observed['pct']==item['levels'][0]['damageModifierPct'],id
 for id,item in support['skills'].items():
  observed=page.evaluate('(id)=>BFOriginalBBV500.get(id)',int(id))
  assert observed['name']==item['name'],id
  assert observed['kind']==item['level1DemoEffect']['type'],id
 assert page.evaluate('BFOriginalBBV500.get(10011).name')=='Flare Ride'
 assert page.evaluate('BFOriginalBBV500.get(20041).low')==600
 assert page.evaluate('BFOriginalBBV500.get(40021).pct')==30
 assert page.evaluate('BFOriginalBBV500.get(999999)') is None
 page.evaluate('BFOriginalBBV500.get(10011).pct=999')
 assert page.evaluate('BFOriginalBBV500.get(10011).pct')==30
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.locator('#bf300-tactics > summary').click()
 before=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert page.evaluate('BFTacticalRoundsV300.startTrial(1)') is True
 assert page.evaluate('BFTacticalRoundsV300.snapshot.sourceBBCount')==30
 assert page.evaluate('BFTacticalRoundsV300.snapshot.party[0].sourceSkill')=='Flare Ride'
 assert page.evaluate('BFTacticalRoundsV300.plan(10011,"sourcebb",0,10011)') is False
 # Guard five allies so Vargas charges over two normal turns.
 for _ in range(2):
  snap=page.evaluate('BFTacticalRoundsV300.snapshot')
  for unit in snap['party'][1:]:
   assert page.evaluate('(id)=>BFTacticalRoundsV300.plan(id,"guard",0,id)',unit['sourceId']) is True
  assert page.evaluate('BFTacticalRoundsV300.stepRound()') is True
 assert page.evaluate('BFTacticalRoundsV300.snapshot.party[0].burst')==2
 assert page.evaluate('BFTacticalRoundsV300.snapshot.wave')==2
 assert page.evaluate('BFTacticalRoundsV300.plan(10011,"sourcebb",0,10011)') is True
 assert page.evaluate('BFTacticalRoundsV300.snapshot.plans[0].kind')=='sourcebb'
 before_bb=page.evaluate('BFTacticalRoundsV300.snapshot')
 assert page.evaluate('BFTacticalRoundsV300.stepRound()') is True
 after_bb=page.evaluate('BFTacticalRoundsV300.snapshot')
 assert any('Flare Ride' in x and 'all_enemies' in x for x in after_bb['recent'])
 assert after_bb['party'][0]['burst']==0
 assert after_bb['damageDealt']>before_bb['damageDealt']
 assert page.evaluate('BFTacticalRoundsV300.undoLastRound()') is True
 assert page.evaluate('BFTacticalRoundsV300.snapshot')==before_bb
 assert page.evaluate('BFTacticalRoundsV300.autoPlan()') is True
 assert page.evaluate('BFTacticalRoundsV300.snapshot.plans[0].kind')=='sourcebb'
 after=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'Original-skill practice cannot change native battle or v7 save'
 assert page.evaluate('BFTacticalRoundsV300.exit()') is True
 assert not errors,errors
 browser.close()
print('PASS v5.00: 30 recovered Global source BB forms, named Lv1 practice, auto-plan, undo and no original save changes')
