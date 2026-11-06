"""Hidden-route paint suppression preserves live combat, effects and saves."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
from bf_capture_progress_audit import INSTALL_STORAGE, SNAPSHOT, assert_unchanged

ROOT = Path(__file__).resolve().parent
A = ROOT/'app/src/main/assets'
with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path=shutil.which('chromium') or
        shutil.which('google-chrome'), args=['--no-sandbox', '--disable-dev-shm-usage'])
    page = browser.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.route('**/*', lambda route: route.abort())
    page.evaluate(INSTALL_STORAGE)
    page.evaluate('''() => {
        HTMLMediaElement.prototype.play=()=>Promise.resolve();
        HTMLMediaElement.prototype.pause=()=>{};
        HTMLMediaElement.prototype.load=()=>{};
    }''')
    page.set_content((A/'index.html').read_text())
    page.add_style_tag(path=str(A/'bf_home_nav.css'))
    page.add_script_tag(path=str(A/'bf_home_nav.js'))
    page.evaluate('''() => {
        const host=document.createElement('div');host.id='bf2000-run';
        document.body.append(host);
        window.__renderPaints=0;window.__renderClear=ctx.clearRect.bind(ctx);
        ctx.clearRect=function(...args){__renderPaints++;return __renderClear(...args)};
    }''')
    baseline = page.evaluate(SNAPSHOT)
    page.add_script_tag(path=str(A/'bf9900_qol_battle_speed.js'))
    page.evaluate('()=>{window.__renderInstalled=draw}')
    page.add_script_tag(path=str(A/'bf9900_qol_battle_speed.js'))
    assert page.evaluate('__renderInstalled===draw')
    assert_unchanged(page, baseline, 'renderer installation')
    state = page.evaluate('JSON.stringify(S)')
    frame_sample = '''async () => {
        for(let i=0;i<3;i++)await new Promise(requestAnimationFrame);
        __renderPaints=0;
        for(let i=0;i<8;i++)await new Promise(requestAnimationFrame);
        return __renderPaints;
    }'''
    for route, visible in (('home',False),('quest',True),('menu',False),('quest',True)):
        page.evaluate('route=>BF_homeNav.go(route)', route)
        count = page.evaluate(frame_sample)
        assert count == (8 if visible else 0), (route,count)
        assert page.evaluate('JSON.stringify(S)') == state, route
        assert_unchanged(page, baseline, route)
        print('PASS battle renderer',route,'paint calls',count,flush=True)
    page.evaluate('''() => {
        BF_homeNav.go('home');
        effects.push({x:1,y:1,color:'#fff',at:performance.now()-10000,
            life:1,__renderExpired:true});
        effects.push({x:1,y:1,color:'#fff',at:performance.now(),
            life:60000,__renderActive:true});
    }''')
    assert page.evaluate(frame_sample) == 0
    assert page.evaluate('!effects.some(fx=>fx.__renderExpired)')
    assert page.evaluate('effects.some(fx=>fx.__renderActive)')
    # A hidden canvas must not pause, fast-forward or skip the battle executor.
    page.evaluate('''() => {
        for(const unit of S.party){
            unit.active=unit.id===0;unit.action=null;
            unit.hp=unit.maxHp=100000;unit.atk=100;unit.bb=0;
        }
        S.enemies=[{...S.enemies[0],slot:0,hp:100000000,
            maxHp:100000000,def:100,atk:1}];
        S.party[0].action={kind:'attack',target:0};S.auto=false;
        __renderPaints=0;
    }''')
    round_before = page.evaluate('S.round')
    page.evaluate('async()=>{await BF_debug.execute()}')
    assert page.evaluate('S.round') == round_before+1
    assert page.evaluate('S.enemies[0].hp<100000000 && !S.busy && !S.over')
    assert page.evaluate('__renderPaints') == 0
    assert page.evaluate('BF_homeNav.current') == 'home'
    assert_unchanged(page, baseline, 'real hidden-route combat')
    page.evaluate("BF_homeNav.go('quest')")
    assert page.evaluate(frame_sample) == 8
    assert_unchanged(page, baseline, 'painting resumes after combat')
    assert not errors, errors
    browser.close()
print('PASS hidden-route rendering, live combat, effect expiration, idempotence and full P/storage preservation')
