"""v90 actual source-roll ledger reconciles v88/v89 without collecting or saving."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf9000_live_crystal_provenance.js').read_text('utf8')
assert len(js.encode())<65536
assert js.count('BF_GLOBAL_LIVE_CRYSTAL_PROVENANCE_V9000')==1
assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid','fetch(','XMLHttpRequest'))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf8900_live_simple_bb_crystals.js")') < java.index('readPackagedText("bf9000_live_crystal_provenance.js")')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True, executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844});errors=[]
 p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""() => {const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),removeItem:k=>delete db[k],
 key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 for name in ('bf700_original_normal_hits.js','bf8100_original_crystal_drop_core.js',
              'bf8200_original_normal_crystal_checks.js','bf8300_original_burst_crystal_checks.js',
              'bf8400_original_normal_crystal_checks.js','bf8500_original_all_bb_checks.js',
              'bf8800_live_normal_crystal_events.js','bf8900_live_simple_bb_crystals.js',
              'bf9000_live_crystal_provenance.js'):
  p.add_script_tag(path=str(A/name))
 assert p.evaluate('P.version')==7
 api='BFGlobalLiveCrystalProvenanceV9000'
 assert p.evaluate(api+'.snapshot().totals.uncollectedBC')==0
 assert p.evaluate(api+'.validEvent({unitId:10023,referenceOnly:true,overkill:false,wave:1,battleCrystals:1,heartCrystals:0},"normal")') is False
 assert p.evaluate(api+'.validEvent({unitId:10011,referenceOnly:true,overkill:false,wave:1,battleCrystals:0,heartCrystals:0,normalHits:3,checksPerHit:2,totalDropChecks:6},"normal")') is True
 original=p.evaluate("""()=>({P:JSON.stringify(P),saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 p.evaluate("""()=>{S.enemies.forEach((e,i)=>{if(i>0)e.hp=0;else{e.hp=25000;e.maxHp=25000;e.def=0;e.atk=0}});
 S.party[0].unitId=10011;S.party[0].bb=100;S.party[0].atk=800;S.party[0].action={kind:'attack',target:0};
 for(let i=1;i<S.party.length;i++)if(S.party[i].active&&S.party[i].hp>0)S.party[i].action={kind:'guard',target:0};
 S.target=0;document.getElementById('speed').value='4';window.__random90=Math.random;Math.random=()=>0;}""")
 p.evaluate('BF_debug.execute()')
 n=p.evaluate('BFGlobalLiveNormalCrystalEventsV8800.snapshot()')
 assert n['observed']==1 and n['battleCrystals']==6 and n['heartCrystals']==3,n
 t=p.evaluate(api+'.refresh()')
 assert t['totals']['normalBC']==6 and t['totals']['normalHC']==3,t
 assert t['totals']['burstBC']==0 and t['totals']['uncollectedBC']==6,t
 p.evaluate("""()=>{S.party[0].bb=100;S.party[0].action={kind:'burst',target:0};
  for(let i=1;i<S.party.length;i++)if(S.party[i].active&&S.party[i].hp>0)S.party[i].action={kind:'guard',target:0}}""")
 p.evaluate('BF_debug.execute()')
 t=p.evaluate(api+'.refresh()')
 assert t['normalEvents']==1 and t['burstTargetEvents']==1,t
 assert t['totals']['normalBC']==6 and t['totals']['normalHC']==3,t
 assert t['totals']['burstBC']==5 and t['totals']['burstHC']==5,t
 assert t['totals']['uncollectedBC']==11 and t['totals']['uncollectedHC']==8,t
 assert t['collected'] is False and t['saved'] is False
 assert len(t['recent'])==2,t
 assert '11 BC / 8 HC' in p.locator('#bf9000-ledger-totals').text_content()
 assert p.evaluate("""()=>({P:JSON.stringify(P),saved:localStorage.getItem('bf_global_offline_demo_v7')})""")==original
 p.evaluate('Math.random=window.__random90')
 p.locator('#reset').click()
 assert p.evaluate(api+'.snapshot().totals.uncollectedBC')==0
 p.locator('#mode').select_option('training')
 assert p.evaluate(api+'.refresh().active') is False
 p.add_script_tag(path=str(A/'bf9000_live_crystal_provenance.js'))
 assert p.locator('#bf9000-crystal-provenance').count()==1
 assert not errors,errors
 b.close()
print('PASS v90 live normal/BB source ledger, exact totals, invalid profile, no collection, v7 save safety')
