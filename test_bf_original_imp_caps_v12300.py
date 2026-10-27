"""v123 verified original 2022 Global Imp bonus-cap reference for all 2,291 units.
Read-only archived source metadata, not demo enhancement or v7 save migration.
"""
import base64,gzip,hashlib,json,re,shutil,struct
from pathlib import Path
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
source=R/'source_data'
meta=json.loads((source/'bf_global_original_unit_catalog_meta.json').read_text('utf8'))
packed=base64.b64decode((source/'bf_global_original_unit_catalog.json.gz.b64').read_text('ascii'))
assert hashlib.sha256(packed).hexdigest()==meta['catalogGzipSha256']
raw=gzip.decompress(packed)
assert hashlib.sha256(raw).hexdigest()==meta['catalogJsonSha256']
archive=json.loads(raw)
assert archive['schema']=='bf-global-unit-archive-2022-v1'
units=archive['units']
assert len(units)==2291
ids=sorted(u['id'] for u in units)
assert len(set(ids))==2291
assert hashlib.sha256(json.dumps(ids,separators=(',',':')).encode()).hexdigest()=='19a96b6d8987a7fb3099fc302185020702e6da248f9493f47268cb4ccba88c89'
code=(R/'app/src/main/assets/bf_global_unit_archive.js').read_text('utf8')
match_i=re.search(r"const which=atob\('([A-Za-z0-9+/=]+)'\)",code)
match_t=re.search(r"const data=atob\('([A-Za-z0-9+/=]+)'\)",code)
assert match_i and match_t
which=base64.b64decode(match_i.group(1),validate=True)
table=base64.b64decode(match_t.group(1),validate=True)
assert len(which)==2291 and len(table)==147*8
assert hashlib.sha256(which).hexdigest()=='99d6b3476f1c3ded0335de55b449eba44fa511624861c1693bfc35ae70d8149c'
assert hashlib.sha256(table).hexdigest()=='40ea95d51f6433bf2bd3cb9a3aebb6403445cb3f8bfeafd3ff1eb420517a1518'
assert max(which)==146 and len(set(which))==147
patterns=[struct.unpack_from('>4H',table,8*i) for i in range(147)]
assert len(set(patterns))==147
caps=[patterns[k] for k in which]
assert sum(all(v==0 for v in c) for c in caps)==129
pairs=[[uid,*c] for uid,c in zip(ids,caps)]
assert hashlib.sha256(json.dumps(pairs,separators=(',',':')).encode()).hexdigest()=='3ab0bc3efaf968dd1959490f892dbfde01c5cad882b0bd3377ee98362c3375de'
by_id=dict(zip(ids,caps))
assert by_id[10011]==(400,160,80,80)
assert by_id[10017]==(2200,880,460,460)
assert by_id[10025]==(1000,240,560,400)
assert by_id[60015]==(700,580,580,280)
assert not any(k in code for k in ('P.unitExp=', 'localStorage.setItem', 'Math.random', 'fetch(', 'XMLHttpRequest'))
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
        executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
        args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page()
    errors=[]
    page.on('pageerror',lambda exc:errors.append(str(exc)))
    page.set_content('<div id="bf-owned-box"></div><script id="bf-global-unit-catalog-data" type="application/json"></script>')
    page.evaluate('payload=>{window.BFUnitBox={};document.getElementById("bf-global-unit-catalog-data").textContent=payload}',json.dumps(archive,separators=(',',':')))
    before=page.evaluate("""()=>{try{return localStorage.getItem('bf_global_offline_demo_v7')}catch(_){return null}}""")
    page.add_script_tag(content=code)
    assert page.evaluate('BFGlobalUnitArchive.count')==2291
    for uid,expected in [(1,[0,0,0,0]),(10011,[400,160,80,80]),(10017,[2200,880,460,460]),(10025,[1000,240,560,400]),(60015,[700,580,580,280]),(87602603,[0,0,0,0])]:
        assert page.evaluate('(id)=>BFGlobalUnitArchive.originalImpCaps(id)',uid)==expected,uid
        assert page.evaluate('(id)=>BFGlobalUnitArchive.showDetail(id)',uid)
        text=page.locator('#bf-archive-detail').text_content()
        assert all(k in text for k in ('Original Imp bonus caps','HP +'+str(expected[0]),'ATK +'+str(expected[1]),'DEF +'+str(expected[2]),'REC +'+str(expected[3]),'source reference only'))
    assert before==page.evaluate("""()=>{try{return localStorage.getItem('bf_global_offline_demo_v7')}catch(_){return null}}""")
    assert not errors,errors
    browser.close()
print('PASS v123: 2291/2291 source-authenticated original Imp caps, 147 patterns, 129 zero caps; read-only Chromium/save guard')
