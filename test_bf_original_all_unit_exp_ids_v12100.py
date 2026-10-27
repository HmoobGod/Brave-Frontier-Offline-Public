"""v121 original 2022 unitExpPatternId mapping for all 2,291 archive IDs.
Read-only. Never changes demoLevel, P.unitExp, saves or summoning.
"""
from collections import Counter
from pathlib import Path
import base64,gzip,hashlib,json,re,shutil
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
code=(A/'bf12100_original_all_unit_exp_ids.js').read_text('utf8')
assert len(code.encode())<64*1024
assert not any(s in code for s in ('P.unitExp=', 'P.roster=', 'localStorage.setItem',
                                'Math.random', 'fetch(', 'XMLHttpRequest'))
match=re.search(r"atob\('([A-Za-z0-9+/=]+)'\)",code)
assert match,'Pinned original source packed IDs absent'
packed=base64.b64decode(match.group(1),validate=True)
assert len(packed)==573
assert hashlib.sha256(packed).hexdigest()=='29b69acf743c50267c92c1022ab7c0f5032bcd22494974afcc100c54c27b4c64'
raw=gzip.decompress(base64.b64decode((R/'source_data/bf_global_original_unit_catalog.json.gz.b64').read_text()))
meta=json.loads((R/'source_data/bf_global_original_unit_catalog_meta.json').read_text())
assert hashlib.sha256(raw).hexdigest()==meta['catalogJsonSha256']
archive=json.loads(raw)
units=archive['units']
assert len(units)==2291
ids=sorted(u['id'] for u in units)
assert len(set(ids))==2291
assert hashlib.sha256(json.dumps(ids,separators=(',',':')).encode()).hexdigest()=='19a96b6d8987a7fb3099fc302185020702e6da248f9493f47268cb4ccba88c89'
codes={0:10,1:15,2:20}
pairs=[]
for index,uid in enumerate(ids):
    value=(packed[index//4] >> (6-2*(index%4))) & 3
    assert value in codes
    pairs.append([uid,codes[value]])
assert hashlib.sha256(json.dumps(pairs,separators=(',',':')).encode()).hexdigest()=='b897f8588d450a111206f16b4b09f5a5d8f3c3750e5f2e24d4ddd9ca0c84c48c'
by_id=dict(pairs)
assert Counter(by_id.values())=={10:248,15:245,20:1798}
old=json.loads((R/'source_data/bf_global_2022_playable_lord_stat_endpoints_v116.json').read_text())
for r in old['rows']: assert by_id[r['unitId']]==r['expPatternId'],r['unitId']
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text()
renderer=(A/'bf_global_unit_archive.js').read_text()
assert 'readPackagedText("bf12100_original_all_unit_exp_ids.js")' in java
assert 'Original EXP pattern ID ' in renderer
assert 'BFGlobalOriginalExpPatternIdsV12100?.lookup?.(id)' in renderer
# Use disposable Chromium page, not the owner's existing device save.
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True,
      executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
      args=['--no-sandbox','--disable-dev-shm-usage'])
    p=b.new_page(viewport={'width':390,'height':844})
    errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
    p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
    assert p.evaluate('P.version')==7
    p.add_script_tag(path=str(A/'bf_home_nav.js'))
    before=p.evaluate("""()=>({data:JSON.stringify(P),
      saved:(()=>{try{return localStorage.getItem('bf_global_offline_demo_v7')}catch(_){return null}})()})""")
    p.add_script_tag(path=str(A/'bf12100_original_all_unit_exp_ids.js'))
    assert p.evaluate('BFGlobalOriginalExpPatternIdsV12100.source.originalUnitRecords')==2291
    assert p.evaluate('BFGlobalOriginalExpPatternIdsV12100.lookup(10025)')==20
    assert p.evaluate('BFGlobalOriginalExpPatternIdsV12100.lookup(87602603)')==15
    assert p.evaluate('BFGlobalOriginalExpPatternIdsV12100.lookup(123456789)') is None
    p.add_script_tag(path=str(A/'bf_global_unit_archive.js'))
    p.locator('.bf-navbar [data-bf-goto="units"]').click()
    p.locator('[data-bf-unit-tab="box"]').click()
    p.locator('#bf-unit-encyclopedia summary').click()
    p.locator('#bf-archive-search').fill('10025')
    p.locator('.bf-archive-unit').click()
    assert 'Original EXP pattern ID 20' in p.locator('#bf-archive-detail').inner_text()
    assert 'not verified' in p.locator('#bf-archive-detail').inner_text()
    after=p.evaluate("""()=>({data:JSON.stringify(P),
      saved:(()=>{try{return localStorage.getItem('bf_global_offline_demo_v7')}catch(_){return null}})()})""")
    assert before==after,(before,after)
    assert not errors,errors
    b.close()
print('PASS v121: all 2291 original EXP-pattern IDs (10/15/20:248/245/1798), 72 original joins, read-only UI/save v7')
