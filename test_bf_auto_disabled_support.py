"""Smart Auto must not suppress a usable buff for a disabled stronger caster."""
import ast
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parent
A=ROOT/'app/src/main/assets'
if '--source-only' in sys.argv:
    s=(ROOT/'prepare_coordinated_auto_v042.py').read_text()
    assert 'BFGlobalParalysisActionLockV6000?.paralyzed(p.id)' in s
    assert 'BFGlobalCurseBBLockV5900?.cursed(p.id)' in s
    assert 'python3 test_bf_auto_disabled_support.py' in (ROOT/'.github/workflows/build-debug-apk.yml').read_text()
    print('PASS source: Smart Auto coordination checks existing action/BB locks')
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
      window.__autoLockStorage=Object.create(null);window.__autoLockWrites=0;
      const db=window.__autoLockStorage;
      Object.defineProperty(window,'localStorage',{value:{
        getItem:k=>db[k]??null,setItem:(k,v)=>{window.__autoLockWrites++;db[k]=String(v)},
        removeItem:k=>{window.__autoLockWrites++;delete db[k]},
        clear:()=>{window.__autoLockWrites++;Object.keys(db).forEach(k=>delete db[k])},
        key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}
      }});
      window.alert=()=>{};window.confirm=()=>false;
      HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
      HTMLMediaElement.prototype.play=()=>Promise.resolve();
    }""")
    page.set_content((A/'index.html').read_text(),wait_until='load',timeout=90000)
    page.add_style_tag(path=str(A/'bf_home_nav.css'))
    for name in modules:page.add_script_tag(path=str(A/name))
    page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
    page.evaluate("""()=>{
      document.getElementById('bf041-smart-auto').checked=true;
      S.party[0].unitId=40021;S.party[1].unitId=40025;
      for(const p of S.party){p.hp=p.maxHp;p.bb=0;p.atkBuff=null;p.action=null;}
      S.party[0].bb=S.party[1].bb=100;
      S.enemies=[{...S.enemies[0],hp:100000,maxHp:100000,def:100}];
      window.__autoLockFresh=JSON.stringify(S);
    }""")
    state='()=>JSON.stringify({player:P,storage:window.__autoLockStorage,writes:window.__autoLockWrites})'
    before=page.evaluate(state)
    kinds='()=>{const plan=BF042AutoCoordination.plan(liveParty());return [plan.get(S.party[0]),plan.get(S.party[1])]}'
    assert page.evaluate(kinds)==['attack','burst']
    for code,cure in ((6,20230),(5,20220)):
        page.evaluate('S=JSON.parse(window.__autoLockFresh)')
        assert page.evaluate('(code)=>BFGlobalOriginalAilmentStateV5700.inflict(1,code)',code)
        actual=page.evaluate(kinds)
        assert actual[0]=='burst',('Disabled stronger caster suppressed usable support',code,actual)
        # Execute the real planned actions, keeping the existing status hooks.
        page.evaluate("""async()=>{
          const plan=BF042AutoCoordination.plan(liveParty());
          for(const p of S.party.slice(0,2)){
            p.action={kind:plan.get(p),target:0};
            await window.performUnit(p,epoch);
          }
        }""")
        assert page.evaluate('currentAtkBoost(S.party[0])')==30
        assert page.evaluate('S.party[0].bb')==0
        assert page.evaluate('S.party[1].bb')==100
        assert page.evaluate(state)==before
        removed=page.evaluate('(id)=>BFGlobalOriginalAilmentStateV5700.cure(1,id).removed',cure)
        assert removed==[code]
        page.evaluate('for(const p of S.party){p.atkBuff=null;p.action=null;}S.party[0].bb=S.party[1].bb=100')
        assert page.evaluate(kinds)==['attack','burst']
        # Expiry must restore the same selection without a permanent blacklist.
        page.evaluate('(code)=>BFGlobalOriginalAilmentStateV5700.inflict(1,code)',code)
        api='BFGlobalParalysisActionLockV6000' if code==6 else 'BFGlobalCurseBBLockV5900'
        page.evaluate(api+'.expireAfterTurn()')
        page.evaluate('S.round++');page.evaluate(api+'.expireAfterTurn()')
        page.evaluate('S.round++');assert page.evaluate(api+'.expireAfterTurn()')==[1]
        assert page.evaluate(kinds)==['attack','burst']
        assert page.evaluate(state)==before
        print('PASS',code,'disabled strongest yields to actual +30% BB; cure/expiry restore strongest; progress unchanged',flush=True)
    # Disable Smart Auto and retain the old null plan/fallback behavior.
    page.evaluate("document.getElementById('bf041-smart-auto').checked=false")
    assert page.evaluate('BF042AutoCoordination.plan(liveParty())') is None
    assert page.evaluate(state)==before
    assert not errors,errors
    browser.close()
