"""v125: 2,258 source-verified 2022 Global normal hit frame references.
Read-only. Original ticks/weights are NOT native playback timing or damage math.
"""
import base64,gzip,hashlib,json,re,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
meta=json.loads((R/'source_data/bf_global_2022_full_normal_frames_v125.json').read_text('utf8'))
assert meta['archiveSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert meta['sourceRecordCount']==2291 and meta['sourceEligible']==2258
assert len(meta['excludedIds'])==33 and 1 in meta['excludedIds'] and 10023 in meta['excludedIds']
assert meta['whitespaceSanitizedIds']==[20926,51136,820317,850347]
code=(A/'bf12500_full_original_normal_hits.js').read_text('utf8')
assert len(code.encode('utf8'))<65536
assert all(s not in code for s in ('P.unitExp=', 'P.roster=', 'localStorage.setItem', 'Math.random', 'fetch(', 'XMLHttpRequest', 'window.BF_ARCHIVE_NORMAL_HITS='))
match=re.search(r"const encoded = atob\('([A-Za-z0-9+/=]+)'\);",code)
assert match
compressed=base64.b64decode(match.group(1),validate=True)
assert len(compressed)==meta['gzipBytes']
assert hashlib.sha256(compressed).hexdigest()==meta['gzipSha256']
data=gzip.decompress(compressed)
assert len(data)==meta['packedBytes']==60443
assert hashlib.sha256(data).hexdigest()==meta['packedSha256']
rows={};pos=0;uid=0
for i in range(2258):
    shift=0;delta=0
    while True:
        assert pos<len(data) and shift<=28
        byte=data[pos];pos+=1
        delta+=(byte&127)<<shift;shift+=7
        if byte<128:break
    uid+=delta
    assert uid not in rows and uid>0
    count=data[pos];pos+=1
    assert 1<=count<=25
    events=[]
    for _ in range(count):
        n=int.from_bytes(data[pos:pos+3],'big');pos+=3
        events.append([n>>12,(n>>5)&127,(n>>3)&3,n&7])
    assert sum(x[1] for x in events)==100
    rows[uid]=events
assert pos==len(data) and len(rows)==2258
canonical=json.dumps([[k,v] for k,v in rows.items()],separators=(',',':')).encode()
assert hashlib.sha256(canonical).hexdigest()==meta['canonicalRowsSha256']=='e99e843c6d0c3c46b30fab217fb3c7415275ebf58782008a3a0127e90df0b836'
assert all(id not in rows for id in meta['excludedIds'])
assert rows[10011]==[[26,50,2,2],[44,30,2,2],[62,20,2,2]]
assert len(rows[840548])==25 and len(rows[20926])==10
# The existing playable set must remain byte-for-byte equivalent in source tuples.
old=json.loads((R/'source_data/bf_global_playable_attack_frames_v061.json').read_text('utf8'))
assert len(old['rows'])==72
for unit in old['rows']:
    id=unit['unitId']
    if id==10023:assert id not in rows;continue
    original=[list(map(int,x.split(':'))) for x in unit['damageFrames'].split(',')]
    assert rows[id]==original,id
# Cross-check the existing full-archive normalHits lookup for all valid forms.
checks=(A/'bf8400_original_normal_crystal_checks.js').read_text('utf8')
m=re.search(r"const packed='([0-9a-z,|]+)';",checks)
assert m
checkRows={};running=0
for part in m.group(1).split('|'):
    d,compound=part.split(',');running+=int(d,36)
    hits,checkCount=divmod(int(compound,36),64)
    checkRows[running]=hits
assert len(checkRows)==2258
assert {uid:len(hits) for uid,hits in rows.items()}==checkRows
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
renderer=(A/'bf_global_unit_archive.js').read_text('utf8')
assert 'readPackagedText("bf12500_full_original_normal_hits.js")' in java
assert java.index('readPackagedText("bf8400_original_normal_crystal_checks.js")')<java.index('readPackagedText("bf12500_full_original_normal_hits.js")')
assert 'BFGlobalOriginalNormalHitArchiveV12500?.lookup?.(id)' in renderer
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
        executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
        args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content('<div id="bf-owned-box"></div><script id="bf-global-unit-catalog-data" type="application/json"></script>')
    packedCatalog=base64.b64decode((R/'source_data/bf_global_original_unit_catalog.json.gz.b64').read_text())
    archive=json.loads(gzip.decompress(packedCatalog))
    assert len(archive['units'])==2291
    page.evaluate('data=>{window.BFUnitBox={};window.BF_ARCHIVE_NORMAL_HITS={"10011":{raw:"26:50:2:2,44:30:2:2,62:20:2:2"}};document.getElementById("bf-global-unit-catalog-data").textContent=data}',json.dumps(archive,separators=(',',':')))
    baseline=page.evaluate('JSON.stringify(window.BF_ARCHIVE_NORMAL_HITS)')
    page.add_script_tag(path=str(A/'bf_global_unit_archive.js'))
    page.add_script_tag(path=str(A/'bf12500_full_original_normal_hits.js'))
    page.wait_for_function('window.BFGlobalOriginalNormalHitArchiveV12500?.count===2258',timeout=30000)
    assert page.evaluate('BFGlobalOriginalNormalHitArchiveV12500.lookup(10023)') is None
    assert page.evaluate('BFGlobalOriginalNormalHitArchiveV12500.lookup(840548).events.length')==25
    assert page.evaluate('BFGlobalOriginalNormalHitArchiveV12500.lookup(10011).events')==rows[10011]
    assert page.evaluate('JSON.stringify(window.BF_ARCHIVE_NORMAL_HITS)')==baseline
    page.locator('#bf-unit-encyclopedia').evaluate('(node)=>{node.open=true}')
    page.locator('#bf-archive-search').fill('840548')
    page.locator('.bf-archive-unit').first.click()
    assert 'ORIGINAL NORMAL ATTACK FRAMES' in page.locator('#bf-archive-detail').inner_text()
    assert 'NOT verified playback seconds' in page.locator('#bf-archive-detail').inner_text()
    assert not errors,errors
    browser.close()
print('PASS v125: 2258/2291 original Global normal attack full frame tuples, 71 playable preserved, no live combat/save writes')
