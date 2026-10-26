"""v14.00: 2022 source evolution material aggregation, six-unit draft and save safety."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
script=(A/'bf1400_evolution_material_planner.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert script.count('/* BF_GLOBAL_EVOLUTION_MATERIAL_PLANNER_V1400 */')==1
assert len(script.encode('utf8'))<65536
assert 'localStorage' not in script and 'saveProgress(' not in script
assert java.index('readPackagedText("bf1000_original_evolution_paths.js")')<java.index('readPackagedText("bf1400_evolution_material_planner.js")')
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
  'bf300_tactical_rounds.js','bf400_original_battle_dossier.js',
  'bf800_archive_draft.js','bf900_optional_labs_hub.js',
  'bf1000_original_evolution_paths.js','bf1400_evolution_material_planner.js'):
  page.add_script_tag(path=str(A/name))
 assert page.evaluate('P.version')==7
 assert page.evaluate('BFOriginalEvolutionV1000.formCount')==2291
 assert page.evaluate('BFEvolutionMaterialPlannerV1400.selected')==[]
 assert page.evaluate('BFEvolutionMaterialPlannerV1400.plan.entries')==[]
 assert page.evaluate('BFEvolutionMaterialPlannerV1400.selectRecipe(10011,10012)') is False
 assert page.evaluate('BFEvolutionMaterialPlannerV1400.autoSelect()')==0
 # Independently discover recorded 2022 recipes for usable archived standard forms.
 valid=page.evaluate("""() => {
  const forms=JSON.parse(document.getElementById('bf-global-unit-catalog-data').textContent).units;
  return forms.filter(u=>u.unitKind===0&&
    [u.unitBaseHp,u.unitBaseAtk,u.unitBaseDef,u.unitBaseRec]
    .every(x=>Number.isSafeInteger(x)&&x>0)&&
    (BFGlobalUnitArchive.originalRecord(u.id)?.recipes||[])
    .some(r=>BFGlobalUnitArchive.find(r.target))).slice(0,6).map(u=>u.id);
 }""")
 assert len(valid)>=2,valid
 selected=valid[:4]
 for id in selected:
  assert page.evaluate('(id)=>BFArchiveDraftV800.add(id)',id) is True
 assert page.evaluate('BFEvolutionMaterialPlannerV1400.selected')==selected
 assert page.evaluate('BFEvolutionMaterialPlannerV1400.sourceOptions(999999)')==[]
 assert page.evaluate('(id)=>BFEvolutionMaterialPlannerV1400.sourceOptions(id)',selected[0])
 assert page.evaluate('(id)=>BFEvolutionMaterialPlannerV1400.selectRecipe(id,999999)',selected[0]) is False
 assert page.evaluate('BFEvolutionMaterialPlannerV1400.selectRecipe(999999,10012)') is False
 assert page.evaluate('BFEvolutionMaterialPlannerV1400.autoSelect()')==len(selected)
 plan=page.evaluate('BFEvolutionMaterialPlannerV1400.plan')
 assert plan['selected']==selected and len(plan['entries'])==len(selected)
 assert plan['missing']==[] and all(row['to']>0 for row in plan['entries'])
 # Independently recompute from the original archived codex, not the planner.
 expected=page.evaluate("""(ids) => {
  const rows=[],materials=new Map();let zel=0,karma=0;
  for(const id of ids){
   const parent=BFGlobalUnitArchive.originalRecord(id);
   const r=parent.recipes.find(x=>BFGlobalUnitArchive.find(x.target));
   if(!r)throw Error('Missing independent recipe: '+id);
   rows.push({from:id,to:r.target});
   zel+=r.zel||0;karma+=r.karma||0;
   for(const mat of (r.materials||[])){
    const key=String(mat.type)+':'+String(mat.id);
    materials.set(key,(materials.get(key)||0)+1);
   }
  }
  return {rows,zel,karma,materials:[...materials].sort()};
 }""",selected)
 assert [(x['from'],x['to']) for x in plan['entries']]==[(x['from'],x['to']) for x in expected['rows']]
 assert plan['totals']['zel']==expected['zel']
 assert plan['totals']['karma']==expected['karma']
 actual_mat=sorted([(f"{x['type']}:{x['id']}",x['count']) for x in plan['totals']['materials']])
 oracle_mat=sorted([(k,n) for k,n in expected['materials']])
 assert actual_mat==oracle_mat,(actual_mat,oracle_mat)
 # Returned summary copies must not corrupt source or future calculations.
 page.evaluate('BFEvolutionMaterialPlannerV1400.plan.totals.materials.push({id:999,count:5})')
 assert page.evaluate('BFEvolutionMaterialPlannerV1400.plan')==plan
 assert page.evaluate('BFEvolutionMaterialPlannerV1400.autoSelect()')==0
 before=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
    save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.locator('#bf900-labs > summary').click()
 page.locator('#bf800-draft > summary').click()
 page.locator('#bf1400-material-planner > summary').click()
 assert page.locator('#bf1400-choices .bf1400-entry').count()==len(selected)
 assert 'ARCHIVED RECIPE TOTALS' in page.locator('#bf1400-report').inner_text()
 assert str(expected['zel']) in page.locator('#bf1400-report').inner_text()
 # Dropping a draft unit prunes its planned recipe; no resource change.
 assert page.evaluate('(id)=>BFArchiveDraftV800.remove(id)',selected[-1]) is True
 assert len(page.evaluate('BFEvolutionMaterialPlannerV1400.plan.entries'))==len(selected)-1
 page.locator('#bf1400-reset').click()
 assert page.evaluate('BFEvolutionMaterialPlannerV1400.plan.entries')==[]
 assert len(page.evaluate('BFEvolutionMaterialPlannerV1400.plan.missing'))==len(selected)-1
 page.locator('#bf1400-auto').click()
 assert len(page.evaluate('BFEvolutionMaterialPlannerV1400.plan.entries'))==len(selected)-1
 after=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'Source planning must never spend Zel, Karma, items or save'
 assert page.evaluate('BFEvolutionMaterialPlannerV1400.clear()') is True
 assert page.evaluate('BFEvolutionMaterialPlannerV1400.plan.entries')==[]
 assert not errors,errors
 browser.close()
print('PASS v14: exact 2022 recipe material aggregation, missing targets, draft edits, UI and v7 save protection')
