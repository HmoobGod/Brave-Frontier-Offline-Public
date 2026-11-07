"""Batch BB commands must fall back to Attack for existing Curse locks.

Real command/status/execute handlers, isolated synthetic P and storage only.
"""
import ast
from pathlib import Path
import shutil

from playwright.sync_api import sync_playwright
from bf_capture_progress_audit import INSTALL_STORAGE, SNAPSHOT, assert_unchanged

ROOT = Path(__file__).resolve().parent
A = ROOT / 'app/src/main/assets'
tree = ast.parse((ROOT / 'test_bf_paralysis_action_lock_v6000.py').read_text())
modules = next(ast.literal_eval(n) for n in ast.walk(tree)
               if isinstance(n, ast.Tuple) and n.elts
               and isinstance(n.elts[0], ast.Constant)
               and n.elts[0].value == 'bf_home_nav.js')
with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path=shutil.which('chromium') or
        shutil.which('google-chrome'), args=['--no-sandbox', '--disable-dev-shm-usage'])
    page = browser.new_page(viewport={'width':393, 'height':852})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.route('**/*', lambda request: request.abort())
    page.evaluate(INSTALL_STORAGE)
    page.evaluate('''() => {
        HTMLMediaElement.prototype.load=()=>{};
        HTMLMediaElement.prototype.pause=()=>{};
        HTMLMediaElement.prototype.play=()=>Promise.resolve();
    }''')
    page.set_content((A / 'index.html').read_text())
    page.add_style_tag(path=str(A / 'bf_home_nav.css'))
    for name in modules:
        page.add_script_tag(path=str(A / name))
    for name in ('bf700_original_normal_hits.js','bf8100_original_crystal_drop_core.js',
                 'bf8200_original_normal_crystal_checks.js','bf8300_original_burst_crystal_checks.js',
                 'bf8400_original_normal_crystal_checks.js','bf8800_live_normal_crystal_events.js',
                 'bf9300_single_hit_critical_combat.js','bf9500_multihit_critical_combat.js'):
        page.add_script_tag(path=str(A / name))
    page.locator('.bf-navbar [data-bf-goto="quest"]').click()
    page.evaluate('''() => {
        for(const unit of S.party){
            unit.active=true;unit.action=null;unit.bb=100;unit.unitId=10011;
            unit.hp=unit.maxHp=10000;
        }
        S.enemies=[{...S.enemies[0],slot:0,hp:100000000,
            maxHp:100000000,def:100,atk:1}];
        document.getElementById('speed').value='4';update();
        window.__trayFresh=JSON.stringify(S);
    }''')
    before = page.evaluate(SNAPSHOT)
    api = 'BFGlobalBattleCommandsV2100'
    for cursed in (0,2,5):
        page.evaluate('S=JSON.parse(__trayFresh);update()')
        assert page.evaluate('slot=>BFGlobalOriginalAilmentStateV5700.inflict(slot,5)', cursed)
        assert page.evaluate(api + '.queueAll("burst")'), (
            cursed, 'Ready BB + Attack stopped partway through a cursed squad')
        assert page.evaluate('S.party.map(p=>p.action.kind)') == [
            'attack' if slot == cursed else 'burst' for slot in range(6)]
        assert page.evaluate('S.party.every(p=>p.bb===100)&&!S.busy&&S.round===1')
        # The original Curse gate still refuses an individual BB command.
        page.evaluate('slot=>{S.selected=slot;update();E.burst.click()}', cursed)
        assert page.evaluate('slot=>S.party[slot].action.kind', cursed) == 'attack'
        assert page.evaluate('(slot)=>BFGlobalOriginalAilmentStateV5700.cure(slot,20220).removed', cursed) == [5]
        assert page.evaluate(api + '.queueAll("burst")')
        assert page.evaluate('S.party.every(p=>p.action.kind==="burst")')
        assert_unchanged(page, before, ('queue/cure', cursed))
        print('PASS batch BB Curse fallback and cure', cursed, flush=True)
    page.evaluate('S=JSON.parse(__trayFresh);S.party[3].bb=40;update()')
    assert page.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(2,5)')
    assert page.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(1,6)')
    page.evaluate('Math.random=()=>0')
    assert page.evaluate(api + '.queueAll("burst")')
    assert page.evaluate('S.party.map(p=>p.action.kind)') == [
        'burst','burst','attack','attack','burst','burst']
    assert page.evaluate(api + '.executeTurn()')
    page.wait_for_function('!S.busy', timeout=30000)
    assert page.evaluate('S.round===2&&!S.over&&!S.auto')
    assert page.evaluate('S.party.map(p=>p.bb)') == [0,100,100,74,0,0]
    events = page.evaluate('BFGlobalMultiHitCriticalV9500.snapshot().recent')
    assert any(e['slot'] == 2 and e['observedHpLoss'] > 0 for e in events), events
    assert not any(e['slot'] == 1 for e in events), events
    assert_unchanged(page, before, 'actual mixed squad turn')
    # Existing busy/Auto/invalid-command refusals remain in force.
    page.evaluate('S.busy=true')
    assert not page.evaluate(api + '.queueAll("burst")')
    page.evaluate('S.busy=false;S.auto=true')
    assert not page.evaluate(api + '.queueAll("burst")')
    page.evaluate('S.auto=false')
    assert not page.evaluate(api + '.queueAll("invalid")')
    assert_unchanged(page, before, 'existing refusal guards')
    assert not errors, errors
    browser.close()
print('PASS actual batch turn: Curse Attack, healthy BB, low gauge Attack, Paralysis skip, P/storage intact')
