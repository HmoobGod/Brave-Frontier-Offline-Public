"""v15.00 exact archived Global evolution paths, totals and offline save isolation."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
script=(A/'bf1500_evolution_chain.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert script.count('/* BF_GLOBAL_EVOLUTION_CHAIN_V1500 */')==1
assert len(script.encode('utf8'))<65536
assert 'localStorage' not in script and 'saveProgress(' not in script
assert java.index('readPackagedText("bf1400_evolution_material_planner.js")')<java.index('readPackagedText("bf1500_evolution_chain.js")')
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
  'bf1500_evolution_chain.js'):
  page.add_script_tag(path=str(A/name))
 assert page.evaluate('P.version')==7
 assert page.evaluate('BFGlobalEvolutionChainV1500.sourceHopCount')>100
 assert page.evaluate('BFGlobalEvolutionChainV1500.findRoute(999999,10011)') is None
 assert page.evaluate('BFGlobalEvolutionChainV1500.findRoute(10011,999999)') is None
 assert page.evaluate('BFGlobalEvolutionChainV1500.findRoute(10011,10011,-1)') is None
 assert page.evaluate('BFGlobalEvolutionChainV1500.findRoute(10011,10011,13)') is None
 assert page.evaluate('BFGlobalEvolutionChainV1500.reachable(999999)')==[]
 same=page.evaluate('BFGlobalEvolutionChainV1500.findRoute(10011,10011)')
 assert same['path']==[10011] and same['steps']==[]
 fixtures=page.evaluate("""() => {
  const units=JSON.parse(document.getElementById('bf-global-unit-catalog-data').textContent).units;
  const eligible=units.filter(u=>u.unitKind===0&&
    [u.unitBaseHp,u.unitBaseAtk,u.unitBaseDef,u.unitBaseRec]
    .every(x=>Number.isSafeInteger(x)&&x>0));
  let direct=null,two=null;
  for(const u of eligible){
   const first=(BFGlobalUnitArchive.originalRecord(u.id)?.recipes||[])
     .filter(r=>BFGlobalUnitArchive.find(r.target));
   if(!direct&&first.length)direct={from:u.id,to:first[0].target};
   for(const a of first){
    const second=(BFGlobalUnitArchive.originalRecord(a.target)?.recipes||[])
      .filter(r=>BFGlobalUnitArchive.find(r.target));
    for(const b of second){
     if(b.target!==u.id&&!first.some(r=>r.target===b.target)){
      two={from:u.id,mid:a.target,to:b.target};break;
     }
    }
    if(two)break;
   }
   if(two&&direct)break;
  }
  return {direct,two};
 }""")
 assert fixtures['direct'],fixtures
 direct=fixtures['direct']
 route=page.evaluate('(pair)=>BFGlobalEvolutionChainV1500.findRoute(pair.from,pair.to)',direct)
 assert route['sourceYear']==2022
 assert route['path']==[direct['from'],direct['to']] and len(route['steps'])==1
 rec=page.evaluate('(pair)=>BFGlobalUnitArchive.originalRecord(pair.from).recipes.find(r=>r.target===pair.to)',direct)
 assert route['steps'][0]['zel']==rec['zel'] and route['steps'][0]['karma']==rec['karma']
 assert route['steps'][0]['materials']==[
  {'id':m['id'],'type':m['type'],'name':m.get('name') or ''} for m in rec['materials']]
 assert page.evaluate('(pair)=>BFGlobalEvolutionChainV1500.findRoute(pair.from,pair.to,0)',direct) is None
 assert direct['to'] in [e['id'] for e in page.evaluate('(id)=>BFGlobalEvolutionChainV1500.reachable(id)',direct['from'])]
 if fixtures['two']:
  chain=fixtures['two']
  full=page.evaluate('(pair)=>BFGlobalEvolutionChainV1500.findRoute(pair.from,pair.to)',chain)
  assert full and len(full['steps'])==2 and full['path']==[chain['from'],chain['mid'],chain['to']]
  assert page.evaluate('(pair)=>BFGlobalEvolutionChainV1500.findRoute(pair.from,pair.to,1)',chain) is None
  original=page.evaluate("""(pair)=>[
   BFGlobalUnitArchive.originalRecord(pair.from).recipes.find(r=>r.target===pair.mid),
   BFGlobalUnitArchive.originalRecord(pair.mid).recipes.find(r=>r.target===pair.to)]""",chain)
  assert full['totals']['zel']==sum((r['zel'] or 0) for r in original)
  assert full['totals']['karma']==sum((r['karma'] or 0) for r in original)
  expected={}
  for row in original:
   for mat in row['materials']:
    k=f"{mat['type']}:{mat['id']}"
    expected[k]=expected.get(k,0)+1
  assert {f"{m['type']}:{m['id']}":m['count'] for m in full['totals']['materials']}==expected
 assert page.evaluate('(pair)=>BFGlobalEvolutionChainV1500.choose(pair.from,pair.to)',direct) is False
 assert page.evaluate('(id)=>BFArchiveDraftV800.add(id)',direct['from']) is True
 assert page.evaluate('(pair)=>BFGlobalEvolutionChainV1500.choose(pair.from,pair.to)',direct) is True
 assert page.evaluate('BFGlobalEvolutionChainV1500.selected')==direct
 assert page.evaluate('BFGlobalEvolutionChainV1500.currentRoute')==route
 page.evaluate('BFGlobalEvolutionChainV1500.currentRoute.totals.materials.push({id:111,count:44})')
 assert page.evaluate('BFGlobalEvolutionChainV1500.currentRoute')==route
 before=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.locator('#bf900-labs > summary').click()
 page.locator('#bf800-draft > summary').click()
 page.locator('#bf1500-chain > summary').click()
 assert page.locator('#bf1500-from option').count()==2
 assert page.locator('#bf1500-to option').count()>=2
 assert page.locator('#bf1500-steps .bf1500-record').count()==1
 assert 'Combined RECORDED costs' in page.locator('#bf1500-report').inner_text()
 after=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
   saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'Recipe route lookup must never change saved game'
 assert not errors,errors
 browser.close()
print('PASS v15: strict source recipe BFS, 2022 cost/material totals, bounded routes and v7 safety')
