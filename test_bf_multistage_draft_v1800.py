"""v18.00: source-exact multi-hop original 2022 squad evolution, battle, undo and safe saves."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import shutil
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf1800_multistage_draft.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_MULTISTAGE_DRAFT_BATCH_V1800 */')==1
assert len(src.encode('utf8'))<65536
assert 'localStorage' not in src and 'saveProgress(' not in src
assert java.index('readPackagedText("bf1700_batch_draft_evolution.js")')<java.index('readPackagedText("bf1800_multistage_draft.js")')
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
  'bf1700_batch_draft_evolution.js','bf1800_multistage_draft.js'):
  page.add_script_tag(path=str(A/n))
 assert page.evaluate('P.version')==7
 assert page.evaluate('BFGlobalUnitArchive.count')==2291
 assert page.evaluate('BFGlobalMultistageDraftV1800.preview.entries')==[]
 assert page.evaluate('BFGlobalMultistageDraftV1800.apply()') is False
 assert page.evaluate('BFGlobalMultistageDraftV1800.undo()') is False
 # Both fixture chains were validated against literal packaged 2022 codex:
 # 10011 -> 10012 -> 10013 and 10021 -> 10022 -> 10023.
 chains=[(10011,10013),(10021,10023)]
 for start,goal in chains:
  assert page.evaluate('(id)=>BFArchiveDraftV800.add(id)',start) is True
  assert page.evaluate('([a,b])=>BFGlobalMultistageDraftV1800.choose(a,b)',[start,goal]) is True
  reach=page.evaluate('(id)=>BFGlobalMultistageDraftV1800.destinations(id)',start)
  assert next(x for x in reach if x['id']==goal)['steps']==2
  assert not any(x['steps']<2 for x in reach)
 assert page.evaluate('BFArchiveDraftV800.selected')==[10011,10021]
 assert page.evaluate('([a,b])=>BFGlobalMultistageDraftV1800.choose(a,b)',[10011,10012]) is False
 assert page.evaluate('([a,b])=>BFGlobalMultistageDraftV1800.choose(a,b)',[10011,999999]) is False
 preview=page.evaluate('BFGlobalMultistageDraftV1800.preview')
 assert preview['ready'] is True and preview['issues']==[]
 assert preview['missing']==[] and len(preview['entries'])==2
 assert preview['sourceYear']==2022
 assert [x['steps'] for x in preview['entries']]==[2,2]
 assert [x['path'] for x in preview['entries']]==[[10011,10012,10013],[10021,10022,10023]]
 # Calculate totals solely from exact source master recipes, independently.
 original=page.evaluate("""() => [
  BFOriginalEvolutionV1000.sourceRecipe(10011,10012),
  BFOriginalEvolutionV1000.sourceRecipe(10012,10013),
  BFOriginalEvolutionV1000.sourceRecipe(10021,10022),
  BFOriginalEvolutionV1000.sourceRecipe(10022,10023)]""")
 assert all(original)
 assert preview['totals']['zel']==sum(x['zel'] for x in original)
 assert preview['totals']['karma']==sum(x['karma'] for x in original)
 counts={}
 for row in original:
  for m in row['materials']:
   key=(str(m['type']),str(m['id']))
   counts[key]=counts.get(key,0)+1
 assert {(str(x['type']),str(x['id'])):x['count']
         for x in preview['totals']['materials']}==counts
 page.evaluate('BFGlobalMultistageDraftV1800.preview.totals.materials.push({id:0,count:999})')
 assert page.evaluate('BFGlobalMultistageDraftV1800.preview')==preview
 before=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
  saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.locator('#bf900-labs > summary').click()
 page.locator('#bf800-draft > summary').click()
 page.locator('#bf1800-multistage > summary').click()
 page.wait_for_function("()=>document.querySelector('#bf1800-total')?.textContent.includes('2 multi-stage source route')")
 assert page.locator('#bf1800-entries select').count()==2
 assert not page.locator('#bf1800-apply').is_disabled()
 assert 'source stages' in page.locator('#bf1800-entries').inner_text()
 assert page.evaluate('BFGlobalMultistageDraftV1800.apply()') is True
 assert page.evaluate('BFArchiveDraftV800.selected')==[10013,10023]
 assert page.evaluate('BFGlobalMultistageDraftV1800.canUndo()') is True
 batch=page.evaluate('BFGlobalMultistageDraftV1800.history')
 assert len(batch)==1 and batch[0]['originalSlots']==[10011,10021]
 assert len(page.evaluate('BFGlobalDraftEvolutionV1600.history'))==2
 # Battle-test the two evolved forms while maintaining the exact slot order.
 assert page.evaluate('BFArchiveDraftV800.start()') is True
 snap=page.evaluate('BFTacticalRoundsV300.snapshot')
 assert snap['mode']=='archive-draft'
 assert snap['draftUnitIds']==[10013,10023]
 assert [x['unitId'] for x in snap['party']]==[10013,10023]
 assert page.evaluate('BFGlobalMultistageDraftV1800.undo()') is False
 assert page.evaluate('BFGlobalMultistageDraftV1800.apply()') is False
 assert page.evaluate('BFTacticalRoundsV300.exit()') is True
 assert page.evaluate('BFGlobalMultistageDraftV1800.undo()') is True
 assert page.evaluate('BFArchiveDraftV800.selected')==[10011,10021]
 assert page.evaluate('BFGlobalMultistageDraftV1800.history')==[]
 assert page.evaluate('BFGlobalDraftEvolutionV1600.history')==[]
 assert page.evaluate('BFGlobalMultistageDraftV1800.undo()') is False
 # Reject a conflict with another selected source; do not change temporary party.
 assert page.evaluate('BFArchiveDraftV800.add(10013)') is True
 assert page.evaluate('([a,b])=>BFGlobalMultistageDraftV1800.choose(a,b)',[10011,10013]) is False
 assert page.evaluate('BFGlobalMultistageDraftV1800.apply()') is False
 assert page.evaluate('BFArchiveDraftV800.selected')==[10011,10021,10013]
 after=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
  saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'No 2022 source research choice may write real game or v7 save'
 assert not errors,errors
 browser.close()
print('PASS v18.00: 2x2-hop exact source recipes, group costs, batch battle, reversible undo, original save isolation')
