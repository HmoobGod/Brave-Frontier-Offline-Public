"""Real Auto scheduling with synthetic visibility events and memory-only saves.

This exercises page lifecycle handling, not physical Android lifecycle delivery.
"""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
from bf_capture_progress_audit import INSTALL_STORAGE, SNAPSHOT, assert_unchanged

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'app/src/main/assets'
with sync_playwright() as pw:
    browser = pw.chromium.launch(
        executable_path=shutil.which('chromium') or shutil.which('google-chrome'),
        args=['--no-sandbox', '--disable-dev-shm-usage'])
    page = browser.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.route('**/*', lambda route: route.abort())
    page.evaluate(INSTALL_STORAGE)
    page.evaluate('''() => {
        HTMLMediaElement.prototype.play=()=>Promise.resolve();
        HTMLMediaElement.prototype.pause=()=>{};
        HTMLMediaElement.prototype.load=()=>{};
        window.__autoHidden=false;
        Object.defineProperty(document,'hidden',{get:()=>__autoHidden});
    }''')
    page.set_content((ASSETS/'index.html').read_text())
    # Production optional planners replace the frozen Auto API using spreads;
    # the shared lifecycle operation must survive both replacements.
    for module in ('bf10500_qol_advanced_smart_auto.js','bf_auto_sbb_demo.js'):
        page.add_script_tag(path=str(ASSETS/module))
        assert page.evaluate("typeof BF041SmartAuto.pauseForBackground==='function'")
    page.evaluate('''() => {
        document.getElementById('mode').value='archive';BF_debug.reset();
        for(const unit of S.party){
            unit.active=unit.id===0;unit.action=null;unit.bb=0;
            unit.hp=unit.maxHp=100000;unit.atk=100;
        }
        S.enemies=[{...S.enemies[0],slot:0,hp:100000000,
            maxHp:100000000,def:100,atk:1}];
        document.getElementById('speed').value='4';
        window.__backgroundCalls=0;window.__backgroundExecute=execute;
        execute=async function(...args){
            __backgroundCalls++;
            return await __backgroundExecute.apply(this,args);
        };
        window.__setAutoHidden=(hidden,notify=true)=>{
            __autoHidden=hidden;
            if(notify)document.dispatchEvent(new Event('visibilitychange'));
        };
    }''')
    baseline = page.evaluate(SNAPSHOT)
    assert page.evaluate('BF041SmartAuto.pauseForBackground()') is False
    # Pending timers cancel without queueing any actions, with Smart on or off.
    for smart in (False, True):
        page.evaluate('''smart => {
            __setAutoHidden(false);
            document.getElementById('bf041-smart-auto').checked=smart;
            S.auto=true;document.getElementById('auto').checked=true;
            scheduleAuto();
        }''', smart)
        assert page.evaluate('timer!==null')
        actions = page.evaluate('S.party.map(unit=>unit.action)')
        page.evaluate('__setAutoHidden(true)')
        assert page.evaluate('!S.auto && !E.auto.checked && timer===null')
        page.wait_for_timeout(500)
        assert page.evaluate('__backgroundCalls') == 0
        assert page.evaluate('S.party.map(unit=>unit.action)') == actions
        page.evaluate('__setAutoHidden(false)')
        page.wait_for_timeout(500)
        assert page.evaluate('__backgroundCalls') == 0
        assert page.evaluate('!S.auto && !E.auto.checked && timer===null')
        assert_unchanged(page, baseline, f'pending/foreground smart={smart}')
    # Scheduler guards also fail closed if lifecycle event delivery is delayed.
    page.evaluate('''() => {
        __setAutoHidden(true,false);S.auto=true;E.auto.checked=true;scheduleAuto();
    }''')
    assert page.evaluate('timer===null && !S.auto && !E.auto.checked')
    page.evaluate('''() => {
        __setAutoHidden(false,false);S.auto=true;E.auto.checked=true;scheduleAuto();
        __setAutoHidden(true,false);
    }''')
    page.wait_for_timeout(500)
    assert page.evaluate('__backgroundCalls') == 0
    assert page.evaluate('timer===null && S.party.every(unit=>unit.action===null)')
    # Return directly without ever notifying the hidden transition. Controls
    # must already be off, rather than checked with no timer and no execution.
    page.evaluate('__setAutoHidden(false)')
    page.wait_for_timeout(500)
    assert page.evaluate('!S.auto && !E.auto.checked && timer===null')
    assert_unchanged(page, baseline, 'delayed visibility signal')
    # A running round finishes normally, then cannot schedule another round.
    page.evaluate('''() => {
        __setAutoHidden(false);
        E.auto.checked=true;E.auto.dispatchEvent(new Event('change'));
    }''')
    page.wait_for_function('S.busy && __backgroundCalls===1')
    round_before = page.evaluate('S.round')
    page.evaluate('__setAutoHidden(true)')
    assert page.evaluate('S.busy && !S.auto && !E.auto.checked')
    page.wait_for_function('!S.busy', timeout=30000)
    assert page.evaluate('S.round') == round_before + 1
    assert page.evaluate('S.party.every(unit=>unit.action===null)')
    assert page.evaluate('timer===null && !S.over')
    page.evaluate('__setAutoHidden(false)')
    page.wait_for_timeout(500)
    assert page.evaluate('__backgroundCalls') == 1
    assert page.evaluate('!S.auto && !E.auto.checked')
    assert_unchanged(page, baseline, 'finish current round, stay paused')
    # Explicit user input can resume Auto; hide again to stop after that round.
    page.evaluate('''() => {
        E.auto.checked=true;E.auto.dispatchEvent(new Event('change'));
    }''')
    page.wait_for_function('S.busy && __backgroundCalls===2')
    page.evaluate('__setAutoHidden(true)')
    page.wait_for_function('!S.busy', timeout=30000)
    assert page.evaluate('__backgroundCalls') == 2
    assert page.evaluate('S.round') == round_before + 2
    assert page.evaluate('!S.auto && !E.auto.checked && timer===null')
    assert_unchanged(page, baseline, 'explicit resume')
    # Existing repeat orchestration must also stay stopped after returning.
    # Only result/replay metadata is mocked; Auto and its round executor are real.
    page.evaluate('''() => {
        __setAutoHidden(false);
        const host=document.createElement('div');host.id='bf2000-run';
        document.body.append(host);
        window.__repeatReplayCalls=0;S.over=true;S.phase='Victory';
        window.BFGlobalBattleResultsV3000={
            snapshot:()=>({missionId:QUEST.missionId,done:S.over,
                victory:S.over,archive:true,stored:true,clears:1,canReplay:S.over}),
            replayBattle:()=>{
                __repeatReplayCalls++;S.over=false;S.phase='Choose actions';return true;
            }
        };
    }''')
    page.add_script_tag(path=str(ASSETS/'bf9800_qol_cleared_quest_repeat.js'))
    assert page.evaluate('BFGlobalQoLQuestRepeatV9800.start(2)')
    page.wait_for_function('S.busy && __backgroundCalls===3')
    # With repeat active, exercise the scheduler fallback without a hidden event.
    page.evaluate('__setAutoHidden(true,false);scheduleAuto()')
    assert page.evaluate('!BFGlobalQoLQuestRepeatV9800.statusSnapshot().active')
    assert page.evaluate('!S.auto && !E.auto.checked')
    page.wait_for_function('!S.busy', timeout=30000)
    page.evaluate('__setAutoHidden(false)')
    page.wait_for_timeout(1100)  # Includes a real repeat polling interval.
    assert page.evaluate('__backgroundCalls===3 && __repeatReplayCalls===1')
    assert page.evaluate('!BFGlobalQoLQuestRepeatV9800.statusSnapshot().active')
    assert page.evaluate('!S.auto && !E.auto.checked && timer===null')
    assert_unchanged(page, baseline, 'repeat interruption')
    # A completed result normally turns Auto off before repeat's next poll.
    # A hidden scheduler guard must still stop that waiting repeat session.
    page.evaluate("()=>{S.over=true;S.phase='Victory'}")
    assert page.evaluate('BFGlobalQoLQuestRepeatV9800.start(2)')
    page.evaluate('''() => {
        if(timer){clearTimeout(timer);timer=null;}
        S.auto=false;E.auto.checked=false;S.over=true;S.phase='Victory';
        __setAutoHidden(true,false);scheduleAuto();
    }''')
    assert page.evaluate('!BFGlobalQoLQuestRepeatV9800.statusSnapshot().active')
    assert page.evaluate("BFGlobalQoLQuestRepeatV9800.statusSnapshot().reason") == 'Stopped: app left foreground'
    page.evaluate('__setAutoHidden(false)')
    page.wait_for_timeout(1100)
    assert page.evaluate('__backgroundCalls===3 && __repeatReplayCalls===2')
    assert page.evaluate('!S.auto && !E.auto.checked && timer===null')
    assert_unchanged(page, baseline, 'repeat waiting at completed result')
    assert not errors, errors
    browser.close()
print('PASS Auto hidden-page timer cancellation, delayed signals, in-flight round, explicit resume, repeat interruption and P/storage isolation')
