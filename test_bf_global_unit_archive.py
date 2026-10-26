"""v0.26 source-integrity, staged assets, UI filters and save/roster isolation.

Never writes user saves; browser uses disposable localStorage only.
"""
import base64,gzip,hashlib,io,json,re,shutil,zipfile
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
META=json.loads((ROOT/'source_data/bf_global_original_unit_catalog_meta.json').read_text('utf-8'))
raw=gzip.decompress(base64.b64decode((ROOT/'source_data/bf_global_original_unit_catalog.json.gz.b64').read_text()))
assert hashlib.sha256(raw).hexdigest()==META['catalogJsonSha256']
source=json.loads(raw)
assert len(source['units'])==META['catalogRecordCount']==2291
assert source['stats']['namesFromEnglish']>=2200
assert source['stats']['namesUnresolved']<=10
assert sum(x['thumbnail'] for x in source['units'])==META['thumbnailCount']==127
assert len({x['id'] for x in source['units']})==2291
with zipfile.ZipFile(io.BytesIO(base64.b64decode(
        (ROOT/'source_assets/bf1/BF1_Global_2022_Unit_Archive_Thumbs_Curated.zip.b64').read_text()))) as z:
    assert len(z.namelist())==127
    for name in z.namelist():
        assert (ASSETS/name).read_bytes()==z.read(name)
index=(ASSETS/'index.html').read_text('utf-8')
assert index.count('id="bf-global-unit-catalog-data"')==1
assert 'BF_GLOBAL_UNIT_ARCHIVE_BEGIN' in index
assert '<script type="application/json" id="bf-global-unit-catalog-data">' in index
assert 'BFGlobalUnitArchive' in (ASSETS/'bf_global_unit_archive.js').read_text('utf-8')
print('PASS 2,291 authenticated unit/form records, localization, evolution IDs, 127 byte-identical original PNGs')

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
        executable_path=shutil.which('google-chrome') or shutil.which('google-chrome-stable') or shutil.which('chromium'),
        args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errs=[]
    page.on('pageerror',lambda e:errs.append(str(e)))
    def serve(route):
        rel=route.request.url.split('bf-assets.test/',1)[-1].split('?',1)[0]
        p=(ASSETS/rel).resolve()
        if p.is_file() and p.is_relative_to(ASSETS.resolve()) and p.suffix in ('.png','.jpg'):
            route.fulfill(status=200,body=p.read_bytes(),content_type='image/png' if p.suffix=='.png' else 'image/jpeg')
        else:route.fulfill(status=404,body=b'')
    page.route('http://bf-assets.test/**',serve)
    page.evaluate('''() => {
      const store={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem(k){return store[k]??null},setItem(k,v){store[k]=String(v)},
        removeItem(k){delete store[k]},key(n){return Object.keys(store)[n]??null},
        get length(){return Object.keys(store).length}
      }});window.alert=()=>{};window.confirm=()=>true;
    }''')
    html=index.replace('<head>','<head><base href="http://bf-assets.test/">',1)
    page.set_content(html,wait_until='load',timeout=60000)
    page.add_style_tag(path=str(ASSETS/'bf_home_nav.css'))
    page.add_script_tag(path=str(ASSETS/'bf_home_nav.js'))
    page.add_style_tag(path=str(ASSETS/'bf_global_unit_archive.css'))
    page.add_script_tag(path=str(ASSETS/'bf_global_unit_archive.js'))
    before=page.evaluate('''() => ({state:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7'),mission:QUEST.missionId,auto:S.auto})''')
    assert page.evaluate('BFGlobalUnitArchive.count')==2291
    assert page.evaluate('BFGlobalUnitArchive.thumbnailCount')==127
    unit=page.evaluate('BFGlobalUnitArchive.find(10011)')
    assert unit['name']=='Fencer Vargas' and unit['unitBaseHp']==1030
    assert 10012 in unit['evo']
    assert page.evaluate('BFGlobalUnitArchive.find(810547).name')=='Natsu Dragneel'
    assert page.evaluate('BFGlobalUnitArchive.find(850198).thumbnail') is True
    page.locator('.bf-navbar [data-bf-goto="units"]').click()
    page.locator('[data-bf-unit-tab="box"]').click()
    page.locator('#bf-unit-encyclopedia summary').click()
    assert page.locator('.bf-archive-unit').count()==24
    assert '2,291' in page.locator('#bf-archive-count').inner_text()
    page.locator('#bf-archive-next').click()
    assert page.evaluate('BFGlobalUnitArchive.activePage')==2
    page.locator('#bf-archive-prev').click()
    assert page.evaluate('BFGlobalUnitArchive.activePage')==1
    page.locator('#bf-archive-search').fill('Natsu Dragneel')
    assert page.locator('.bf-archive-unit').count()==2  # two original Natsu evolution forms
    page.locator('#bf-archive-search').fill('810547')
    assert page.locator('.bf-archive-unit').count()==1
    page.locator('.bf-archive-unit').click()
    assert page.locator('#bf-archive-detail').is_visible()
    assert 'Original unit ID 810547' in page.locator('#bf-archive-detail').inner_text()
    assert 'Leader skill ID' in page.locator('#bf-archive-detail').inner_text()
    page.locator('#bf-archive-search').fill('10011')
    assert page.locator('.bf-archive-unit').count()==1
    assert page.locator('.bf-archive-unit img').count()==1
    image=page.locator('.bf-archive-unit img')
    page.wait_for_function("document.querySelector('.bf-archive-unit img').naturalWidth > 0")
    page.locator('#bf-archive-search').fill('')
    page.locator('#bf-archive-element').select_option('1')
    assert 0 < page.evaluate('BFGlobalUnitArchive.matchingCount') < 2291
    page.locator('#bf-archive-rarity').select_option('2')
    assert 0 < page.evaluate('BFGlobalUnitArchive.matchingCount') < 2291
    page.locator('#bf-archive-search').fill('zzz_impossible_original')
    assert page.locator('.bf-archive-unit').count()==0
    assert 'No matching' in page.locator('#bf-archive-results').inner_text()
    after=page.evaluate('''() => ({state:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7'),mission:QUEST.missionId,auto:S.auto})''')
    assert before==after,(before,after)
    assert not errs,errs
    print('PASS portrait UI, paginated search, element/rarity, detail view, sprite loading, unchanged save/roster/Auto')
    browser.close()
