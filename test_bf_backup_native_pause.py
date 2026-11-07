"""Exact native pause bridge captures current saved bytes without a DOM hide."""
import json
from pathlib import Path
import re
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
java = (ROOT / 'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text()
literal = re.search(r'private static final String UI_BACKGROUND_JS\s*=\s*("[^\n]+");', java)
assert literal
bridge = json.loads(literal[1])

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path=shutil.which('chromium') or
        shutil.which('google-chrome'), args=['--no-sandbox', '--disable-dev-shm-usage'])
    page = browser.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.set_content('<section id="questlist"></section>')
    page.evaluate('''() => {
        window.__db = {}; window.__writes = []; window.__denyBackup = false;
        Object.defineProperty(window, 'localStorage', {value: {
            getItem: key => __db[key] ?? null,
            setItem: (key, value) => {
                if (__denyBackup && key === 'bf_global_offline_qol_rotating_backups_v97')
                    throw new DOMException('Synthetic quota failure', 'QuotaExceededError');
                __writes.push(key); __db[key] = String(value);
            }, removeItem: key => { __writes.push(key); delete __db[key]; }
        }});
        // Synthetic disposable save bytes, including opaque earned-data records.
        window.P = {version:7, roster:[10011], squad:[10011], questClears:{1:1},
            earned:{gems:17, imps:{hp:3}, receipt:'synthetic-preserve-exactly'}};
        localStorage.setItem('bf_global_offline_demo_v7', JSON.stringify(P));
        window.__nativeCount = 0; window.__hiddenCount = 0;
        window.addEventListener('bf-native-background', () => __nativeCount++);
        document.addEventListener('visibilitychange', () => __hiddenCount++);
    }''')
    page.add_script_tag(path=str(ROOT / 'app/src/main/assets/bf9700_qol_rotating_backups.js'))
    assert page.evaluate('document.hidden') is False
    # Change only the synthetic persisted input; do not manually call capture.
    page.evaluate('''() => {
        const key=BFGlobalQoLBackupsV9700.liveKey;
        const saved=JSON.parse(localStorage.getItem(key));saved.questClears[1]=2;
        localStorage.setItem(key,JSON.stringify(saved));__writes=[];
    }''')
    before = page.evaluate('JSON.stringify({player:P,live:__db[BFGlobalQoLBackupsV9700.liveKey]})')
    page.evaluate(bridge)
    assert page.evaluate('''() => {
        const api=BFGlobalQoLBackupsV9700;
        return JSON.parse(localStorage.getItem(api.key)).slots[0].raw===localStorage.getItem(api.liveKey);
    }'''), 'Native pause did not back up the latest saved bytes while DOM stayed visible'
    assert page.evaluate('JSON.stringify({player:P,live:__db[BFGlobalQoLBackupsV9700.liveKey]})') == before
    assert page.evaluate('__writes') == ['bf_global_offline_qol_rotating_backups_v97']
    page.evaluate('__writes=[]')
    page.evaluate(bridge)
    assert page.evaluate('__writes') == [], 'Duplicate pause rotated identical saved bytes'
    for n in (3,4):
        page.evaluate('''n => {
            const api=BFGlobalQoLBackupsV9700;
            const saved=JSON.parse(localStorage.getItem(api.liveKey));saved.questClears[1]=n;
            localStorage.setItem(api.liveKey,JSON.stringify(saved));
        }''', n)
        page.evaluate(bridge)
    assert page.evaluate('JSON.parse(__db[BFGlobalQoLBackupsV9700.key]).slots.map(x=>JSON.parse(x.raw).questClears[1])') == [4,3,2]
    # Opt-out and quota/corrupt failures retain all previous good snapshots.
    page.evaluate('BFGlobalQoLBackupsV9700.enable(false)')
    page.evaluate('''() => {const k=BFGlobalQoLBackupsV9700.liveKey;
        const saved=JSON.parse(__db[k]);saved.questClears[1]=5;
        localStorage.setItem(k,JSON.stringify(saved));__writes=[];}''')
    backups = page.evaluate('__db[BFGlobalQoLBackupsV9700.key]')
    page.evaluate(bridge)
    assert page.evaluate('__writes') == []
    assert page.evaluate('__db[BFGlobalQoLBackupsV9700.key]') == backups
    page.evaluate('BFGlobalQoLBackupsV9700.enable(true)')
    page.evaluate('''() => {const k=BFGlobalQoLBackupsV9700.liveKey;
        const saved=JSON.parse(__db[k]);saved.questClears[1]=6;
        localStorage.setItem(k,JSON.stringify(saved));__denyBackup=true;__writes=[];}''')
    backups = page.evaluate('__db[BFGlobalQoLBackupsV9700.key]')
    before = page.evaluate('JSON.stringify({player:P,live:__db[BFGlobalQoLBackupsV9700.liveKey]})')
    page.evaluate(bridge)
    assert page.evaluate('__db[BFGlobalQoLBackupsV9700.key]') == backups
    assert page.evaluate('JSON.stringify({player:P,live:__db[BFGlobalQoLBackupsV9700.liveKey]})') == before
    page.evaluate('''() => {__denyBackup=false;localStorage.setItem(BFGlobalQoLBackupsV9700.liveKey,'{broken');__writes=[];}''')
    page.evaluate(bridge)
    assert page.evaluate('__db[BFGlobalQoLBackupsV9700.key]') == backups
    assert page.evaluate('__writes') == []
    # Exercise the diagnostic harness's dispatch-time isolation against the
    # actual module listener, without a timer or synthetic visibility signal.
    page.evaluate('''() => {
        const api=BFGlobalQoLBackupsV9700;
        localStorage.setItem(api.liveKey,JSON.stringify(P));api.capture();
        const nativeDispatch=window.dispatchEvent;
        window.dispatchEvent=function(event){
            if(event.type==='bf-native-background'){
                window.dispatchEvent=nativeDispatch;localStorage.removeItem(api.key);
            }
            return nativeDispatch.call(this,event);
        };
        window.addEventListener('bf-native-background',()=>{
            window.__capturePhaseProof=JSON.parse(localStorage.getItem(api.key)||'null')
                ?.slots?.[0]?.raw===localStorage.getItem(api.liveKey);
        },{once:true});
    }''')
    page.evaluate(bridge)
    assert page.evaluate('__capturePhaseProof') is True
    assert page.evaluate('__nativeCount') == 8
    assert page.evaluate('__hiddenCount') == 0
    assert page.evaluate('document.hidden') is False
    assert not errors, errors
    browser.close()
print('PASS exact native pause bridge: fresh canonical backup, dedupe, rotation, opt-out, quota/corrupt isolation; no DOM hide')
