"""v17: batch exact 2022 source evolution, same-slot trial, group undo and native v7 protection."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
source=(A/'bf1700_batch_draft_evolution.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert source.count('/* BF_GLOBAL_BATCH_DRAFT_EVOLUTION_V1700 */')==1
assert len(source.encode('utf8'))<65536
assert 'localStorage' not in source and 'saveProgress(' not in source
assert java.index('readPackagedText("bf1600_draft_evolution.js")')<java.index('readPackagedText("bf1700_batch_draft_evolution.js")')
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
  'bf1700_batch_draft_evolution.js'):
  page.add_script_tag(path=str(A/n))
 assert page.evaluate('P.version')==7 and page.evaluate('BFGlobalUnitArchive.count')==2291
 assert page.evaluate('BFGlobalBatchDraftEvolutionV1700.apply()') is False
 assert page.evaluate('BFGlobalBatchDraftEvolutionV1700.undo()') is False
 assert page.evaluate('BFGlobalBatchDraftEvolutionV1700.history')==[]
 # Locate two independent, documented single-stage original 2022 recipes
 # whose forms have source-backed positive base stats.
 fixtures=page.evaluate("""() => {
  const units=JSON.parse(document.getElementById('bf-global-unit-catalog-data').textContent).units;
  const candidates=[];
  for(const u of units){
   if(!BFArchiveDraftV800.eligible(u.id))continue;
   for(const rec of BFOriginalEvolutionV1000.sourceRecipes(u.id)){
    if(BFArchiveDraftV800.eligible(rec.target)&&rec.target!==u.id){
     candidates.push({from:u.id,to:rec.target,recipe:rec});break;
    }
   }
  }
  for(let i=0;i<candidates.length;i++)
   for(let j=i+1;j<candidates.length;j++){
    const a=candidates[i],b=candidates[j];
    if(new Set([a.from,a.to,b.from,b.to]).size===4)return [a,b];
   }
  return [];
 }""")
 assert len(fixtures)==2,fixtures
 a,b=fixtures
 for item in fixtures:
  assert page.evaluate('(id)=>BFArchiveDraftV800.add(id)',item['from']) is True
  assert page.evaluate('([u,v])=>BFEvolutionMaterialPlannerV1400.selectRecipe(u,v)',
   [item['from'],item['to']]) is True
 assert page.evaluate('BFArchiveDraftV800.selected')==[a['from'],b['from']]
 preview=page.evaluate('BFGlobalBatchDraftEvolutionV1700.preview')
 assert preview['ready'] is True and preview['issues']==[]
 assert preview['selected']==[a['from'],b['from']]
 assert len(preview['entries'])==2
 assert preview['missing']==[]
 assert preview['totals']['zel']==a['recipe']['zel']+b['recipe']['zel']
 assert preview['totals']['karma']==a['recipe']['karma']+b['recipe']['karma']
 material_count={}
 for r in fixtures:
  for m in r['recipe']['materials']:
   k=(str(m['type']),str(m['id']))
   material_count[k]=material_count.get(k,0)+1
 assert {(str(m['type']),str(m['id'])):m['count']
         for m in preview['totals']['materials']}==material_count
 page.evaluate('BFGlobalBatchDraftEvolutionV1700.preview.totals.materials.push({id:4,count:999})')
 assert page.evaluate('BFGlobalBatchDraftEvolutionV1700.preview')==preview
 before=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
  save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.locator('#bf900-labs > summary').click()
 page.locator('#bf800-draft > summary').click()
 page.locator('#bf1700-batch > summary').click()
 page.wait_for_function("()=>document.querySelector('#bf1700-plan')?.textContent.includes('2 valid of 2')")
 assert '2 valid of 2' in page.locator('#bf1700-plan').inner_text()
 assert not page.locator('#bf1700-apply').is_disabled()
 assert 'Zel' in page.locator('#bf1700-plan').inner_text()
 page.locator('#bf1700-apply').click()
 assert page.evaluate('BFArchiveDraftV800.selected')==[a['to'],b['to']]
 assert page.evaluate('BFGlobalBatchDraftEvolutionV1700.canUndo()') is True
 history=page.evaluate('BFGlobalBatchDraftEvolutionV1700.history')
 assert len(history)==1 and len(history[0]['entries'])==2
 assert history[0]['originalSlots']==[a['from'],b['from']]
 assert len(page.evaluate('BFGlobalDraftEvolutionV1600.history'))==2
 # Testing new 2022 forms in synthetic 2014 combat never changes owned unit data.
 assert page.evaluate('BFArchiveDraftV800.start()') is True
 battle=page.evaluate('BFTacticalRoundsV300.snapshot')
 assert battle['mode']=='archive-draft' and battle['draftUnitIds']==[a['to'],b['to']]
 assert [u['unitId'] for u in battle['party']]==[a['to'],b['to']]
 assert page.evaluate('BFGlobalBatchDraftEvolutionV1700.undo()') is False
 assert page.evaluate('BFGlobalBatchDraftEvolutionV1700.apply()') is False
 assert page.evaluate('BFTacticalRoundsV300.exit()') is True
 assert page.evaluate('BFGlobalBatchDraftEvolutionV1700.undo()') is True
 assert page.evaluate('BFArchiveDraftV800.selected')==[a['from'],b['from']]
 assert page.evaluate('BFGlobalBatchDraftEvolutionV1700.history')==[]
 assert page.evaluate('BFGlobalDraftEvolutionV1600.history')==[]
 assert page.evaluate('BFGlobalBatchDraftEvolutionV1700.undo()') is False
 # Reject a double-destination conflict without modifying the draft.
 assert page.evaluate('([u,v])=>BFEvolutionMaterialPlannerV1400.selectRecipe(u,v)',[a['from'],a['to']]) is True
 assert page.evaluate('([u,v])=>BFEvolutionMaterialPlannerV1400.selectRecipe(u,v)',[b['from'],b['to']]) is True
 page.evaluate('(v)=>BFArchiveDraftV800.add(v)',a['to'])
 invalid=page.evaluate('BFGlobalBatchDraftEvolutionV1700.preview')
 assert invalid['issues'] and invalid['ready'] is False
 snap=page.evaluate('BFArchiveDraftV800.selected')
 assert page.evaluate('BFGlobalBatchDraftEvolutionV1700.apply()') is False
 assert page.evaluate('BFArchiveDraftV800.selected')==snap
 assert page.evaluate('(id)=>BFArchiveDraftV800.remove(id)',a['to']) is True
 after=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
  save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'Batch source evolution/trials cannot affect actual saved game'
 assert not errors,errors
 browser.close()
print('PASS v17.00: two-source atomic draft evolutions, exact costs, group undo, conflict checks and v7 save')
