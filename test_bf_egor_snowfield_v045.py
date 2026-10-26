"""v0.45: live Egor mission chain and original snowfield background."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import hashlib,json,shutil
R=Path(__file__).resolve().parent; A=R/'app/src/main/assets'
j=json.loads((R/'source_data/bf_global_egor_snowfield_v045.json').read_text())
src=(R/'source_assets/bf1/dungeon/dungeon_battle_10300.jpg').read_bytes()
assert hashlib.sha256(src).hexdigest()==j['sources']['backgroundSha256']
assert (A/'content/dungeon/dungeon_battle_10300.jpg').read_bytes()==src
html=(A/'index.html').read_text()
assert html.count('/* BF_EGOR_SNOWFIELD_V045 */')==1
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':390,'height':844});errors=[]
 page.on('pageerror',lambda err:errors.append(str(err)))
 def images(route):
  rel=route.request.url.split('bf-assets.test/',1)[-1];p=A/rel
  if p.is_file() and p.resolve().is_relative_to(A.resolve()) and p.suffix in ('.png','.jpg'):
   route.fulfill(status=200,body=p.read_bytes(),content_type='image/png' if p.suffix=='.png' else 'image/jpeg')
  else:route.fulfill(status=404,body=b'')
 page.route('http://bf-assets.test/**',images)
 page.evaluate("""()=>{const data={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
  getItem:k=>data[k]??null,setItem:(k,v)=>{data[k]=String(v)},
  removeItem:k=>{delete data[k]},key:n=>Object.keys(data)[n]??null,
  get length(){return Object.keys(data).length}}});window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve();}""")
 page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=90000)
 page.add_style_tag(path=str(A/'bf_home_nav.css'))
 page.add_script_tag(path=str(A/'bf_home_nav.js'))
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.evaluate('QUESTS.map(q=>q.missionId).slice(0,13)')==[1,2,10,11,12,20,21,22,23,30,31,32,33]
 assert page.locator('.bf-mission-step-row button').count()==106
 assert page.locator('.bf-mistral-pin').count()==9
 assert page.evaluate('BFMistralMap.isUnlocked(30)') is False
 assert page.evaluate('BFMistralMap.reveal(30)') is False
 for row,eng in zip(j['quests'],j['english']):
  q=page.evaluate('(id)=>QUESTS.find(q=>q.missionId===id)',row['missionId'])
  assert q==row,(q,row)
  lookup=page.evaluate('(id)=>BFGlobalQuestText.sourceFor(QUESTS.find(q=>q.missionId===id))',row['missionId'])
  assert lookup['mission']==eng and lookup['dungeon']['name']=='Egor Snowfield',lookup
 snap=page.evaluate("""()=>({roster:JSON.stringify(P.roster),squad:JSON.stringify(P.squad),
  level:P.version,exp:JSON.stringify(P.unitExp)})""")
 page.evaluate('()=>{P.questClears[23]=1;renderQuestList()}')
 assert page.evaluate('BFMistralMap.isUnlocked(30)') is True
 page.locator('[data-bf-map-list="30"]').click()
 assert page.evaluate('BFQuestAreas.selectedDungeon')=='30'
 for idx,row in enumerate(j['quests']):
  if idx:
   page.evaluate('(id)=>{P.questClears[id]=1;renderQuestList()}',j['quests'][idx-1]['missionId'])
   page.locator(f'[data-bf-mission="{row["missionId"]}"]').click()
  assert page.evaluate('QUEST.missionId')==row['missionId']
  assert page.evaluate('S.totalWaves')==row['battles']
  assert j['english'][idx]['name'] in page.locator('#bf-mission-name').inner_text()
  assert page.locator('.bf-global-mission-description p').inner_text()==j['english'][idx]['description']
  assert page.evaluate('originalBg.src').endswith('/content/dungeon/dungeon_battle_10300.jpg')
 page.wait_for_function('()=>originalBg.complete && originalBg.naturalWidth>0')
 assert page.evaluate('P.version')==snap['level']==7
 assert page.evaluate('JSON.stringify(P.roster)')==snap['roster']
 assert page.evaluate('JSON.stringify(P.squad)')==snap['squad']
 assert page.evaluate('JSON.stringify(P.unitExp)')==snap['exp']
 assert not errors,errors
 print('PASS v0.45 Egor 30-33 source unlocks, 5/5/5/6 wave counts, original art, v7 roster')
 b.close()
