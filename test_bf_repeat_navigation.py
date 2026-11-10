"""Real router, result replay and Auto timers must stop repeating on Quest exit.

Uses disposable memory-only player/storage and synthetic completed results;
no real save, fabricated reward execution or Android acceptance is claimed.
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
# Include the real story/result dependencies, up to the result controller.
modules = modules[:modules.index('bf3000_battle_results.js') + 1]

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path=shutil.which('chromium') or
        shutil.which('google-chrome'), args=['--no-sandbox', '--disable-dev-shm-usage'])
    for route, phase in [('home', 'pending'), ('units', 'pending'),
                         ('summon', 'pending'), ('menu', 'pending'),
                         ('home', 'running'), ('menu', 'result')]:
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
        page.add_script_tag(path=str(A / 'bf9800_qol_cleared_quest_repeat.js'))
        page.evaluate('''() => {
            BF_homeNav.go('quest');
            document.getElementById('mode').value='archive';BF_debug.reset();
            P.questClears[QUEST.missionId]=1;
            // The source-backed replay gate now requires an explicit positive
            // economy receipt and exact live/source wave parity. This isolated
            // navigation fixture supplies those proofs without altering
            // production campaign records or owner storage.
            QUEST.battles=Number.isSafeInteger(QUEST.battles)&&QUEST.battles>0
                ?QUEST.battles:1;
            S.totalWaves=QUEST.battles;
            // Keep the real campaign's navigation API: the battle HUD calls
            // nextPlayable() while building its result snapshot. Replace only
            // readiness responses in this disposable browser fixture.
            const campaign=window.BFGrandGaiaCampaignV100;
            if(!campaign||typeof campaign.nextPlayable!=='function')
                throw Error('Source campaign navigation fixture unavailable');
            // Copy frozen campaign methods into a writable, independent mock.
            // Inheriting their read-only properties blocks Object.assign overrides.
            window.BFGrandGaiaCampaignV100=Object.assign({},campaign,{
                waveReadiness:id=>({missionId:id,verifiedWaveCount:QUEST.battles}),
                sourceEconomyReadiness:()=>true
            });
            // Commit only the disposable fixture's clear before the baseline.
            // Native Auto Repeat now requires a matching canonical v7 receipt.
            localStorage.setItem('bf_global_offline_demo_v7',JSON.stringify(P));
            S.over=true;S.phase='Victory';update();
            document.getElementById('speed').value='4';
            window.__navExecutions=0;
            const realExecute=execute;
            execute=async function(...args){
                __navExecutions++;return await realExecute.apply(this,args);
            };
        }''')
        before = page.evaluate(SNAPSHOT)
        round_before = page.evaluate('''({route,phase}) => {
            if(!BFGlobalQoLQuestRepeatV9800.start(2))throw Error('Fixture not eligible');
            // Keep a genuine round non-terminal so no rewards are written.
            for(const unit of S.party){
                unit.active=unit.id===0;unit.action=null;unit.bb=0;
                unit.hp=unit.maxHp=100000;unit.atk=100;
            }
            S.enemies=[{...S.enemies[0],slot:0,hp:100000000,
                maxHp:100000000,def:100,atk:1}];
            const round=S.round;
            // Navigate in the same task as Start: the pending timer cannot race
            // browser automation on slower CI machines.
            if(phase==='pending')document.querySelector(
                '.bf-navbar [data-bf-goto="'+route+'"]').click();
            return round;
        }''', {'route':route, 'phase':phase})
        if phase == 'running':
            page.wait_for_function('S.busy && __navExecutions===1')
        elif phase == 'result':
            # Native finish disables Auto before the repeat poll sees a result.
            # Model only that completed-result state, never call reward code.
            page.evaluate('''() => {
                if(timer){clearTimeout(timer);timer=null;}
                S.over=true;S.phase='Victory';S.auto=false;E.auto.checked=false;
                P.questClears[QUEST.missionId]++;
                // This synthetic completed result must have a matching committed
                // receipt before the later explicit restart eligibility check.
                localStorage.setItem('bf_global_offline_demo_v7',JSON.stringify(P));
            }''')
            before = page.evaluate(SNAPSHOT)
        if phase != 'pending':
            # Includes the same router path used by programmatic/native Back.
            page.evaluate('route=>BF_homeNav.go(route)', route)
        assert page.evaluate('BF_homeNav.current') == route
        assert not page.evaluate('BFGlobalQoLQuestRepeatV9800.statusSnapshot().active'), (
            route, phase, 'Repeat continued after leaving Quest')
        assert page.evaluate('!S.auto && !E.auto.checked && timer===null')
        if phase == 'running':
            page.wait_for_function('!S.busy', timeout=30000)
        assert page.evaluate('S.round') == round_before + (phase == 'running')
        calls = page.evaluate('__navExecutions')
        assert calls == (phase == 'running')
        page.evaluate("BF_homeNav.go('quest')")
        page.wait_for_timeout(1200)  # Includes a real repeat polling interval.
        assert not page.evaluate('BFGlobalQoLQuestRepeatV9800.statusSnapshot().active')
        assert page.evaluate('__navExecutions') == calls
        assert page.evaluate('!S.auto && !E.auto.checked && timer===null')
        assert_unchanged(page, before, (route, phase))
        # A completed result cannot start a repeat from another page.
        page.evaluate('''() => {S.over=true;S.phase='Victory';BF_homeNav.go('menu')}''')
        assert not page.evaluate('BFGlobalQoLQuestRepeatV9800.start(2)')
        assert page.locator('#bf9800-start').is_disabled()
        assert_unchanged(page, before, 'off-Quest start refused')
        page.evaluate('''() => {
            BF_homeNav.go('quest');
            const repeat=BFGlobalQoLQuestRepeatV9800;
            if(!repeat.start(2))throw Error('Explicit Quest restart rejected');
            if(!BF_homeNav.go('quest')||BF_homeNav.go('invalid-route')||
               !repeat.statusSnapshot().active)throw Error('Unchanged/rejected route cancelled repeat');
            // A missed event must still be caught by the polling guard.
            const dispatch=window.dispatchEvent;
            window.dispatchEvent=function(event){
                return event.type==='bf-route-change'?true:dispatch.call(this,event);
            };
            try{BF_homeNav.go('menu')}finally{window.dispatchEvent=dispatch}
            if(!repeat.statusSnapshot().active)throw Error('Fixture did not suppress route event');
            repeat.poll();
            if(repeat.statusSnapshot().active||S.auto||E.auto.checked||timer!==null)
                throw Error('Missed-event polling fallback failed');
            // Ordinary manual Auto retains its pre-existing navigation behavior.
            BF_homeNav.go('quest');E.auto.click();BF_homeNav.go('home');
            if(!S.auto||!E.auto.checked)throw Error('Unrelated manual Auto changed');
            E.auto.click();
        }''')
        assert_unchanged(page, before, 'explicit restart, fallback and manual Auto')
        assert not errors, errors
        print('PASS repeat navigation', route, phase, 'real Auto + result replay; P/storage intact', flush=True)
        page.close()
    browser.close()
