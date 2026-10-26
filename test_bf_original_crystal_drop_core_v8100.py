"""v81 exact original BC and HC base drop rates with source normal hit counts."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf8100_original_crystal_drop_core.js').read_text('utf8')
assert js.count('BF_GLOBAL_ORIGINAL_CRYSTAL_DROP_CORE_V8100')==1
assert len(js.encode('utf8'))<65536
assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf700_original_normal_hits.js")')<java.index('readPackagedText("bf8100_original_crystal_drop_core.js")')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
 executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
 args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844});errors=[]
 p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
 removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
 get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 p.add_script_tag(path=str(A/'bf700_original_normal_hits.js'))
 p.add_script_tag(path=str(A/'bf8100_original_crystal_drop_core.js'))
 assert p.evaluate('P.version')==7
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.source.bcBasePercent')==35
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.source.hcBasePercent')==10
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.source.overkillMultiplier')==2
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.hitCount(10011)')==3
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.hitCount(40011)')==1
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.hitCount(10023)') is None
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.hitCount(999999)') is None
 exp=p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.expected(10011)')
 assert exp['normalHits']==3 and abs(exp['expectedHeartCrystals']-.3)<1e-10
 assert exp['expectedBattleCrystals'] is None and exp['unknownBattleCrystalChecks']
 before=p.evaluate("""()=>({P:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7'),
 party:S.party.map(u=>[u.hp,u.bb,u.atk,u.rec])})""")
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.sampleBC()') is None
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.sampleBC(401)') is None
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.sampleBC(-1)') is None
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.sampleBC(0)')==0
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.sampleBC(4,{random:()=>0})')==4
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.sampleBC(4,{random:()=>.99})')==0
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.sampleBC(4,{overkill:true,random:()=>.5})')==4
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.sampleBC(4,{overkill:false,random:()=>.5})')==0
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.sampleHC(10011,{random:()=>0})')==3
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.sampleHC(10011,{random:()=>.2})')==0
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.sampleHC(10011,{overkill:true,random:()=>.15})')==3
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.sampleHC(10023)') is None
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.chance(0,()=>0)') is False
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.chance(100,()=>.99)') is True
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.integerRoll(()=>0)')==0
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.integerRoll(()=>.99999999)')==100
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.integerRoll(()=>-1)') is None
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.integerRoll(()=>1)') is None
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.chance(35,()=>.35)') is True
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.chance(35,()=>.36)') is False
 assert p.evaluate('BFGlobalOriginalCrystalDropCoreV8100.snapshot().source.unitHitSource')!=''
 after=p.evaluate("""()=>({P:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7'),
 party:S.party.map(u=>[u.hp,u.bb,u.atk,u.rec])})""")
 assert before==after,(before,after)
 p.add_script_tag(path=str(A/'bf8100_original_crystal_drop_core.js'))
 assert p.evaluate('typeof BFGlobalOriginalCrystalDropCoreV8100.sampleHC')=='function'
 assert not errors,errors
 b.close()
print('PASS v81 Global crystal source hit counts, exact 35% BC/drop-check and 10% HC/hit, 2x overkill, fail-closed unknown BC checks, saves unchanged')
