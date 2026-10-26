"""v0.46 Global Forest of Beasts mission source/progression browser regressions."""
from pathlib import Path
import hashlib,json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
m=json.loads((R/'source_data/bf_global_forest_of_beasts_v046.json').read_text('utf8'))
assert m['schema']=='bf-global-forest-of-beasts-v046'
raw=(R/'source_assets/bf1/dungeon/dungeon_battle_10400.jpg').read_bytes()
assert hashlib.sha256(raw).hexdigest()==m['sources']['backgroundSha256']
assert (A/'content/dungeon/dungeon_battle_10400.jpg').read_bytes()==raw
html=(A/'index.html').read_text('utf8')
for mark in ('/* BF_FOREST_OF_BEASTS_V046 */','/* BF_EGOR_SNOWFIELD_V045 */','/* BF_EXPERIMENTAL_SBB_V044 */'):
 assert html.count(mark)==1,mark
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':390,'height':844})
 errors=[]
 page.on('pageerror',lambda err:errors.append(str(err)))
 def serve(route):
  rel=route.request.url.split('bf-assets.test/',1)[-1]; f=A/rel
  if f.is_file() and f.resolve().is_relative_to(A.resolve()) and f.suffix in ('.png','.jpg'):
   route.fulfill(status=200,body=f.read_bytes(),content_type='image/png' if f.suffix=='.png' else 'image/jpeg')
  else:route.fulfill(status=404,body=b'')
 page.route('http://bf-assets.test/**',serve)
 page.evaluate("""()=>{const saved={};
  Object.defineProperty(window,'localStorage',{configurable:true,value:{
  getItem:k=>saved[k]??null,setItem:(k,v)=>{saved[k]=String(v)},
  removeItem:k=>{delete saved[k]},key:i=>Object.keys(saved)[i]??null,
  get length(){return Object.keys(saved).length}}});
  window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};
  HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve();}""")
 page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=90000)
 page.add_style_tag(path=str(A/'bf_home_nav.css'))
 page.add_script_tag(path=str(A/'bf_home_nav.js'))
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.evaluate('QUESTS.map(q=>q.missionId).slice(0,17)')==[1,2,10,11,12,20,21,22,23,30,31,32,33,40,41,42,43]
 assert page.locator('.bf-mission-step-row button').count()==106
 assert page.locator('.bf-mistral-pin').count()==9
 assert page.evaluate('BFMistralMap.isUnlocked(40)') is False
 assert page.evaluate('BFMistralMap.reveal(40)') is False
 for row,eng in zip(m['quests'],m['english']):
  current=page.evaluate('(id)=>QUESTS.find(q=>q.missionId===id)',row['missionId'])
  assert current==row,(current,row)
  found=page.evaluate('(id)=>BFGlobalQuestText.sourceFor(QUESTS.find(q=>q.missionId===id))',row['missionId'])
  assert found['mission']==eng and found['dungeon']['name']=='Forest of Beasts',found
  assert page.locator(f'[data-bf-mission="{row["missionId"]}"]').is_disabled()
 snap=page.evaluate("""()=>({roster:JSON.stringify(P.roster),squad:JSON.stringify(P.squad),
  exp:JSON.stringify(P.unitExp),save:localStorage.getItem('bf_global_offline_demo_v7'),version:P.version})""")
 page.evaluate('()=>{P.questClears[33]=1;renderQuestList()}')
 assert page.evaluate('BFMistralMap.isUnlocked(40)') is True
 page.locator('[data-bf-map-list="40"]').click()
 assert page.evaluate('BFQuestAreas.selectedDungeon')=='40'
 assert page.locator('#questlist .questcard:visible').count()==4
 for index,row in enumerate(m['quests']):
  if index:
   page.evaluate('(id)=>{P.questClears[id]=1;renderQuestList()}',m['quests'][index-1]['missionId'])
   page.locator(f'[data-bf-mission="{row["missionId"]}"]').click()
  assert page.evaluate('QUEST.missionId')==row['missionId']
  assert page.evaluate('S.totalWaves')==row['battles']
  assert page.evaluate('QUEST.background')=='dungeon_battle_10400.jpg'
  assert m['english'][index]['name'] in page.locator('#bf-mission-name').inner_text()
  assert page.locator('.bf-global-mission-description p').inner_text()==m['english'][index]['description']
  assert page.evaluate('originalBg.src').endswith('/content/dungeon/dungeon_battle_10400.jpg')
 page.wait_for_function('()=>originalBg.complete && originalBg.naturalWidth>0')
 assert page.evaluate('P.version')==snap['version']==7
 assert page.evaluate('JSON.stringify(P.roster)')==snap['roster']
 assert page.evaluate('JSON.stringify(P.squad)')==snap['squad']
 assert page.evaluate('JSON.stringify(P.unitExp)')==snap['exp']
 assert 'simulated' in page.locator('#questinfo').inner_text().lower()
 assert not errors,errors
 print('PASS v0.46 Forest quests 40–43, 5/5/5/6 waves, English, unlocking, original forest art, v7 integrity',flush=True)
 b.close()
