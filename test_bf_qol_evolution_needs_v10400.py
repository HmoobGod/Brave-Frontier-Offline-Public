"""v104: owned archive source recipe requirements compared with demo inventory."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf10400_qol_evolution_needs.js').read_text('utf8')
assert js.count('BF_GLOBAL_QOL_EVOLUTION_NEEDS_V10400')==1
assert len(js.encode())<65536
assert not any(x in js for x in ('saveProgress(', 'localStorage', 'P.materials=', 'P.roster=', 'awardDemoRewards('))
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.set_content('<html><body><div id="evoinventory">Inventory</div></body></html>')
 p.evaluate("""()=>{
   window.P={version:7,roster:[10011],squad:[10011],
     materials:{10130:1,50120:0},unitExp:{10011:0},zel:3000,evolutions:{}};
   window.effectiveUnit=id=>id===10011?{id:10011,name:'Vargas'}:null;
   window.demoLevel=exp=>exp>=10?2:1;
   window.BF_EvolutionRoadmapV039={plan:base=>base!==10011?null:{
     current:{id:10011},target:{id:10012},demoZel:1500,
     materials:[{itemId:'10130',required:1,owned:P.materials[10130]},
                {itemId:'50120',required:2,owned:P.materials[50120]}]
   }};
   window.BFGlobalUnitArchive={find:id=>
     id===10011?{name:'Vargas'}:id===10012?{name:'Burning Vargas'}:null};
   window.BFOriginalEvolutionV1000={sourceRecipes:id=>id===10011?[{
     target:10012,zel:2500,karma:0,
     materials:[{id:10130,name:'Red Spirit',type:'material'},
                {id:50120,name:'Light Totem',type:'material'},
                {id:50120,name:'Light Totem',type:'material'}]
   }]:[]};
 }""")
 before=p.evaluate('JSON.stringify(P)')
 p.add_script_tag(path=str(A/'bf10400_qol_evolution_needs.js'))
 api='BFGlobalQoLEvolutionNeedsV10400'
 s=p.evaluate(api+'.snapshot()')
 assert s['recordedPaths']==1 and s['readyMaterialPaths']==0
 assert s['demoCostsReadyPaths']==0 and s['paths'][0]['demoCostsReady'] is False
 assert s['paths'][0]['missingCount']==2
 assert s['paths'][0]['materials'][0]['required']==1
 assert s['paths'][0]['materials'][1]['required']==2
 p.locator('#bf10400-evolution-needs > summary').click()
 # A <details> toggle event renders asynchronously; wait for the actual
 # source-backed missing-count row rather than racing the event queue.
 p.wait_for_function("document.querySelector('#bf10400-rows').textContent.includes('2 missing')")
 assert '2 missing' in p.locator('#bf10400-rows').inner_text()
 p.evaluate('P.materials[50120]=2')
 assert p.evaluate(api+'.snapshot().readyMaterialPaths')==1
 assert p.evaluate(api+'.snapshot().paths[0].missingCount')==0
 assert p.evaluate(api+'.snapshot().demoCostsReadyPaths')==0 # still level 1
 p.evaluate('P.unitExp[10011]=10')
 assert p.evaluate(api+'.snapshot().demoCostsReadyPaths')==1
 p.locator('#bf10400-filter').select_option('demo')
 p.wait_for_function("document.querySelector('#bf10400-rows').textContent.includes('0 missing')")
 assert '0 missing' in p.locator('#bf10400-rows').inner_text()
 # Search is read-only, case-insensitive, and matches next-form names/IDs.
 p.locator('#bf10400-search').fill('burning')
 assert p.locator('#bf10400-rows').inner_text().count('Burning Vargas')==1
 p.locator('#bf10400-search').fill('no such unit')
 p.wait_for_function("document.querySelector('#bf10400-rows').textContent.includes('No recorded evolution paths')")
 assert p.locator('#bf10400-rows > div').count()==0
 p.locator('#bf10400-search').fill('10012')
 p.wait_for_function("document.querySelector('#bf10400-rows').textContent.includes('Burning Vargas')")
 p.locator('#bf10400-sort').select_option('missing')
 p.locator('#bf10400-sort').select_option('name')
 assert p.evaluate('JSON.stringify(P)')==save_before_nav
 p.locator('#bf10400-search').fill('')
 p.locator('#bf10400-filter').select_option('missing')
 p.wait_for_function("document.querySelector('#bf10400-rows').textContent.includes('No recorded evolution paths')")
 assert p.locator('#bf10400-rows > div').count()==0
 p.locator('#bf10400-filter').select_option('materials')
 p.wait_for_function("document.querySelector('#bf10400-rows').textContent.includes('0 missing')")
 save_before_nav=p.evaluate('JSON.stringify(P)')
 p.evaluate("""()=>{window.__go=[];
   window.BF_homeNav={go:route=>{window.__go.push(route);return true}};
   window.BFInnerScreens={setTab:tab=>{window.__go.push(tab);return true}};
 }""")
 p.locator('#bf10400-training-shortcut').click()
 assert p.evaluate('window.__go')==['units','training']
 assert p.evaluate('JSON.stringify(P)')==save_before_nav
 assert p.evaluate('JSON.stringify(P)')!=before
 p.evaluate('P.materials[50120]=0')
 assert p.evaluate(api+'.snapshot().paths[0].missingCount')==2
 assert p.evaluate(api+'.snapshot().demoCostsReadyPaths')==0
 p.locator('#bf10400-filter').select_option('missing')
 p.wait_for_function("document.querySelector('#bf10400-rows').textContent.includes('2 missing')")
 p.add_script_tag(path=str(A/'bf10400_qol_evolution_needs.js'))
 assert p.locator('#bf10400-evolution-needs').count()==1
 assert not errors,errors
 b.close()
print('PASS v104 source-only next-recipe material needs, demo inventory comparison, idempotence')
