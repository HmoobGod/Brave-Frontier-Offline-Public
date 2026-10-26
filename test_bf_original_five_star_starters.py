"""v0.35 source+live Chromium tests for six real playable 5-star starter evolutions."""
from pathlib import Path
import base64,hashlib,json,shutil,zipfile,io
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent;A=ROOT/'app/src/main/assets'
M=json.loads((ROOT/'source_data/bf_global_six_five_star_v035.json').read_text('utf8'))
ids={10014,20014,30014,40014,50014,60014}
assert M['schema']=='bf-global-six-five-star-starters-2022-v035'
assert {int(i) for i in M['records']}==ids
pack=base64.b64decode((ROOT/'source_assets/bf1/BF1_Global_2022_Six_Five_Star.zip.b64').read_text('ascii'))
assert hashlib.sha256(pack).hexdigest()==M['sourcePackSha256']
with zipfile.ZipFile(io.BytesIO(pack)) as z:
 for record in M['records'].values():
  for path,expected in record['sourceFilesSha256'].items():
   assert hashlib.sha256(z.read(path)).hexdigest()==expected
for uid in ids:
 for tail in (f'unit_anime_atlas_{uid}.png',f'unit_ills_thum_{uid}.png'):
  assert (A/'content/five_star_evolution'/tail).is_file()
html=(A/'index.html').read_text('utf8')
assert html.count('/* BF_GLOBAL_FIVE_STAR_STARTERS_V035 */')==1
assert 'bf_global_offline_demo_v7' in html
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844});errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 def serve(route):
  from urllib.parse import urlsplit
  path=(A/urlsplit(route.request.url).path.lstrip('/')).resolve()
  if not path.is_relative_to(A.resolve()) or not path.is_file():route.fulfill(status=404,body=b'');return
  route.fulfill(status=200,content_type='image/png' if path.suffix=='.png' else 'text/plain',body=path.read_bytes())
 page.route('http://bf-assets.test/**',serve)
 page.evaluate('''()=>{const data={};window.__testStore=data;Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem(k){return data[k]??null},setItem(k,v){data[k]=String(v)},removeItem(k){delete data[k]},key(i){return Object.keys(data)[i]??null},get length(){return Object.keys(data).length}}});window.confirm=()=>true;window.alert=()=>{};}''')
 page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=90000)
 data=page.evaluate('''()=>({base:STARTERS.length,evolved:BF_EVOLVED_UNITS.length,recipes:EVO_RECIPES.length,bb:Object.keys(window.BF_ARCHIVE_BB_HITS).length,
 forms:[10014,20014,30014,40014,50014,60014].map(id=>({id,unit:UNIT_BY_ID.get(id)?.name,rarity:UNIT_BY_ID.get(id)?.rarity,cap:UNIT_BY_ID.get(id)?.originalMaxLevel,scope:bfOriginalBB(id)?.target,power:bfOriginalBBPower(id)?.base,levels:bfOriginalBBPower(id)?.levels,frames:UNIT_BY_ID.get(id)?.frameCount})),
 version:P.version,saveKey:SAVE_KEY})''')
 assert (data['base'],data['evolved'],data['recipes'],data['bb'],data['version'])==(18,54,54,72,7),data
 assert data['saveKey']=='bf_global_offline_demo_v7'
 assert all(x['rarity']==5 and x['cap']==80 and x['scope']=='all_enemies' and x['power']==70 and x['frames']>=12 and x['levels']==[70,80,90,100,110,120,130,140,150,160] for x in data['forms']),data
 assert not errors,errors
 print('PASS 54 original playable forms and all six 5-star BB first-parameter level tables',flush=True)
 page.wait_for_function('''()=>[10014,20014,30014,40014,50014,60014].every(id=>imagesById.get(id)?.naturalWidth>0)''',timeout=30000)
 print('PASS six original 5-star animations/portraits render offline',flush=True)
 for uid in sorted(ids):
  source=M['records'][str(uid)];base=uid-3;prev=uid-1
  before=page.evaluate('''({base,prev,materials})=>{BF_debug.reset();P.roster=[...new Set([...P.roster,base])];P.squad=[base];
   P.evolutions={};P.evolutions[base]=prev;P.unitExp[base]=80;P.materials={};
   P.zel=100000;for(const [id,n] of Object.entries(materials))P.materials[id]=n;
   renderEvolutionPanel();const card=[...document.querySelectorAll('.evocard')].find(c=>c.textContent.includes(UNIT_BY_ID.get(prev).name));
   const btn=card?.querySelector('.evoaction');return {label:btn?.textContent,disabled:btn?.disabled,text:card?.textContent,old:effectiveUnit(base).id};
  }''',{'base':base,'prev':prev,'materials':source['sourceRecipe']['materials']})
  assert before['old']==prev and before['label']=='Evolve' and before['disabled'] is False and '200,000' in before['text'] and '7,500' in before['text'],before
  page.evaluate('''({prev})=>{const card=[...document.querySelectorAll('.evocard')].find(c=>c.textContent.includes(UNIT_BY_ID.get(prev).name));card.querySelector('.evoaction').click()}''',{'prev':prev})
  after=page.evaluate('''({base})=>({form:P.evolutions[base],active:effectiveUnit(base)?.id,party:S.party[0]?.unitId,exp:P.unitExp[base],zel:P.zel,saved:JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'))})''',{'base':base})
  assert after['form']==uid and after['active']==uid and after['party']==uid and after['exp']==0 and after['zel']==92500,after
  assert after['saved']['version']==7 and after['saved']['evolutions'][str(base)]==uid,after
  assert not errors,errors
  print('PASS stage-three original evolution',prev,'→',uid,source['name'],flush=True)
 # Full 3 successive stages and save-parser protections, same owned base ID.
 result=page.evaluate('''()=>{BF_debug.reset();P.roster=[...STARTER_IDS];P.squad=[10011];P.evolutions={};P.unitExp[10011]=50;
    P.materials={'10130':3,'10131':2,'10132':2,'10133':1};P.zel=100000;
    const step=(from)=>{renderEvolutionPanel();const card=[...document.querySelectorAll('.evocard')].find(c=>c.textContent.includes(UNIT_BY_ID.get(from).name));
      const btn=card?.querySelector('.evoaction');if(!btn||btn.disabled)throw Error('Missing evolution from '+from);btn.click();P.unitExp[10011]=50;return P.evolutions[10011]};
    const chain=[step(10011),step(10012),step(10013)];
    const stored=JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'));
    let refused=false;const invalid={...stored,evolutions:{'10011':123456}};
    try{parseProgress(invalid)}catch(e){refused=true}
    const old={...stored,evolutions:{'10011':10013}};
    return {chain,form:stored.evolutions['10011'],refused,oldValid:parseProgress(old).evolutions['10011']};
 }''')
 assert result=={'chain':[10012,10013,10014],'form':10014,'refused':True,'oldValid':10013},result
 print('PASS all 3 stages in order, old-v7 evolution accepted, forged save form rejected',flush=True)
 # All six source BBs target multiple foes, no status or original element effects invented.
 dmg=page.evaluate('''async()=>{BF_debug.reset();wait=()=>Promise.resolve();
   const p=S.party[0];p.unitId=10014;p.active=true;p.hp=p.maxHp;p.bb=100;
   S.enemies=[0,1,2].map(slot=>({slot,name:'Target',hp:80000,maxHp:80000,def:30,atk:20}));
   p.action={kind:'burst',target:1};await performUnit(p,epoch);
   return {damage:S.enemies.map(x=>80000-x.hp),bb:p.bb,skill:bfOriginalBB(10014).name,mult:bbDamageMultiplier(p,true)};
 }''')
 assert all(n>0 for n in dmg['damage']) and dmg['bb']==0 and dmg['skill']=='Infinity Nova' and abs(dmg['mult']-1.7)<0.00001,dmg
 print('PASS 5-star original all-enemy targeting and Lv1 DEMO damage-scalar mapping',flush=True)
 # Existing every-6th tier3 rewards remain; 12th clear adds tier4.
 rewards=page.evaluate('''()=>{const out={};for(const idx of [0,5]){
     BF_debug.reset();P.questClears[QUESTS[idx].missionId]=11;QUEST=QUESTS[idx];P.materials={};
     awardDemoRewards();out[idx]={...P.materials}}
     return out;
   }''')
 assert rewards['0'].get('10132')==1 and rewards['0'].get('10133')==1,rewards
 assert rewards['5'].get('60122')==1 and rewards['5'].get('60123')==1,rewards
 print('PASS 12th clear gives extra tier4 DEMO material without displacing tier3',flush=True)
 # Save/reload with the new 5-star form, no new schema/version or cloud calls.
 page.evaluate('''()=>{BF_debug.reset();P.roster=[...STARTER_IDS];P.squad=[10011];P.evolutions={'10011':10014};saveProgress()}''')
 saved=page.evaluate('window.__testStore')
 page.close();page=browser.new_page(viewport={'width':390,'height':844});page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('http://bf-assets.test/**',serve)
 page.evaluate('''(saved)=>{window.__testStore=saved;Object.defineProperty(window,'localStorage',{configurable:true,value:{
   getItem(k){return saved[k]??null},setItem(k,v){saved[k]=String(v)},removeItem(k){delete saved[k]},key(i){return Object.keys(saved)[i]??null},get length(){return Object.keys(saved).length}}});window.confirm=()=>true;window.alert=()=>{};}''',saved)
 page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=90000)
 post=page.evaluate('''()=>({version:P.version,evolved:P.evolutions[10011],party:S.party[0]?.unitId,key:SAVE_KEY,recovery:saveRecoveryPending})''')
 assert post=={'version':7,'evolved':10014,'party':10014,'key':'bf_global_offline_demo_v7','recovery':False},post
 assert not errors,errors
 print('PASS v7 saved 5-star form loads after restart and Android-style offline assets resolve',flush=True)
 browser.close()
