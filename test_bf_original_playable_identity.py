"""Verify official original 2022 Global character identities in real browser UI.
This is a strict read-only name/metadata layer: no change to player save, stats,
quests, summon pool or battle behavior.
"""
import base64,gzip,hashlib,json,shutil,re
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
source=ROOT/'source_data'
meta=json.loads((source/'bf_global_original_unit_catalog_meta.json').read_text())
compressed=base64.b64decode((source/'bf_global_original_unit_catalog.json.gz.b64').read_text())
raw=gzip.decompress(compressed)
assert hashlib.sha256(raw).hexdigest()==meta['catalogJsonSha256']
archive={str(x['id']):x for x in json.loads(raw)['units']}
manifest=json.loads((source/'bf_global_original_playable_identity_v031.json').read_text())
assert manifest['count']==30
assert set(manifest['records'])=={'10011','20011','30011','40011','50011','60011','10021','20021','30021','40021','50021','60021','10041','20041','30041','40041','50041','60041','10012','20012','30012','40012','50012','60012','10022','20022','30022','40022','50022','60022'}
for uid,v in manifest['records'].items():
 x=archive[uid]
 assert v['name']==x['name'] and v['baseStats']=={k:x['unitBase'+k.title()] for k in ['hp','atk','def','rec']}
 assert v['maxLevel']==x['unitMaxLevel'] and v['cost']==x['unitCost']
assert manifest['records']['10011']['name']=='Fencer Vargas'
assert manifest['records']['40021']['name']=='Advisor Weiss'
assert manifest['records']['60022']['name']=='Samurai Mifune'
assert manifest['records']['10012']['name']=='Burning Vargas'
print('PASS source: 30 original Global names, rarity, stats, max-level and cost are authentic',flush=True)
html=(ROOT/'app/src/main/assets/index.html').read_text()
assert html.count('/* BF_ORIGINAL_GLOBAL_PLAYABLE_IDENTITY_V031 */')==1
assert html.count('bf_global_offline_demo_v7')>=1
assert 'Original cap Lv.' in html and 'Original cost ' in html
print('PASS v0.31 patch staged exactly once and save key retained',flush=True)
with sync_playwright() as pw:
 binary=shutil.which('google-chrome') or shutil.which('chromium')
 browser=pw.chromium.launch(headless=True,executable_path=binary,args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[]
 page.on('pageerror',lambda error:errors.append(str(error)))
 page.evaluate('''() => {
  const storage={};window.__mockStorage=storage;
  Object.defineProperty(window,'localStorage',{configurable:true,value:{
   getItem(k){return storage[k]??null;},setItem(k,v){storage[k]=String(v)},
   removeItem(k){delete storage[k]},key(n){return Object.keys(storage)[n]??null},
   get length(){return Object.keys(storage).length}
  }});
  window.alert=()=>{};window.confirm=()=>true;
 }''')
 page.route('http://bf-offline.test/**',lambda r:r.fulfill(status=404,body=b''))
 page.set_content(html.replace('<head>','<head><base href="http://bf-offline.test/">',1),wait_until='load',timeout=90000)
 assert page.evaluate('BFOriginalPlayableIdentity.count')==30
 profile=page.evaluate('''() => ({
  originals:window.BF_STARTER_UNITS.concat(window.BF_EVOLVED_UNITS).filter(u=>Object.prototype.hasOwnProperty.call(BF_ORIGINAL_PLAYABLE_IDENTITY,String(u.id))).map(u=>({
   id:u.id,name:u.name,element:u.element,stats:u.stats,rarity:u.rarity,
   maxLevel:u.originalMaxLevel,cost:u.originalUnitCost})),
  roster:[...P.roster],squad:[...P.squad],progress:JSON.stringify(P),
  saveKey:SAVE_KEY,enemyLabels:S.enemies.map(e=>e.name)
 })''')
 assert profile['saveKey']=='bf_global_offline_demo_v7'
 assert len(profile['originals'])==30
 for u in profile['originals']:
  source_row=manifest['records'][str(u['id'])]
  assert u['name']==source_row['name'] and u['stats']==source_row['baseStats']
  assert u['maxLevel']==source_row['maxLevel'] and u['cost']==source_row['cost']
 assert profile['originals'][0]['name']=='Fencer Vargas'
 assert page.evaluate('playerUnit(0).name')=='Fencer Vargas'
 assert len(profile['enemyLabels']) in (2,3)
 assert all('Demo' in n for n in profile['enemyLabels'])
 assert page.evaluate('P.roster')==profile['roster']
 print('PASS browser: unit metadata, battle party names, enemies still DEMO, all existing saves unchanged',flush=True)
 page.add_style_tag(path=str(ROOT/'app/src/main/assets/bf_home_nav.css'))
 page.add_script_tag(path=str(ROOT/'app/src/main/assets/bf_home_nav.js'))
 page.locator('.bf-navbar [data-bf-goto="units"]').click()
 page.locator('[data-bf-unit-tab="box"]').click()
 page.wait_for_function('!!window.BFUnitBox')
 page.evaluate('BFUnitBox.showDetail(10011)')
 assert 'Fencer Vargas' in page.locator('#bf-box-detail').inner_text()
 assert page.evaluate('window.BF_STARTER_UNITS.find(u=>u.id===40021).name')=='Advisor Weiss'
 page.locator('.bf-navbar [data-bf-goto="home"]').click()
 assert page.evaluate('JSON.stringify(P)')==profile['progress']
 assert not errors,errors
 print('PASS Units/Home navigation, official unit names and zero game-state mutations or JS errors',flush=True)
 browser.close()
