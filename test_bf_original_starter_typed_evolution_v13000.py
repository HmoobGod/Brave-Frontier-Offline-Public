"""v130 source 2022 Global 7/8 starter typed evolution recipes — fail-closed/read-only."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,hashlib,shutil
R=Path(__file__).resolve().parent; A=R/'app/src/main/assets'
V=json.loads((R/'source_data/bf_global_2022_starter_typed_evolution_v130.json').read_text('utf8'))
S=json.loads((R/'source_data/bf_global_2022_starter_7_8_source_readiness_v127.json').read_text('utf8'))
assert V['schema']=='bf-global-2022-starter-7-8-typed-evolution-v130'
assert V['sourceZipSha256']==S['sourceZipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert V['verifiedInputCanonical12Sha256']==S['canonical12SourceSha256']
rows=V['rows']
assert len(rows)==len(S['rows'])==12
expected=[]
for s in S['rows']:
 e=s['originalEvo'];expected.append([s['unitId'],s['previousFormId'],s['rarity'],s['unitCost'],s['unitMaxLevel'],e['zel'],e['karma'],[[m['sourceSlot'],m['type'],m['id']] for m in e['materialSlots']]])
assert rows==expected
encoded=json.dumps(rows,separators=(',',':'))
assert hashlib.sha256(encoded.encode()).hexdigest()==V['typedRowsSha256']=='a5b91a61b5101f378fcc2692ca97b601c2034cf150c0716e9b561aebc7a0bed6'
for uid,prev,rarity,cost,maxLv,zel,karma,mats in rows:
 assert uid==prev+1 and uid%100 in (16,17) and len(mats)==(5 if rarity==7 else 8)
 assert (cost,maxLv,zel,karma)==((38,120,1500000,0) if rarity==7 else (45,150,3000000,1000000))
 assert [m[1] for m in mats]==[1]*(len(mats)-1)+[2]
 assert [m[2] for m in mats if m[1]==2]==[110100]
assert V['saveMutation'] is False and V['playableChange'] is False
js=(A/'bf13000_original_starter_typed_evolution.js').read_text('utf8')
assert len(js.encode())<65536
assert all(x not in js for x in ['localStorage','P.materials[','P.roster=','P.evolutions[','fetch(','XMLHttpRequest','Math.random'])
assert js.count(V['typedRowsSha256'])==1
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert 'readPackagedText("bf13000_original_starter_typed_evolution.js")' in java
assert java.index('bf12600_original_squad_cost.js')<java.index('bf13000_original_starter_typed_evolution.js')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage'])
 p=browser.new_page(viewport={'width':390,'height':844}); errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate('''()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),removeItem:k=>delete db[k]}});window.alert=()=>{};window.confirm=()=>true;HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.play=()=>Promise.resolve();HTMLMediaElement.prototype.pause=()=>{}}''')
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 assert p.evaluate('P.version')==7
 before=p.evaluate('JSON.stringify(P)')
 stored=p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 p.add_script_tag(path=str(A/'bf13000_original_starter_typed_evolution.js'))
 api='BFGlobalOriginalStarterTypedEvolutionV13000'
 assert p.evaluate(api+'.source.totalForms')==12
 assert p.evaluate(api+'.source.inventoryMutated') is False
 assert p.evaluate(api+'.lookup(10016).zel')==1500000
 assert p.evaluate(api+'.lookup(10017).karma')==1000000
 assert p.evaluate(api+'.lookup(10017).materials.at(-1).kind')=='original item'
 assert p.evaluate(api+'.lookup(999999)') is None
 assert p.locator('#bf13000-source-evolutions').count()==1
 assert p.locator('#bf13000-materials li').count()==5
 p.locator('#bf13000-source-evolutions').evaluate('(el)=>el.open=true')
 p.select_option('#bf13000-select','20017')
 assert p.locator('#bf13000-materials li').count()==8
 assert 'ITEM #110100' in p.locator('#bf13000-materials').inner_text()
 assert '3,000,000 Zel' in p.locator('#bf13000-price').inner_text()
 assert p.evaluate('JSON.stringify(P)')==before
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==stored
 p.evaluate('P.evolutions[10011]=10015')
 # Separate fixture change: verifies *read-only* selection for the 7★ target.
 before2=p.evaluate('JSON.stringify(P)')
 candidates=p.evaluate(api+'.snapshot().possible')
 assert any(x['fromId']==10015 and x['sourceNextId']==10016 for x in candidates)
 assert p.evaluate('JSON.stringify(P)')==before2
 p.add_script_tag(path=str(A/'bf13000_original_starter_typed_evolution.js'))
 assert p.locator('#bf13000-source-evolutions').count()==1
 assert not errors,errors
 browser.close()
print('PASS v130: original 12 typed 7/8-star starter recipes, 110100 item distinct from material units, v7 save isolated')
