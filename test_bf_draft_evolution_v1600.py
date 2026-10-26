"""v16.00: fully sourced temporary evolution, exact costs, stable draft slots and undo."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf1600_draft_evolution.js').read_text('utf8')
draftjs=(A/'bf800_archive_draft.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_ARCHIVE_DRAFT_EVOLUTION_V1600 */')==1
assert len(src.encode('utf8'))<65536 and len(draftjs.encode('utf8'))<65536
assert 'localStorage' not in src and 'saveProgress(' not in src
assert java.index('readPackagedText("bf1500_evolution_chain.js")')<java.index('readPackagedText("bf1600_draft_evolution.js")')
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
  'bf1000_original_evolution_paths.js','bf1400_evolution_material_planner.js',
  'bf1500_evolution_chain.js','bf1600_draft_evolution.js'):
  page.add_script_tag(path=str(A/name))
 assert page.evaluate('P.version')==7
 assert page.evaluate('BFGlobalUnitArchive.count')==2291
 assert page.evaluate('BFGlobalDraftEvolutionV1600.history')==[]
 assert page.evaluate('BFGlobalDraftEvolutionV1600.evolve(10011,10012)') is False
 assert page.evaluate('BFGlobalDraftEvolutionV1600.undo()') is False
 assert page.evaluate('BFArchiveDraftV800.replace(10011,10012)') is False
 # Find an authentic recovered 2022 evolution recipe whose source and target
 # are both eligible standard playable archive forms with positive base stats.
 fixture=page.evaluate("""() => {
  const forms=JSON.parse(document.getElementById('bf-global-unit-catalog-data').textContent).units
    .filter(x=>BFArchiveDraftV800.eligible(x.id));
  for(const u of forms){
   const recipe=BFOriginalEvolutionV1000.sourceRecipes(u.id)
    .find(x=>BFArchiveDraftV800.eligible(x.target));
   if(recipe){const other=forms.find(x=>x.id!==u.id&&x.id!==recipe.target);
     return {from:u.id,to:recipe.target,other:other.id,recipe};}
  }
  return null;
 }""")
 assert fixture, 'No eligible documented source recipe to exercise'
 a,b,c=fixture['from'],fixture['to'],fixture['other']
 assert page.evaluate('(id)=>BFArchiveDraftV800.eligible(id)',a) is True
 assert page.evaluate('BFArchiveDraftV800.eligible(999999)') is False
 assert page.evaluate('(id)=>BFArchiveDraftV800.add(id)',a) is True
 assert page.evaluate('(id)=>BFArchiveDraftV800.add(id)',c) is True
 assert page.evaluate('BFArchiveDraftV800.selected')==[a,c]
 assert page.evaluate('(id)=>BFGlobalDraftEvolutionV1600.available(id)',a)
 assert b in [x['id'] for x in page.evaluate('(id)=>BFGlobalDraftEvolutionV1600.available(id)',a)]
 assert page.evaluate('(ids)=>BFGlobalDraftEvolutionV1600.choose(ids[0],ids[1])',[a,b]) is True
 route=page.evaluate('BFGlobalDraftEvolutionV1600.activeRoute')
 assert route and route['path']==[a,b] and len(route['steps'])==1
 assert route['steps'][0]['materials']==fixture['recipe']['materials']
 assert route['totals']['zel']==fixture['recipe']['zel']
 assert route['totals']['karma']==fixture['recipe']['karma']
 assert len(route['totals']['materials'])<=len(fixture['recipe']['materials'])
 # Safe copyout and source provenance.
 page.evaluate('BFGlobalDraftEvolutionV1600.activeRoute.totals.materials.push({id:999,count:999})')
 assert page.evaluate('BFGlobalDraftEvolutionV1600.activeRoute')==route
 before=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.locator('#bf900-labs > summary').click()
 page.locator('#bf800-draft > summary').click()
 page.locator('#bf1600-draft-evolution > summary').click()
 assert page.locator('#bf1600-from option').count()==3
 assert page.locator('#bf1600-to option').count()>=2
 assert not page.locator('#bf1600-apply').is_disabled()
 assert 'SOURCE Zel' in page.locator('#bf1600-route-summary').inner_text()
 page.locator('#bf1600-apply').click()
 assert page.evaluate('BFArchiveDraftV800.selected')==[b,c]
 h=page.evaluate('BFGlobalDraftEvolutionV1600.history')
 assert len(h)==1 and h[0]['path']==[a,b] and h[0]['steps']==1
 assert page.evaluate('(ids)=>BFArchiveDraftV800.replace(ids[0],ids[1])',[b,a]) is True
 assert page.evaluate('BFArchiveDraftV800.selected')==[a,c]
 assert page.evaluate('(ids)=>BFArchiveDraftV800.replace(ids[0],ids[1])',[a,b]) is True
 assert page.evaluate('BFArchiveDraftV800.selected')==[b,c]
 assert page.evaluate('(ids)=>BFArchiveDraftV800.replace(ids[0],ids[1])',[c,b]) is False
 assert page.evaluate('(ids)=>BFGlobalDraftEvolutionV1600.evolve(ids[0],ids[1])',[b,b]) is False
 assert page.evaluate('BFArchiveDraftV800.start()') is True
 snap=page.evaluate('BFTacticalRoundsV300.snapshot')
 assert snap['mode']=='archive-draft'
 assert snap['draftUnitIds']==[b,c]
 assert snap['party'][0]['unitId']==b
 assert snap['party'][1]['unitId']==c
 assert page.evaluate('BFGlobalDraftEvolutionV1600.undo()') is False
 assert page.evaluate('(ids)=>BFArchiveDraftV800.replace(ids[0],ids[1])',[b,a]) is False
 assert page.evaluate('BFTacticalRoundsV300.exit()') is True
 assert page.evaluate('BFGlobalDraftEvolutionV1600.undo()') is True
 assert page.evaluate('BFArchiveDraftV800.selected')==[a,c]
 assert page.evaluate('BFGlobalDraftEvolutionV1600.history')==[]
 assert page.evaluate('BFGlobalDraftEvolutionV1600.undo()') is False
 assert page.evaluate('(ids)=>BFGlobalDraftEvolutionV1600.evolve(ids[0],ids[1])',[a,999999]) is False
 assert page.evaluate('(ids)=>BFGlobalDraftEvolutionV1600.evolve(ids[0],ids[1])',[c,a]) is False
 after=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'Temporary source evolution and synthetic trial may not alter actual game or saved v7'
 assert not errors,errors
 browser.close()
print('PASS v16.00: original recipe-only draft evolution, retained slot, battle test, undo, invalid guards, save isolation')
