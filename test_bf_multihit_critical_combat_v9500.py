"""v95 source-scoped per-hit critical damage, browser regression and save isolation."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
name='bf9500_multihit_critical_combat.js'
src=(A/name).read_text('utf8')
assert len(src.encode())<65536
assert src.count('BF_GLOBAL_MULTIHIT_CRITICAL_COMBAT_V9500')==1
assert not any(x in src for x in ('localStorage','saveProgress(', 'BFAndroid','XMLHttpRequest','fetch('))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text()
assert java.index('readPackagedText("bf9300_single_hit_critical_combat.js")')<java.index('readPackagedText("'+name+'")')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[]
 p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),removeItem:k=>delete db[k],
 key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 for file in ('bf700_original_normal_hits.js','bf8100_original_crystal_drop_core.js',
  'bf8200_original_normal_crystal_checks.js','bf8300_original_burst_crystal_checks.js',
  'bf8400_original_normal_crystal_checks.js','bf9300_single_hit_critical_combat.js',
  name):p.add_script_tag(path=str(A/file))
 api='BFGlobalMultiHitCriticalV9500'
 assert p.evaluate('P.version')==7
 assert p.evaluate('BFGlobalAllNormalCrystalChecksV8400.lookup(10011).normalHits')==3
 assert p.evaluate('BFGlobalAllNormalCrystalChecksV8400.lookup(40011).normalHits')==1
 assert p.evaluate(api+'.roll(()=>0)') is True
 assert p.evaluate(api+'.roll(()=>0.1)') is False
 assert p.evaluate(api+'.roll(()=>NaN)') is None
 assert p.evaluate(api+'.criticalDamage(101,true)')==151
 assert p.evaluate(api+'.criticalDamage(101,false)')==101
 saved=p.evaluate("""()=>({P:JSON.stringify(P),stored:localStorage.getItem('bf_global_offline_demo_v7')})""")
 def perform(unit,random,kind='attack'):
  p.locator('#mode').select_option('archive')
  p.locator('#reset').click()
  p.evaluate("""({unit,random,kind})=>{
   S.enemies.forEach((e,i)=>{if(i>0)e.hp=0;else{e.hp=20000;e.maxHp=20000;e.atk=0;e.def=0}});
   const actor=S.party[0];actor.unitId=unit;actor.atk=800;actor.bb=100;
   actor.action={kind,target:0};
   for(let i=1;i<S.party.length;i++)if(S.party[i].active&&S.party[i].hp>0)
     S.party[i].action={kind:'guard',target:0};
   S.target=0;document.getElementById('speed').value='4';
   window.__priorRandom95=Math.random;Math.random=()=>random;seed=771;
  }""",{'unit':unit,'random':random,'kind':kind})
  p.evaluate('BF_debug.execute()')
  ss=p.evaluate(api+'.snapshot()')
  hp=20000-p.evaluate('S.enemies[0].hp')
  p.evaluate('Math.random=window.__priorRandom95')
  return ss,hp
 ordinary,plainDamage=perform(10011,.95)
 assert ordinary['observed']==1 and ordinary['criticalHits']==0,(ordinary,plainDamage)
 assert ordinary['recent'][0]['rolls']==3 and ordinary['recent'][0]['criticals']==0
 assert p.locator('#bf9500-critical-banner').is_hidden()
 crit,criticalDamage=perform(10011,0)
 assert crit['observed']==1 and crit['criticalHits']==3,(crit,criticalDamage)
 assert crit['recent'][0]['rolls']==3 and crit['recent'][0]['criticals']==3
 assert len(crit['recent'][0]['hits'])==3
 assert all(h['critical'] for h in crit['recent'][0]['hits'])
 assert criticalDamage>=int(plainDamage*1.35),(criticalDamage,plainDamage)
 assert p.locator('#bf9500-critical-banner').is_visible()
 assert p.locator('#log .bf9500-critical-notice').count()==1
 assert '3 CRITICAL HITS!' in p.locator('#log .bf9500-critical-notice').text_content()
 assert p.evaluate('BFGlobalSingleHitCriticalV9300.snapshot().observed')==0
 single,damage=perform(40011,0)
 assert single['observed']==0 and single['criticalHits']==0,(single,damage)
 assert p.evaluate('BFGlobalSingleHitCriticalV9300.snapshot().criticals')==1
 assert p.locator('#bf9500-critical-banner').is_hidden()
 assert damage>0
 burst,damage=perform(10011,0,'burst')
 assert burst['observed']==0 and burst['criticalHits']==0,(burst,damage)
 assert p.locator('#bf9500-critical-banner').is_hidden()
 p.locator('#mode').select_option('training')
 assert p.evaluate(api+'.snapshot().mode')=='training'
 p.locator('#mode').select_option('archive')
 p.locator('#reset').click()
 assert p.evaluate(api+'.snapshot().observed')==0
 assert saved==p.evaluate("""()=>({P:JSON.stringify(P),stored:localStorage.getItem('bf_global_offline_demo_v7')})""")
 p.evaluate('()=>{window.__v95=window.performUnit;return true}')
 p.add_script_tag(path=str(A/name))
 assert p.evaluate('window.__v95===window.performUnit')
 assert p.locator('#bf9500-multihit-critical').count()==1
 assert not errors,errors
 b.close()
print('PASS v95 source-backed multi-hit critical combat, exclusions, v93 coexistence, v7 save/offline')
