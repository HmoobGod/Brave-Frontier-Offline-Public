"""v88: source-backed crystal rolls happen only after actual eligible DEMO normal attacks."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent; A=R/'app/src/main/assets'
js=(A/'bf8800_live_normal_crystal_events.js').read_text('utf8')
assert len(js.encode('utf8'))<65536
assert js.count('BF_GLOBAL_LIVE_NORMAL_CRYSTAL_EVENTS_V8800')==1
assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid','fetch(','XMLHttpRequest'))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf8400_original_normal_crystal_checks.js")')<java.index('readPackagedText("bf8800_live_normal_crystal_events.js")')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844}); errors=[]
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
              'bf8400_original_normal_crystal_checks.js','bf8800_live_normal_crystal_events.js'):
  p.add_script_tag(path=str(A/name))
 assert p.evaluate('P.version')==7
 assert p.evaluate('BFGlobalLiveNormalCrystalEventsV8800.source.allowedProfiles')==2258
 assert p.evaluate('BFGlobalLiveNormalCrystalEventsV8800.source.doesNotGrantPickups') is True
 assert p.locator('#bf8800-crystals').count()==1
 assert p.locator('#bf8800-crystals').evaluate('(el)=>el.parentElement.tagName')!='CANVAS'
 assert p.evaluate('BFGlobalLiveNormalCrystalEventsV8800.snapshot().observed')==0
 before=p.evaluate("""()=>({p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 p.evaluate("""()=>{S.enemies.forEach((e,i)=>{if(i>0)e.hp=0;else{
   e.hp=20000;e.maxHp=20000;e.def=0;e.atk=0}});
   S.party[0].unitId=10011;S.party[0].atk=800;S.party[0].bb=0;
   S.party[0].action={kind:'attack',target:0};
   for(let i=1;i<S.party.length;i++)if(S.party[i].active&&S.party[i].hp>0)
     S.party[i].action={kind:'guard',target:0};
   S.target=0;document.getElementById('speed').value='4';
   window.__v88random=Math.random;Math.random=()=>0;
 }""")
 p.evaluate('BF_debug.execute()')
 a=p.evaluate('BFGlobalLiveNormalCrystalEventsV8800.snapshot()')
 assert a['observed']==1,a
 assert a['battleCrystals']==6 and a['heartCrystals']==3,a
 assert a['recent'][0]['unitId']==10011 and a['recent'][0]['totalDropChecks']==6,a
 assert a['recent'][0]['normalHits']==3 and a['recent'][0]['checksPerHit']==2,a
 assert a['recent'][0]['overkill'] is False and a['recent'][0]['referenceOnly'] is True,a
 # The isolated test deliberately does not navigate the live battle tab.
 # Inspect DOM content; end-to-end visibility is covered by packaged UI suites.
 assert 'ORIGINAL NORMAL ATTACK BC / HC EVENTS' in p.locator('#bf8800-crystals summary').text_content()
 assert '6 BC / 3 HC' in p.locator('#bf8800-events').text_content()
 p.evaluate("""()=>{Math.random=()=>.99; S.party[0].action={kind:'attack',target:0};
   for(let i=1;i<S.party.length;i++)if(S.party[i].active&&S.party[i].hp>0)
     S.party[i].action={kind:'guard',target:0}}""")
 p.evaluate('BF_debug.execute()')
 a=p.evaluate('BFGlobalLiveNormalCrystalEventsV8800.snapshot()')
 assert a['observed']==2 and a['battleCrystals']==6 and a['heartCrystals']==3,a
 assert a['recent'][-1]['battleCrystals']==0 and a['recent'][-1]['heartCrystals']==0,a
 # Unknown/malformed archived normal frames never produce a crystal record.
 p.evaluate("""()=>{S.party[0].unitId=10023;S.party[0].action={kind:'attack',target:0};
   for(let i=1;i<S.party.length;i++)if(S.party[i].active&&S.party[i].hp>0)
     S.party[i].action={kind:'guard',target:0}}""")
 p.evaluate('BF_debug.execute()')
 assert p.evaluate('BFGlobalLiveNormalCrystalEventsV8800.snapshot().observed')==2
 # Guard has no production, even for an otherwise supported unit.
 p.evaluate("""()=>{S.party[0].unitId=10011;S.party[0].action={kind:'guard',target:0};
   for(let i=1;i<S.party.length;i++)if(S.party[i].active&&S.party[i].hp>0)
     S.party[i].action={kind:'guard',target:0}}""")
 p.evaluate('BF_debug.execute()')
 assert p.evaluate('BFGlobalLiveNormalCrystalEventsV8800.snapshot().observed')==2
 after=p.evaluate("""()=>({p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after, (before,after)
 p.evaluate('Math.random=window.__v88random')
 p.locator('#reset').click()
 assert p.evaluate('BFGlobalLiveNormalCrystalEventsV8800.snapshot().observed')==0
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalLiveNormalCrystalEventsV8800.snapshot().observed')==0
 p.add_script_tag(path=str(A/'bf8800_live_normal_crystal_events.js'))
 assert p.locator('#bf8800-crystals').count()==1
 assert not errors,errors
 b.close()
print('PASS v88 actual normal-attack-only source BC/HC rolls, unknown/guard exclusions, session isolation, v7 save')
