"""Adversarial tests for read-only source screenshot evidence; no real saves."""
import ast
import json
from pathlib import Path
import shutil
import subprocess
import sys
from bf_capture_progress_audit import INSTALL_STORAGE, SNAPSHOT, assert_unchanged

ROOT = Path(__file__).resolve().parent
CASES = {
    'quest-progress': "P.questClears.demo = 1",
    'viewed-dialogue': "P.viewedDialogue.push('synthetic')",
    'inventory': "P.inventory.catalyst = 1",
    'training': "P.trainingSpent = 5",
    'other-save-key': "localStorage.setItem('other-key', 'synthetic')",
    'primary-save-key': "localStorage.setItem('bf_global_offline_demo_v7', 'synthetic')",
    'restored-write': "localStorage.setItem('temp', 'x'); localStorage.removeItem('temp')",
    'absent-remove': "localStorage.removeItem('absent')",
    'empty-clear': "localStorage.clear()",
    'same-value-write': "localStorage.setItem('fixture', 'same')",
}
PLAYER = "window.P = {questClears:{},viewedDialogue:[],inventory:{},trainingSpent:0}"

# Run the actual browser expressions without browser dependencies in source CI.
js = '\n'.join([
    "const assert = require('node:assert/strict'); global.window = global;",
    INSTALL_STORAGE, PLAYER,
    "localStorage.setItem('fixture', 'same');",
    f'const snapshot = {SNAPSHOT};',
    "const baseline = snapshot(); assert.deepEqual(snapshot(), baseline);",
    *[f"{PLAYER}; const b{i}=snapshot(); {mutation}; assert.notDeepEqual(snapshot(),b{i});"
      for i, mutation in enumerate(CASES.values())],
    "assert.equal(localStorage.getItem('absent'), null);",
    "localStorage.setItem(123, 456); assert.equal(localStorage.getItem('123'), '456');",
    "console.log('PASS source: 10 progress/storage negative controls detected');",
])
subprocess.run(['node', '-e', js], check=True)

# Both real runners must use this tested guard, rather than a partial snapshot.
for filename in ('test_bf_ui_screen_capture_v26300.py', 'test_bf_nested_ui_capture_v27200.py'):
    source = (ROOT / filename).read_text()
    tree = ast.parse(source)
    assert 'from bf_capture_progress_audit import INSTALL_STORAGE, SNAPSHOT, assert_unchanged' in source
    assert 'page.evaluate(SNAPSHOT)' in source
    assert 'assert_unchanged(page,' in source
    assert '**audit' in source
    assert 'INSTALL_STORAGE' in source
pre = (ROOT / '.github/workflows/android-back-ui-source-preflight.yml').read_text()
build = (ROOT / '.github/workflows/build-debug-apk.yml').read_text()
assert 'bf_capture_progress_audit.py' in pre
assert 'test_bf_capture_progress_audit.py --source-only' in pre
assert 'python3 test_bf_capture_progress_audit.py --browser' in build

if '--source-only' in sys.argv:
    raise SystemExit(0)
assert '--browser' in sys.argv, 'Use --source-only or --browser explicitly'
from playwright.sync_api import sync_playwright
chrome = shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable')
assert chrome, 'Chromium required'
results = []
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=chrome,
                                args=['--no-sandbox', '--disable-dev-shm-usage'])
    for name, mutation in CASES.items():
        context = browser.new_context(service_workers='block')
        page = context.new_page()
        page.route('**/*', lambda route: route.abort())
        page.evaluate(INSTALL_STORAGE)
        page.evaluate(PLAYER)
        page.evaluate("localStorage.setItem('fixture', 'same')")
        baseline = page.evaluate(SNAPSHOT)
        assert_unchanged(page, baseline, 'read-only positive')
        page.evaluate('() => {' + mutation + '}')
        try:
            assert_unchanged(page, baseline, name)
        except AssertionError:
            results.append(name)
        else:
            raise AssertionError(f'Audit missed mutation: {name}')
        context.close()
    browser.close()
assert len(results) == len(CASES)
print('PASS Chromium: 10/10 negative controls rejected; read-only positives accepted')
