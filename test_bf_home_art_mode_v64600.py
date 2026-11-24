"""v646 R6: explicit Home art modes fail closed; no silent downgrade (source/logic only, no artwork)."""
import os
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

import bf_home_test_module_order as H

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'app/src/main/assets'
ACTIVITY = (ROOT / 'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf-8')
WORKFLOW = (ROOT / '.github/workflows/build-debug-apk.yml').read_text('utf-8')
NAV_BYTES = (ASSETS / H.NAV).read_bytes()


def fails(fn, *args, contains=''):
    try:
        fn(*args)
    except AssertionError as error:
        assert contains in str(error), (contains, str(error))
        return True
    raise AssertionError(f'expected fail-closed: {fn.__name__}{args}')


class Env:
    def __init__(self, value, manifest=None, pin=None):
        self.values = dict(zip((H.MODE_ENV, H.MANIFEST_ENV, H.MANIFEST_PIN_ENV), (value, manifest, pin)))

    def __enter__(self):
        self.saved = {k: os.environ.get(k) for k in self.values}
        for k, v in self.values.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = str(v)

    def __exit__(self, *exc):
        for k, v in self.saved.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v


def tree(*, selector=True, art=()):
    """Disposable asset tree with the real CSS/nav/selector; art entries are synthetic bytes only."""
    root = Path(tempfile.mkdtemp(prefix='bf646mode_'))
    for name in (H.CSS, H.NAV) + ((H.ART,) if selector else ()):
        shutil.copy(ASSETS / name, root / name)
    for form, data in art:
        path = root / H.full_path(form)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return root


# --- constants and real checkout ---------------------------------------------
assert H.ART_REDISTRIBUTION_AUTHORIZED is False
assert H.MODES == ('fallback-only', 'full-art')
assert len(NAV_BYTES) <= 131072, len(NAV_BYTES)
assert H.ART in ACTIVITY and (ASSETS / H.ART).is_file(), 'v646 selector must be integrated for this test'
assert not list(ASSETS.glob('content/unit/img/unit_ills_full_*')) or os.environ.get(H.MODE_ENV) == 'full-art', \
    'restricted artwork present outside full-art mode'
print(f'PASS v646 mode source: redistribution false, nav {len(NAV_BYTES)}/131072 B')

# --- unnamed / invalid modes --------------------------------------------------
for value in (None, '', 'full', 'fallback', 'FULL-ART', 'Fallback-Only', ' full-art', 'auto'):
    with Env(value):
        fails(H.home_modules, ACTIVITY, ASSETS)
for value in ('', 'full', 'auto'):
    fails(H.art_mode, False, {H.MODE_ENV: value}, contains='invalid')
fails(H.art_mode, True, {}, contains='must name')
fails(H.art_mode, False, {H.MODE_ENV: 'fallback-only'}, contains='not integrated')
assert H.art_mode(False, {}) is None
print('PASS v646 mode: unnamed and invalid modes fail closed')

# --- private manifest admission; synthetic bytes only -----------------------
with tempfile.TemporaryDirectory(prefix='bf646manifest_') as folder:
    manifest = Path(folder) / 'synthetic.json'
    fixture = {str(f): hashlib.sha256(f'synthetic-{f}'.encode()).hexdigest() for f in H.FULL_ART_IDS}
    def put(data):
        manifest.write_bytes(data)
        return hashlib.sha256(data).hexdigest()
    def encode(obj):
        return json.dumps(obj).encode()
    valid = encode(fixture)
    pin = put(valid)
    with Env('full-art'):
        fails(H.home_modules, ACTIVITY, ASSETS, contains='requires external manifest')
    for bad in ('', '0'*63, 'A'*64, 'g'*64):
        with Env('full-art', manifest, bad):
            fails(H.load_full_art_manifest, contains='manifest')
    with Env('full-art', manifest, '0'*64):
        fails(H.load_full_art_manifest, contains='pin mismatch')
    for obj in ({}, {k:v for k,v in fixture.items() if k!='10011'}, dict(fixture, extra='0'*64),
                dict(fixture, **{'10011':'bad'}), dict(fixture, **{'10011':True}), list(fixture)):
        with Env('full-art', manifest, put(encode(obj))):
            fails(H.load_full_art_manifest)
    duplicate = valid[:-1] + b', "10011": "duplicate"}'
    with Env('full-art', manifest, put(duplicate)):
        fails(H.load_full_art_manifest, contains='duplicate')
    for bad in (b'not-json', b'x'*8193):
        with Env('full-art', manifest, put(bad)):
            fails(H.load_full_art_manifest)
    pin = put(valid)
    with Env('full-art', 'relative.json', pin):
        fails(H.load_full_art_manifest, contains='absolute')
    with tempfile.TemporaryDirectory(dir=ROOT, prefix='bf646manifest_inside_') as inner:
        internal = Path(inner) / 'synthetic.json'
        internal.write_bytes(valid)
        with Env('full-art', internal, pin):
            fails(H.load_full_art_manifest, contains='outside checkout')
        link = manifest.with_name('internal-link.json')
        link.symlink_to(internal)
        with Env('full-art', link, pin):
            fails(H.load_full_art_manifest, contains='outside checkout')
    with Env('full-art', manifest.with_name('missing.json'), pin):
        fails(H.load_full_art_manifest, contains='unavailable')
    with Env('full-art', manifest, pin):
        assert set(H.load_full_art_manifest()) == set(H.FULL_ART_IDS)
        for art in ((), ((10011, b'not-art'),), tuple((f, f'synthetic-{f}'.encode()) for f in H.FULL_ART_IDS[:5]),
                    tuple((f, b'x') for f in H.FULL_ART_IDS)):
            root = tree(art=art)
            try:
                fails(H.home_modules, ACTIVITY, root)
                fails(H.active_mode, contains='resolve')
            finally:
                shutil.rmtree(root)
        # Positive *synthetic integrity* test only, not artwork or rendering evidence.
        print('SYNTHETIC MANIFEST/FILE INTEGRITY TEST ONLY — not authentic full-art evidence', flush=True)
        root = tree(art=tuple((f, f'synthetic-{f}'.encode()) for f in H.FULL_ART_IDS))
        try:
            assert H.home_modules(ACTIVITY, root)[:3] == [H.CSS, H.ART, H.NAV]
            assert H.active_mode() == 'full-art'
        finally:
            shutil.rmtree(root)
    with Env('fallback-only', manifest, pin):
        fails(H.home_modules, ACTIVITY, ASSETS, contains='must not receive')
print('PASS v646 mode: private pinned manifest admission; missing, partial and wrong art fail; synthetic integrity only')

# --- fallback-only: restricted artwork must be absent -------------------------
for art in (((10011, b'x'),), tuple((f, b'x') for f in H.FULL_ART_IDS)):
    root = tree(art=art)
    try:
        with Env('fallback-only'):
            fails(H.home_modules, ACTIVITY, root, contains='to be absent')
    finally:
        shutil.rmtree(root)
root = tree()
try:
    with Env('fallback-only'):
        modules = H.home_modules(ACTIVITY, root)
    assert modules[:3] == [H.CSS, H.ART, H.NAV], modules[:3]
    assert H.active_mode() == 'fallback-only'
finally:
    shutil.rmtree(root)
print('PASS v646 mode: fallback-only requires absent artwork and keeps CSS -> selector -> nav order')

# --- per-card expectation: no cross-mode substitution -------------------------
portrait = 'data:image/png;base64,AAAA'
for form in H.FULL_ART_IDS:
    assert H.expected_src(form, portrait, 'full-art') == H.full_path(form)
    assert H.expected_src(form, portrait, 'fallback-only') == portrait
assert H.expected_src(10012, portrait, 'full-art') == portrait
fails(H.expected_src, 10011, portrait, 'auto')
print('PASS v646 mode: full-art expects exact illustrations; fallback-only expects V266 portraits')

# --- public CI wiring ---------------------------------------------------------
step = WORKFLOW.split('      - name: Test save recovery and offline combat\n', 1)[1].split('\n      - name: ', 1)[0]
assert '          BF_HOME_ART_MODE: fallback-only\n' in step
assert 'full-art' not in WORKFLOW.replace('full-art runs only on an authorized private machine', '')
for test in ('test_bf_home_squad_frame_v63500.py', 'test_bf_home_artwork_first_v63600.py',
             'test_bf_home_six_slot_custom_v64000.py', 'test_bf_home_adaptive_fit_v64500.py',
             'test_bf_home_art_mode_v64600.py'):
    assert step.count(f'python3 {test}\n') == 1, test
assert 'unit_ills_full' not in WORKFLOW
print('PASS v646 mode: public CI step pins fallback-only and never stages restricted artwork')
