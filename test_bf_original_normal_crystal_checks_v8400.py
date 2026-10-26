"""v84 2258 source-aligned collectible normal attack hit/check profiles and save isolation."""
from pathlib import Path
import re,json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent; A=R/'app/src/main/assets'
source=json.loads((R/'source_data/bf_global_2022_full_normal_crystal_checks_v8400.json').read_text('utf8'))
assert source['schema']=='bf-global-2022-all-source-normal-crystal-checks-v8400'
assert source['sourceZipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert source['archivedUnits']==2291 and source['validCollectibleProfiles']==2258
assert len(source['excluded'])==33 and {e['unitId'] for e in source['excluded']} >= {1,10023}
assert set(source['whitespaceOnlySanitizedIds'])=={20926,51136,820317,850347}
assert len(source['unitTableParts'])==2
old=json.loads((R/'source_data/bf_global_2022_normal_crystal_checks_v8200.json').read_text('utf8'))['rows']
js=(A/'bf8400_original_normal_crystal_checks.js').read_text('utf8')
assert len(js.encode('utf8'))<65536
assert js.count('BF_GLOBAL_FULL_NORMAL_CRYSTAL_CHECKS_V8400')==1
assert all(s not in js for s in ('localStorage','saveProgress(', 'BFAndroid'))
match=re.search(r"const packed='([0-9a-z,|]+)';",js)
assert match
packed=match.group(1)
v=2166136261
for c in packed.encode('ascii'):
 v=((v^c)*16777619)&0xffffffff
assert f'{v:08x}'==source['packedFNV1a32']=='690fb10d'
rows={};unit=0
for rec in packed.split('|'):
 delta,compound=rec.split(',')
 unit+=int(delta,36)
 hits,checks=divmod(int(compound,36),64)
 assert unit>0 and unit not in rows and 1<=hits<=200 and 1<=checks<=63
 rows[unit]=(hits,checks)
assert len(rows)==2258 and 1 not in rows and 10023 not in rows
assert rows[10011]==(3,2) and rows[840548]==(25,3) and rows[860788]==(1,55)
assert rows[20926]==(10,4) and rows[810547]==(12,4)
for r in old: assert rows[r['unitId']][1]==r['dropCheckCount'],r
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf8300_original_burst_crystal_checks.js")')<java.index('readPackagedText("bf8400_original_normal_crystal_checks.js")')
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
              'bf8200_original_normal_crystal_checks.js','bf8300_original_burst_crystal_checks.js',
              'bf8400_original_normal_crystal_checks.js'):
  p.add_script_tag(path=str(A/name))
 assert p.evaluate('P.version')==7
 assert p.evaluate('BFGlobalAllNormalCrystalChecksV8400.source.profileCount')==2258
 assert p.evaluate('BFGlobalAllNormalCrystalChecksV8400.lookup(10023)') is None
 assert p.evaluate('BFGlobalAllNormalCrystalChecksV8400.lookup(1)') is None
 assert p.evaluate('BFGlobalAllNormalCrystalChecksV8400.lookup(9999999)') is None
 assert p.evaluate('BFGlobalAllNormalCrystalChecksV8400.lookup(840548).totalDropChecks')==75
 assert p.evaluate('BFGlobalAllNormalCrystalChecksV8400.lookup(860788).totalDropChecks')==55
 assert p.evaluate('BFGlobalAllNormalCrystalChecksV8400.lookup(20926).normalHits')==10
 ids=[r['unitId'] for r in old]
 agree=p.evaluate("""ids=>ids.map(id=>{
 const a=BFGlobalAllNormalCrystalChecksV8400.lookup(id),b=BFGlobalNormalCrystalChecksV8200.lookup(id);
 return a.normalHits===b.normalHits&&a.checksPerHit===b.checksPerHit&&a.totalDropChecks===b.totalDropChecks
})""",ids)
 assert len(agree)==71 and all(agree)
 before=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
 P:JSON.stringify(P),party:S.party.map(u=>[u.hp,u.bb,u.atk,u.rec])})""")
 yes=p.evaluate('BFGlobalAllNormalCrystalChecksV8400.rollNormal(840548,{random:()=>0})')
 assert yes['battleCrystals']==75 and yes['heartCrystals']==25
 no=p.evaluate('BFGlobalAllNormalCrystalChecksV8400.rollNormal(840548,{random:()=>.99})')
 assert no['battleCrystals']==0 and no['heartCrystals']==0
 ov=p.evaluate('BFGlobalAllNormalCrystalChecksV8400.rollNormal(10011,{random:()=>.15,overkill:true})')
 assert ov['battleCrystals']==6 and ov['heartCrystals']==3
 assert p.evaluate('BFGlobalAllNormalCrystalChecksV8400.rollNormal(10023)') is None
 assert p.evaluate('BFGlobalAllNormalCrystalChecksV8400.rollNormal(10011,{random:()=>1})') is None
 assert p.evaluate('BFGlobalAllNormalCrystalChecksV8400.rollNormal(10011,null)') is None
 after=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
 P:JSON.stringify(P),party:S.party.map(u=>[u.hp,u.bb,u.atk,u.rec])})""")
 assert before==after,(before,after)
 p.add_script_tag(path=str(A/'bf8400_original_normal_crystal_checks.js'))
 assert p.evaluate('BFGlobalAllNormalCrystalChecksV8400.source.profileCount')==2258
 assert not errors,errors
 b.close()
print('PASS v84 2258 source hit/check profiles, 71 v82 matches, fail-closed invalids, original rates, v7 save isolation')