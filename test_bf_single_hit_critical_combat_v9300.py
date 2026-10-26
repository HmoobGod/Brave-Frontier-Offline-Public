"""v93 native-source single-hit 10% critical combat with conservative scope."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf9300_single_hit_critical_combat.js').read_text('utf8')
assert len(js.encode())<65536
assert js.count('BF_GLOBAL_SINGLE_HIT_CRITICAL_COMBAT_V9300')==1
assert all(v not in js for v in ('localStorage','saveProgress(', 'BFAndroid','fetch(','XMLHttpRequest'))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text()
assert java.index('readPackagedText("bf9200_source_offensive_bb_levels.js")')<java.index('readPackagedText("bf9300_single_hit_critical_combat.js")')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844});errors=[]
 p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),removeItem:k=>delete db[k],
 key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 for name in ('bf700_original_normal_hits.js','bf8100_original_crystal_drop_core.js',
   'bf8200_original_normal_crystal_checks.js','bf8300_original_burst_crystal_checks.js',
   'bf8400_original_normal_crystal_checks.js','bf9300_single_hit_critical_combat.js'):
  p.add_script_tag(path=str(A/name))
 assert p.evaluate('P.version')==7
 api='BFGlobalSingleHitCriticalV9300'
 assert p.evaluate('BFGlobalAllNormalCrystalChecksV8400.lookup(40011).normalHits')==1
 assert p.evaluate('BFGlobalAllNormalCrystalChecksV8400.lookup(10011).normalHits')==3
 assert p.evaluate(api+'.source.actualScope').startswith('Source-verified single')
 assert p.evaluate(api+'.roll(()=>0)') is True
 assert p.evaluate(api+'.roll(()=>0.0999)') is True
 assert p.evaluate(api+'.roll(()=>0.1)') is False
 assert p.evaluate(api+'.roll(()=>0.99)') is False
 assert p.evaluate(api+'.roll(()=>NaN)') is None
 assert p.evaluate(api+'.criticalDamage(100,true)')==150
 assert p.evaluate(api+'.criticalDamage(11,true)')==16
 assert p.evaluate(api+'.criticalDamage(100,false)')==100
 before=p.evaluate("""()=>({P:JSON.stringify(P),stored:localStorage.getItem('bf_global_offline_demo_v7')})""")
 def perform(unit,random):
  p.locator('#reset').click()
  p.evaluate("""({unit,random})=>{S.enemies.forEach((e,i)=>{if(i>0)e.hp=0;else{
    e.hp=20000;e.maxHp=20000;e.atk=0;e.def=0}});
    const actor=S.party[0];actor.unitId=unit;actor.atk=800;actor.bb=0;
    actor.action={kind:'attack',target:0};
    for(let i=1;i<S.party.length;i++)if(S.party[i].active&&S.party[i].hp>0)
      S.party[i].action={kind:'guard',target:0};
    S.target=0;document.getElementById('speed').value='4';
    window.__priorRandom93=Math.random;Math.random=()=>random;seed=771;}""",{'unit':unit,'random':random})
  p.evaluate('BF_debug.execute()')
  s=p.evaluate(api+'.snapshot()')
  lost=20000-p.evaluate('S.enemies[0].hp')
  p.evaluate('Math.random=window.__priorRandom93')
  return s,lost
 ordinary,damage=perform(40011,0.95)
 assert ordinary['observed']==1 and ordinary['criticals']==0,(ordinary,damage)
 assert ordinary['recent'][0]['critical'] is False,ordinary
 assert p.locator('#log .bf9400-critical-notice').count()==0
 assert p.locator('#bf9400-critical-banner').is_hidden()
 assert damage>0
 crit,critical_damage=perform(40011,0)
 assert crit['observed']==1 and crit['criticals']==1,(crit,critical_damage)
 assert crit['recent'][0]['critical'] is True,crit
 assert p.locator('#log .bf9400-critical-notice').count()==1
 # The combat log is collapsed by default; verify its stored DOM text, not rendered innerText.
 assert 'CRITICAL HIT!' in p.locator('#log .bf9400-critical-notice').text_content()
 assert p.locator('#bf9400-critical-banner').is_visible()
 assert 'CRITICAL HIT!' in p.locator('#bf9400-critical-banner').inner_text()
 assert critical_damage>=int(damage*1.35),(critical_damage,damage)
 assert crit['recent'][0]['sourceSingleHit'] is True
 # The previous round's critical banner must not stay over a later normal
 # attack in the SAME battle; the old critical remains recorded in history.
 p.evaluate("""async()=>{
   S.round+=1;
   const unit=S.party[0];unit.action={kind:'attack',target:0};
   const oldRandom=Math.random,oldWait=wait;
   try{
     Math.random=()=>0.95;wait=()=>Promise.resolve();
     await window.performUnit(unit,epoch);
   }finally{Math.random=oldRandom;wait=oldWait;}
 }""")
 assert p.locator('#bf9400-critical-banner').is_hidden()
 assert p.evaluate(api+'.snapshot().criticals')==1
 multi,multi_damage=perform(10011,0)
 assert multi['observed']==0 and multi['criticals']==0,(multi,multi_damage)
 assert p.locator('#log .bf9400-critical-notice').count()==0
 assert multi_damage>0
 assert p.locator('#bf9400-critical-banner').is_hidden()
 p.locator('#mode').select_option('training')
 assert p.evaluate(api+'.snapshot().mode')=='training'
 assert p.evaluate(api+'.roll(()=>0)') is True
 p.locator('#mode').select_option('archive')
 p.locator('#reset').click()
 assert p.evaluate(api+'.snapshot().observed')==0
 after=p.evaluate("""()=>({P:JSON.stringify(P),stored:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,(before,after)
 p.evaluate('window.__crit93=window.prototypeDamage')
 p.add_script_tag(path=str(A/'bf9300_single_hit_critical_combat.js'))
 assert p.evaluate('window.__crit93===window.prototypeDamage')
 assert p.locator('#bf9300-critical').count()==1
 assert not errors,errors
 b.close()
print('PASS v93 critical 10%/150% actual source-one-hit demo attack, multihit exclusion, reset/save/offline')
