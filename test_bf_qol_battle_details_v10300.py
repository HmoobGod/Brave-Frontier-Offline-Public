"""v103: read-only detailed battle observer stays separate from gameplay."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf10300_qol_battle_details.js').read_text('utf8')
assert src.count('BF_GLOBAL_QOL_BATTLE_DETAILS_V10300')==1
assert len(src.encode())<65536
assert not any(t in src for t in ('localStorage','saveProgress(', 'awardDemoRewards(', 'S.party=','S.enemies=','P.squad='))
assert 'min-height:44px' in src
assert 'Number.isFinite(u.maxHp)' in src
assert 'UNVERIFIED DEMO HP RECORD' in src
assert 'function criticalCount()' in src and 'criticalCountsVerified:criticals!==null' in src
assert 'waveVerified:liveWaveValid' in src and 'DEMO wave unavailable' in src
assert 'liveWaveValid&&recorded===S.totalWaves' in src
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.set_content('<html><body><div id="bf2000-run">Original battle</div></body></html>')
 p.evaluate("""()=>{
   window.P={version:7,roster:[10011],squad:[10011],questClears:{1:2}};
   window.QUEST={missionId:1,battles:3};
   window.BFGrandGaiaCampaignV100={waveReadiness:id=>({
     missionId:id,verifiedWaveCount:3,enemyFormationsVerified:false,
     dropsVerified:false,nativeMultiWaveEnabled:false})};
   window.S={mode:'archive',wave:0,totalWaves:3,round:1,busy:false,
   over:false,phase:'Action',
   party:[{name:'Vargas',unitId:10011,active:true,hp:600,maxHp:1000,bb:70,guard:false}],
   enemies:[{name:'Enemy',unitId:20011,hp:220,maxHp:440}]};
   window.BFGlobalSingleHitCriticalV9300={snapshot:()=>({criticals:2})};
   window.BFGlobalMultiHitCriticalV9500={snapshot:()=>({criticalHits:3})};
 }""")
 before=p.evaluate("JSON.stringify({P,S})")
 p.add_script_tag(path=str(A/'bf10300_qol_battle_details.js'))
 api='BFGlobalQoLBattleDetailsV10300'
 s=p.evaluate(api+'.snapshot()')
 assert s['wave']==1 and s['totalWaves']==3 and s['round']==1
 assert s['sourceRecordedWaveCount']==3 and s['sourceWaveStatus']=='MATCH'
 assert s['sourceScopedCriticalHits']==5
 assert s['allies'][0]['hpPercent']==60 and s['allies'][0]['bb']==70
 assert s['foes'][0]['hpPercent']==50
 assert s['invalidAllies']==0 and s['invalidFoes']==0
 assert s['waveVerified'] is True and s['criticalCountsVerified'] is True
 # v451: corrupt DEMO wave positions must never become invented Wave 1/N
 # or authenticate recorded source count when current wave is unusable.
 wave_checks=p.evaluate("""()=>{
   const before=JSON.stringify({P,S}),api=BFGlobalQoLBattleDetailsV10300;
   const wave=S.wave,total=S.totalWaves,got={};
   try{
     got.wave=[];
     for(const value of [-1,3,3.5,'0',NaN,Infinity,null,undefined]){
       S.wave=value;const v=api.snapshot();
       got.wave.push([v.wave,v.waveVerified,v.sourceWaveStatus]);
     }
     S.wave=wave;
     got.total=[];
     for(const value of [-1,0,101,3.5,'3',NaN,Infinity,null,undefined]){
       S.totalWaves=value;const v=api.snapshot();
       got.total.push([v.totalWaves,v.wave,v.waveVerified,v.sourceWaveStatus]);
     }
   }finally{S.wave=wave;S.totalWaves=total;api.refresh();}
   got.restored=before===JSON.stringify({P,S});
   return got;
 }""")
 assert all(x==[None,False,'MISMATCH'] for x in wave_checks['wave']),wave_checks
 assert all(x==[None,None,False,'MISMATCH'] for x in wave_checks['total']),wave_checks
 assert wave_checks['restored'],wave_checks
 # If an optional critical counter throws, disappears, reports strings or
 # overflows safe integers, show "unavailable" rather than zero or crash.
 critical_checks=p.evaluate("""()=>{
   const originalA=BFGlobalSingleHitCriticalV9300;
   const originalB=BFGlobalMultiHitCriticalV9500;
   const api=BFGlobalQoLBattleDetailsV10300,got={};
   try{
     window.BFGlobalSingleHitCriticalV9300={snapshot:()=>{throw Error('critical source missing')}};
     got.throwing=api.refresh();
     window.BFGlobalSingleHitCriticalV9300={snapshot:()=>({criticals:'2'})};
     got.string=api.snapshot();
     window.BFGlobalSingleHitCriticalV9300={snapshot:()=>({criticals:-1})};
     got.negative=api.snapshot();
     window.BFGlobalSingleHitCriticalV9300={snapshot:()=>({criticals:3.5})};
     got.fractional=api.snapshot();
     window.BFGlobalSingleHitCriticalV9300={snapshot:()=>({criticals:Number.MAX_SAFE_INTEGER})};
     got.overflow=api.snapshot();
     delete window.BFGlobalMultiHitCriticalV9500;
     got.missing=api.snapshot();
   }finally{
     window.BFGlobalSingleHitCriticalV9300=originalA;
     window.BFGlobalMultiHitCriticalV9500=originalB;
     api.refresh();
   }
   got.recovered=api.snapshot();
   return got;
 }""")
 for key in ('throwing','string','negative','fractional','overflow','missing'):
  assert critical_checks[key]['sourceScopedCriticalHits'] is None,key
  assert critical_checks[key]['criticalCountsVerified'] is False,key
 assert critical_checks['recovered']['sourceScopedCriticalHits']==5,critical_checks
 assert critical_checks['recovered']['criticalCountsVerified'] is True,critical_checks
 # v430: refuse to invent 1 HP or valid HP for invalid live DEMO data.
 invalid=p.evaluate("""()=>{
   const api=BFGlobalQoLBattleDetailsV10300;
   const ally=S.party[0],foe=S.enemies[0];
   const old={aHp:ally.hp,aMax:ally.maxHp,fHp:foe.hp,fMax:foe.maxHp};
   const original=JSON.stringify({P,S});const result={};
   try {
     ally.maxHp=0;
     result.zeroMax=api.refresh();
     ally.maxHp=old.aMax;foe.hp=NaN;
     result.nan=api.refresh();
     foe.hp=old.fHp;foe.hp=foe.maxHp+1;
     result.overMax=api.refresh();
     foe.hp='220';
     result.stringHp=api.refresh();
     foe.hp=old.fHp;foe.maxHp=-5;
     result.negativeMax=api.refresh();
   }finally{
     ally.hp=old.aHp;ally.maxHp=old.aMax;
     foe.hp=old.fHp;foe.maxHp=old.fMax;
     api.refresh();
   }
   result.unchanged=JSON.stringify({P,S})===original;
   return result;
 }""")
 assert invalid['zeroMax']['invalidAllies']==1 and invalid['zeroMax']['allies']==[]
 for key in ('nan','overMax','stringHp','negativeMax'):
  assert invalid[key]['invalidFoes']==1 and invalid[key]['foes']==[],(key,invalid[key])
 assert invalid['unchanged'],invalid
 # Expand before asserting visible warning text; keep panel open for the rest of the test.
 p.locator('#bf10300-details > summary').click()
 assert p.locator('#bf10300-details').get_attribute('open') is not None
 p.evaluate("S.wave=3;BFGlobalQoLBattleDetailsV10300.refresh()")
 assert 'DEMO wave unavailable' in p.locator('#bf10300-header').inner_text()
 assert 'MISMATCH' in p.locator('#bf10300-header').inner_text()
 p.evaluate("S.wave=0;BFGlobalQoLBattleDetailsV10300.refresh()")
 assert 'DEMO Wave 1/3' in p.locator('#bf10300-header').inner_text()
 p.evaluate("""()=>{window.__criticalOriginal=BFGlobalSingleHitCriticalV9300;
   BFGlobalSingleHitCriticalV9300={snapshot:()=>{throw Error('unavailable')}};
   BFGlobalQoLBattleDetailsV10300.refresh()}""")
 assert 'critical count unavailable' in p.locator('#bf10300-header').inner_text()
 p.evaluate("""()=>{BFGlobalSingleHitCriticalV9300=window.__criticalOriginal;
   BFGlobalQoLBattleDetailsV10300.refresh()}""")
 assert '5 source-eligible critical hits' in p.locator('#bf10300-header').inner_text()
 # Explanations are visible, not a forged HP display or false 1-HP unit.
 p.evaluate("S.enemies[0].maxHp=0;BFGlobalQoLBattleDetailsV10300.refresh()")
 assert '1 UNVERIFIED DEMO HP RECORD HIDDEN' in p.locator('#bf10300-enemies').inner_text()
 assert '1 HP' not in p.locator('#bf10300-enemies').inner_text()
 p.evaluate("S.enemies[0].maxHp=440;BFGlobalQoLBattleDetailsV10300.refresh()")
 for width in (320,390,540):
  p.set_viewport_size({'width':width,'height':844})
  rect=p.locator('#bf10300-details > summary').bounding_box()
  assert rect and rect['height']>=44,(width,rect)
 p.set_viewport_size({'width':390,'height':844})
 assert 'Vargas' in p.locator('#bf10300-allies').inner_text()
 assert 'Enemy' in p.locator('#bf10300-enemies').inner_text()
 assert '2022 recorded wave count: 3 (MATCH)' in p.locator('#bf10300-header').inner_text()
 # Changing DEMO totals must not be mistaken for changed original source.
 mismatch=p.evaluate("""()=>{
   S.totalWaves=4;
   const source=BFGlobalQoLBattleDetailsV10300.refresh();
   S.totalWaves=3;
   return {status:source.sourceWaveStatus,recorded:source.sourceRecordedWaveCount};
 }""")
 assert mismatch=={'status':'MISMATCH','recorded':3},mismatch
 # Fractional totals must not floor into a false verified match.
 fractional=p.evaluate("""()=>{
   S.totalWaves=3.5;
   try{return BFGlobalQoLBattleDetailsV10300.refresh().sourceWaveStatus;}
   finally{S.totalWaves=3;}
 }""")
 assert fractional=='MISMATCH',fractional
 p.evaluate(api+'.refresh()')
 assert '3 (MATCH)' in p.locator('#bf10300-header').inner_text()
 # Reject a tampered/unavailable API even when the DEMO count looks valid.
 unavailable=p.evaluate("""()=>{
   const api=window.BFGrandGaiaCampaignV100;
   try{
     window.BFGrandGaiaCampaignV100={waveReadiness:()=>null};
     return BFGlobalQoLBattleDetailsV10300.snapshot().sourceWaveStatus;
   }finally{window.BFGrandGaiaCampaignV100=api;}
 }""")
 assert unavailable=='UNAVAILABLE',unavailable
 p.evaluate("S.party[0].hp=0")
 p.evaluate(api+'.refresh()')
 assert 'KO' in p.locator('#bf10300-allies').inner_text()
 assert before != p.evaluate("JSON.stringify({P,S})")
 assert p.evaluate("P.version")==7
 p.add_script_tag(path=str(A/'bf10300_qol_battle_details.js'))
 assert p.locator('#bf10300-details').count()==1
 assert not errors,errors
 b.close()
print('PASS v103 read-only battle HP/BB/source critical HUD, no save or combat writes')
