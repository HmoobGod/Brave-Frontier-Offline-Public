"""v82 exact 2022 Global F_UNIT normal attack BC drop checks and HC source counts."""
from pathlib import Path
import ast,json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
source=json.loads((R/'source_data/bf_global_2022_normal_crystal_checks_v8200.json').read_text('utf8'))
assert source['schema']=='bf-global-2022-normal-attack-drop-checks-v8200'
assert source['provenance']['column']=='dropCheckCount'
assert len(source['rows'])==71 and len({r['unitId'] for r in source['rows']})==71
assert len(source['provenance']['tableParts'])==2
assert [x['sha256'] for x in source['provenance']['tableParts']]==[
 '1146f09489a07b9187cd3f04bf7dc3ef3bb74e35385869534671af95bf8ea645',
 '0696ccda59fccf48598c5267eaeb8a306e994618384151cead38cec6a9195b2b']
assert next(r for r in source['rows'] if r['unitId']==10011)['dropCheckCount']==2
assert next(r for r in source['rows'] if r['unitId']==40011)['dropCheckCount']==8
assert next(r for r in source['rows'] if r['unitId']==30015)['dropCheckCount']==5
assert source['excluded'][0]['unitId']==10023
js=(A/'bf8200_original_normal_crystal_checks.js').read_text('utf8')
assert js.count('BF_GLOBAL_SOURCE_NORMAL_CRYSTAL_CHECKS_V8200')==1
assert len(js.encode('utf8'))<65536
assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf8100_original_crystal_drop_core.js")')<java.index('readPackagedText("bf8200_original_normal_crystal_checks.js")')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
 executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
 args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844});errors=[]
 p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
 removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 for name in ('bf700_original_normal_hits.js','bf8100_original_crystal_drop_core.js',
              'bf8200_original_normal_crystal_checks.js'):
  p.add_script_tag(path=str(A/name))
 assert p.evaluate('P.version')==7
 assert p.evaluate('BFGlobalNormalCrystalChecksV8200.source.profileCount')==71
 assert p.evaluate('BFGlobalNormalCrystalChecksV8200.lookup(10023)') is None
 assert p.evaluate('BFGlobalNormalCrystalChecksV8200.lookup(999999)') is None
 assert p.evaluate('BFGlobalNormalCrystalChecksV8200.lookup(10011).normalHits')==3
 assert p.evaluate('BFGlobalNormalCrystalChecksV8200.lookup(10011).totalDropChecks')==6
 assert p.evaluate('BFGlobalNormalCrystalChecksV8200.lookup(40011).totalDropChecks')==8
 assert p.evaluate('BFGlobalNormalCrystalChecksV8200.lookup(30015).totalDropChecks')==25
 assert abs(p.evaluate('BFGlobalNormalCrystalChecksV8200.lookup(10011).expectedBattleCrystals')-2.1)<1e-10
 assert abs(p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.expected(10011).expectedBattleCrystals')-2.1)<1e-10
 for row in source['rows']:
  data=p.evaluate(f'BFGlobalNormalCrystalChecksV8200.lookup({row["unitId"]})')
  assert data['checksPerHit']==row['dropCheckCount']
  assert data['totalDropChecks']==data['normalHits']*data['checksPerHit']
 baseline=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
 P:JSON.stringify(P),party:S.party.map(p=>[p.hp,p.bb,p.atk,p.rec])})""")
 allDrops=p.evaluate('BFGlobalNormalCrystalChecksV8200.rollNormal(10011,{random:()=>0})')
 assert allDrops['battleCrystals']==6 and allDrops['heartCrystals']==3
 noDrops=p.evaluate('BFGlobalNormalCrystalChecksV8200.rollNormal(10011,{random:()=>.99})')
 assert noDrops['battleCrystals']==0 and noDrops['heartCrystals']==0
 overkill=p.evaluate('BFGlobalNormalCrystalChecksV8200.rollNormal(10011,{overkill:true,random:()=>.15})')
 assert overkill['battleCrystals']==6 and overkill['heartCrystals']==3
 assert p.evaluate('BFGlobalNormalCrystalChecksV8200.rollNormal(10023)') is None
 assert p.evaluate('BFGlobalNormalCrystalChecksV8200.rollNormal(10011,{overkill:"yes"})') is None
 after=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
 P:JSON.stringify(P),party:S.party.map(p=>[p.hp,p.bb,p.atk,p.rec])})""")
 assert baseline==after,(baseline,after)
 p.add_script_tag(path=str(A/'bf8200_original_normal_crystal_checks.js'))
 assert p.evaluate('BFGlobalNormalCrystalChecksV8200.source.profileCount')==71
 assert not errors,errors
 b.close()
print('PASS v82 source 71 exact F_UNIT normal dropChecks, original BC/HC roll counts, overkill, unknown safe, v7 save integrity')
