"""Actual Auto support execution rechecks changing ally state before spending BB."""
import ast
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parent
A=ROOT/'app/src/main/assets'
if '--source-only' in sys.argv:
    src=(ROOT/'prepare_source_aware_auto_v041.py').read_text()
    assert 'window.BF041SmartAuto?.reconsider?.(p);' in src
    assert 'function reconsider(p)' in src
    assert 'python3 test_bf_auto_support_recheck.py' in (ROOT/'.github/workflows/build-debug-apk.yml').read_text()
    print('PASS source: optional Auto support execution recheck registered')
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
      window.__recheckStorage=Object.create(null);window.__recheckWrites=0;
      const db=window.__recheckStorage;
      Object.defineProperty(window,'localStorage',{value:{
        getItem:k=>db[k]??null,setItem:(k,v)=>{window.__recheckWrites++;db[k]=String(v)},
        removeItem:k=>{window.__recheckWrites++;delete db[k]},
        clear:()=>{window.__recheckWrites++;Object.keys(db).forEach(k=>delete db[k])},
        key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}
      }});
      window.alert=()=>{};window.confirm=()=>false;
      HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
      HTMLMediaElement.prototype.play=()=>Promise.resolve();
    }""")
    page.set_content((A/'index.html').read_text(),wait_until='load',timeout=90000)
    page.add_style_tag(path=str(A/'bf_home_nav.css'))
    for name in modules:page.add_script_tag(path=str(A/name))
    page.add_script_tag(path=str(A/'bf10500_qol_advanced_smart_auto.js'))
    page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
    page.evaluate("""()=>{
      S.party[0].unitId=20041;S.party[1].unitId=30041;
      for(const p of S.party){p.hp=1;p.maxHp=500;p.bb=0;p.action=null;p.atkBuff=null;}
      S.party[0].bb=S.party[1].bb=100;
      S.enemies=[{...S.enemies[0],slot:0,hp:100000,maxHp:100000,def:1},
                 {...S.enemies[0],slot:1,hp:100000,maxHp:100000,def:1}];
      window.__recheckFresh=JSON.stringify(S);
      document.getElementById('bf041-smart-auto').checked=true;
      S.auto=true;document.getElementById('auto').checked=true;
    }""")
    state='()=>JSON.stringify({player:P,storage:window.__recheckStorage,writes:window.__recheckWrites})'
    before=page.evaluate(state)
    planned=page.evaluate("()=>{const plan=BF042AutoCoordination.plan(liveParty());for(const p of S.party.slice(0,2))p.action={kind:plan.get(p),target:0};return S.party.slice(0,2).map(p=>p.action.kind)}")
    assert planned==['burst','burst']
    page.evaluate('async()=>{await window.performUnit(S.party[0],epoch)}')
    assert page.evaluate('liveParty().every(p=>p.hp===p.maxHp)')
    assert page.evaluate('S.party[0].bb')==0
    enemy_before=page.evaluate('S.enemies[0].hp')
    page.evaluate('S.target=1')
    page.evaluate('async()=>{await window.performUnit(S.party[1],epoch)}')
    gauge=page.evaluate('S.party[1].bb')
    assert gauge==100,('Auto wasted second healer BB after full recovery',gauge)
    assert page.evaluate('S.party[1].action.kind')=='attack'
    assert page.evaluate('S.enemies[0].hp')<enemy_before
    assert page.evaluate('S.enemies[1].hp')==100000
    assert page.evaluate(state)==before
    # A disabled first healer must not suppress a still-needed second heal.
    page.evaluate('S=JSON.parse(window.__recheckFresh);S.auto=true')
    assert page.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,6)')
    page.evaluate("""async()=>{
      const plan=BF042AutoCoordination.plan(liveParty());
      for(const p of S.party.slice(0,2)){p.action={kind:plan.get(p),target:0};await window.performUnit(p,epoch);}
    }""")
    assert page.evaluate('S.party[0].bb')==100
    assert page.evaluate('S.party[1].bb')==0
    assert page.evaluate('liveParty().every(p=>p.hp===p.maxHp)')
    assert page.evaluate(state)==before
    # Manual BB commands and default Smart-OFF Auto keep their old behavior.
    for automatic,smart in ((False,True),(True,False)):
        page.evaluate('([automatic,smart])=>{S=JSON.parse(window.__recheckFresh);S.auto=automatic;document.getElementById("auto").checked=automatic;document.getElementById("bf041-smart-auto").checked=smart}',[automatic,smart])
        page.evaluate("""async()=>{
          for(const p of S.party.slice(0,2)){p.action={kind:'burst',target:0};await window.performUnit(p,epoch);}
        }""")
        assert page.evaluate('S.party.slice(0,2).map(p=>p.bb)')==[0,0]
        assert page.evaluate(state)==before
    # Execution must use the current Advanced threshold, not a closed-over base.
    for threshold,expected_gauge in ((35,100),(75,0)):
        page.evaluate('S=JSON.parse(window.__recheckFresh);S.auto=true;document.getElementById("bf041-smart-auto").checked=true;for(const p of S.party){p.hp=700;p.maxHp=1000;}')
        prior=json.loads(page.evaluate(state))
        assert page.evaluate('(heal)=>BFGlobalQoLAdvancedAutoV10500.set({on:true,heal,target:"percent",burst:"normal"})',threshold)
        setup=page.evaluate(state);checked=json.loads(setup)
        assert checked['player']==prior['player'] and checked['writes']==prior['writes']+1
        pref='bf_global_offline_qol_advanced_auto_v105'
        assert {k:v for k,v in checked['storage'].items() if k!=pref}=={k:v for k,v in prior['storage'].items() if k!=pref}
        page.evaluate("async()=>{S.party[1].action={kind:'burst',target:0};await window.performUnit(S.party[1],epoch)}")
        assert page.evaluate('S.party[1].bb')==expected_gauge
        assert page.evaluate('liveParty().every(p=>p.hp==='+str(700 if expected_gauge else 1000)+')')
        assert page.evaluate(state)==setup
    page.evaluate('S.auto=false;document.getElementById("auto").checked=false')
    assert not errors,errors
    print('PASS real Auto rechecks heals, disabled caster, Advanced thresholds, manual/default-OFF and progress intact',flush=True)
    browser.close()
