"""v0.33 source+interactive browser checks: six playable 4-star 2nd-stage forms."""
from pathlib import Path
import json,shutil,base64,zipfile,hashlib
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
A=ROOT/'app/src/main/assets'
MAN=json.loads((ROOT/'source_data/bf_global_second_stage_evolutions_v033.json').read_text())
IDS={10013,20013,30013,40013,50013,60023}
assert {int(id) for id in MAN['records']}==IDS
payload=base64.b64decode((ROOT/'source_assets/bf1/BF1_Global_2022_Second_Stage_Evolutions.zip.b64').read_text())
assert hashlib.sha256(payload).hexdigest()==MAN['sourcePackSha256']
with zipfile.ZipFile(__import__('io').BytesIO(payload)) as z:
 for record in MAN['records'].values():
  for path,digest in record['sourceFilesSha256'].items():
   assert hashlib.sha256(z.read(path)).hexdigest()==digest
for uid in IDS:
 for suffix in [f'unit_anime_atlas_{uid}.png',f'unit_ills_thum_{uid}.png']:
  assert (A/'content/second_evolution'/suffix).is_file()

with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=shutil.which('google-chrome') or shutil.which('chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[]
 page.on('pageerror',lambda error:errors.append(str(error)))
 def serve(route):
  from urllib.parse import urlsplit
  p=urlsplit(route.request.url).path.lstrip('/') or 'index.html'
  path=(A/p).resolve()
  if not path.is_file() or not path.is_relative_to(A.resolve()):route.fulfill(status=404,body=b'not-found');return
  route.fulfill(status=200,content_type='image/png' if p.endswith('.png') else 'text/plain',body=path.read_bytes())
 page.route('http://bf-assets.test/**',serve)
 page.evaluate('''()=>{const store={};window.__store=store;
  Object.defineProperty(window,'localStorage',{configurable:true,value:{
   getItem(k){return store[k]??null},setItem(k,v){store[k]=String(v)},removeItem(k){delete store[k]},
   key(n){return Object.keys(store)[n]??null},get length(){return Object.keys(store).length}
  }});window.confirm=()=>true;window.alert=()=>{};}''')
 html=(A/'index.html').read_text()
 assert html.count('/* BF_GLOBAL_SECOND_EVOLUTIONS_V033 */')==1
 page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=90000)
 state=page.evaluate('''()=>({base:STARTERS.length,evolved:window.BF_EVOLVED_UNITS.length,
   recipes:EVO_RECIPES.length,bb:Object.keys(window.BF_ARCHIVE_BB_HITS).length,
   data:[10013,20013,30013,40013,50013,60023].map(id=>({id,name:UNIT_BY_ID.get(id)?.name,
   rarity:UNIT_BY_ID.get(id)?.rarity,scope:bfOriginalBB(id)?.target,power:bfOriginalBBPower(id)?.base,
   atlas:imagesById.get(id)?.src,levels:bfOriginalBBPower(id)?.levels.length}))})''')
 assert state['base']==18 and state['evolved']==54 and state['recipes']==54 and state['bb']==72,state
 assert all(item['scope']=='all_enemies' and item['rarity']==4 and item['power'] in (50,90) and item['levels']==10 for item in state['data']),state
 print('PASS source 54 playable forms, all six 4-star BB effects and ten power reference levels',flush=True)
 page.wait_for_function('''()=>[10013,20013,30013,40013,50013,60023].every(id=>imagesById.get(id)?.naturalWidth>0)''',timeout=40000)
 assert not errors,errors
 print('PASS all six source-based 4-star sprite atlases resolve inside offline renderer',flush=True)

 # A properly evolved v7 owned base can advance directly to the next source
 # form after paying demo Zel and original catalyst IDs; no new save fields.
 for uid in sorted(IDS):
  data=MAN['records'][str(uid)];base=data['ownedBaseId'];previous=data['fromId']
  result=page.evaluate('''({base,previous,uid,requirements})=>{
   BF_debug.reset();P.roster=[...new Set([...P.roster,base])];P.squad=[base];
   P.evolutions={};P.evolutions[base]=previous;P.unitExp[base]=50;P.zel=150000;
   P.materials={};for(const [id,n] of Object.entries(requirements))P.materials[id]=n;
   renderEvolutionPanel();
   const card=[...document.querySelectorAll('.evocard')].find(e=>e.innerText.includes(UNIT_BY_ID.get(previous).name));
   const button=card?.querySelector('.evoaction');
   return {base,previous,uid,ready:button?.textContent,disabled:button?.disabled,
           text:card?.innerText,original:effectiveUnit(base)?.id};
  }''',{'base':base,'previous':previous,'uid':uid,'requirements':data['sourceRecipe']['materials']})
  assert result['original']==previous and result['ready']=='Evolve' and not result['disabled'],result
  assert '100,000' in result['text'] and '5,000' in result['text'],result
  page.evaluate('''({previous})=>{const card=[...document.querySelectorAll('.evocard')].find(e=>e.innerText.includes(UNIT_BY_ID.get(previous).name));card.querySelector('.evoaction').click();}''',{'previous':previous})
  result=page.evaluate('''({base,uid})=>({form:P.evolutions[base],active:effectiveUnit(base)?.id,
     party:S.party[0]?.unitId,exp:P.unitExp[base],zel:P.zel,
     save:JSON.parse(localStorage.getItem('bf_global_offline_demo_v7')),
     canSkip:EVO_RECIPES.filter(r=>r.baseId===base).length})''',{'base':base,'uid':uid})
  assert result['form']==uid and result['active']==uid and result['party']==uid,result
  assert result['exp']==0 and result['zel']==145000 and result['canSkip']==4,result
  assert result['save']['version']==7 and result['save']['evolutions'][str(base)]==uid,result
  assert not errors,errors
  print('PASS original next evolution',previous,'→',uid,data['name'],flush=True)

 # Both stages in one uninterrupted v7 session: first 10011→10012, then
 # 10012→10013. Verify the older saves' existing first-step value still loads.
 result=page.evaluate('''()=>{
   BF_debug.reset();P.roster=[...new Set([...P.roster,10011])];P.squad=[10011];
   P.evolutions={};P.materials={'10130':1,'10131':1,'10132':1};P.unitExp[10011]=50;P.zel=20000;
   renderEvolutionPanel();const btn=[...document.querySelectorAll('.evocard')].find(c=>c.innerText.includes('Fencer Vargas')).querySelector('.evoaction');
   btn.click();const first=P.evolutions[10011];
   P.unitExp[10011]=50;
   renderEvolutionPanel();const card=[...document.querySelectorAll('.evocard')].find(c=>c.innerText.includes('Burning Vargas'));
   const enabled=!card.querySelector('.evoaction').disabled;
   card.querySelector('.evoaction').click();
   const second=P.evolutions[10011];
   return {first,second,enabled,stored:JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'))};
 }''')
 assert result['first']==10012 and result['second']==10013 and result['enabled'],result
 assert result['stored']['evolutions']['10011']==10013,result
 # Validate the exact old first-stage v7 mapping still imports and is not
 # misclassified as invalid by the new multi-stage evolution parser.
 parsed=page.evaluate('''()=>{
   const old=JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'));
   old.evolutions={'10011':10012};
   const valid=parseProgress(old).evolutions['10011'];
   old.evolutions={'10011':99999};
   let refused=false;try{parseProgress(old);}catch(e){refused=true;}
   return {valid,refused};
 }''')
 assert parsed=={'valid':10012,'refused':True},parsed
 print('PASS two sequential legitimate evolutions retain only existing v7 current-form mapping',flush=True)

 # Ordinary quest rewards now offer the needed tier 3 catalyst every 6th
 # clear, strictly labeled as DEMO rather than claimed original enemy drops.
 reward=page.evaluate('''()=>{
   const initial={};
   for(const idx of [0,5]){
    const mission=QUESTS[idx].missionId;
    QUEST=QUESTS[idx];P.questClears[mission]=5;P.materials={};
    const out=awardDemoRewards();
    initial[idx]={id:mission,materials:{...P.materials},clears:P.questClears[mission],saved:out.stored};
   }
   return initial;
 }''')
 assert reward['0']['materials'].get('10132')==1 and reward['5']['materials'].get('60122')==1,reward
 print('PASS demo quest milestones provide source-recipe tier-three catalysts for Fire and Dark forms',flush=True)
 # The current gameplay-save remains valid after page reload.
 saved=page.evaluate('window.__store')
 page.close()
 page=browser.new_page(viewport={'width':390,'height':844})
 page.on('pageerror',lambda error:errors.append(str(error)))
 page.route('http://bf-assets.test/**',serve)
 page.evaluate('''(saved)=>{window.__store=saved;Object.defineProperty(window,'localStorage',{configurable:true,value:{
    getItem(k){return saved[k]??null},setItem(k,v){saved[k]=String(v)},removeItem(k){delete saved[k]},
    key(n){return Object.keys(saved)[n]??null},get length(){return Object.keys(saved).length}}});window.confirm=()=>true;window.alert=()=>{};}''',saved)
 page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=90000)
 loaded=page.evaluate('''()=>({v:P.version,form:P.evolutions[10011],chosen:S.party[0]?.unitId,schema:SAVE_KEY,
   intact:!saveRecoveryPending,png:imagesById.get(10013)?.naturalWidth})''')
 assert loaded['v']==7 and loaded['form']==10013 and loaded['chosen']==10013,loaded
 assert loaded['intact'] and loaded['png']>0 and not errors,(loaded,errors)
 print('PASS reload saved v7 stage-three form, original sprite, and existing save key',flush=True)
 browser.close()
