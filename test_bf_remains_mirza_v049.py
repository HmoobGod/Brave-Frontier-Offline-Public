"""v0.49 original Global Remains of Mirza: browser, quest/map, artwork, v7."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys
from playwright.sync_api import sync_playwright
R = Path(__file__).resolve().parent
A = R/'app/src/main/assets'
m = json.loads((R/'source_data/bf_global_remains_mirza_v049.json').read_text('utf-8'))
assert m['schema']=='bf-global-remains-mirza-v049'
original = (R/'source_assets/bf1/dungeon/dungeon_battle_10600.jpg').read_bytes()
assert len(original)==66699
assert hashlib.sha256(original).hexdigest()==m['sources']['backgroundSha256']
assert (A/'content/dungeon/dungeon_battle_10600.jpg').read_bytes()==original
html=(A/'index.html').read_text('utf-8')
assert html.count('/* BF_REMAINS_OF_MIRZA_V049 */') == 1
assert html.count('/* BF_MAGUTAGAL_WETLANDS_V047 */') == 1
assert html.count('/* BF_GLOBAL_QUEST_TEXT_DATA_V048 */') == 1
assert 'bf_global_offline_demo_v7' in html
assert len((A/'bf_home_nav.js').read_bytes()) < 65536
before=hashlib.sha256(html.encode()).digest()
subprocess.run([sys.executable,str(R/'prepare_remains_mirza_v049.py')],check=True,cwd=R)
assert hashlib.sha256((A/'index.html').read_bytes()).digest()==before

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
        executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
        args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    def local(route):
        rel=route.request.url.split('bf-assets.test/',1)[-1]
        f=A/rel
        if f.is_file() and f.resolve().is_relative_to(A.resolve()) and f.suffix in ('.png','.jpg'):
            route.fulfill(status=200,body=f.read_bytes(),content_type='image/png' if f.suffix=='.png' else 'image/jpeg')
        else:
            route.fulfill(status=404,body=b'')
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
    page.add_style_tag(path=str(A/'bf_home_nav.css'))
    page.add_script_tag(path=str(A/'bf_home_nav.js'))
    page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
    assert page.evaluate('QUESTS.map(q=>q.missionId).slice(0,25)')==[
      1,2,10,11,12,20,21,22,23,30,31,32,33,40,41,42,43,50,51,52,53,60,61,62,63]
    assert page.locator('.bf-mission-step-row button').count()==106
    assert page.locator('.bf-mistral-pin').count()==9
    assert page.evaluate('BFMistralMap.isUnlocked(60)') is False
    assert page.evaluate('BFMistralMap.reveal(60)') is False
    for row,english in zip(m['quests'],m['english']):
        found=page.evaluate('(id)=>QUESTS.find(q=>q.missionId===id)',row['missionId'])
        assert found==row,(found,row)
        matched=page.evaluate('(id)=>BFGlobalQuestText.sourceFor(QUESTS.find(q=>q.missionId===id))',row['missionId'])
        assert matched['mission']==english and matched['dungeon']['name']=='Remains of Mirza', matched
        assert page.locator(f'[data-bf-mission="{row["missionId"]}"]').is_disabled()
    snap=page.evaluate("""() => ({version:P.version,roster:JSON.stringify(P.roster),
        squad:JSON.stringify(P.squad),exp:JSON.stringify(P.unitExp)})""")
    page.evaluate('()=>{P.questClears[53]=1;renderQuestList()}')
    assert page.evaluate('BFMistralMap.isUnlocked(60)') is True
    page.locator('[data-bf-map-list="60"]').click()
    assert page.evaluate('QUEST.missionId')==60
    assert page.evaluate('BFQuestAreas.selectedDungeon')=='60'
    assert page.locator('#questlist .questcard:visible').count()==4
    for i,row in enumerate(m['quests']):
        if i:
            page.evaluate('(id)=>{P.questClears[id]=1;renderQuestList()}',m['quests'][i-1]['missionId'])
            page.locator(f'[data-bf-mission="{row["missionId"]}"]').click()
        assert page.evaluate('QUEST.missionId')==row['missionId']
        assert page.evaluate('S.totalWaves')==row['battles']
        assert page.evaluate('QUEST.background')=='dungeon_battle_10600.jpg'
        assert m['english'][i]['name'] in page.locator('#bf-mission-name').inner_text()
        assert page.locator('.bf-global-mission-description p').inner_text()==m['english'][i]['description']
        assert page.evaluate('originalBg.src').endswith('/content/dungeon/dungeon_battle_10600.jpg')
    page.wait_for_function('()=>originalBg.complete && originalBg.naturalWidth>0')
    final=page.evaluate("""() => ({version:P.version,roster:JSON.stringify(P.roster),
        squad:JSON.stringify(P.squad),exp:JSON.stringify(P.unitExp)})""")
    assert snap==final and snap['version']==7,(snap,final)
    assert 'simulated' in page.locator('#questinfo').inner_text().lower()
    assert not errors,errors
    browser.close()
print('PASS v0.49 source Mirza missions 60–63, unlock after 53, 6/6/6/7, original JPEG, v7')
