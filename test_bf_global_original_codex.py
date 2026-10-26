"""v0.27: authentic 2022 Global lore/BB/LS/SBB/UBB/evolution-source viewer.

Read-only: no saved data, owned unit, summon, quest or combat behavior changes.
"""
from pathlib import Path
import base64,gzip,hashlib,json,shutil,re
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
A=ROOT/'app/src/main/assets'
META=json.loads((ROOT/'source_data/bf_global_original_lore_meta.json').read_text())
compressed=base64.b64decode((ROOT/'source_data/bf_global_original_lore_codex.json.gz.b64').read_text())
assert hashlib.sha256(compressed).hexdigest()==META['payloadGzipSha256']
raw=gzip.decompress(compressed)
assert hashlib.sha256(raw).hexdigest()==META['payloadJsonSha256']
archive=json.loads(raw)
assert archive['stats']['rows']==2291
assert len(archive['units'])==2291
assert len({u['id'] for u in archive['units']})==2291
assert archive['stats']['story']>=1600
assert archive['stats']['bb']>=1600
assert archive['stats']['recipes']>=1200
assert archive['provenance']['mstZipSha256']==META['mstZipSha256']
assert archive['provenance']['englishTextZipSha256']==META['englishTextZipSha256']
byid={u['id']:u for u in archive['units']}
assert byid[10011]['bb']['name']=='Flare Ride'
assert byid[10011]['leader']['name']=="Fire Spirit's Power"
assert byid[10011]['recipes'][0]['target']==10012
assert byid[10011]['recipes'][0]['zel']==2500
assert byid[810547]['leader']['name']=='Fire Dragon Slayer Magic'
assert byid[810547]['recipes'][0]['zel']==3000000
assert byid[850198]['ubb']['name']=='Sakurafubuki Waltz'
html=(A/'index.html').read_text('utf-8')
assert html.count('id="bf-original-unit-lore-data"')==1
assert html.count('BF_GLOBAL_UNIT_LORE_BEGIN')==1
match=re.search(r'<script type="application/json" id="bf-original-unit-lore-data">(.*?)</script>',html,re.S)
assert match
assert json.loads(match.group(1))==archive
assert '</script>' not in match.group(1).lower()
assert 'bf-codex-ability' in (A/'bf_global_unit_archive.js').read_text('utf-8')
print('PASS original Global 2022 codex SHA, 2,291 unit forms, localized BB and full evolution source records')

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
        executable_path=shutil.which('google-chrome') or shutil.which('google-chrome-stable') or shutil.which('chromium'),
        args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.evaluate('''() => {
      const store={}; Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem(k){return store[k]??null},setItem(k,v){store[k]=String(v)},
        removeItem(k){delete store[k]},key(n){return Object.keys(store)[n]??null},
        get length(){return Object.keys(store).length}
      }});window.alert=()=>{};window.confirm=()=>true;
    }''')
    page.route('http://bf-assets.test/**',lambda route:route.fulfill(status=404,body=b''))
    page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=60000)
    page.add_style_tag(path=str(A/'bf_home_nav.css'))
    page.add_script_tag(path=str(A/'bf_home_nav.js'))
    page.add_style_tag(path=str(A/'bf_global_unit_archive.css'))
    page.add_script_tag(path=str(A/'bf_global_unit_archive.js'))
    assert page.evaluate('BFGlobalUnitArchive.originalCodexAvailable') is True
    assert page.evaluate('BFGlobalUnitArchive.loreCount')==archive['stats']['story']
    before=page.evaluate('''() => ({save:localStorage.getItem('bf_global_offline_demo_v7'),
      player:JSON.stringify(P),mission:QUEST.missionId,auto:S.auto})''')
    page.locator('.bf-navbar [data-bf-goto="units"]').click()
    page.locator('[data-bf-unit-tab="box"]').click()
    page.evaluate('BFUnitBox.showDetail(10011)')
    button=page.locator('#bf-box-detail .bf-box-original-profile')
    assert button.count()==1
    button.click()
    assert page.locator('#bf-unit-encyclopedia').evaluate('(e)=>e.open') is True
    assert 'Fencer Vargas' in page.locator('#bf-archive-detail').inner_text()
    assert 'ORIGINAL GLOBAL RECORDS' in page.locator('#bf-archive-detail').inner_text()
    page.locator('#bf-archive-detail .bf-codex-skills > summary').click()
    assert 'Flare Ride' in page.locator('#bf-archive-detail').inner_text()
    assert "Fire Spirit's Power" in page.locator('#bf-archive-detail').inner_text()
    assert 'NOT implemented demo battle effects' in page.locator('#bf-archive-detail').inner_text()
    page.locator('#bf-archive-detail .bf-codex-recipes summary').click()
    assert '2,500 Zel' in page.locator('#bf-archive-detail').inner_text()
    assert 'Material 10130' in page.locator('#bf-archive-detail').inner_text()
    page.locator('#bf-archive-detail .bf-codex-evo-jump').click()
    assert 'Burning Vargas' in page.locator('#bf-archive-detail').inner_text()
    # Crossover lore/skills/evolution: source text, not speculative gameplay.
    assert page.evaluate('BFGlobalUnitArchive.showDetail(810547)') is True
    assert page.locator('#bf-archive-detail .bf-codex-ability').count()>=4
    page.locator('#bf-archive-detail .bf-codex-story summary').click()
    assert 'Dragon Slayer' in page.locator('#bf-archive-detail').inner_text()
    page.locator('#bf-archive-detail .bf-codex-recipes summary').click()
    assert '3,000,000 Zel' in page.locator('#bf-archive-detail').inner_text()
    assert '1,000,000 Karma' in page.locator('#bf-archive-detail').inner_text()
    assert page.evaluate('BFGlobalUnitArchive.showDetail(850198)') is True
    page.locator('#bf-archive-detail .bf-codex-skills > summary').click()
    assert 'Sakurafubuki Waltz' in page.locator('#bf-archive-detail').inner_text()
    after=page.evaluate('''() => ({save:localStorage.getItem('bf_global_offline_demo_v7'),
      player:JSON.stringify(P),mission:QUEST.missionId,auto:S.auto})''')
    assert before==after,(before,after)
    assert not errors,errors
    print('PASS owned-to-archive navigation, original skill lore and recipes, crossover records, no save/combat mutations')
    browser.close()
