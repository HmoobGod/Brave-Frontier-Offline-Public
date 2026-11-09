"""Cursed Auto actors choose normal attacks before normal-hit handlers inspect them."""
import ast
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parent
A=ROOT/'app/src/main/assets'
if '--source-only' in sys.argv:
    smart=(ROOT/'prepare_source_aware_auto_v041.py').read_text()
    advanced=(A/'bf10500_qol_advanced_smart_auto.js').read_text()
    assert 'BFGlobalCurseBBLockV5900?.cursed(p?.id)' in smart
    assert 'if(!ownedAutoActor(unit))return previous' in advanced
    assert 'BFGlobalCurseBBLockV5900?.cursed(unit.id)' in advanced
    assert 'python3 test_bf_auto_curse_choice.py' in (ROOT/'.github/workflows/build-debug-apk.yml').read_text()
    print('PASS source: default/Smart/Advanced Auto respect existing Curse BB lock')
    raise SystemExit(0)

from playwright.sync_api import sync_playwright
tree=ast.parse((ROOT/'test_bf_paralysis_action_lock_v6000.py').read_text())
modules=next(ast.literal_eval(n) for n in ast.walk(tree) if isinstance(n,ast.Tuple) and
             n.elts and isinstance(n.elts[0],ast.Constant) and n.elts[0].value=='bf_home_nav.js')
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':393,'height':852})
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.route('**/*',lambda route:route.abort())
    page.evaluate("""()=>{
      window.__curseAutoStorage=Object.create(null);window.__curseAutoWrites=0;
      const db=window.__curseAutoStorage;
      Object.defineProperty(window,'localStorage',{value:{
        getItem:k=>db[k]??null,setItem:(k,v)=>{window.__curseAutoWrites++;db[k]=String(v)},
        removeItem:k=>{window.__curseAutoWrites++;delete db[k]},
        clear:()=>{window.__curseAutoWrites++;Object.keys(db).forEach(k=>delete db[k])},
        key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}
      }});
      window.alert=()=>{};window.confirm=()=>false;
      HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
      HTMLMediaElement.prototype.play=()=>Promise.resolve();
    }""")
    page.set_content((A/'index.html').read_text(),wait_until='load',timeout=90000)
    page.add_style_tag(path=str(A/'bf_home_nav.css'))
    for name in modules:page.add_script_tag(path=str(A/name))
    for name in ('bf700_original_normal_hits.js','bf8100_original_crystal_drop_core.js',
                 'bf8200_original_normal_crystal_checks.js','bf8300_original_burst_crystal_checks.js',
                 'bf8400_original_normal_crystal_checks.js','bf8800_live_normal_crystal_events.js',
                 'bf9300_single_hit_critical_combat.js','bf9500_multihit_critical_combat.js',
                 'bf10500_qol_advanced_smart_auto.js','bf_sbb_fallback_dispatch.js'):
        page.add_script_tag(path=str(A/name))
    page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
    page.evaluate("""()=>{
      for(const p of S.party){p.active=p.id===0;p.hp=200;p.maxHp=1000;p.action=null;p.atkBuff=null;}
      S.party[0].unitId=10011;S.party[0].bb=100;
      S.enemies=[{...S.enemies[0],slot:0,hp:100000,maxHp:100000,atk:1,def:1}];
      window.__curseAutoFresh=JSON.stringify(S);
      document.getElementById('speed').value='4';
    }""")
    state='()=>JSON.stringify({player:P,storage:window.__curseAutoStorage,writes:window.__curseAutoWrites})'
    for smart,unit,gauge,advanced in ((False,10011,100,False),(True,10011,100,False),
                                      (False,10011,40,False),(True,20041,100,True)):
        page.evaluate('([smart,unit,gauge])=>{S=JSON.parse(window.__curseAutoFresh);S.party[0].unitId=unit;S.party[0].bb=gauge;document.getElementById("bf041-smart-auto").checked=smart}',[smart,unit,gauge])
        if advanced:
            prior=json.loads(page.evaluate(state))
            assert page.evaluate('BFGlobalQoLAdvancedAutoV10500.set({on:true,heal:75,target:"percent",burst:"normal"})')
            setup=json.loads(page.evaluate(state));pref='bf_global_offline_qol_advanced_auto_v105'
            assert setup['player']==prior['player'] and setup['writes']==prior['writes']+1
            assert {k:v for k,v in setup['storage'].items() if k!=pref}=={k:v for k,v in prior['storage'].items() if k!=pref}
        before=page.evaluate(state)
        assert page.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,5)')
        planned=page.evaluate('BF041SmartAuto.kindFor(S.party[0])')
        page.evaluate("""()=>{
          S.auto=true;document.getElementById('auto').checked=true;
          window.__curseAutoRandom=Math.random;Math.random=()=>0;
          window.__curseAutoSeen=false;
          window.__curseAutoStop=new MutationObserver(()=>{
            if(E.phase.textContent==='Enemy phase'){
              S.auto=false;document.getElementById('auto').checked=false;
              window.__curseAutoSeen=true;window.__curseAutoStop.disconnect();
            }
          });
          window.__curseAutoStop.observe(E.phase,{childList:true,characterData:true,subtree:true});
          scheduleAuto();
        }""")
        page.wait_for_function('()=>window.__curseAutoSeen&&!S.busy',timeout=30000)
        page.evaluate('Math.random=window.__curseAutoRandom')
        critical=page.evaluate('BFGlobalSingleHitCriticalV9300.snapshot().recent.concat(BFGlobalMultiHitCriticalV9500.snapshot().recent)')
        assert any(e['unitId']==unit and (e.get('critical') is True or e.get('criticals',0)>0) for e in critical), ('Cursed Auto missed normal critical processing',planned)
        assert planned=='attack'
        assert any(e['unitId']==unit for e in page.evaluate('BFGlobalLiveNormalCrystalEventsV8800.snapshot().recent'))
        assert page.evaluate('S.enemies[0].hp')<100000
        assert page.evaluate('S.party[0].bb')==gauge
        assert page.evaluate('S.round===JSON.parse(window.__curseAutoFresh).round+1')
        assert page.evaluate(state)==before
        print('PASS',smart,unit,gauge,advanced,'actual cursed Auto normal critical/crystal path and gauge lock; progress unchanged',flush=True)
    before=page.evaluate(state)
    assert page.evaluate('BFGlobalOriginalAilmentStateV5700.cure(0,20220).removed')==[5]
    page.evaluate('S.party[0].unitId=10011;S.party[0].bb=100')
    assert page.evaluate('BF041SmartAuto.kindFor(S.party[0])')=='burst'
    assert page.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,5)')
    assert page.evaluate('BF041SmartAuto.kindFor(S.party[0])')=='attack'
    assert page.evaluate('BFGlobalCurseBBLockV5900.expireAfterTurn()')==[]
    page.evaluate('S.round++');assert page.evaluate('BFGlobalCurseBBLockV5900.expireAfterTurn()')==[]
    page.evaluate('S.round++');assert page.evaluate('BFGlobalCurseBBLockV5900.expireAfterTurn()')==[0]
    assert page.evaluate('BF041SmartAuto.kindFor(S.party[0])')=='burst'
    assert page.evaluate(state)==before
    assert not errors,errors
    browser.close()
