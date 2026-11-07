"""Manual offensive buttons cannot replace existing paid item Guard turns."""
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
    page.locator('.bf-navbar [data-bf-goto="quest"]').click()
    page.evaluate('''() => {
        for(const unit of S.party){
            unit.active=true;unit.unitId=10015;unit.action=null;unit.bb=100;
            unit.hp=unit.maxHp=10000;unit.atk=100;
        }
        S.party[0].hp=1;S.party[2].hp=0;
        S.enemies=[{...S.enemies[0],slot:0,hp:100000000,
            maxHp:100000000,def:100,atk:1}];
        E.speed.value='4';update();
        document.getElementById('bf043-sbb-preview').open=true;
        document.getElementById('bf044-enable').checked=true;
        BF044SBBDemo.refresh();
    }''')
    before = page.evaluate(SNAPSHOT)
    assert page.evaluate('BFGlobalDemoPotionV4200.usePotion(0)')
    assert page.evaluate('BFGlobalSourceFullReviveV4700.useFullRevive(1,2)')
    reservations = page.evaluate('BFGlobalItemTurnReservationsV4500.snapshot().reservations')
    stocks = page.evaluate('[BFGlobalDemoPotionV4200.snapshot().remaining,BFGlobalSourceFullReviveV4700.snapshot().remaining]')
    for slot in (0,1,2):
        for command in ('attack','burst'):
            page.locator('#slots > button').nth(slot).click()
            page.locator('#' + command).click()
            assert page.evaluate('slot=>S.party[slot].action.kind', slot) == 'guard', (
                slot, command, 'Manual command replaced a paid item Guard')
            assert page.evaluate('slot=>S.party[slot].bb', slot) == 100
    # SBB normally rejects any queued action. Exercise a cleared action, as the
    # existing reservation regression does, while leaving the paid ledger intact.
    page.evaluate('S.selected=0;S.party[0].action=null;update();BF044SBBDemo.refresh()')
    assert page.locator('#bf044-queue').is_enabled()
    page.locator('#bf044-queue').click()
    assert page.evaluate('S.party[0].action.kind') == 'guard'
    assert page.locator('#bf044-queue').is_disabled()
    assert page.evaluate('BFGlobalItemTurnReservationsV4500.snapshot().reservations') == reservations
    assert page.evaluate('[BFGlobalDemoPotionV4200.snapshot().remaining,BFGlobalSourceFullReviveV4700.snapshot().remaining]') == stocks
    assert_unchanged(page, before, 'blocked manual attacks/BB/SBB')
    # Unreserved allies still use the same real native buttons.
    for slot, command in ((3,'attack'),(4,'burst'),(5,'guard')):
        page.locator('#slots > button').nth(slot).click()
        page.locator('#' + command).click()
        assert page.evaluate('slot=>S.party[slot].action.kind', slot) == command
    page.locator('#execute').click()
    page.wait_for_function('!S.busy', timeout=30000)
    assert page.evaluate('S.round===2&&!S.over')
    assert page.evaluate('S.party.map(p=>p.bb)') == [100,100,100,100,0,100]
    assert page.evaluate('BFGlobalItemTurnReservationsV4500.snapshot().reservations') == []
    for command in ('attack','burst'):
        page.locator('#slots > button').nth(0).click()
        page.locator('#' + command).click()
        assert page.evaluate('S.party[0].action.kind') == command
    page.evaluate('S.selected=0;S.party[0].action=null;update();BF044SBBDemo.refresh()')
    page.locator('#bf044-queue').click()
    assert page.evaluate('S.party[0].action.kind') == 'sbb_demo'
    assert_unchanged(page, before, 'actual turn and released manual commands')
    assert not errors, errors
    browser.close()
print('PASS actual manual Attack/BB/SBB reservation guards, native turn, expiry and P/storage')
