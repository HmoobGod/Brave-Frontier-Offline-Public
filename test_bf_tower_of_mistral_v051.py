"""v0.51 archived Global Tower of Mistral 81-85; browser and save regressions."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import hashlib, json, shutil, subprocess, sys

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
source=json.loads((ROOT/'source_data/bf_global_tower_of_mistral_v051.json').read_text('utf-8'))
assert source['schema']=='bf-global-tower-of-mistral-v051'
original=(ROOT/'source_assets/bf1/dungeon/dungeon_battle_10800.jpg').read_bytes()
assert len(original)==46410 and hashlib.sha256(original).hexdigest()==source['sources']['backgroundSha256']
assert (ASSETS/'content/dungeon/dungeon_battle_10800.jpg').read_bytes()==original
html_file=ASSETS/'index.html'
html=html_file.read_text('utf-8')
for marker in ('/* BF_TOWER_OF_MISTRAL_V051 */','/* BF_MONSTERS_NEST_V050 */',
               '/* BF_REMAINS_OF_MIRZA_V049 */','/* BF_GLOBAL_QUEST_TEXT_DATA_V048 */'):
    assert html.count(marker)==1,marker
assert 'bf_global_offline_demo_v7' in html
assert len((ASSETS/'bf_home_nav.js').read_bytes()) < 65536
html_sha=hashlib.sha256(html.encode()).digest()
subprocess.run([sys.executable,str(ROOT/'prepare_tower_of_mistral_v051.py')],cwd=ROOT,check=True)
assert hashlib.sha256(html_file.read_bytes()).digest()==html_sha

with sync_playwright() as pw:
    browser=pw.chromium.launch(
        executable_path=shutil.which('chromium') or shutil.which('google-chrome')
                        or shutil.which('google-chrome-stable'),
        headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda e: errors.append(str(e)))
    def serve(route):
        rel=route.request.url.split('bf-assets.test/',1)[-1]
        f=ASSETS/rel
        if f.is_file() and f.resolve().is_relative_to(ASSETS.resolve()) and f.suffix in ('.png','.jpg'):
            route.fulfill(status=200,body=f.read_bytes(),
                content_type='image/jpeg' if f.suffix=='.jpg' else 'image/png')
        else:
            route.fulfill(status=404,body=b'')
    page.route('http://bf-assets.test/**',serve)
    page.evaluate("""() => {
      const items={};
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:k=>items[k]??null,setItem:(k,v)=>{items[k]=String(v)},
        removeItem:k=>{delete items[k]},key:i=>Object.keys(items)[i]??null,
        get length(){return Object.keys(items).length}}});
      window.alert=()=>{}; window.confirm=()=>true;
      HTMLMediaElement.prototype.load=()=>{};
      HTMLMediaElement.prototype.pause=()=>{};
      HTMLMediaElement.prototype.play=()=>Promise.resolve();
    }""")
    page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),
        wait_until='load',timeout=90000)
    state=page.evaluate("""() => ({
        version:P.version, roster:JSON.stringify(P.roster),
        squad:JSON.stringify(P.squad),exp:JSON.stringify(P.unitExp),
        zel:P.zel,karma:P.karma,
        save:localStorage.getItem('bf_global_offline_demo_v7')
    })""")
    page.add_style_tag(path=str(ASSETS/'bf_home_nav.css'))
    page.add_script_tag(path=str(ASSETS/'bf_home_nav.js'))
    page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
    assert page.evaluate('QUESTS.map(q=>q.missionId).slice(0,34)') == [
      1,2,10,11,12,20,21,22,23,30,31,32,33,40,41,42,43,
      50,51,52,53,60,61,62,63,70,71,72,73,81,82,83,84,85]
    assert page.locator('.bf-mission-step-row button').count()==106
    assert page.locator('.bf-mistral-pin').count()==9
    assert page.evaluate('BFMistralMap.isUnlocked(80)') is False
    assert page.evaluate('BFMistralMap.reveal(80)') is False
    for quest,english in zip(source['quests'],source['english']):
        stored=page.evaluate('(id)=>QUESTS.find(q=>q.missionId===id)',quest['missionId'])
        assert stored==quest,(quest,stored)
        matched=page.evaluate('(id)=>BFGlobalQuestText.sourceFor(QUESTS.find(q=>q.missionId===id))',quest['missionId'])
        assert matched['mission']==english and matched['dungeon']['name']=='Tower of Mistral'
        assert page.locator(f'[data-bf-mission="{quest["missionId"]}"]').is_disabled()
    page.evaluate('()=>{P.questClears[73]=1;renderQuestList()}')
    assert page.evaluate('BFMistralMap.isUnlocked(80)') is True
    page.locator('[data-bf-map-list="80"]').click()
    assert page.evaluate('QUEST.missionId')==81
    assert page.evaluate('BFQuestAreas.selectedDungeon')=='80'
    assert page.locator('#questlist .questcard:visible').count()==5
    for i,quest in enumerate(source['quests']):
        if i:
            page.evaluate('(id)=>{P.questClears[id]=1;renderQuestList()}',
                          source['quests'][i-1]['missionId'])
            page.locator(f'[data-bf-mission="{quest["missionId"]}"]').click()
        assert page.evaluate('QUEST.missionId')==quest['missionId']
        assert page.evaluate('S.totalWaves')==quest['battles']
        assert page.evaluate('QUEST.background')=='dungeon_battle_10800.jpg'
        assert source['english'][i]['name'] in page.locator('#bf-mission-name').inner_text()
        assert page.locator('.bf-global-mission-description p').inner_text()==source['english'][i]['description']
        assert page.evaluate('originalBg.src').endswith('/content/dungeon/dungeon_battle_10800.jpg')
    page.wait_for_function('()=>originalBg.complete && originalBg.naturalWidth>0')
    final=page.evaluate("""() => ({
        version:P.version, roster:JSON.stringify(P.roster),
        squad:JSON.stringify(P.squad),exp:JSON.stringify(P.unitExp)
    })""")
    for field in ('version','roster','squad','exp'):
        assert final[field]==state[field],field
    assert state['version']==7
    assert 'simulated' in page.locator('#questinfo').inner_text().lower()
    assert not errors,errors
    browser.close()
print('PASS v0.51 Tower quests 81-85, 7/7/7/7/8, original Global, original art, unlock after 73, v7')
