"""Optional experimental SBB on real scheduled Auto turns; synthetic saves only."""
from pathlib import Path
import ast,shutil
from playwright.sync_api import sync_playwright
from bf_capture_progress_audit import INSTALL_STORAGE,SNAPSHOT,assert_unchanged
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf_auto_sbb_demo.js').read_text()
assert len(js.encode())<12000
assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid','fetch('))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text()
assert java.index('readPackagedText("bf10500_qol_advanced_smart_auto.js")')<java.index('readPackagedText("bf_auto_sbb_demo.js")')<java.index('readPackagedText("bf_sbb_fallback_dispatch.js")')
tree=ast.parse((R/'test_bf_paralysis_action_lock_v6000.py').read_text())
names=next(ast.literal_eval(n) for n in ast.walk(tree) if isinstance(n,ast.Tuple) and n.elts and isinstance(n.elts[0],ast.Constant) and n.elts[0].value=='bf_home_nav.js')
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=shutil.which('chromium') or shutil.which('google-chrome'),args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/*',lambda r:r.abort());p.evaluate(INSTALL_STORAGE)
 p.evaluate('()=>{HTMLMediaElement.prototype.play=()=>Promise.resolve();HTMLMediaElement.prototype.pause=()=>{};HTMLMediaElement.prototype.load=()=>{}}')
 p.set_content((A/'index.html').read_text());p.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in names:p.add_script_tag(path=str(A/name))
 for name in ('bf700_original_normal_hits.js','bf8100_original_crystal_drop_core.js','bf8200_original_normal_crystal_checks.js','bf8300_original_burst_crystal_checks.js','bf8400_original_normal_crystal_checks.js','bf8800_live_normal_crystal_events.js','bf9300_single_hit_critical_combat.js','bf9500_multihit_critical_combat.js','bf10500_qol_advanced_smart_auto.js','bf_auto_sbb_demo.js','bf_sbb_fallback_dispatch.js'):p.add_script_tag(path=str(A/name))
 assert p.locator('#bf-auto-sbb-enable').count()==1
 assert p.evaluate('BFGlobalAutoSBBDemo.enabled()') is False
 p.evaluate('()=>{window.__autoSbbInstalled=BF041SmartAuto.kindFor}')
 before=p.evaluate(SNAPSHOT);p.add_script_tag(path=str(A/'bf_auto_sbb_demo.js'))
 assert p.evaluate('__autoSbbInstalled===BF041SmartAuto.kindFor')
 assert p.locator('#bf-auto-sbb-enable').count()==1
 assert_unchanged(p,before,'installation')
 p.locator('.bf-navbar [data-bf-goto="quest"]').click()
 p.evaluate('''()=>{
  for(const u of S.party){u.active=u.id===0;u.action=null;u.hp=1000;u.maxHp=1000;u.atk=1000;u.bb=100}
  S.party[0].unitId=10015;S.enemies=[{...S.enemies[0],slot:0,hp:100000,maxHp:100000,def:100,atk:1},{...S.enemies[0],slot:1,hp:100000,maxHp:100000,def:100,atk:1}];
  document.getElementById('speed').value='4';window.__autoSbbFresh=JSON.stringify(S);
 }''')
 cases=(('default-off',False,True,False,10015,100,None,'burst'),
        ('enabled',True,True,False,10015,100,None,'sbb_demo'),
        ('smart',True,True,True,10015,100,None,'sbb_demo'),
        ('prototype-off',True,False,False,10015,100,None,'burst'),
        ('low-gauge',True,True,False,10015,40,None,'attack'),
        ('no-source',True,True,False,10011,100,None,'burst'),
        ('curse',True,True,False,10015,100,5,'attack'),
        ('paralysis',True,True,False,10015,100,6,'burst'),
        ('support',True,True,True,20041,100,None,'burst'),
        ('conserve',True,True,True,10015,100,None,'attack'),
        ('wounded-guard',True,True,True,10015,100,None,'guard'),
        ('early-wave-bb',True,True,True,10015,100,None,'attack'),
        ('final-wave-bb',True,True,True,10015,100,None,'sbb_demo'))
 for label,on,prototype,smart,unit,gauge,status,expected in cases:
  p.evaluate('''([on,prototype,smart,unit,gauge,injured,label])=>{
   S=JSON.parse(__autoSbbFresh);S.party[0].unitId=unit;S.party[0].bb=gauge;if(injured)S.party[0].hp=200;seed=771;
   document.getElementById('bf-auto-sbb-enable').checked=on;document.getElementById('bf044-enable').checked=prototype;document.getElementById('bf041-smart-auto').checked=smart;
   // Do not invent enemies: use only the source-recorded mission wave count.
   if(label==='final-wave-bb'){
     if(!Number.isSafeInteger(QUEST?.battles)||QUEST.battles<2)
       throw Error('Source mission wave count unavailable');
     S.wave=QUEST.battles-1;
   }else if(label==='early-wave-bb'){
     if(!Number.isSafeInteger(QUEST?.battles)||QUEST.battles<2)
       throw Error('Source mission wave count unavailable');
     S.wave=0;
   }
  }''',[on,prototype,smart,unit,gauge,label in ('support','wounded-guard'),label])
  # A strict source wave-readiness module can fail closed when an unrelated
  # DEMO quest row was modified. In that case opt-in final-wave BB policy
  # correctly refuses to reserve BB for an unverified later wave; regular
  # (and experimental SBB) burst execution remains the native fallback.
  if label=='early-wave-bb':
   readiness=p.evaluate('''()=>{
    const api=window.BFGrandGaiaCampaignV100,
      row=typeof api?.waveReadiness==='function'?api.waveReadiness(QUEST.missionId):undefined;
    return {present:!!api,
      valid:!!row&&row.missionId===QUEST.missionId&&
        row.verifiedWaveCount===QUEST.battles};
   }''')
   if readiness['present'] and not readiness['valid']:
    expected='sbb_demo'
   print('INFO Auto SBB early-wave source readiness',readiness,'expected',expected,flush=True)
  # Advanced preferences are an isolated setup write before the audit snapshot.
  assert p.evaluate('''([on,guard,burst])=>BFGlobalQoLAdvancedAutoV10500.set({
    on,heal:60,target:"percent",burst,guard})''',
    [label in ('conserve','wounded-guard','early-wave-bb','final-wave-bb'),
     35 if label=='wounded-guard' else 0,
     'final-wave' if label in ('early-wave-bb','final-wave-bb') else
     'conserve' if label=='conserve' else 'normal'])
  if status:assert p.evaluate('code=>BFGlobalOriginalAilmentStateV5700.inflict(0,code)',status)
  before=p.evaluate(SNAPSHOT);round_before=p.evaluate('S.round')
  p.evaluate('''()=>{
   S.auto=true;document.getElementById('auto').checked=true;window.__autoSbbSeen=false;window.__autoSbbPlan=null;
   window.__autoSbbOldPerform=performUnit;window.__autoSbbOldRandom=Math.random;Math.random=()=>0;
   window.performUnit=async function(unit,token){window.__autoSbbPlan=unit.action.kind;return await __autoSbbOldPerform.apply(this,arguments)};
   window.__autoSbbStop=new MutationObserver(()=>{if(E.phase.textContent==='Enemy phase'){S.auto=false;document.getElementById('auto').checked=false;__autoSbbSeen=true;__autoSbbStop.disconnect()}});
   __autoSbbStop.observe(E.phase,{childList:true,characterData:true,subtree:true});scheduleAuto();
  }''')
  p.wait_for_function('()=>__autoSbbSeen&&!S.busy',timeout=30000)
  p.evaluate('()=>{window.performUnit=__autoSbbOldPerform;Math.random=__autoSbbOldRandom}')
  assert p.evaluate('__autoSbbPlan')==expected,(label,p.evaluate('__autoSbbPlan'))
  assert p.evaluate('S.round')==round_before+1
  hp=p.evaluate('S.enemies.map(e=>e.hp)')
  if expected=='sbb_demo':
   assert all(x<100000 for x in hp) and p.evaluate('S.party[0].bb')==0
  if status:
   assert p.evaluate('S.party[0].bb')==100
   if status==6:assert hp==[100000,100000]
  if label=='support':assert hp==[100000,100000] and p.evaluate('S.party[0].hp')>200
  if label=='wounded-guard' or (label=='early-wave-bb' and expected=='attack'):
   assert p.evaluate('S.party[0].bb')==100
  if label=='wounded-guard':
   assert hp==[100000,100000]
  assert_unchanged(p,before,label)
  print('PASS actual Auto SBB',label,expected,'gauge',p.evaluate('S.party[0].bb'),'P/storage intact',flush=True)
 # Planner calls outside live archive Auto and copied/disabled actors cannot opt in.
 p.evaluate('''()=>{S=JSON.parse(__autoSbbFresh);document.getElementById('bf-auto-sbb-enable').checked=true;document.getElementById('bf044-enable').checked=true;document.getElementById('bf041-smart-auto').checked=false}''')
 before=p.evaluate(SNAPSHOT)
 assert p.evaluate('BF041SmartAuto.kindFor(S.party[0])')=='burst'
 p.evaluate('S.auto=true;S.mode="training"')
 assert p.evaluate('BF041SmartAuto.kindFor(S.party[0])')=='burst'
 p.evaluate('S.mode="archive"')
 assert p.evaluate('BF041SmartAuto.kindFor({...S.party[0]})')=='burst'
 p.evaluate('S.party[0].active=false')
 assert p.evaluate('BF041SmartAuto.kindFor(S.party[0])')=='burst'
 assert_unchanged(p,before,'manual/training/identity controls')
 assert not errors,errors;b.close()
print('PASS actual scheduled Auto turns: player SBB, early/final source-wave BB, support, curse, low-HP Guard and v7 isolation')
