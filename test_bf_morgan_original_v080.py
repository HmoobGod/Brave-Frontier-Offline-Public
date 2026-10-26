"""v0.80: 2022 source-backed Morgan seven dungeons, 36 missions and original artwork.

Validates all archived quest fields, chain requirements, map coordinates,
original English, Android asset staging and preservation of v7 save schema.
Demo combat is not misrepresented as the historical native wave composition.
"""
from pathlib import Path
import json,hashlib,zipfile,subprocess,sys,shutil
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
m=json.loads((R/'source_data/bf_global_morgan_original_v080.json').read_text('utf-8'))
assert m['schema']=='bf-global-morgan-2022-original-quests-v080'
assert len(m['dungeons'])==7 and len(m['quests'])==36
assert m['quests'][0]['requires']==85
assert [q['missionId'] for q in m['quests']]==[
    *range(200,205),*range(210,215),*range(220,225),*range(230,235),
    *range(240,245),*range(250,255),*range(260,266)]
for d in m['dungeons']:
    art=(A/'content/dungeon'/d['background']).read_bytes()
    assert len(art)==d['imageBytes']
    assert hashlib.sha256(art).hexdigest()==d['imageSha256']
assert (A/'content/area/area_0002.jpg').stat().st_size==169225
assert (A/'content/area/area_plate_0002.png').stat().st_size==17075
assert (A/'bf080_morgan_map.js').is_file()
assert 'readPackagedText("bf080_morgan_map.js")' in (
    R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf-8')
assert (A/'bf_home_nav.js').stat().st_size < 65536
path=A/'index.html';html=path.read_text('utf-8')
assert html.count('/* BF_ORIGINAL_MORGAN_QUESTS_V080 */')==1
assert 'bf_global_offline_demo_v7' in html
before=hashlib.sha256(html.encode()).digest()
subprocess.run([sys.executable,str(R/'prepare_morgan_quests_v080.py')],check=True,cwd=R)
assert hashlib.sha256(path.read_bytes()).digest()==before

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
       executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
       args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    def local(route):
        rel=route.request.url.split('bf-assets.test/',1)[-1]
        file=A/rel
        if file.is_file() and file.resolve().is_relative_to(A.resolve()) and file.suffix in ('.png','.jpg'):
            route.fulfill(status=200,body=file.read_bytes(),
              content_type='image/jpeg' if file.suffix=='.jpg' else 'image/png')
        else:route.fulfill(status=404,body=b'')
    page.route('http://bf-assets.test/**',local)
    page.evaluate("""() => {
       const db={};
       Object.defineProperty(window,'localStorage',{configurable:true,value:{
          getItem:k=>db[k]??null,setItem:(k,v)=>{db[k]=String(v)},
          removeItem:k=>{delete db[k]},key:i=>Object.keys(db)[i]??null,
          get length(){return Object.keys(db).length}}});
       window.alert=()=>{};window.confirm=()=>true;
       HTMLMediaElement.prototype.load=()=>{};
       HTMLMediaElement.prototype.pause=()=>{};
       HTMLMediaElement.prototype.play=()=>Promise.resolve();
    }""")
    page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),
       wait_until='load',timeout=90000)
    saved=page.evaluate("""() => ({version:P.version,roster:JSON.stringify(P.roster),
       squad:JSON.stringify(P.squad),unitExp:JSON.stringify(P.unitExp)})""")
    assert saved['version']==7
    page.add_style_tag(path=str(A/'bf_home_nav.css'))
    page.add_script_tag(path=str(A/'bf_home_nav.js'))
    page.add_script_tag(path=str(A/'bf080_morgan_map.js'))
    assert page.evaluate('QUESTS.length')==106
    assert page.evaluate('BFGlobalQuestText.missions.length')==106
    assert page.evaluate('BFGlobalQuestText.dungeons.length')==23
    assert page.evaluate('BFMistralMap.entries.length')==9
    assert page.locator('.bf-mistral-pin').count()==9
    assert page.locator('.bf-mission-step-row button').count()==106
    assert page.locator('.bf-quest-area-tabs button').count()==24
    assert page.evaluate('BFMorganMapV080.entries.length')==7
    assert page.evaluate('BFMorganMapV080.selectedRegion')=='mistral'
    assert page.locator('#bf080-morgan-map').is_hidden()
    assert page.evaluate('BFMorganMapV080.isUnlocked(200)') is False
    assert page.evaluate('BFMorganMapV080.openDungeon(200)') is False
    page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
    page.locator('[data-bf-region="morgan"]').click()
    assert page.locator('#bf080-morgan-map').is_visible()
    assert page.locator('.bf-mistral-map').is_hidden()
    assert page.locator('.bf080-pin').count()==7
    assert page.locator('[data-bf-morgan-list]').count()==7
    assert page.evaluate('BFMorganMapV080.isUnlocked(210)') is False
    for original in m['quests']:
        q=page.evaluate('(id)=>QUESTS.find(q=>q.missionId===id)',original['missionId'])
        assert q is not None
        assert [q[k] for k in ('missionId','dungeonId','requires','battles','energy','exp','zel','karma')]==[
            original[k] for k in ('missionId','dungeonId','requires','battles','energy','exp','zel','karma')]
        d=next(d for d in m['dungeons'] if d['id']==original['dungeonId'])
        assert q['background']==d['background']
        lookup=page.evaluate('(id)=>BFGlobalQuestText.sourceFor(QUESTS.find(q=>q.missionId===id))',
                             original['missionId'])
        assert lookup['mission']['name']==original['name']
        assert lookup['mission']['description']==original['description']
        assert lookup['dungeon']['name']==d['name']
    # Morgan requires completion of Mistral's final mission, without bypass.
    page.evaluate('()=>{P.questClears[85]=1;renderQuestList()}')
    assert page.evaluate('BFMorganMapV080.isUnlocked(200)') is True
    assert page.evaluate('BFMorganMapV080.isUnlocked(210)') is False
    assert page.evaluate('BFMorganMapV080.openDungeon(200)') is True
    assert page.evaluate('QUEST.missionId')==200
    assert page.evaluate('BFQuestAreas.selectedDungeon')=='200'
    assert page.locator('#questlist .questcard:visible').count()==5
    assert page.evaluate('S.totalWaves')==7
    assert page.evaluate('BFMorganMapV080.selectedRegion')=='morgan'
    # Exact seven dungeon progression chain, simulated clears only.
    for i,q in enumerate(m['quests']):
        if i:
            page.evaluate('(id)=>{P.questClears[id]=1;renderQuestList()}',m['quests'][i-1]['missionId'])
            if i in (5,10,15,20,25,30):
                assert page.evaluate('(id)=>BFMorganMapV080.isUnlocked(id)',q['dungeonId']) is True
                assert page.evaluate('(id)=>BFMorganMapV080.openDungeon(id)',q['dungeonId']) is True
            else:
                assert page.evaluate('(id)=>BFQuestAreas.choose(QUESTS.find(q=>q.missionId===id))',
                                     q['missionId']) is True
        assert page.evaluate('QUEST.missionId')==q['missionId']
        assert page.evaluate('S.totalWaves')==q['battles']
        assert page.evaluate('QUEST.background')==next(d['background'] for d in m['dungeons'] if d['id']==q['dungeonId'])
        assert page.locator('.bf-global-mission-description p').text_content()==q['description']
        assert q['name'] in page.locator('#bf-mission-name').text_content()
    page.wait_for_function('()=>originalBg.complete && originalBg.naturalWidth>0')
    assert page.evaluate('originalBg.src').endswith('/content/dungeon/dungeon_battle_20700.jpg')
    final=page.evaluate("""() => ({version:P.version,roster:JSON.stringify(P.roster),
       squad:JSON.stringify(P.squad),unitExp:JSON.stringify(P.unitExp)})""")
    assert final==saved,(saved,final)
    assert not errors,errors
    browser.close()
print('PASS v0.80 original Morgan 36 missions, 7 new dungeons/map, unlock chain, authentic JPEG, save v7')
