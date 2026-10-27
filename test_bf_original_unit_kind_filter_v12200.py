"""v122 original 2022 source unit-kind filter, strictly read-only."""
import base64,gzip,hashlib,json,shutil
from collections import Counter
from pathlib import Path
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
meta=json.loads((R/'source_data/bf_global_original_unit_catalog_meta.json').read_text('utf8'))
packed=base64.b64decode((R/'source_data/bf_global_original_unit_catalog.json.gz.b64').read_text('ascii'))
assert hashlib.sha256(packed).hexdigest()==meta['catalogGzipSha256']
raw=gzip.decompress(packed)
assert hashlib.sha256(raw).hexdigest()==meta['catalogJsonSha256']
archive=json.loads(raw)
assert archive['schema']=='bf-global-unit-archive-2022-v1'
units=archive['units']
assert len(units)==2291
pairs=sorted([[u['id'],u['unitKind']] for u in units])
assert len(pairs)==len({x[0] for x in pairs})==2291
assert all(type(x[0]) is int and type(x[1]) is int for x in pairs)
digest=hashlib.sha256(json.dumps(pairs,separators=(',',':')).encode()).hexdigest()
assert digest=='0843acff8014d1b06f22004a61b2757b03ebb1d081c96a125265cecd8af9dbb2',digest
counts=Counter(k for _,k in pairs)
assert counts[0]==2164 and sum(n for k,n in counts.items() if k!=0)==127
assert counts[1]==40 and counts[2]==55 and counts[3]==5 and len(counts)==15
code=(R/'app/src/main/assets/bf_global_unit_archive.js').read_text('utf8')
assert 'localStorage.setItem' not in code and 'P.unitExp=' not in code
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
        executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
        args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page()
    errors=[]
    page.on('pageerror',lambda exc:errors.append(str(exc)))
    page.set_content('<div id="bf-owned-box"></div><script id="bf-global-unit-catalog-data" type="application/json"></script>')
    page.evaluate('payload=>{window.BFUnitBox={};document.getElementById("bf-global-unit-catalog-data").textContent=payload}',json.dumps(archive,separators=(',',':')))
    previous=page.evaluate("""()=>{try{return localStorage.getItem('bf_global_offline_demo_v7')}catch(_){return null}}""")
    page.add_script_tag(content=code)
    assert page.evaluate('BFGlobalUnitArchive.count')==2291
    assert page.evaluate('BFGlobalUnitArchive.matchingCount')==2291
    choice=page.locator('#bf-archive-type')
    assert choice.locator('option').all_text_contents()==['All original records','Standard unit entries','Other original kind codes']
    choice.select_option('0')
    assert page.evaluate('BFGlobalUnitArchive.matchingCount')==2164
    choice.select_option('other')
    assert page.evaluate('BFGlobalUnitArchive.matchingCount')==127
    page.locator('#bf-archive-search').fill('10011')
    assert page.evaluate('BFGlobalUnitArchive.matchingCount')==0
    page.locator('#bf-archive-search').fill('')
    choice.select_option('all')
    assert page.evaluate('BFGlobalUnitArchive.matchingCount')==2291
    assert previous==page.evaluate("""()=>{try{return localStorage.getItem('bf_global_offline_demo_v7')}catch(_){return null}}""")
    assert not errors,errors
    browser.close()
print('PASS v122: all 2291 original 2022 unit-kind labels; 2164 standard + 127 other; no save writes')
