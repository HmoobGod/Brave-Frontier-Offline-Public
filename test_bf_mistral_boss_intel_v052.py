"""v0.52 source-backed Mistral boss info and opt-in encounter browser regressions."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
archive=json.loads((ROOT/'source_data/bf_global_mistral_boss_intel_v052.json').read_text())
assert archive['schema']=='bf-global-mistral-boss-intel-v052'
assert [r['missionId'] for r in archive['entries']]==[81,82,83,84,85]
assert archive['entries'][-1]['bosses'][0]['hp']==50000
assert archive['optIn']['activeByDefault'] is False
html_file=ASSETS/'index.html'
html=html_file.read_text('utf-8')
assert html.count('/* BF_MISTRAL_BOSS_HOOK_V052 */')==1
assert html.count('/* BF_MISTRAL_BOSS_INTEL_V052 */')==1
assert 'bf_global_offline_demo_v7' in html
before=hashlib.sha256(html.encode()).hexdigest()
subprocess.run([sys.executable,str(ROOT/'prepare_story_boss_v052.py')],cwd=ROOT,check=True)
assert hashlib.sha256(html_file.read_bytes()).hexdigest()==before,'prep must be idempotent'

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
        executable_path=shutil.which('chromium') or shutil.which('google-chrome')
                        or shutil.which('google-chrome-stable'),
        args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    def local(route):
        rel=route.request.url.split('bf-assets.test/',1)[-1]
        path=ASSETS/rel
        if path.is_file() and path.resolve().is_relative_to(ASSETS.resolve()) and path.suffix in ('.png','.jpg'):
            route.fulfill(status=200,body=path.read_bytes(),
               content_type='image/jpeg' if path.suffix=='.jpg' else 'image/png')
        else:route.fulfill(status=404,body=b'')
    page.route('http://bf-assets.test/**',local)
    page.evaluate("""() => {
      const saved={};
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:k=>saved[k]??null,setItem:(k,v)=>{saved[k]=String(v)},
        removeItem:k=>{delete saved[k]},key:i=>Object.keys(saved)[i]??null,
        get length(){return Object.keys(saved).length}}});
      window.alert=()=>{};window.confirm=()=>true;
      HTMLMediaElement.prototype.load=()=>{};
      HTMLMediaElement.prototype.pause=()=>{};
      HTMLMediaElement.prototype.play=()=>Promise.resolve();
    }""")
    page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),
                     wait_until='load',timeout=90000)
    assert page.evaluate('BF_MONSTER_DATA.monster.gel.id')=='0001'
    assert page.evaluate('BF052BossIntel.enabled') is False
    assert page.evaluate('BF052BossIntel.entries.length')==5
    assert page.evaluate('P.version')==7
    page.add_style_tag(path=str(ASSETS/'bf_home_nav.css'))
    page.add_script_tag(path=str(ASSETS/'bf_home_nav.js'))
    page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
    page.evaluate('()=>{P.questClears[84]=1;renderQuestList()}')
    page.locator('[data-bf-mission="85"]').click()
    page.wait_for_function("()=>document.querySelector('#bf052-boss-intel')?.hidden===false")
    assert 'Juggernaut' in page.locator('#bf052-boss-intel').inner_text()
    assert '50,000 HP' in page.locator('#bf052-boss-intel').inner_text()
    assert page.evaluate('QUEST.missionId')==85
    initial=page.evaluate("""() => ({
       save:localStorage.getItem('bf_global_offline_demo_v7'),
       progress:JSON.stringify(P),
       roster:JSON.stringify(P.roster),
       squad:JSON.stringify(P.squad)
    })""")
    # Experimental mode off by default, and old demo encounter preserved.
    page.evaluate('()=>{S.wave=7;S.enemies=makeWave(7);update()}')
    assert page.evaluate('S.enemies.some(e=>e.sourceBackedBoss)') is False
    page.locator('#bf052-enable-original-juggernaut').check()
    assert page.evaluate('BF052BossIntel.enabled') is True
    assert page.evaluate('S.wave')==0,'opt-in resets current fight'
    page.evaluate('()=>{S.wave=7;S.enemies=makeWave(7);update()}')
    bosses=page.evaluate("S.enemies.map(e=>({id:e.id,name:e.name,maxHp:e.maxHp,element:e.element,source:e.sourceBackedBoss}))")
    assert bosses==[{'id':'gel','name':'Juggernaut · demo combat','maxHp':50000,
                    'element':'Thunder','source':True}],bosses
    assert page.evaluate('S.enemies[0].hp')==50000
    assert page.evaluate('BF_debug.state().enemies[0].name')=='Juggernaut · demo combat'
    assert page.locator('#bf052-enable-original-juggernaut').is_checked()
    unchanged=page.evaluate("""() => ({
       save:localStorage.getItem('bf_global_offline_demo_v7'),
       progress:JSON.stringify(P),
       roster:JSON.stringify(P.roster),
       squad:JSON.stringify(P.squad)
    })""")
    assert unchanged==initial,(initial,unchanged)
    # Opt-in cannot affect training mode, other missions, or non-boss waves.
    assert page.evaluate("""() => BF052BossIntel.encounter(85,6,8,'archive',
        [{id:'gel',atk:20,def:10}])""") is None
    assert page.evaluate("""() => BF052BossIntel.encounter(85,7,8,'training',
        [{id:'gel',atk:20,def:10}])""") is None
    assert page.evaluate("""() => BF052BossIntel.encounter(84,6,7,'archive',
        [{id:'gel',atk:20,def:10}])""") is None
    page.locator('#bf052-enable-original-juggernaut').uncheck()
    page.evaluate('()=>{S.wave=7;S.enemies=makeWave(7)}')
    assert page.evaluate('S.enemies.some(e=>e.sourceBackedBoss)') is False
    assert page.evaluate('JSON.stringify(P)')==initial['progress']
    assert not errors,errors
    browser.close()
print('PASS v0.52 wiki-sourced boss preview, opt-in authentic Juggernaut name/art/HP, demo math, v7 unchanged')
