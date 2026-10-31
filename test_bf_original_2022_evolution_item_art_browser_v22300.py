"""v223 read-only browser/actual image probe using an isolated file:// fixture.

Requires prepare_bf_original_2022_evolution_item_art_v22300.py first.
"""
from pathlib import Path
import json
import shutil
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
CAT=json.loads((ROOT/'source_data/bf_global_2022_evolution_item_art_catalog_v222.json').read_text('utf8'))
JS=ASSETS/'bf22300_original_2022_evolution_item_gallery.js'
assert JS.exists()
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome'),args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
    valid={"/content/item/"+row[2] for row in CAT['rows']}
    def serve(route):
        path=urlparse(route.request.url).path
        if path=="/index.html":
            route.fulfill(status=200,content_type="text/html; charset=utf-8",body='<html><body><details id="bf15300-legend-stone-source"><summary>Legend Stone</summary></details></body></html>')
        elif path in valid:
            route.fulfill(status=200,content_type="image/png",body=(ASSETS/path.lstrip('/')).read_bytes())
        else:
            route.abort()
    page.route('https://bf-v223-test.invalid/**',serve)
    page.set_content('<html><head><base href="https://bf-v223-test.invalid/"></head><body><details id="bf15300-legend-stone-source"><summary>Legend Stone</summary></details></body></html>')
    page.evaluate('''() => {
    let writes=0; const save={'bf_global_offline_demo_v7':'owner-save-untouched'};
    Object.defineProperty(window,'localStorage',{configurable:true,value:{
      getItem:k=>save[k]??null,setItem:(k,v)=>{writes++;save[k]=v},
      removeItem:k=>{writes++;delete save[k]}}});
    window.__writes=()=>writes;
    window.P={version:7,roster:[10011],unitExp:{10011:30},materials:{}};
    window.S={mode:'idle',party:[],enemies:[]};
    window.BFGlobalOriginalLegendStoneExchangeV15300={source:{liveAcquisition:false,saveMutation:false}};
    }''')
    before=page.evaluate('''() => ({p:JSON.stringify(P),s:JSON.stringify(S),save:localStorage.getItem('bf_global_offline_demo_v7'),writes:__writes()})''')
    page.add_script_tag(path=str(JS))
    gallery=page.locator('#bf22300-original-evolution-item-gallery')
    assert gallery.count()==1
    assert page.locator('#bf22300-original-item-grid img').count()==31
    assert page.evaluate('BFGlobalOriginalEvolutionItemGalleryV22300.source.itemCount')==31
    assert page.evaluate('BFGlobalOriginalEvolutionItemGalleryV22300.source.changesSaves') is False
    assert page.evaluate('BFGlobalOriginalEvolutionItemGalleryV22300.lookup(110100).image')=='item_thum_111000.png'
    assert gallery.evaluate('(el)=>el.open') is False
    gallery.evaluate('(el)=>{el.open=true}')
    page.evaluate('''() => {document.querySelectorAll('#bf22300-original-item-grid img').forEach(img=>img.loading='eager')}''')
    page.wait_for_function('''()=>[...document.querySelectorAll('#bf22300-original-item-grid img')].every(img=>img.complete && img.naturalWidth>0 && img.naturalHeight>0)''',timeout=10000)
    page.add_script_tag(path=str(JS))
    assert page.locator('#bf22300-original-item-grid img').count()==31
    after=page.evaluate('''() => ({p:JSON.stringify(P),s:JSON.stringify(S),save:localStorage.getItem('bf_global_offline_demo_v7'),writes:__writes()})''')
    assert before==after, (before,after)
    assert not errors, errors
    browser.close()
print('PASS v223 Chromium: 31/31 original PNG load, panel default closed, no localStorage or P/S writes')
