"""v13.00: validate read-only 2022 original evolution recipes, costs and materials."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import shutil
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
source=(A/'bf1000_original_evolution_paths.js').read_text('utf8')
assert len(source.encode('utf8'))<65536
assert 'localStorage' not in source and 'saveProgress(' not in source
assert 'sourceRecipes' in source and 'sourceRecipe' in source
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
  'bf1000_original_evolution_paths.js'):
  page.add_script_tag(path=str(A/name))
 assert page.evaluate('P.version')==7
 assert page.evaluate('BFOriginalEvolutionV1000.formCount')==2291
 assert page.evaluate('BFOriginalEvolutionV1000.sourceRecipes(999999)')==[]
 assert page.evaluate('BFOriginalEvolutionV1000.sourceRecipe(10011,999999)') is None
 outcome=page.evaluate("""() => {
   const forms=JSON.parse(document.getElementById('bf-global-unit-catalog-data').textContent).units;
   let recipes=0,unitsWithRecipes=0,first=null,failures=[];
   for(const f of forms){
     const original=BFGlobalUnitArchive.originalRecord(f.id);
     const expected=(original?.recipes||[]).map(rec=>({
       target:rec.target,zel:rec.zel,karma:rec.karma,
       materials:(rec.materials||[]).map(m=>({id:m.id,type:m.type,name:m.name||''}))
     }));
     const actual=BFOriginalEvolutionV1000.sourceRecipes(f.id);
     if(JSON.stringify(expected)!==JSON.stringify(actual))failures.push(f.id);
     if(expected.length){unitsWithRecipes++;recipes+=expected.length;
       if(!first)first={from:f.id,target:expected[0].target};}
   }
   return {recipes,unitsWithRecipes,first,failures};
 }""")
 assert outcome['recipes']>100,outcome
 assert outcome['unitsWithRecipes']>50,outcome
 assert not outcome['failures'],outcome['failures'][:20]
 first=outcome['first']
 if page.evaluate('(ids)=>BFGlobalUnitArchive.find(ids.target)!==null',first):
  recipe=page.evaluate('(ids)=>BFOriginalEvolutionV1000.sourceRecipe(ids.from,ids.target)',first)
  assert recipe and recipe['target']==first['target']
 selected=page.evaluate('BFOriginalEvolutionV1000.sourceRecipes(10011)')
 if selected:
  page.evaluate('BFOriginalEvolutionV1000.sourceRecipes(10011)[0].zel=999999999')
  assert page.evaluate('BFOriginalEvolutionV1000.sourceRecipes(10011)')==selected
 before=page.evaluate("""()=>({player:JSON.stringify(P),battle:JSON.stringify(S),
  save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.locator('#bf900-labs > summary').click()
 page.locator('#bf800-draft > summary').click()
 page.locator('#bf1000-evolution > summary').click()
 assert page.evaluate('(id)=>BFOriginalEvolutionV1000.show(id)',first['from']) is True
 report=page.locator('#bf1000-relations').inner_text()
 assert 'ARCHIVED 2022 EVOLUTION RECIPES' in report
 assert 'RECORDED SOURCE COST' in report
 assert 'Zel' in report
 after=page.evaluate("""()=>({player:JSON.stringify(P),battle:JSON.stringify(S),
  save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'Reading source recipes must not spend resources or modify save'
 assert not errors,errors
 browser.close()
print('PASS v13: exact archived recipe materials/costs, missing recipes, UI and v7 no-save protection')
