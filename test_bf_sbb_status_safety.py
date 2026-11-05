"""Experimental SBB obeys existing Curse and Paralysis, including queued casts."""
import ast
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parent
A=ROOT/'app/src/main/assets'
if '--source-only' in sys.argv:
    curse=(A/'bf5900_curse_bb_lock.js').read_text()
    sbb=(ROOT/'prepare_experimental_sbb_v044.py').read_text()
    assert "['burst','sbb_demo'].includes(p?.action?.kind)" in curse
    assert 'BFGlobalCurseBBLockV5900?.cursed(p?.id)' in sbb
    assert 'BFGlobalParalysisActionLockV6000?.paralyzed(p?.id)' in sbb
    assert 'python3 test_bf_sbb_status_safety.py' in (ROOT/'.github/workflows/build-debug-apk.yml').read_text()
    print('PASS source: queued BB/SBB and experimental SBB check existing status locks')
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
      window.__sbbLockStorage=Object.create(null);window.__sbbLockWrites=0;
      const db=window.__sbbLockStorage;
      Object.defineProperty(window,'localStorage',{value:{
        getItem:k=>db[k]??null,setItem:(k,v)=>{window.__sbbLockWrites++;db[k]=String(v)},
        removeItem:k=>{window.__sbbLockWrites++;delete db[k]},
        clear:()=>{window.__sbbLockWrites++;Object.keys(db).forEach(k=>delete db[k])},
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
      document.getElementById('bf044-enable').checked=true;
      S.selected=0;S.party[0].unitId=10015;S.party[0].bb=100;
      S.party[0].hp=S.party[0].maxHp;S.party[0].action=null;
      S.enemies=[{...S.enemies[0],slot:0,hp:100000,maxHp:100000,def:100},
                 {...S.enemies[0],slot:1,hp:100000,maxHp:100000,def:100}];
      window.__sbbLockFresh=JSON.stringify(S);
    }""")
    state='()=>JSON.stringify({player:P,storage:window.__sbbLockStorage,writes:window.__sbbLockWrites})'
    before=page.evaluate(state)
    assert page.evaluate('BF044SBBDemo.canQueue()')
    for code,cure in ((5,20220),(6,20230)):
        page.evaluate('S=JSON.parse(window.__sbbLockFresh)')
        assert page.evaluate('(code)=>BFGlobalOriginalAilmentStateV5700.inflict(0,code)',code)
        can_queue=page.evaluate('BF044SBBDemo.canQueue()')
        assert not can_queue,('Disabled actor can queue experimental SBB',code,can_queue)
        page.evaluate('BF044SBBDemo.refresh()')
        assert page.locator('#bf044-queue').is_disabled()
        assert page.evaluate('BF044SBBDemo.queue()') is False
        # Calling the exported prototype cannot bypass the status rules either.
        page.evaluate("async()=>{S.party[0].action={kind:'sbb_demo',target:0};await BF044SBBDemo.perform(S.party[0],epoch)}")
        assert page.evaluate('S.party[0].bb')==100
        hp=page.evaluate('S.enemies.map(e=>e.hp)')
        assert hp[1]==100000
        assert (hp[0]<100000) if code==5 else (hp[0]==100000)
        assert page.evaluate(state)==before
        # A previously valid queued action must be rechecked at execution.
        page.evaluate('S=JSON.parse(window.__sbbLockFresh)')
        assert page.evaluate('BF044SBBDemo.queue()') is True
        assert page.evaluate('(code)=>BFGlobalOriginalAilmentStateV5700.inflict(0,code)',code)
        page.evaluate('async()=>{await window.performUnit(S.party[0],epoch)}')
        assert page.evaluate('S.party[0].bb')==100
        hp=page.evaluate('S.enemies.map(e=>e.hp)')
        assert hp[1]==100000
        assert (hp[0]<100000) if code==5 else (hp[0]==100000)
        if code==5:assert page.evaluate('S.party[0].action.kind')=='attack'
        assert page.evaluate(state)==before
        # Cure restores the actual all-enemy prototype and normal gauge cost.
        assert page.evaluate('(id)=>BFGlobalOriginalAilmentStateV5700.cure(0,id).removed',cure)==[code]
        page.evaluate('S.selected=0;S.party[0].action=null')
        assert page.evaluate('BF044SBBDemo.canQueue()')
        assert page.evaluate('BF044SBBDemo.queue()')
        page.evaluate('async()=>{await window.performUnit(S.party[0],epoch)}')
        assert page.evaluate('S.party[0].bb')==0
        assert all(hp<100000 for hp in page.evaluate('S.enemies.map(e=>e.hp)'))
        assert page.evaluate(state)==before
        print('PASS',code,'SBB queue/direct/late execution blocked; cure restores actual all-enemy SBB; progress unchanged',flush=True)
    page.evaluate("document.getElementById('bf044-enable').checked=false;S.party[0].action=null;S.selected=0;S.party[0].bb=100")
    assert page.evaluate('BF044SBBDemo.canQueue()') is False
    assert page.evaluate(state)==before
    assert not errors,errors
    browser.close()
