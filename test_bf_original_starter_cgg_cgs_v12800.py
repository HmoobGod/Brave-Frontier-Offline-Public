"""v128: source CGG/CGS geometry only; no gameplay or native rendering claims."""
from pathlib import Path
import base64,gzip,hashlib,json,re,shutil
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
meta=json.loads((R/'source_data/bf_global_2022_starter_cgg_geometry_v128.json').read_text('utf8'))
old=json.loads((R/'source_data/bf_global_2022_starter_7_8_source_readiness_v127.json').read_text('utf8'))
assert meta['schema']=='bf-global-2022-starter-cgg-cgs-sequences-v128'
assert meta['sourceZipSha256']==old['sourceZipSha256']
assert meta['v127Canonical12SourceSha256']==old['canonical12SourceSha256']
assert meta['sourceAssetsBundled'] is False and meta['playableExpansion'] is False
assert meta['originalNativeRendererVerified'] is False
ids=[r['unitId'] for r in old['rows']]
assert ids==meta['formIds'] and len(ids)==12
js=(A/'bf12800_original_starter_cgg_cgs.js').read_text('utf8')
assert len(js.encode())<65536
assert 'DecompressionStream' in js
assert not any(x in js for x in ['localStorage','P.unitExp=','P.evolutions=','P.roster=', 'fetch(', 'XMLHttpRequest','Math.random'])
match=re.search(r"const bytes=atob\('([A-Za-z0-9+/=]+)'\);",js)
assert match
z=base64.b64decode(match.group(1),validate=True)
assert len(z)==meta['normalizedGzipBytes']==22994
assert hashlib.sha256(z).hexdigest()==meta['normalizedGzipSha256']=='b0f3a29cbec8640b70a1ee0d77512d1f966f473840ec2c9002df9f108a60b976'
raw=gzip.decompress(z)
assert hashlib.sha256(raw).hexdigest()==meta['normalizedJsonSha256']=='7535ec0bae51fe425fc8db7ee3341d0dda0b6e80d6586c88cd888161c4f0951a'
assert len(raw)==meta['normalizedJsonBytes']==184101
rows=json.loads(raw)
assert [r[0] for r in rows]==ids
assert len(rows)==12
assert sum(len(row[1]) for row in rows)==meta['totalCggFrames']==308
assert sum(f[1] for row in rows for f in row[1])==meta['totalCggLayers']==5378
for (uid,cgg,idle,atk,move),prior in zip(rows,old['rows']):
 assert uid==prior['unitId']
 assert len(cgg)==prior['animation']['cggSourceFrameCount']
 assert all(f[0]==0 and len(f)==2+11*f[1] for f in cgg)
 for sequence in (idle,atk,move):
  assert sequence and all(len(q)==4 and all(type(v) is int for v in q) and 0<=q[0]<len(cgg) and q[3]>0 for q in sequence)
 for f in cgg:
  for p in (f[2+11*j:2+11*(j+1)] for j in range(f[1])):
   assert len(p)==11 and p[2] in (0,1,2,3) and p[3] in (0,1)
   assert 0<=p[4]<=100 and p[5] in (-180,-90,0,90,180) and p[10]==0
assert all(uid not in [r['unitId'] for r in old['rows'] if r['unitId'] not in ids] for uid in ids)
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert 'readPackagedText("bf12800_original_starter_cgg_cgs.js")' in java
archive=(A/'bf_global_unit_archive.js').read_text('utf8')
assert 'BFGlobalOriginalStarterCggV12800?.lookup?.(id)' in archive

with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
 # about:blank has no localStorage authority in CI. Use isolated, throw-free
 # save emulation, exactly as the v127 owner-save regression does.
 page.evaluate("""() => {
   const db={};
   Object.defineProperty(window,'localStorage',{configurable:true,value:{
     getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
     removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
     get length(){return Object.keys(db).length}}});
   window.alert=()=>{};window.confirm=()=>true;
   HTMLMediaElement.prototype.load=()=>{};
   HTMLMediaElement.prototype.pause=()=>{};
   HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 page.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 assert page.evaluate('P.version')==7
 before=page.evaluate("""()=>({player:JSON.stringify(P),saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 page.add_script_tag(path=str(A/'bf12800_original_starter_cgg_cgs.js'))
 assert page.evaluate('async()=>await BFGlobalOriginalStarterCggV12800.ready') is True
 assert page.evaluate('BFGlobalOriginalStarterCggV12800.count')==12
 assert page.evaluate('BFGlobalOriginalStarterCggV12800.lookup(10016).cggFrameCount')==24
 assert page.evaluate('BFGlobalOriginalStarterCggV12800.lookup(20017).cggFrameCount')==32
 assert page.evaluate('BFGlobalOriginalStarterCggV12800.lookup(10015)') is None
 assert page.evaluate('BFGlobalOriginalStarterCggV12800.lookup(10016).sequences.atk.length')>8
 assert page.evaluate('BFGlobalOriginalStarterCggV12800.source.nativeRenderVerified') is False
 # Read-only encyclopedia. There are 2,291 archived forms, only 72 playable.
 page.add_script_tag(path=str(A/'bf_home_nav.js'))
 page.add_script_tag(path=str(A/'bf_global_unit_archive.js'))
 page.locator('.bf-navbar [data-bf-goto="units"]').click()
 page.locator('[data-bf-unit-tab="box"]').click()
 page.locator('#bf-unit-encyclopedia summary').click()
 page.locator('#bf-archive-search').fill('10016')
 page.locator('.bf-archive-unit').first.click()
 detail=page.locator('#bf-archive-detail')
 assert 'ORIGINAL 2022 SPRITE CGG / CGS' in detail.inner_text()
 detail.locator('summary').filter(has_text='ORIGINAL 2022 SPRITE CGG / CGS').click()
 assert 'Native 2022 rendering is not verified' in detail.inner_text()
 assert '24 source frames' in detail.inner_text()
 page.add_script_tag(path=str(A/'bf12800_original_starter_cgg_cgs.js'))
 assert page.evaluate('BFGlobalOriginalStarterCggV12800.count')==12
 after=page.evaluate("""()=>({player:JSON.stringify(P),saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,(before,after)
 assert not errors,errors
 browser.close()
print('PASS v128: exact 12 source CGG/CGS sequences, 308 frames, 5378 layers, read-only encyclopedia, 72 playable, v7 saves unchanged')
