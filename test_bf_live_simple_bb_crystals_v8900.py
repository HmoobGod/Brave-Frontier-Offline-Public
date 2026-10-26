"""v89: exact source-approved single-group BB crystal events after real burst damage."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf8900_live_simple_bb_crystals.js').read_text('utf8')
assert len(js.encode('utf8'))<65536
assert js.count('BF_GLOBAL_LIVE_SIMPLE_BB_CRYSTAL_EVENTS_V8900')==1
assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid','fetch(','XMLHttpRequest'))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf8500_original_all_bb_checks.js")')<java.index('readPackagedText("bf8900_live_simple_bb_crystals.js")')
assert java.index('readPackagedText("bf8800_live_normal_crystal_events.js")')<java.index('readPackagedText("bf8900_live_simple_bb_crystals.js")')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True, executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844});errs=[]
 p.on('pageerror',lambda e:errs.append(str(e)))
 p.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
  getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),removeItem:k=>delete db[k],
  key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});
  window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 for name in ('bf700_original_normal_hits.js','bf8100_original_crystal_drop_core.js',
              'bf8200_original_normal_crystal_checks.js','bf8300_original_burst_crystal_checks.js',
              'bf8400_original_normal_crystal_checks.js','bf8500_original_all_bb_checks.js',
              'bf8800_live_normal_crystal_events.js','bf8900_live_simple_bb_crystals.js'):
  p.add_script_tag(path=str(A/name))
 assert p.evaluate('P.version')==7
 assert p.evaluate('BFGlobalLiveSimpleBBCrystalsV8900.source.strictOffensiveProfiles')==213
 assert p.evaluate('BFGlobalLiveSimpleBBCrystalsV8900.snapshot().observed')==0
 old=p.evaluate("""()=>({p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 p.evaluate("""()=>{S.enemies.forEach((e,i)=>{if(i>0)e.hp=0;else{
   e.hp=20000;e.maxHp=20000;e.def=0;e.atk=0}});
   S.party[0].unitId=10011;S.party[0].bb=100;S.party[0].atk=800;
   S.party[0].action={kind:'burst',target:0};
   for(let i=1;i<S.party.length;i++)if(S.party[i].active&&S.party[i].hp>0)
     S.party[i].action={kind:'guard',target:0};
   S.target=0;document.getElementById('speed').value='4';
   window.__old89=Math.random;Math.random=()=>0;}""")
 p.evaluate('BF_debug.execute()')
 s=p.evaluate('BFGlobalLiveSimpleBBCrystalsV8900.snapshot()')
 assert s['observed']==1,s
 assert s['battleCrystals']==5 and s['heartCrystals']==5,s
 assert s['recent'][0]['unitId']==10011,s
 assert s['recent'][0]['skillId']==10011,s
 assert s['recent'][0]['simpleDamageEvents']==5,s
 assert p.evaluate('BFGlobalLiveNormalCrystalEventsV8800.snapshot().observed')==0
 assert '5 BC / 5 HC' in p.locator('#bf8900-events').text_content()
 # Source support skill #40021 lacks an offensive per-target timeline.
 p.evaluate("""()=>{S.party[0].unitId=40021;S.party[0].bb=100;
  S.party[0].action={kind:'burst',target:0};
  for(let i=1;i<S.party.length;i++)if(S.party[i].active&&S.party[i].hp>0)
    S.party[i].action={kind:'guard',target:0}}""")
 p.evaluate('BF_debug.execute()')
 assert p.evaluate('BFGlobalLiveSimpleBBCrystalsV8900.snapshot().observed')==1
 after=p.evaluate("""()=>({p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert old==after,(old,after)
 p.evaluate('Math.random=window.__old89')
 p.locator('#reset').click()
 assert p.evaluate('BFGlobalLiveSimpleBBCrystalsV8900.snapshot().observed')==0
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalLiveSimpleBBCrystalsV8900.snapshot().observed')==0
 p.add_script_tag(path=str(A/'bf8900_live_simple_bb_crystals.js'))
 assert p.locator('#bf8900-bb-crystals').count()==1
 assert not errs,errs
 b.close()
print('PASS v89 source-simple actual BB production, original BC/HC, v88 coexistence, v7 save safe')
