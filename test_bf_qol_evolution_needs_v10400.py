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
     materials:{10130:1,50120:0},evolutions:{}};
   window.effectiveUnit=id=>id===10011?{id:10011,name:'Vargas'}:null;
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
 assert s['paths'][0]['missingCount']==2
 assert s['paths'][0]['materials'][0]['required']==1
 assert s['paths'][0]['materials'][1]['required']==2
 p.locator('#bf10400-evolution-needs > summary').click()
 assert '2 missing' in p.locator('#bf10400-rows').inner_text()
 p.evaluate('P.materials[50120]=2')
 assert p.evaluate(api+'.snapshot().readyMaterialPaths')==1
 assert p.evaluate(api+'.snapshot().paths[0].missingCount')==0
 assert p.evaluate('JSON.stringify(P)')!=before
 p.evaluate('P.materials[50120]=0')
 assert p.evaluate(api+'.snapshot().paths[0].missingCount')==2
 p.add_script_tag(path=str(A/'bf10400_qol_evolution_needs.js'))
 assert p.locator('#bf10400-evolution-needs').count()==1
 assert not errors,errors
 b.close()
print('PASS v104 source-only next-recipe material needs, demo inventory comparison, idempotence')
