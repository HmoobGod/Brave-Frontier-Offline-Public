"""v96: a multi-hit attack must not roll phantom criticals after lethal contact."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
js=(A/'bf9500_multihit_critical_combat.js').read_text('utf8')
assert js.count('V9600_OVERKILL_GUARD')==1
assert 'let remaining=local.target.hp;' in js
assert 'const landed=damage>0&&remaining>0;' in js
assert 'const critical=landed&&roll()===true;' in js
assert not any(x in js for x in ('localStorage','saveProgress(', 'BFAndroid','XMLHttpRequest','fetch('))
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
   getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),removeItem:k=>delete db[k],
   key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});
   window.alert=()=>{};window.confirm=()=>true;
   HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
   HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 for name in ('bf700_original_normal_hits.js','bf8100_original_crystal_drop_core.js',
   'bf8200_original_normal_crystal_checks.js','bf8300_original_burst_crystal_checks.js',
   'bf8400_original_normal_crystal_checks.js','bf9300_single_hit_critical_combat.js',
   'bf9500_multihit_critical_combat.js'):
  p.add_script_tag(path=str(A/name))
 saved=p.evaluate("""()=>({P:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 api='BFGlobalMultiHitCriticalV9500'
 def run(roll,foeHP):
  p.locator('#mode').select_option('archive')
  p.locator('#reset').click()
  p.evaluate("""({roll,foeHP})=>{
    S.enemies.forEach((e,i)=>{
      e.hp=i===0?foeHP:i===1?20000:0;
      e.maxHp=i===0?foeHP:20000;e.atk=0;e.def=0;
    });
    const u=S.party[0];u.unitId=10011;u.atk=800;u.bb=0;
    u.action={kind:'attack',target:0};
    for(let i=1;i<S.party.length;i++)
      if(S.party[i].active&&S.party[i].hp>0)
        S.party[i].action={kind:'guard',target:0};
    S.target=0;document.getElementById('speed').value='4';
    window.__v96random=Math.random;Math.random=()=>roll;seed=771;
  }""",{'roll':roll,'foeHP':foeHP})
  p.evaluate('BF_debug.execute()')
  event=p.evaluate(api+'.snapshot().recent[0]')
  result=p.evaluate("""()=>({hp:S.enemies[0].hp,notices:document.querySelectorAll('#log .bf9500-critical-notice').length})""")
  p.evaluate('Math.random=window.__v96random')
  return event,result
 allHits,alive=run(0,20000)
 assert allHits['rolls']==3 and allHits['criticals']==3,allHits
 assert all(h['landed'] and h['critical'] and h['appliedDamage']>0 for h in allHits['hits'])
 assert alive['hp']>0 and alive['notices']==1,(allHits,alive)
 lethal,dead=run(0,1)
 assert lethal['rolls']==1 and lethal['criticals']==1,lethal
 assert [x['landed'] for x in lethal['hits']]==[True,False,False],lethal
 assert [x['critical'] for x in lethal['hits']]==[True,False,False],lethal
 assert [x['appliedDamage'] for x in lethal['hits']]==[1,0,0],lethal
 assert dead['hp']==0 and dead['notices']==1,(lethal,dead)
 assert lethal['observedHpLoss']==1
 plain,deadPlain=run(.95,1)
 assert plain['rolls']==1 and plain['criticals']==0,plain
 assert [h['landed'] for h in plain['hits']]==[True,False,False],plain
 assert deadPlain['hp']==0 and deadPlain['notices']==0
 assert saved==p.evaluate("""()=>({P:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert not errors,errors
 b.close()
print('PASS v96 normal/multi-hit critical rollout respects KO, preserves v7 save and no phantom popup')
