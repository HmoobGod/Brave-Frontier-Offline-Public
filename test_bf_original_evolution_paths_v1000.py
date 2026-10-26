"""v10.00 2,291 original 2022 evolution records with source-derived forward/back links."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import shutil
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
script=(A/'bf1000_original_evolution_paths.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert script.count('/* BF_GLOBAL_ORIGINAL_EVOLUTION_PATHS_V1000 */')==1
assert len(script.encode('utf8'))<65536
assert 'localStorage' not in script and 'saveProgress(' not in script
assert java.index('readPackagedText("bf900_optional_labs_hub.js")')<java.index('readPackagedText("bf1000_original_evolution_paths.js")')
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
 edges=page.evaluate('BFOriginalEvolutionV1000.linkCount')
 assert edges>10
 assert page.evaluate('BFOriginalEvolutionV1000.show(999999)') is False
 assert page.evaluate('BFOriginalEvolutionV1000.show(10011)') is True
 assert page.evaluate('BFOriginalEvolutionV1000.selectedId')==10011
 direct=page.evaluate('BFOriginalEvolutionV1000.next(10011)')
 assert direct==page.evaluate('BFGlobalUnitArchive.find(10011).evo')
 for child in direct:
  assert 10011 in page.evaluate('(id)=>BFOriginalEvolutionV1000.previous(id)',child)
 nodes=page.evaluate('BFOriginalEvolutionV1000.descendants(10011)')
 assert nodes[0]['id']==10011 and nodes[0]['depth']==0
 assert len(nodes)<=100
 assert page.evaluate('BFOriginalEvolutionV1000.descendants(10011,21)')==[]
 assert page.evaluate('BFOriginalEvolutionV1000.descendants(999999)')==[]
 # Ensure every archived evolution link is exactly reversible in the viewer.
 data=page.evaluate("""() => JSON.parse(
   document.getElementById('bf-global-unit-catalog-data').textContent).units
     .map(u=>[u.id,u.evo])""")
 assert len(data)==2291
 for id,children in data:
  assert page.evaluate('(id)=>BFOriginalEvolutionV1000.next(id)',id)==children,id
  for child in children:
   parents=page.evaluate('(id)=>BFOriginalEvolutionV1000.previous(id)',child)
   assert id in parents,(id,child)
 before=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.locator('#bf900-labs > summary').click()
 page.locator('#bf800-draft > summary').click()
 page.locator('#bf1000-evolution > summary').click()
 assert page.locator('#bf1000-evolution').is_visible()
 page.locator('#bf1000-search').fill('Vargas')
 assert 'Vargas' in page.locator('#bf1000-search-results').inner_text()
 assert page.evaluate('BFOriginalEvolutionV1000.show(10012)') is True
 assert '10012' in page.locator('#bf1000-detail').inner_text()
 page.locator('#bf1000-detail button').click()
 assert 10012 in page.evaluate('BFArchiveDraftV800.selected')
 after=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'Evolution source reading cannot unlock, evolve or save units'
 assert not errors,errors
 browser.close()
print('PASS v10.00: 2291 original forms, exact forward and reverse source links, no evolution/summon/save changes')
