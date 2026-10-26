"""v19.00: same 2014 enemy, before/after original 2022 squad bounded synthetic auto-trial."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf1900_evolution_ab.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_EVOLUTION_AB_TRIALS_V1900 */')==1
assert len(src.encode('utf8'))<65536
assert 'localStorage' not in src and 'saveProgress(' not in src
assert java.index('readPackagedText("bf1800_multistage_draft.js")')<java.index('readPackagedText("bf1900_evolution_ab.js")')
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
  'bf500_source_bb_evidence.js','bf700_original_normal_hits.js',
  'bf300_tactical_rounds.js','bf400_original_battle_dossier.js',
  'bf800_archive_draft.js','bf900_optional_labs_hub.js',
  'bf1000_original_evolution_paths.js','bf1400_evolution_material_planner.js',
  'bf1500_evolution_chain.js','bf1600_draft_evolution.js',
  'bf1700_batch_draft_evolution.js','bf1800_multistage_draft.js',
  'bf1900_evolution_ab.js'):
  page.add_script_tag(path=str(A/n))
 assert page.evaluate('P.version')==7 and page.evaluate('BFGlobalUnitArchive.count')==2291
 assert page.evaluate('BFGlobalEvolutionABV1900.result') is None
 assert page.evaluate('BFGlobalEvolutionABV1900.ready') is False
 assert page.evaluate('BFGlobalEvolutionABV1900.run(5)') is None
 for first,last in [(10011,10013),(10021,10023)]:
  assert page.evaluate('(id)=>BFArchiveDraftV800.add(id)',first) is True
  assert page.evaluate('([a,b])=>BFGlobalMultistageDraftV1800.choose(a,b)',[first,last]) is True
 assert page.evaluate('BFGlobalEvolutionABV1900.ready') is True
 assert page.evaluate('BFGlobalEvolutionABV1900.run(0)') is None
 assert page.evaluate('BFGlobalEvolutionABV1900.run(6)') is None
 assert page.evaluate('BFGlobalEvolutionABV1900.run(1.1)') is None
 before=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
  saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 party=page.evaluate('BFArchiveDraftV800.selected')
 depth=page.evaluate('BFGlobalDraftEvolutionV1600.history.length')
 result=page.evaluate('BFGlobalEvolutionABV1900.run(1)')
 assert result is not None
 assert result['originalYear']==2022 and result['historicalEnemyYear']==2014
 assert result['synthetic'] is True and result['missionId']==1
 assert result['roundLimit']==1
 assert result['before']['sourceFormIds']==[10011,10021]
 assert result['after']['sourceFormIds']==[10013,10023]
 assert [x['formId'] for x in result['before']['sourceStats']]==[10011,10021]
 assert [x['formId'] for x in result['after']['sourceStats']]==[10013,10023]
 assert [x['sourceStages'] for x in result['changedForms']]==[2,2]
 assert result['before']['results']['rounds']<=1
 assert result['after']['results']['rounds']<=1
 assert result['difference']['damageDealt']==(
  result['after']['results']['damageDealt']-result['before']['results']['damageDealt'])
 assert page.evaluate('BFTacticalRoundsV300.snapshot') is None
 assert page.evaluate('BFArchiveDraftV800.selected')==party
 assert page.evaluate('BFGlobalDraftEvolutionV1600.history.length')==depth
 page.evaluate('BFGlobalEvolutionABV1900.result.before.sourceFormIds.push(999999)')
 assert page.evaluate('BFGlobalEvolutionABV1900.result')==result
 # The actual on-screen control runs the same temporary A/B trial synchronously.
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.locator('#bf900-labs > summary').click()
 page.locator('#bf800-draft > summary').click()
 page.locator('#bf1900-ab > summary').click()
 page.wait_for_function("()=>document.querySelector('#bf1900-status')?.textContent.includes('Ready')")
 assert not page.locator('#bf1900-run').is_disabled()
 page.locator('#bf1900-rounds').select_option('5')
 page.locator('#bf1900-run').click()
 checked=page.evaluate('BFGlobalEvolutionABV1900.result')
 assert checked['roundLimit']==5
 assert checked['missionId']==1
 assert checked['before']['sourceFormIds']==party
 assert checked['after']['sourceFormIds']==[10013,10023]
 assert checked['before']['results']['rounds']<=5
 assert checked['after']['results']['rounds']<=5
 assert 'EXPERIMENTAL DIFFERENCES' in page.locator('#bf1900-results').inner_text()
 assert page.evaluate('BFTacticalRoundsV300.snapshot') is None
 assert page.evaluate('BFArchiveDraftV800.selected')==party
 # Existing synthetic battles must block comparison, and remain untouched.
 assert page.evaluate('BFArchiveDraftV800.start()') is True
 existing=page.evaluate('BFTacticalRoundsV300.snapshot')
 assert page.evaluate('BFGlobalEvolutionABV1900.run(1)') is None
 assert page.evaluate('BFTacticalRoundsV300.snapshot')==existing
 assert page.evaluate('BFTacticalRoundsV300.exit()') is True
 after=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
  saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'A/B experiments must never modify original units, battle or v7 save'
 assert not errors,errors
 browser.close()
print('PASS v19.00: matched historical 2014 A/B trials for original vs evolved source teams, UI, blocked battles and v7 save isolation')
