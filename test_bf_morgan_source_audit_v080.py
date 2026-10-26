"""v0.80 independent Morgan quest, map and world art validation."""
from pathlib import Path
import json,hashlib,zipfile,shutil
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
A=ROOT/'app/src/main/assets'
m=json.loads((ROOT/'source_data/bf_global_morgan_original_v080.json').read_text())
assert len(m['quests'])==36 and len(m['dungeons'])==7
z=zipfile.ZipFile(ROOT/'source_assets/bf1/morgan/BF1_Morgan_Original_Battle_2022_v080.zip')
for d in m['dungeons']:
 p='content/dungeon/'+d['background']
 assert hashlib.sha256(z.read(p)).hexdigest()==d['imageSha256']
 assert (A/p).read_bytes()==z.read(p)
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""() => {
 const db={};
 Object.defineProperty(window,'localStorage',{configurable:true,value:{
  getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
  removeItem:k=>{delete db[k]},key:i=>Object.keys(db)[i]??null,
  get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};
 HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 page.set_content((A/'index.html').read_text(),wait_until='load',timeout=90000)
 page.add_style_tag(path=str(A/'bf_home_nav.css'))
 page.add_script_tag(path=str(A/'bf_home_nav.js'))
 page.add_script_tag(path=str(A/'bf080_morgan_map.js'))
 assert page.evaluate('P.version')==7
 assert page.evaluate('QUESTS.length')==106
 assert page.evaluate('QUESTS.map(q=>q.missionId).slice(34,70)')==[q['missionId'] for q in m['quests']]
 assert page.evaluate('BFMistralMap.entries.length')==9
 assert page.evaluate('BFMorganMapV080.entries.length')==7
 assert page.evaluate('BFMorganMapV080.isUnlocked(200)') is False
 for q in m['quests']:
  actual=page.evaluate('(id)=>QUESTS.find(q=>q.missionId===id)',q['missionId'])
  assert all(actual[k]==q[k] for k in ('missionId','requires','battles','energy','exp','zel','karma'))
  text=page.evaluate('(id)=>BFGlobalQuestText.sourceFor(QUESTS.find(q=>q.missionId===id))',q['missionId'])
  assert text['mission']['name']==q['name'] and text['mission']['description']==q['description']
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 page.evaluate('()=>{P.questClears[85]=1;renderQuestList()}')
 assert page.evaluate('BFMorganMapV080.isUnlocked(200)') is True
 assert page.evaluate('BFMorganMapV080.openDungeon(200)') is True
 assert page.evaluate('QUEST.missionId')==200
 page.evaluate('()=>{for(let i=200;i<=204;i++)P.questClears[i]=1;renderQuestList()}')
 assert page.evaluate('BFMorganMapV080.isUnlocked(210)') is True
 assert page.evaluate('BFMorganMapV080.openDungeon(210)') is True
 assert page.evaluate('QUEST.missionId')==210
 assert not errors,errors
 browser.close()
print('PASS v0.80 36 original Morgan quests, seven battle JPEGs, source localization and locked world-map progression')
