"""Home browser-test ordering and exact v646 art assertions (test-only).

v646 R6: once the optional selector is integrated, every run must name its art
mode in BF_HOME_ART_MODE. Nothing is inferred from which files happen to exist.
  full-art      all twelve externally admitted fingerprints and exact full-art rendering
  fallback-only restricted artwork must be ABSENT; every card must show its V266 portrait
"""
import hashlib
import json
from pathlib import Path
import os
import re

CSS = 'bf_home_nav.css'
NAV = 'bf_home_nav.js'
ART = 'bf_home_full_art_v646.js'
STARTER_ART_IDS = (10011, 20011, 30011, 40011, 50011, 60011)
EVOLVED_ART_IDS = (10012, 20012, 30012, 40012, 50012, 60012)
FULL_ART_IDS = tuple(sorted(STARTER_ART_IDS + EVOLVED_ART_IDS))
MANIFEST_ENV = 'BF_HOME_ART_MANIFEST'
MANIFEST_PIN_ENV = 'BF_HOME_ART_MANIFEST_SHA256'
# The private operator supplies a previously authenticated pin from a trusted
# record, independently of the manifest file. An arbitrary self-pinned file
# does not establish original-art provenance or authorization.

MODE_ENV = 'BF_HOME_ART_MODE'
MODES = ('fallback-only', 'full-art')
ART_REDISTRIBUTION_AUTHORIZED = False
_active_mode = None
if not __debug__:
    raise RuntimeError('Home art admission requires Python assertions enabled')


def art_mode(enabled, environ=None):
    """Fail closed: invalid always fails; unset fails once the selector is integrated."""
    raw = (os.environ if environ is None else environ).get(MODE_ENV)
    if raw is not None and raw not in MODES:
        raise AssertionError(f'{MODE_ENV}={raw!r} is invalid; use one of {MODES}')
    if enabled:
        assert raw in MODES, f'{MODE_ENV} must name fallback-only or full-art once the v646 selector is integrated'
    else:
        assert raw is None, f'{MODE_ENV}={raw!r} set but the v646 selector is not integrated'
    return raw


def active_mode():
    assert _active_mode in MODES, 'home_modules() must resolve the art mode first'
    return _active_mode


def full_path(form):
    return f'content/unit/img/unit_ills_full_{form}.png'


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, 'duplicate manifest key'
        result[key] = value
    return result


def load_full_art_manifest(environ=None):
    """Require an external manifest and an independently trusted SHA-256 pin.

    The caller must obtain the pin from the previously authenticated private
    record; this integrity check is not a permission or provenance grant.
    Never emit manifest paths, contents or digest values to test logs.
    """
    env = os.environ if environ is None else environ
    source, pin = env.get(MANIFEST_ENV), env.get(MANIFEST_PIN_ENV)
    assert source and pin, 'full-art mode requires external manifest and trusted pin'
    assert re.fullmatch(r'[0-9a-f]{64}', pin), 'invalid manifest pin'
    path = Path(source)
    assert path.is_absolute(), 'manifest path must be absolute'
    try:
        path = path.resolve(strict=True)
        assert not path.is_relative_to(Path(__file__).resolve().parent), 'manifest must be outside checkout'
        assert path.is_file(), 'manifest must be a regular file'
        with path.open('rb') as stream:
            data = stream.read(8193)
    except (OSError, ValueError, RuntimeError):
        raise AssertionError('manifest unavailable') from None
    assert len(data) <= 8192, 'manifest too large'
    assert hashlib.sha256(data).hexdigest() == pin, 'manifest pin mismatch'
    try:
        manifest = json.loads(data, object_pairs_hook=_unique_object)
    except (ValueError, UnicodeError, RecursionError):
        raise AssertionError('invalid manifest JSON') from None
    assert isinstance(manifest, dict), 'manifest must be an object'
    assert set(manifest) == {str(form) for form in FULL_ART_IDS}, 'manifest must contain exactly twelve forms'
    assert all(isinstance(d, str) and re.fullmatch(r'[0-9a-f]{64}', d) for d in manifest.values()), 'invalid artwork digest'
    return {form: manifest[str(form)] for form in FULL_ART_IDS}


def home_modules(activity, assets):
    """Match native execution of the initial CSS/selector/nav block, not declaration order."""
    global _active_mode
    _active_mode = None
    names = list(dict.fromkeys(re.findall(r'bf[0-9a-z_]*\.(?:js|css)', activity)))
    assert names[:2] == [NAV, CSS], names[:2]
    assert all((assets / name).is_file() for name in (CSS, NAV))
    nav = (assets / NAV).read_text('utf-8')
    enabled = ART in names
    assert enabled == ('window.BFHomeFullArtV646?.(' in nav), 'partial v646 integration'
    assert enabled == (assets / ART).is_file(), 'missing or orphan selector'
    css_call = '"style.textContent=" + JSONObject.quote(css)'
    nav_call = 'view.evaluateJavascript(js, null);'
    assert activity.count(css_call) == activity.count(nav_call) == 1
    assert activity.index(css_call) < activity.index(nav_call)
    prefix = [CSS]
    if enabled:
        assert nav.count('img.bfArtAttach?.();') == 1, 'missing or duplicate Home art attachment hook'
        read = 'readPackagedText("' + ART + '")'
        call = 'view.evaluateJavascript(fullArt, null);'
        assert activity.count(read) == activity.count(call) == 1
        assert activity.index(css_call) < activity.index(read) < activity.index(call) < activity.index(nav_call)
        assert names[2] == ART, names[:3]
        mode = art_mode(True)
        if mode == 'full-art':
            admitted = load_full_art_manifest()
            present = {str(p.relative_to(assets)) for p in assets.glob('content/unit/img/unit_ills_full_*')}
            assert present <= {full_path(form) for form in admitted}, 'unexpected full-art file'
            for form, digest in admitted.items():
                assert (assets / full_path(form)).is_file(), (form, 'full-art mode: artwork missing')
                data = (assets / full_path(form)).read_bytes()
                assert hashlib.sha256(data).hexdigest() == digest, (form, 'art bytes')
            banner = 'full-art (12/12 fingerprints verified)'
        else:
            assert not any(k in os.environ for k in (MANIFEST_ENV, MANIFEST_PIN_ENV)), 'fallback-only mode must not receive private manifest settings'
            present = sorted(str(p.relative_to(assets)) for p in assets.glob('content/unit/img/unit_ills_full_*'))
            assert not present, ('fallback-only mode requires restricted artwork to be absent', present)
            banner = 'fallback-only (full-art NOT verified)'
        _active_mode = mode
        print('HOME ART MODE: ' + banner, flush=True)
        prefix.append(ART)
    else:
        art_mode(False)
    prefix.append(NAV)
    return prefix + [n for n in names if n not in prefix and (assets / n).is_file()]


CARD_PROBE = '''()=>Array.from(document.querySelectorAll('#bf-scene-party > .bf-scene-member'),(c,i)=>{
  const base=P.squad[i],u=effectiveUnit(base),img=c.querySelector(':scope > img');
  return {base,owned:P.roster.includes(base),card:Number(c.dataset.bfHomeUnitId),form:u?.id,
    expectedPortrait:u?.portrait,src:img?.getAttribute('src'),decoded:!!(img?.complete&&img.naturalWidth>0),
    name:c.querySelector('strong')?.textContent,expectedName:u?.name,leader:!!c.querySelector('.bf-scene-leader')};})'''


def expected_src(form, portrait, mode=None):
    """full-art: exact allowed form -> its full illustration; fallback-only: always the V266 portrait."""
    mode = active_mode() if mode is None else mode
    assert mode in MODES, mode
    return full_path(form) if mode == 'full-art' and form in FULL_ART_IDS else portrait


def assert_exact_home_art(page, *, starter_fixture=False):
    page.wait_for_function("()=>[...document.querySelectorAll('#bf-scene-party > .bf-scene-member > img')].every(i=>i.complete&&i.naturalWidth>0)")
    rows = page.evaluate(CARD_PROBE)
    assert len(rows) == 6 and len({r['base'] for r in rows}) == 6
    for i, r in enumerate(rows):
        assert r['owned'] and r['card'] == r['base'] and r['decoded']
        assert r['name'] == r['expectedName'] and r['leader'] == (i == 0)
        expected = expected_src(r['form'], r['expectedPortrait'])
        assert r['src'] == expected, (r['base'], r['form'], 'wrong or missing exact-form artwork')
    if starter_fixture:
        assert {r['form'] for r in rows} == set(STARTER_ART_IDS), 'fixture must exercise all six starter forms'
    return rows


def exercise_exact_form_and_missing_art(page, snapshot, open_missing):
    """Real effectiveUnit and refreshParty; synthetic in-memory state only, restored in finally."""
    before = page.evaluate(snapshot)
    assert_exact_home_art(page, starter_fixture=True)
    # All six authenticated first evolutions; synthetic in-memory fixture only.
    pairs = list(zip(STARTER_ART_IDS, EVOLVED_ART_IDS))
    page.evaluate('''pairs=>{if(pairs.some(([base,form])=>P.evolutions[base]!==undefined||!UNIT_BY_ID.has(form)))throw Error('bad evolution fixture');}''', pairs)
    try:
        page.evaluate('''pairs=>{for(const [base,form] of pairs)P.evolutions[base]=form;BFGlobalHome.refreshParty();}''', pairs)
        rows = assert_exact_home_art(page)
        expected = dict(pairs)
        assert {r['base']: r['form'] for r in rows} == expected
        for row in rows:
            assert row['src'] == expected_src(expected[row['base']], row['expectedPortrait'])
    finally:
        page.evaluate('pairs=>{for(const [base] of pairs)delete P.evolutions[base];BFGlobalHome.refreshParty();}', pairs)
    assert_exact_home_art(page, starter_fixture=True)
    assert page.evaluate(snapshot) == before
    # Force the missing image in a fresh context before the first request.
    # Re-rendering an already decoded image can bypass routing in Chromium.
    pattern = '**/' + full_path(10011)
    intercepted = []
    def missing(route):
        route.fulfill(status=404, body=b'')
        intercepted.append(True)

    missing_page, missing_errors = open_missing(lambda p: p.route(pattern, missing))
    try:
        missing_before = missing_page.evaluate(snapshot)
        assert missing_before['w'] == 0, 'fresh missing-art fixture wrote storage'
        card = missing_page.locator('#bf-scene-party > [data-bf-home-unit-id="10011"]')
        missing_page.wait_for_function('''()=>{const i=document.querySelector('#bf-scene-party > [data-bf-home-unit-id="10011"] > img');
          return i?.complete&&i.naturalWidth>0&&i.getAttribute('src')===effectiveUnit(10011).portrait;}''')
        assert intercepted, 'missing-art route was never intercepted'
        assert card.evaluate("c=>!!c.querySelector('.bf-scene-leader')&&c.getAttribute('aria-label').startsWith('Inspect '+effectiveUnit(10011).name+', ')")
        missing_page.wait_for_function("()=>[...document.querySelectorAll('#bf-scene-party > .bf-scene-member > img')].every(i=>i.complete&&i.naturalWidth>0)")
        rows = missing_page.evaluate(CARD_PROBE)
        assert len(rows) == 6 and len({r['base'] for r in rows}) == 6
        assert {r['form'] for r in rows} == set(STARTER_ART_IDS)
        for i, row in enumerate(rows):
            assert row['owned'] and row['card'] == row['base'] and row['decoded']
            assert row['name'] == row['expectedName'] and row['leader'] == (i == 0)
            expected = row['expectedPortrait'] if row['form'] == 10011 else expected_src(row['form'], row['expectedPortrait'])
            assert row['src'] == expected, (row['form'], 'wrong missing-art fixture image')
        assert missing_page.evaluate(snapshot) == missing_before
        assert not missing_errors, 'missing-art fixture page error'
    finally:
        missing_page.close()
    # The original all-art page was never routed or mutated by the negative probe.
    assert_exact_home_art(page, starter_fixture=True)
    assert page.evaluate(snapshot) == before
