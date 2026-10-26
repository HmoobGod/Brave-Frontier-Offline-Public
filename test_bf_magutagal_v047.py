"""Magutagal v0.47: source-backed missions, locks, descriptions, JPEG and v7."""
from pathlib import Path
import hashlib,json,shutil
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent;ASSETS=ROOT/'app/src/main/assets'
m=json.loads((ROOT/'source_data/bf_global_magutagal_v047.json').read_text('utf-8'))
assert m['schema']=='bf-global-magutagal-v047'
background=(ROOT/'source_assets/bf1/dungeon/dungeon_battle_10500.jpg').read_bytes()
assert len(background)==43940
assert hashlib.sha256(background).hexdigest()==m['sources']['backgroundSha256']
assert (ASSETS/'content/dungeon/dungeon_battle_10500.jpg').read_bytes()==background
html=(ASSETS/'index.html').read_text('utf-8')
assert html.count('/* BF_MAGUTAGAL_WETLANDS_V047 */')==1
assert html.count('/* BF_FOREST_OF_BEASTS_V046 */')==1
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda err:errors.append(str(err)))
    def local(route):
        rel=route.request.url.split('bf-assets.test/',1)[-1]
        p=ASSETS/rel
        if p.is_file() and p.resolve().is_relative_to(ASSETS.resolve()) and p.suffix in ('.png','.jpg'):
            route.fulfill(status=200,body=p.read_bytes(),content_type='image/png' if p.suffix=='.png' else 'image/jpeg')
        else:
            route.fulfill(status=404,body=b'')
    page.route('http://bf-assets.test/**',local)
    page.evaluate("""() => {const db={};
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:k=>db[k]??null,setItem:(k,v)=>{db[k]=String(v)},
        removeItem:k=>{delete db[k]},key:i=>Object.keys(db)[i]??null,
        get length(){return Object.keys(db).length}}});
      window.alert=()=>{};window.confirm=()=>true;
      HTMLMediaElement.prototype.load=()=>{};
      HTMLMediaElement.prototype.pause=()=>{};
      HTMLMediaElement.prototype.play=()=>Promise.resolve();
    }""")
    page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=90000)
    page.add_style_tag(path=str(ASSETS/'bf_home_nav.css'))
    page.add_script_tag(path=str(ASSETS/'bf_home_nav.js'))
    page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
    assert page.evaluate('QUESTS.map(q=>q.missionId).slice(0,21)')==[1,2,10,11,12,20,21,22,23,30,31,32,33,40,41,42,43,50,51,52,53]
    assert page.locator('.bf-mission-step-row button').count()==106
    assert page.locator('.bf-mistral-pin').count()==9
    assert page.evaluate('BFMistralMap.isUnlocked(50)') is False
    assert page.evaluate('BFMistralMap.reveal(50)') is False
    for row,english in zip(m['quests'],m['english']):
        found=page.evaluate('(id)=>QUESTS.find(q=>q.missionId===id)',row['missionId'])
        assert found==row,(found,row)
        text=page.evaluate('(id)=>BFGlobalQuestText.sourceFor(QUESTS.find(q=>q.missionId===id))',row['missionId'])
        assert text['mission']==english and text['dungeon']['name']=='Magutagal Wetlands',text
        assert page.locator(f'[data-bf-mission="{row["missionId"]}"]').is_disabled()
    snap=page.evaluate("""()=>({roster:JSON.stringify(P.roster),
      squad:JSON.stringify(P.squad),exp:JSON.stringify(P.unitExp),version:P.version})""")
    page.evaluate("()=>{P.questClears[43]=1;renderQuestList()}")
    assert page.evaluate('BFMistralMap.isUnlocked(50)') is True
    page.locator('[data-bf-map-list="50"]').click()
    assert page.evaluate('QUEST.missionId')==50
    assert page.evaluate('BFQuestAreas.selectedDungeon')=='50'
    assert page.locator('#questlist .questcard:visible').count()==4
    for i,row in enumerate(m['quests']):
        if i:
            page.evaluate('(id)=>{P.questClears[id]=1;renderQuestList()}',m['quests'][i-1]['missionId'])
            page.locator(f'[data-bf-mission="{row["missionId"]}"]').click()
        assert page.evaluate('QUEST.missionId')==row['missionId']
        assert page.evaluate('S.totalWaves')==row['battles']
        assert page.evaluate('QUEST.background')=='dungeon_battle_10500.jpg'
        assert m['english'][i]['name'] in page.locator('#bf-mission-name').inner_text()
        assert page.locator('.bf-global-mission-description p').inner_text()==m['english'][i]['description']
        assert page.evaluate('originalBg.src').endswith('/content/dungeon/dungeon_battle_10500.jpg')
    page.wait_for_function('()=>originalBg.complete && originalBg.naturalWidth>0')
    assert page.evaluate('P.version')==snap['version']==7
    assert page.evaluate('JSON.stringify(P.roster)')==snap['roster']
    assert page.evaluate('JSON.stringify(P.squad)')==snap['squad']
    assert page.evaluate('JSON.stringify(P.unitExp)')==snap['exp']
    assert not errors,errors
    print('PASS Magutagal 50–53: source quest records, unlocks, 5/5/5/6, original map/background, v7',flush=True)
    browser.close()
