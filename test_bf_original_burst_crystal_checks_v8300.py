"""v83 original BB/SBB skill crystal dropCheckCount, strict group validation and save isolation."""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
d=json.loads((R/'source_data/bf_global_2022_burst_drop_checks_v8300.json').read_text('utf8'))
assert d['schema']=='bf-global-2022-bb-sbb-dropcheck-source-v8300'
assert d['archiveSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert len(d['skillTableParts'])==9 and len(d['unitTableParts'])==2
rows=d['rows']
assert len(rows)==83 and len(set((r['unitId'],r['kind']) for r in rows))==83
assert sum(r['kind']=='BB' for r in rows)==71
assert sum(r['kind']=='SBB' for r in rows)==12
assert sum(r['simpleDamageEvents'] is not None for r in rows)==61
assert sum(r['offensiveDamageEvidence'] for r in rows)==48
assert sum(r['simpleDamageEvents'] is not None and not r['offensiveDamageEvidence'] for r in rows)==13
assert next(r for r in rows if r['unitId']==60025 and r['kind']=='SBB')['dropCheckCount']==25
js=(A/'bf8300_original_burst_crystal_checks.js').read_text('utf8')
assert len(js.encode('utf8'))<65536
assert js.count('BF_GLOBAL_SOURCE_BURST_CRYSTAL_CHECKS_V8300')==1
assert all(s not in js for s in ('localStorage','saveProgress(', 'BFAndroid'))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf8200_original_normal_crystal_checks.js")')<java.index('readPackagedText("bf8300_original_burst_crystal_checks.js")')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[]
 p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
 removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 for name in ('bf700_original_normal_hits.js','bf8100_original_crystal_drop_core.js',
              'bf8200_original_normal_crystal_checks.js','bf8300_original_burst_crystal_checks.js'):
  p.add_script_tag(path=str(A/name))
 assert p.evaluate('P.version')==7
 assert p.evaluate('BFGlobalBurstCrystalChecksV8300.source.bbProfiles')==71
 assert p.evaluate('BFGlobalBurstCrystalChecksV8300.source.sbbProfiles')==12
 for r in rows:
  found=p.evaluate('BFGlobalBurstCrystalChecksV8300.lookup(%d,"%s")'%(r['unitId'],r['kind']))
  assert found and found['skillId']==r['skillId'] and found['checksPerEvent']==r['dropCheckCount'],r
  assert found['simpleDamageEvents']==r['simpleDamageEvents'],r
  assert found['isOffensiveDamage']==r['offensiveDamageEvidence'],r
  assert found['nonOffensiveEffect']==(r['simpleDamageEvents'] is not None and not r['offensiveDamageEvidence']),r
  assert found['unknownComplexDamageGroups']==(r['simpleDamageEvents'] is None),r
  expect=None if not r['offensiveDamageEvidence'] else r['simpleDamageEvents']*r['dropCheckCount']
  assert found['checksPerTarget']==expect,r
 assert p.evaluate('BFGlobalBurstCrystalChecksV8300.lookup(10011,"BB").checksPerTarget')==5
 assert p.evaluate('BFGlobalBurstCrystalChecksV8300.lookup(60025,"SBB").checksPerTarget')==25
 assert p.evaluate('BFGlobalBurstCrystalChecksV8300.lookup(10021,"BB").checksPerTarget') is None
 assert p.evaluate('BFGlobalBurstCrystalChecksV8300.lookup(20041,"BB").checksPerTarget') is None
 assert p.evaluate('BFGlobalBurstCrystalChecksV8300.lookup(40021,"BB").checksPerTarget') is None
 assert p.evaluate('BFGlobalBurstCrystalChecksV8300.lookup(10023,"BB")') is None
 assert p.evaluate('BFGlobalBurstCrystalChecksV8300.lookup(10011,"SBB")') is None
 before=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
 P:JSON.stringify(P),party:S.party.map(u=>[u.hp,u.bb,u.atk,u.rec])})""")
 assert p.evaluate('BFGlobalBurstCrystalChecksV8300.rollPerTarget(10011,"BB",{random:()=>0}).battleCrystals')==5
 assert p.evaluate('BFGlobalBurstCrystalChecksV8300.rollPerTarget(60025,"SBB",{random:()=>0}).battleCrystals')==25
 assert p.evaluate('BFGlobalBurstCrystalChecksV8300.rollPerTarget(10011,"BB",{random:()=>.99}).battleCrystals')==0
 assert p.evaluate('BFGlobalBurstCrystalChecksV8300.rollPerTarget(10021,"BB")') is None
 assert p.evaluate('BFGlobalBurstCrystalChecksV8300.rollPerTarget(20041,"BB")') is None
 assert p.evaluate('BFGlobalBurstCrystalChecksV8300.rollPerTarget(40021,"BB")') is None
 assert p.evaluate('BFGlobalBurstCrystalChecksV8300.rollPerTarget(10011,"BB",{overkill:"yes"})') is None
 assert p.evaluate('BFGlobalBurstCrystalChecksV8300.rollPerTarget(10011,"BB",null)') is None
 after=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
 P:JSON.stringify(P),party:S.party.map(u=>[u.hp,u.bb,u.atk,u.rec])})""")
 assert before==after,(before,after)
 p.add_script_tag(path=str(A/'bf8300_original_burst_crystal_checks.js'))
 assert p.evaluate('BFGlobalBurstCrystalChecksV8300.source.simpleDamageGroups')==61
 assert p.evaluate('BFGlobalBurstCrystalChecksV8300.source.offensiveSimpleGroups')==48
 assert not errors,errors
 b.close()
print('PASS v83 71 BB/12 SBB recovered source check fields, 48 offensive simple groups, 13 support ineligible, 22 complex unknowns, v7 saves unchanged')
