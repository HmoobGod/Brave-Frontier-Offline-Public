"""Existing target fallback must retain normal critical/reference-crystal handlers."""
from pathlib import Path
import ast
import shutil
import sys

R = Path(__file__).resolve().parent
A = R / 'app/src/main/assets'
modules = ('bf8800_live_normal_crystal_events.js',
           'bf9300_single_hit_critical_combat.js',
           'bf9500_multihit_critical_combat.js')
for name in modules:
    js = (A / name).read_text()
    assert "typeof pickTarget==='function'?pickTarget(" in js, name
assert 'python3 test_bf_normal_retarget.py' in (R / '.github/workflows/build-debug-apk.yml').read_text()
if '--source-only' in sys.argv:
    print('PASS normal-hit handlers reuse existing engine target selector')
    raise SystemExit(0)

from playwright.sync_api import sync_playwright
from bf_capture_progress_audit import INSTALL_STORAGE, SNAPSHOT, assert_unchanged

tree = ast.parse((R / 'test_bf_paralysis_action_lock_v6000.py').read_text())
base = next(ast.literal_eval(n) for n in ast.walk(tree)
            if isinstance(n, ast.Tuple) and n.elts
            and isinstance(n.elts[0], ast.Constant)
            and n.elts[0].value == 'bf_home_nav.js')
with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path=shutil.which('chromium') or
                                shutil.which('google-chrome'), args=['--no-sandbox'])
    page = browser.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.route('**/*', lambda route: route.abort())
    page.evaluate(INSTALL_STORAGE)
    page.evaluate('''()=>{HTMLMediaElement.prototype.play=()=>Promise.resolve();
      HTMLMediaElement.prototype.pause=()=>{};HTMLMediaElement.prototype.load=()=>{}}''')
    page.set_content((A / 'index.html').read_text())
    page.add_style_tag(path=str(A / 'bf_home_nav.css'))
    for name in base:
        page.add_script_tag(path=str(A / name))
    for name in ('bf700_original_normal_hits.js', 'bf8100_original_crystal_drop_core.js',
                 'bf8200_original_normal_crystal_checks.js', 'bf8300_original_burst_crystal_checks.js',
                 'bf8400_original_normal_crystal_checks.js', *modules):
        page.add_script_tag(path=str(A / name))
    page.locator('.bf-navbar [data-bf-goto="quest"]').click()
    page.evaluate('window.__retargetStart=JSON.stringify(S)')
    for unit in (10011, 40011):  # source multi-hit and single-hit normal profiles
        for case in ('queued-ko', 'already-dead', 'live-target', 'paralyzed'):
            page.evaluate('''({unit,scenario})=>{
              S=JSON.parse(__retargetStart);
              for(const u of S.party){u.active=u.id<2;u.action=null;u.hp=1000;u.maxHp=1000;u.bb=0}
              S.party[0].unitId=10011;S.party[1].unitId=unit;
              const e={...S.enemies[0],def:1,atk:1};
              S.enemies=[{...e,slot:0,name:'First',hp:scenario==='already-dead'?0:1,maxHp:1},
                {...e,slot:1,name:'Survivor',hp:100000,maxHp:100000}];
              S.selected=0;S.target=0;document.getElementById('speed').value='4';update();
            }''', {'unit': unit, 'scenario': case})
            page.locator('#attack' if case in ('queued-ko', 'paralyzed') else '#guard').click()
            if case == 'live-target':
                page.evaluate('()=>{S.target=1;update()}')
            page.locator('#attack').click()
            if case == 'already-dead':
                # Queue() already repairs dead targets. Model a queued action whose
                # target subsequently died, while the preceding ally only guards.
                page.evaluate('S.party[1].action.target=0')
            if case == 'paralyzed':
                assert page.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(1,6)')
            assert page.evaluate('S.party[1].action.target') == (1 if case == 'live-target' else 0)
            before = page.evaluate(SNAPSHOT)
            page.evaluate('''async()=>{const old=Math.random;Math.random=()=>0;
              try{await BF_debug.execute()}finally{Math.random=old}}''')
            events = page.evaluate('''BFGlobalSingleHitCriticalV9300.snapshot().recent
              .concat(BFGlobalMultiHitCriticalV9500.snapshot().recent).filter(e=>e.slot===1)''')
            crystals = page.evaluate('BFGlobalLiveNormalCrystalEventsV8800.snapshot().recent')
            if case == 'paralyzed':
                assert not events, events
                assert page.evaluate('S.enemies[1].hp') == 100000
                assert all(e['target'] != 'Survivor' for e in crystals), crystals
            else:
                assert len(events) == 1, (unit, case, events)
                event = events[0]
                assert event.get('critical') is True or event.get('criticals', 0) > 0, event
                loss = 100000 - page.evaluate('S.enemies[1].hp')
                assert loss > 0 and event['observedHpLoss'] == loss, (event, loss)
                assert sum(e['target'] == 'Survivor' and e['unitId'] == unit
                           and e['referenceOnly'] is True for e in crystals) == 1, crystals
            assert_unchanged(page, before, (unit, case))
            print('PASS normal retarget', unit, case, 'critical/reference events and unchanged P/storage', flush=True)
    assert not errors, errors
    browser.close()
