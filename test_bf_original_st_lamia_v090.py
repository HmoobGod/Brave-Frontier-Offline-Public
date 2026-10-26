"""v0.90 source-backed St. Lamia 36 mission and original area map regression."""
from pathlib import Path
from zipfile import ZipFile
import json,hashlib,shutil,subprocess,sys
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
S=R/'source_assets/bf1/stlamia'
with ZipFile(S/'StLamia_2022_Source_Dataset_v090.zip') as z:
    source=json.loads(z.read('source_data/bf_global_st_lamia_original_v090.json'))
assert source['schema']=='bf-global-st-lamia-2022-original-quests-v090'
assert len(source['dungeons'])==7 and len(source['quests'])==36
with ZipFile(S/'StLamia_2022_Original_Battle_Backgrounds.zip') as z:
    for d in source['dungeons']:
        dest='content/dungeon/'+d['background']
        assert hashlib.sha256(z.read(dest)).hexdigest()==d['imageSha256']
        assert (A/dest).read_bytes()==z.read(dest)
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,
      executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
      args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.evaluate("""() => {
       const data={};
       Object.defineProperty(window,'localStorage',{configurable:true,value:{
         getItem:k=>data[k]??null,setItem:(k,v)=>{data[k]=String(v)},
         removeItem:k=>{delete data[k]},key:i=>Object.keys(data)[i]??null,
         get length(){return Object.keys(data).length}}});
       window.alert=()=>{};window.confirm=()=>true;
       HTMLMediaElement.prototype.load=()=>{};
       HTMLMediaElement.prototype.pause=()=>{};
       HTMLMediaElement.prototype.play=()=>Promise.resolve();
    }""")
    html=(A/'index.html').read_text('utf-8')
    page.set_content(html,wait_until='load',timeout=90000)
    page.add_style_tag(path=str(A/'bf_home_nav.css'))
    page.add_script_tag(path=str(A/'bf_home_nav.js'))
    page.add_script_tag(path=str(A/'bf080_morgan_map.js'))
    page.add_script_tag(path=str(A/'bf090_st_lamia_map.js'))
    assert page.evaluate('P.version')==7
    assert page.evaluate('QUESTS.length')==106
    assert page.evaluate('QUESTS.map(q=>q.missionId).slice(70)')==[r['missionId'] for r in source['quests']]
    assert page.evaluate('BFMistralMap.entries.length')==9
    assert page.evaluate('BFMorganMapV080.entries.length')==7
    assert page.evaluate('BFStLamiaMapV090.entries.length')==7
    assert page.locator('.bf080-region-tabs button').count()==3
    assert page.evaluate('BFStLamiaMapV090.isUnlocked(300)') is False
    for q in source['quests']:
        found=page.evaluate('(id)=>QUESTS.find(q=>q.missionId===id)',q['missionId'])
        assert all(found[k]==q[k] for k in ['requires','battles','exp','zel','karma','energy'])
        translated=page.evaluate('(id)=>BFGlobalQuestText.sourceFor(QUESTS.find(q=>q.missionId===id))',q['missionId'])
        assert translated['mission']['name']==q['name']
        assert translated['mission']['description']==q['description']
    saved=page.evaluate("""() => ({
        roster:JSON.stringify(P.roster),squad:JSON.stringify(P.squad),
        version:P.version
    })""")
    page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
    assert page.evaluate('BFStLamiaMapV090.openDungeon(300)') is False
    page.evaluate('()=>{P.questClears[265]=1;renderQuestList()}')
    assert page.evaluate('BFStLamiaMapV090.isUnlocked(300)') is True
    assert page.evaluate('BFStLamiaMapV090.openDungeon(300)') is True
    assert page.evaluate('QUEST.missionId')==300
    assert page.evaluate('BFStLamiaMapV090.selectedRegion')=='stlamia'
    assert page.evaluate('S.totalWaves')==source['quests'][0]['battles']
    assert page.evaluate('QUEST.background')=='dungeon_battle_30100.jpg'
    page.evaluate('()=>{for(let id=300;id<=304;id++)P.questClears[id]=1;renderQuestList()}')
    assert page.evaluate('BFStLamiaMapV090.isUnlocked(310)') is True
    assert page.evaluate('BFStLamiaMapV090.openDungeon(310)') is True
    assert page.evaluate('QUEST.missionId')==310
    assert page.evaluate('P.version')==saved['version']==7
    assert page.evaluate('JSON.stringify(P.roster)')==saved['roster']
    assert page.evaluate('JSON.stringify(P.squad)')==saved['squad']
    assert not errors,errors
    browser.close()
print('PASS v0.90 original St. Lamia 36 quests/7 dungeons/3 regions, 2022 art and English, save v7')
