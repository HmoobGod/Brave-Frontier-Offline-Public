"""v85 original source BB per-skill check counts across 2125 archived units."""
from pathlib import Path
import json,re,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
source=json.loads((R/'source_data/bf_global_2022_all_bb_checks_v8500.json').read_text('utf8'))
assert source['schema']=='bf-global-2022-original-all-bb-dropchecks-v8500'
assert source['sourceZipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert source['validatedOriginalUnitIds']==2258 and source['bbSkillJoins']==2125
assert source['withoutBBSkill']==133 and source['strictOffensiveSimpleGroups']==213
assert source['complexOrUnparsed']==1808 and source['simpleNonOffensiveEffects']==95
assert source['invalidDamageWeightSums']==9 and len(source['skillTableParts'])==9
js=(A/'bf8500_original_all_bb_checks.js').read_text('utf8')
assert len(js.encode('utf8'))<65536 and js.count('BF_GLOBAL_ALL_BB_DROP_CHECKS_V8500')==1
assert all(s not in js for s in ('localStorage','saveProgress(', 'BFAndroid'))
packed=re.search(r"const packed='([0-9a-z,|]+)';",js).group(1)
assert len(packed.split('|'))==2125
h=2166136261
for c in packed.encode('ascii'):h=((h^c)*16777619)&0xffffffff
assert f'{h:08x}'==source['packedFNV1a32']=='3ee23008'
rows={};unit=0
for record in packed.split('|'):
 delta,sid,checks,hits=record.split(',')
 unit+=int(delta,36);id=int(sid,36);dc=int(checks,36);n=int(hits,36)
 assert unit not in rows and id>0 and 1<=dc<=100 and 0<=n<=200
 rows[unit]=(id,dc,n)
assert len(rows)==2125 and rows[10011]==(10011,1,5)
assert rows[40021]==(40021,1,0) and rows[860788][1]==60
prev=json.loads((R/'source_data/bf_global_2022_burst_drop_checks_v8300.json').read_text('utf8'))
for r in prev['rows']:
 if r['kind']=='BB':
  assert rows[r['unitId']][:2]==(r['skillId'],r['dropCheckCount'])
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf8400_original_normal_crystal_checks.js")')<java.index('readPackagedText("bf8500_original_all_bb_checks.js")')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844});errors=[]
 p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),removeItem:k=>delete db[k],
 key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 for name in ('bf700_original_normal_hits.js','bf8100_original_crystal_drop_core.js','bf8200_original_normal_crystal_checks.js',
              'bf8300_original_burst_crystal_checks.js','bf8400_original_normal_crystal_checks.js','bf8500_original_all_bb_checks.js'):
  p.add_script_tag(path=str(A/name))
 assert p.evaluate('P.version')==7
 assert p.evaluate('BFGlobalAllBBDropChecksV8500.source.joinedBBProfiles')==2125
 assert p.evaluate('BFGlobalAllBBDropChecksV8500.lookup(10023)') is None
 assert p.evaluate('BFGlobalAllBBDropChecksV8500.lookup(1)') is None
 assert p.evaluate('BFGlobalAllBBDropChecksV8500.lookup(10011).checksPerTarget')==5
 assert p.evaluate('BFGlobalAllBBDropChecksV8500.lookup(40021).checksPerTarget') is None
 assert p.evaluate('BFGlobalAllBBDropChecksV8500.lookup(860788).checksPerEvent')==60
 assert p.evaluate('BFGlobalAllBBDropChecksV8500.lookup(860788).checksPerTarget') is None
 ids=[r['unitId'] for r in prev['rows'] if r['kind']=='BB']
 agree=p.evaluate("""ids=>ids.map(id=>{
 const a=BFGlobalAllBBDropChecksV8500.lookup(id),b=BFGlobalBurstCrystalChecksV8300.lookup(id,'BB');
 return a.skillId===b.skillId&&a.checksPerEvent===b.checksPerEvent&&a.checksPerTarget===b.checksPerTarget
})""",ids)
 assert len(agree)==71 and all(agree)
 before=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
 P:JSON.stringify(P),party:S.party.map(u=>[u.hp,u.bb,u.atk,u.rec])})""")
 assert p.evaluate('BFGlobalAllBBDropChecksV8500.rollPerTarget(10011,{random:()=>0}).battleCrystals')==5
 assert p.evaluate('BFGlobalAllBBDropChecksV8500.rollPerTarget(10011,{random:()=>.99}).battleCrystals')==0
 assert p.evaluate('BFGlobalAllBBDropChecksV8500.rollPerTarget(40021)') is None
 assert p.evaluate('BFGlobalAllBBDropChecksV8500.rollPerTarget(860788)') is None
 assert p.evaluate('BFGlobalAllBBDropChecksV8500.rollPerTarget(10011,{random:()=>1})') is None
 after=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
 P:JSON.stringify(P),party:S.party.map(u=>[u.hp,u.bb,u.atk,u.rec])})""")
 assert before==after,(before,after)
 p.add_script_tag(path=str(A/'bf8500_original_all_bb_checks.js'))
 assert p.evaluate('BFGlobalAllBBDropChecksV8500.source.joinedBBProfiles')==2125
 assert not errors,errors
 b.close()
print('PASS v85 all 2125 source BB checks; 213 strict offensive, support and complex unknown; v83 matches; saves safe')