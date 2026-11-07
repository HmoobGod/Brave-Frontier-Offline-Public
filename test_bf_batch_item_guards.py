"""Batch orders must preserve existing paid item/revive Guard reservations.

Synthetic player/storage only; uses the actual command buttons and executor.
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
    page.locator('.bf-navbar [data-bf-goto="quest"]').click()
    page.evaluate('''() => {
        for(const unit of S.party){
            unit.active=true;unit.unitId=10011;unit.action=null;unit.bb=100;
            unit.hp=unit.maxHp=10000;unit.atk=100;
        }
        S.party[0].hp=1;S.party[2].hp=0;S.party[4].bb=40;
        S.enemies=[{...S.enemies[0],slot:0,hp:100000000,
            maxHp:100000000,def:100,atk:1}];
        document.getElementById('speed').value='4';update();
    }''')
    before = page.evaluate(SNAPSHOT)
    assert page.evaluate('BFGlobalDemoPotionV4200.usePotion(0)')
    assert page.evaluate('BFGlobalSourceFullReviveV4700.useFullRevive(1,2)')
    assert page.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(3,5)')
    reservations = page.evaluate('BFGlobalItemTurnReservationsV4500.snapshot().reservations')
    assert [r['slot'] for r in reservations] == [0,1,2]
    stocks = page.evaluate('''() => ({potion:BFGlobalDemoPotionV4200.snapshot().remaining,
        revive:BFGlobalSourceFullReviveV4700.snapshot().remaining})''')
    for mode, expected in (
        ('attack', ['guard','guard','guard','attack','attack','attack']),
        ('guard', ['guard'] * 6),
        ('burst', ['guard','guard','guard','attack','attack','burst']),
    ):
        assert page.evaluate('mode=>BFGlobalBattleCommandsV2100.queueAll(mode)', mode)
        assert page.evaluate('S.party.map(p=>p.action.kind)') == expected, (
            mode, 'Batch orders overwrote paid item/revive Guard actions')
        assert page.evaluate('S.party.every(p=>p.bb===(p.id===4?40:100))&&!S.busy')
        assert page.evaluate('BFGlobalItemTurnReservationsV4500.snapshot().reservations') == reservations
        assert_unchanged(page, before, ('queued', mode))
    assert page.evaluate('''() => ({potion:BFGlobalDemoPotionV4200.snapshot().remaining,
        revive:BFGlobalSourceFullReviveV4700.snapshot().remaining})''') == stocks
    page.evaluate('''() => {
        window.__itemGuardPhase=null;
        const observer=new MutationObserver(()=>{
            if(E.phase.textContent==='Enemy phase'){
                __itemGuardPhase=S.party.map(p=>p.guard);observer.disconnect();
            }
        });
        observer.observe(E.phase,{childList:true,characterData:true,subtree:true});
    }''')
    assert page.evaluate('BFGlobalBattleCommandsV2100.executeTurn()')
    page.wait_for_function('!S.busy', timeout=30000)
    assert page.evaluate('__itemGuardPhase') == [True,True,True,False,False,False]
    assert page.evaluate('S.round===2&&!S.over')
    assert page.evaluate('S.party.map(p=>p.bb)') == [100,100,100,100,74,0]
    assert page.evaluate('BFGlobalItemTurnReservationsV4500.snapshot().reservations') == []
    assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("attack")')
    assert page.evaluate('S.party.every(p=>p.action.kind==="attack")')
    assert_unchanged(page, before, 'real turn and reservation expiry')
    # The optional ledger must not be required by older embeds.
    page.evaluate('''() => {
        window.__itemTurns=BFGlobalItemTurnReservationsV4500;
        delete window.BFGlobalItemTurnReservationsV4500;
    }''')
    assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("guard")')
    assert page.evaluate('S.party.every(p=>p.action.kind==="guard")')
    page.evaluate('window.BFGlobalItemTurnReservationsV4500=__itemTurns')
    assert_unchanged(page, before, 'optional ledger absent')
    assert not errors, errors
    browser.close()
print('PASS batch Attack/Guard/BB preserve paid Potion/revive guards, actual turn, expiry and P/storage')
