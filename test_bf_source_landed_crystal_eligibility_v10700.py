"""v107: 2022 BC/HC source-hit check eligibility excludes post-KO DEMO hits.

No pickup/BB charging/HP restore is invented. Uses authentic v84 2258-unit
drop-check catalog and existing v93/v95 observed battle events.
"""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
src=(A/'bf10700_source_landed_crystal_eligibility.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('BF_GLOBAL_ORIGINAL_LANDED_CRYSTAL_ELIGIBILITY_V10700')==1
assert len(src.encode('utf8'))<65536
assert 'source.lookup(event.unitId)' in src
assert 'const eligibleBCChecks=landed*profile.checksPerHit' in src
assert 'const skippedPostKO=profile.normalHits-landed' in src
assert 'collected:false' in src and 'nativePickupNotImplemented:true' in src
assert not any(x in src for x in ['saveProgress(', 'localStorage', 'awardDemoRewards(',
                                 'S.party=', 'P.roster=', 'fetch(', 'XMLHttpRequest',
                                 'Math.random', 'performUnit=', 'sampleBC('])
assert java.index('readPackagedText("bf9500_multihit_critical_combat.js")')<java.index('readPackagedText("bf10700_source_landed_crystal_eligibility.js")')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{
   const data={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
     getItem:k=>data[k]??null,setItem:(k,v)=>data[k]=String(v),
     removeItem:k=>delete data[k],key:i=>Object.keys(data)[i]??null,
     get length(){return Object.keys(data).length}}});
 }""")
 p.set_content('<html><body><div id="bf2000-run">Battle</div></body></html>')
 p.evaluate("""()=>{
   window.P={version:7,roster:[10011,40011],squad:[10011,40011],questClears:{}};
   window.S={mode:'archive',round:1,wave:0,party:[],enemies:[]};
   localStorage.setItem('bf_global_offline_demo_v7',JSON.stringify(P));
   window.__one107=[];window.__multi107=[];
   window.BFGlobalSingleHitCriticalV9300={snapshot:()=>({recent:__one107})};
   window.BFGlobalMultiHitCriticalV9500={snapshot:()=>({recent:__multi107})};
 }""")
 initial=p.evaluate("""()=>({p:JSON.stringify(P),
   save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 for name in ['bf700_original_normal_hits.js','bf8100_original_crystal_drop_core.js',
              'bf8200_original_normal_crystal_checks.js',
              'bf8400_original_normal_crystal_checks.js',
              'bf10700_source_landed_crystal_eligibility.js']:
  p.add_script_tag(path=str(A/name))
 api='BFGlobalLandedCrystalEligibilityV10700'
 assert p.locator('#bf10700-landed-crystals').count()==1
 assert p.evaluate('BFGlobalAllNormalCrystalChecksV8400.lookup(10011).totalDropChecks')==6
 assert p.evaluate('BFGlobalAllNormalCrystalChecksV8400.lookup(40011).totalDropChecks')==8
 assert p.evaluate(api+'.snapshot().totals.eligibleBCChecks')==0
 p.evaluate("""()=>{
  __multi107.push({unitId:10011,wave:1,round:1,sourceMultiHit:true,
   nativeDamageFormula:false,observedHpLoss:25,rolls:1,criticals:0,
   hits:[{index:1,landed:true,critical:false,baseDamage:40,
      resultDamage:40,appliedDamage:25},
     {index:2,landed:false,critical:false,baseDamage:24,
      resultDamage:24,appliedDamage:0},
     {index:3,landed:false,critical:false,baseDamage:16,
      resultDamage:16,appliedDamage:0}]});
 }""")
 summary=p.evaluate(api+'.snapshot()')
 x=summary['recent'][0]
 assert x['landedHits']==1 and x['sourceHits']==3
 assert x['eligibleBCChecks']==2 and x['unverifiedPostKOBCChecks']==4
 assert x['eligibleHCChecks']==1 and x['skippedPostKO']==2
 assert summary['totals']['eligibleBCChecks']==2
 assert summary['totals']['unverifiedPostKOBCChecks']==4
 # Source one-hit unit (e.g. thunder 40011) is independently eligible.
 p.evaluate("""()=>{
  __one107.push({unitId:40011,wave:1,round:1,
    sourceSingleHit:true,observedHpLoss:70,critical:true});
 }""")
 summary=p.evaluate(api+'.snapshot()')
 assert summary['totals']['eligibleBCChecks']==10
 assert summary['totals']['eligibleHCChecks']==2
 assert summary['recent'][0]['eligibleBCChecks']==8
 # All three normal hit events when positive damage lands.
 p.evaluate("""()=>{
 __multi107.push({unitId:10011,wave:1,round:2,sourceMultiHit:true,
   nativeDamageFormula:false,observedHpLoss:60,rolls:3,criticals:1,
   hits:[
    {index:1,landed:true,critical:false,baseDamage:20,
     resultDamage:20,appliedDamage:20},
    {index:2,landed:true,critical:true,baseDamage:20,
     resultDamage:30,appliedDamage:30},
    {index:3,landed:true,critical:false,baseDamage:10,
     resultDamage:10,appliedDamage:10}]});
 }""")
 x=p.evaluate(api+'.snapshot().recent.at(-1)')
 assert x['eligibleBCChecks']==6 and x['unverifiedPostKOBCChecks']==0
 assert x['criticalHits']==1
 # Reject data that looks like a source hit but claims post-KO criticals.
 p.evaluate("""()=>{
 __multi107.push({unitId:10011,wave:1,round:3,sourceMultiHit:true,
 nativeDamageFormula:false,observedHpLoss:25,rolls:2,criticals:1,
 hits:[
  {index:1,landed:true,critical:false,baseDamage:40,resultDamage:40,appliedDamage:25},
  {index:2,landed:false,critical:true,baseDamage:24,resultDamage:36,appliedDamage:0},
  {index:3,landed:false,critical:false,baseDamage:16,resultDamage:16,appliedDamage:0}]});
 }""")
 assert p.evaluate(api+'.audit(__multi107.at(-1),"normal-multi")') is None
 assert p.evaluate(api+'.audit({unitId:10023,round:0,wave:1,sourceSingleHit:true,observedHpLoss:10,critical:false},"normal-single")') is None
 assert p.evaluate(api+'.audit({unitId:40011,round:0,wave:1,sourceSingleHit:true,observedHpLoss:0,critical:false},"normal-single")') is None
 assert p.evaluate(api+'.audit(__one107[0],"bb")') is None
 p.locator('#bf10700-landed-crystals > summary').click()
 p.wait_for_function("""()=>document.querySelector('#bf10700-totals').textContent.includes('potential BC checks')""")
 assert 'post-KO BC checks outside confirmed landed baseline' in p.locator('#bf10700-totals').inner_text()
 p.evaluate('S.mode="training"')
 assert p.evaluate(api+'.snapshot().active') is False
 assert p.evaluate("""()=>{
   const now={p:JSON.stringify(P),
       save:localStorage.getItem('bf_global_offline_demo_v7')};
   return now;
 }""")==initial
 p.add_script_tag(path=str(A/'bf10700_source_landed_crystal_eligibility.js'))
 assert p.locator('#bf10700-landed-crystals').count()==1
 assert not errors,errors
 b.close()
print('PASS v107 2022 landed BC/HC checks: kill boundaries, one/multi hit, invalid trace rejection and v7 isolation')
