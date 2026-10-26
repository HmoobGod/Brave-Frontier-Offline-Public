"""v0.37: six authentic 2022 Global 6-star starters; offline browser/Save v7 regression."""
from pathlib import Path
import base64,hashlib,io,json,shutil,zipfile
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent;A=ROOT/'app/src/main/assets'
M=json.loads((ROOT/'source_data/bf_global_six_star_starters_v037.json').read_text('utf8'))
IDS={10015,20015,30015,40015,50015,60015}
assert M['schema']=='bf-global-six-original-six-star-starters-2022-v037' and set(map(int,M['records']))==IDS
blob=base64.b64decode((ROOT/'source_assets/bf1/BF1_Global_2022_Six_Star_Starters.zip.b64').read_text('ascii'))
assert hashlib.sha256(blob).hexdigest()==M['sourcePackSha256']
with zipfile.ZipFile(io.BytesIO(blob)) as pack:
 for row in M['records'].values():
  for path,digest in row['sourceFilesSha256'].items():assert hashlib.sha256(pack.read(path)).hexdigest()==digest
for uid in IDS:
 for name in (f'unit_anime_atlas_{uid}.png',f'unit_ills_thum_{uid}.png'):
  assert (A/'content/six_star_evolution'/name).is_file(),name
html=(A/'index.html').read_text('utf8')
assert html.count('/* BF_GLOBAL_SIX_STAR_STARTERS_V037 */')==1

with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844});errors=[]
 page.on('pageerror',lambda error:errors.append(str(error)))
 def serve(route):
  from urllib.parse import urlsplit
  p=(A/urlsplit(route.request.url).path.lstrip('/')).resolve()
  if not p.is_relative_to(A.resolve()) or not p.is_file():route.fulfill(status=404,body=b'');return
  route.fulfill(status=200,content_type='image/png' if p.suffix=='.png' else 'text/plain',body=p.read_bytes())
 page.route('http://bf-assets.test/**',serve)
 page.evaluate('''()=>{const store={};window.__store=store;
   Object.defineProperty(window,'localStorage',{configurable:true,value:{
    getItem(k){return store[k]??null},setItem(k,v){store[k]=String(v)},removeItem(k){delete store[k]},
    key(i){return Object.keys(store)[i]??null},get length(){return Object.keys(store).length}
   }});window.confirm=()=>true;window.alert=()=>{};}''')
 page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=90000)
 got=page.evaluate('''()=>({base:STARTERS.length,evolved:window.BF_EVOLVED_UNITS.length,recipes:EVO_RECIPES.length,
    bb:Object.keys(window.BF_ARCHIVE_BB_HITS).length,version:P.version,key:SAVE_KEY,
    rows:[10015,20015,30015,40015,50015,60015].map(id=>({id,name:UNIT_BY_ID.get(id)?.name,
      rarity:UNIT_BY_ID.get(id)?.rarity,cap:UNIT_BY_ID.get(id)?.originalMaxLevel,
      bb:bfOriginalBB(id)?.name,target:bfOriginalBB(id)?.target,
      levels:BFOriginalSixStar.sourceLevelsFor(id)?.length,
      power:bfOriginalBBPower(id)?.base,frames:UNIT_BY_ID.get(id)?.frameCount}))})''')
 assert (got['base'],got['evolved'],got['recipes'],got['bb'],got['version'],got['key'])==(18,54,54,72,7,'bf_global_offline_demo_v7'),got
 assert all(r['rarity']==6 and r['cap']==100 and r['target']=='all_enemies' and r['levels']==10 and r['power']==100 for r in got['rows']),got
 for row in got['rows']:
  src=M['records'][str(row['id'])];assert row['name']==src['name'] and row['bb']==src['bb']['name'] and row['frames']==src['frameCount']
 assert not errors,errors
 print('PASS v0.37 66 playable original forms, six 6-star source skills and original Level 1-10 raw BB data',flush=True)
 page.wait_for_function('''()=>[10015,20015,30015,40015,50015,60015].every(id=>imagesById.get(id)?.naturalWidth>0)''',timeout=45000)
 print('PASS six source sprite atlases load offline, including archived Unholy Magress layers',flush=True)
 for uid in sorted(IDS):
  row=M['records'][str(uid)];owned=row['ownedBaseId'];prev=row['fromId']
  info=page.evaluate('''({owned,prev,mats})=>{BF_debug.reset();P.roster=[...new Set([...P.roster,owned])];P.squad=[owned];
    P.evolutions={};P.evolutions[owned]=prev;P.unitExp[owned]=60;P.materials={};P.zel=100000;
    for(const [id,n] of Object.entries(mats))P.materials[id]=n;
    renderEvolutionPanel();const card=[...document.querySelectorAll('.evocard')].find(x=>x.textContent.includes(UNIT_BY_ID.get(prev).name));
    return {form:effectiveUnit(owned)?.id,button:card?.querySelector('button.evoaction')?.textContent,
      disabled:card?.querySelector('button.evoaction')?.disabled,detail:card?.textContent};
   }''',{'owned':owned,'prev':prev,'mats':row['sourceRecipe']['materials']})
  assert info['form']==prev and info['button']=='Evolve' and info['disabled'] is False,info
  assert '500,000' in info['detail'] and '10,000' in info['detail'] and '50354' in info['detail'],info
  page.evaluate('''prev=>{const card=[...document.querySelectorAll('.evocard')].find(x=>x.textContent.includes(UNIT_BY_ID.get(prev).name));card.querySelector('button.evoaction').click();}''',prev)
  result=page.evaluate('''owned=>({current:P.evolutions[owned],active:effectiveUnit(owned)?.id,
    combat:S.party[0]?.unitId,exp:P.unitExp[owned],zel:P.zel,save:JSON.parse(localStorage.getItem(SAVE_KEY))})''',owned)
  assert (result['current'],result['active'],result['combat'],result['exp'],result['zel'])==(uid,uid,uid,0,90000),result
  assert result['save']['version']==7 and result['save']['evolutions'][str(owned)]==uid,result
  assert not errors,errors
  print('PASS actual 5-to-6-star evolution',prev,'->',uid,row['name'],flush=True)
 # Four sequential original forms from owned Vargas 2-star -> 6-star.
 chain=page.evaluate('''()=>{BF_debug.reset();P.roster=[...STARTER_IDS];P.squad=[10011];P.evolutions={};P.unitExp[10011]=60;P.zel=80000;
   P.materials={'10130':8,'10131':8,'10132':8,'10133':4,'50354':2};
   const evolve=(from)=>{renderEvolutionPanel();const card=[...document.querySelectorAll('.evocard')].find(x=>x.textContent.includes(UNIT_BY_ID.get(from).name));
    const btn=card?.querySelector('button.evoaction');if(!btn||btn.disabled)throw Error('Evolution unavailable from '+from);
    btn.click();P.unitExp[10011]=60;return P.evolutions[10011]};
   const sequence=[evolve(10011),evolve(10012),evolve(10013),evolve(10014)];
   const old=JSON.parse(localStorage.getItem(SAVE_KEY));old.evolutions={'10011':10014};
   const prior=parseProgress(old).evolutions[10011];old.evolutions={'10011':99999};
   let invalidRejected=false;try{parseProgress(old)}catch(e){invalidRejected=true}
   return {sequence,prior,invalidRejected};
 }''')
 assert chain=={'sequence':[10012,10013,10014,10015],'prior':10014,'invalidRejected':True},chain
 print('PASS four consecutive stages from 2-star to 6-star; v7 5-star save accepted, unknown form rejected',flush=True)
 # 6-star BB authentic all-enemy target scope and archived hit timing, DEMO source-first-parameter damage conversion.
 dmg=page.evaluate('''async()=>{BF_debug.reset();wait=()=>Promise.resolve();
  const p=S.party[0];p.active=true;p.hp=p.maxHp;p.unitId=10015;p.bb=100;
  S.enemies=[0,1,2].map(slot=>({id:4000+slot,slot,name:'Demo foe',hp:100000,maxHp:100000,atk:30,def:50}));
  p.action={kind:'burst',target:1};await performUnit(p,epoch);
  return {damage:S.enemies.map(e=>100000-e.hp),bb:p.bb,skill:bfOriginalBB(10015).name,mult:bbDamageMultiplier(p,true)};
 }''')
 assert all(x>0 for x in dmg['damage']) and dmg['bb']==0 and dmg['skill']=='Final Burst' and dmg['mult']==2,dmg
 print('PASS all-enemy 6-star source BB scope and Lv1+100 first-parameter demo mapping; native second parameter unmodeled',flush=True)
 # Every 24th quest clear gives common catalyst 50354 AND existing tier3/tier4. 18th special unaffected.
 reward=page.evaluate('''()=>{BF_debug.reset();QUEST=QUESTS[0];const id=QUEST.missionId;P.questClears[id]=23;P.materials={};
   awardDemoRewards();return {...P.materials};}''')
 assert reward.get('50354')==1 and reward.get('10132')==1 and reward.get('10133')==1,reward
 print('PASS 24th clear grants shared 50354 source-ID catalyst as DEMO reward without displacing existing rewards',flush=True)
 # Force correct v7 saved form and reload in another page, no schema changes.
 page.evaluate('''()=>{BF_debug.reset();P.roster=[...STARTER_IDS];P.squad=[10011];P.evolutions={'10011':10015};saveProgress()}''')
 saved=page.evaluate('window.__store');page.close()
 page=browser.new_page(viewport={'width':390,'height':844});page.on('pageerror',lambda error:errors.append(str(error)));page.route('http://bf-assets.test/**',serve)
 page.evaluate('''saved=>{window.__store=saved;Object.defineProperty(window,'localStorage',{configurable:true,value:{
   getItem(k){return saved[k]??null},setItem(k,v){saved[k]=String(v)},removeItem(k){delete saved[k]},
   key(i){return Object.keys(saved)[i]??null},get length(){return Object.keys(saved).length}}});window.confirm=()=>true;window.alert=()=>{};}''',saved)
 page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=90000)
 restored=page.evaluate('''()=>({v:P.version,form:P.evolutions[10011],battle:S.party[0]?.unitId,key:SAVE_KEY,recover:saveRecoveryPending})''')
 assert restored=={'v':7,'form':10015,'battle':10015,'key':'bf_global_offline_demo_v7','recover':False},restored
 assert not errors,errors
 print('PASS Android-like v7 storage restart loads original six-star unit, existing roster and no repair state',flush=True)
 browser.close()
