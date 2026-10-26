"""Source-backed 2022 SBB/UBB drop checks: 1290 SBB and 932 UBB profiles."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,re,shutil
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
audit=json.loads((R/'source_data/bf_global_2022_all_sbb_ubb_checks_v8600.json').read_text('utf8'))
assert audit['schema']=='bf-global-2022-original-all-sbb-ubb-dropchecks-v8600'
assert audit['validatedNormalUnitIds']==2258
assert audit['sourceZipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert len(audit['unitTableParts'])==2 and len(audit['skillTableParts'])==9
assert audit['sbb']['count']==1290 and audit['ubb']['count']==932
assert audit['sbb']['stats']['offensiveSimple']==7 and audit['ubb']['stats'].get('offensiveSimple',0)==0
js=(A/'bf8600_original_all_sbb_ubb_checks.js').read_text('utf8')
assert len(js.encode())<65536
assert js.count('BF_GLOBAL_ALL_SBB_UBB_DROP_CHECKS_V8600')==1
assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
for kind in ('sbb','ubb'):
 packed=re.search(r"const packed%s='([0-9a-z,|]+)';"%kind.upper(),js).group(1)
 assert len(packed.split('|'))==audit[kind]['count']
 h=2166136261
 for ch in packed.encode('ascii'):h=((h^ch)*16777619)&0xffffffff
 assert f'{h:08x}'==audit[kind]['packedHashFNV32']
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf8500_original_all_bb_checks.js")')<java.index('readPackagedText("bf8600_original_all_sbb_ubb_checks.js")')
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
 for name in ('bf700_original_normal_hits.js','bf8100_original_crystal_drop_core.js','bf8200_original_normal_crystal_checks.js','bf8300_original_burst_crystal_checks.js','bf8400_original_normal_crystal_checks.js','bf8500_original_all_bb_checks.js','bf8600_original_all_sbb_ubb_checks.js'):
  p.add_script_tag(path=str(A/name))
 assert p.evaluate('P.version')==7
 assert p.evaluate('BFGlobalAllSBBUBBDropChecksV8600.source.sbbProfiles')==1290
 assert p.evaluate('BFGlobalAllSBBUBBDropChecksV8600.source.ubbProfiles')==932
 assert p.evaluate('BFGlobalAllSBBUBBDropChecksV8600.lookup(10023)') is None
 assert p.evaluate('BFGlobalAllSBBUBBDropChecksV8600.lookup(10011,"UBB")') is None
 assert p.evaluate('BFGlobalAllSBBUBBDropChecksV8600.lookup(60025,"SBB").checksPerTarget')==25
 assert p.evaluate('BFGlobalAllSBBUBBDropChecksV8600.lookup(60025,"SBB").skillId')==160025
 assert p.evaluate('BFGlobalAllSBBUBBDropChecksV8600.lookup(60025,"UBB")') is None
 prev=json.loads((R/'source_data/bf_global_2022_burst_drop_checks_v8300.json').read_text('utf8'))
 for row in prev['rows']:
  if row['kind']=='SBB':
   old=p.evaluate('BFGlobalBurstCrystalChecksV8300.lookup(%d,"SBB")'%row['unitId'])
   new=p.evaluate('BFGlobalAllSBBUBBDropChecksV8600.lookup(%d,"SBB")'%row['unitId'])
   assert new and new['skillId']==old['skillId'] and new['checksPerEvent']==old['checksPerEvent'] and new['checksPerTarget']==old['checksPerTarget'],row
 vals=p.evaluate("""()=>({before:localStorage.getItem('bf_global_offline_demo_v7'),prog:JSON.stringify(P),s:S.party.map(x=>[x.hp,x.bb,x.atk,x.rec])})""")
 assert p.evaluate('BFGlobalAllSBBUBBDropChecksV8600.rollPerTarget(60025,"SBB",{random:()=>0}).battleCrystals')==25
 assert p.evaluate('BFGlobalAllSBBUBBDropChecksV8600.rollPerTarget(60025,"SBB",{random:()=>.99}).battleCrystals')==0
 assert p.evaluate('BFGlobalAllSBBUBBDropChecksV8600.rollPerTarget(10011,"UBB")') is None
 assert p.evaluate('BFGlobalAllSBBUBBDropChecksV8600.rollPerTarget(60025,"SBB",{random:()=>1})') is None
 assert vals==p.evaluate("""()=>({before:localStorage.getItem('bf_global_offline_demo_v7'),prog:JSON.stringify(P),s:S.party.map(x=>[x.hp,x.bb,x.atk,x.rec])})""")
 p.add_script_tag(path=str(A/'bf8600_original_all_sbb_ubb_checks.js'))
 assert p.evaluate('BFGlobalAllSBBUBBDropChecksV8600.source.sbbProfiles')==1290
 assert not errors,errors
 b.close()
print('PASS v86 1290 SBB and 932 UBB source check counts with 7 supported SBB and zero UBB simulated, save safe')