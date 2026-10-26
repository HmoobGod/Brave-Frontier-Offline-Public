"""Chromium v0.43: source-verified 12 SBB previews, UI and save isolation."""
from pathlib import Path
import base64,gzip,hashlib,json,re,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent; D=R/'source_data'
html=(R/'app/src/main/assets/index.html').read_text('utf8')
assert html.count('/* BF_GLOBAL_SBB_PREVIEW_V043 */')==1
for m in ['/* BF_COORDINATED_AUTO_V042 */','/* BF_SOURCE_AWARE_AUTO_V041 */','/* BF_EVOLUTION_ROADMAP_V039 */']:
    assert html.count(m)==1,m
meta=json.loads((D/'bf_global_original_lore_meta.json').read_text('utf8'))
packed=base64.b64decode((D/'bf_global_original_lore_codex.json.gz.b64').read_text('ascii'))
assert hashlib.sha256(packed).hexdigest()==meta['payloadGzipSha256']
raw=gzip.decompress(packed)
assert hashlib.sha256(raw).hexdigest()==meta['payloadJsonSha256']
lore={x['id']:x for x in json.loads(raw)['units']}
ids=[10015,20015,30015,40015,50015,60015,10025,20025,30025,40025,50025,60025]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.route('http://bf-assets.test/**',lambda route:route.fulfill(status=404,body=b''))
    page.evaluate("""() => {
      const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:k=>db[k]??null,setItem:(k,v)=>{db[k]=String(v)},removeItem:k=>{delete db[k]},
        key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});
      window.alert=()=>{};window.confirm=()=>true;
    }""")
    page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=90000)
    assert page.locator('#bf043-sbb-preview').count()==1
    assert page.locator('#burst').count()==1
    assert page.evaluate('BF043SBBSource.count')==12
    initial=page.evaluate("()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),progress:JSON.stringify(P)})")
    data=page.evaluate("""(ids)=>ids.map(id=>BF043SBBSource.infoFor(id))""",ids)
    for id,rec in zip(ids,data):
        src=lore[id]['sbb']
        assert rec['skillId']==src['id'] and rec['name']==src['name'] and rec['description']==src['description'],(id,rec)
        assert rec['target']=='all_enemies',rec
        match=re.search(r'\b(\d+) combo\b',src['description'],re.I)
        assert rec['combo']==(int(match.group(1)) if match else None),rec
    assert page.evaluate('BF043SBBSource.infoFor(987654)') is None
    assert page.evaluate('BF043SBBSource.infoFor("10015bad")') is None
    assert page.evaluate('BF043SBBSource.infoFor(10011)') is None
    page.evaluate("document.querySelector('#bf043-sbb-preview summary').click()")
    page.evaluate("""()=>{
      BF_debug.reset();S.selected=0;S.party[0].unitId=10015;BF043SBBSource.refresh();
    }""")
    text=page.locator('#bf043-sbb-preview .bf043-body').text_content()
    assert 'Sacred Sunshine' in text and 'NOT PLAYABLE' not in text or 'not playable' in text.lower(),text
    assert '10 combo' in text and 'REFERENCE ONLY' in text
    page.evaluate("()=>{S.party[0].unitId=60025;BF043SBBSource.refresh()}")
    text=page.locator('#bf043-sbb-preview .bf043-body').text_content()
    assert 'Ultimate Art: Avatamsa' in text and 'Target: all enemies' in text and 'combo' not in text,text
    page.evaluate("()=>{S.party[0].unitId=10011;BF043SBBSource.refresh()}")
    assert 'no verified' in page.locator('#bf043-sbb-preview .bf043-body').text_content()
    assert page.evaluate("P.version")==7
    assert page.evaluate("JSON.stringify(P)")==initial['progress']
    assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==initial['save']
    assert not errors,errors
    print('PASS v0.43: twelve verified Global SBB previews, absent entries excluded, no real SBB action, v7 save unchanged',flush=True)
    browser.close()
