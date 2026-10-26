"""Browser integration and source checks for original Global v0.36 second-group 5-star units."""
from pathlib import Path
import json,shutil,zipfile,hashlib,base64,io
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent; A=ROOT/'app/src/main/assets'
M=json.loads((ROOT/'source_data/bf_global_other_five_star_v036.json').read_text())
IDS={10024,20024,30024,40024,50024,60024}
assert set(map(int,M['records']))==IDS
raw=base64.b64decode((ROOT/'source_assets/bf1/BF1_Global_2022_Other_Five_Star.zip.b64').read_text())
assert hashlib.sha256(raw).hexdigest()==M['sourcePackSha256']
with zipfile.ZipFile(io.BytesIO(raw)) as z:
 for row in M['records'].values():
  for path,digest in row['sourceFilesSha256'].items():assert hashlib.sha256(z.read(path)).hexdigest()==digest
for id in IDS:
 for prefix in ('unit_anime_atlas_','unit_ills_thum_'):
  assert (A/'content/other_five_star'/f'{prefix}{id}.png').is_file()
html=(A/'index.html').read_text('utf-8')
assert html.count('/* BF_GLOBAL_OTHER_FIVE_STAR_V036 */')==1
print('PASS 6 source-verified Global five-star alt forms and original CGG/CGS/PNG/English/recipe hashes',flush=True)

with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=shutil.which('google-chrome') or shutil.which('chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 def serve(route):
  from urllib.parse import urlsplit
  rel=urlsplit(route.request.url).path.lstrip('/') or 'index.html';p=(A/rel).resolve()
  if not p.is_relative_to(A.resolve()) or not p.is_file():route.fulfill(status=404,body=b'not found');return
  route.fulfill(status=200,content_type='image/png' if rel.endswith('.png') else 'text/html' if rel.endswith('.html') else 'text/plain',body=p.read_bytes())
 page.route('http://bf-assets.test/**',serve)
 page.evaluate('''()=>{const saved={};window.__saved=saved;
  Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem(k){return saved[k]??null},setItem(k,v){saved[k]=String(v)},removeItem(k){delete saved[k]},key(n){return Object.keys(saved)[n]??null},get length(){return Object.keys(saved).length}}});
  window.confirm=()=>true;window.alert=()=>{};}''')
 page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=90000)
 state=page.evaluate('''()=>({starters:STARTERS.length,evolved:window.BF_EVOLVED_UNITS.length,recipes:EVO_RECIPES.length,
   bb:Object.keys(window.BF_ARCHIVE_BB_HITS).length,version:P.version,
   newUnits:[10024,20024,30024,40024,50024,60024].map(id=>({id,name:UNIT_BY_ID.get(id)?.name,rarity:UNIT_BY_ID.get(id)?.rarity,
   image:imagesById.get(id)?.src,frames:UNIT_BY_ID.get(id)?.frameCount,scope:bfOriginalBB(id)?.target,
   skill:bfOriginalBB(id)?.name,raw:BFOriginalFiveStarOther.sourceLevelsFor(id)?.[0],
   support:originalSupport(id)?.pct??null,power:bfOriginalBBPower(id)?.base??null}))})''')
 assert (state['starters'],state['evolved'],state['recipes'],state['bb'],state['version'])==(18,54,54,72,7),state
 for u in state['newUnits']:
  src=M['records'][str(u['id'])]
  assert u['name']==src['name'] and u['rarity']==5 and u['frames']==src['frameCount'],u
  assert u['scope']==src['bb']['target'] and u['skill']==src['bb']['name'],u
  assert u['raw']['params']==src['bb']['levels'][0]['params'],u
  assert u['support']==(80 if u['id']==40024 else None),u
  assert u['power'] is None,'Unknown native offense code must remain DEMO fallback'
 assert not errors,errors
 print('PASS game registers 60 forms, 42 recipes, 6 authenticated BB scopes, no guessed source damage formulas',flush=True)
 page.wait_for_function('''()=>[10024,20024,30024,40024,50024,60024].every(id=>imagesById.get(id)?.naturalWidth>0)''',timeout=45000)
 print('PASS original six animated source atlases load through offline Android asset path',flush=True)
 # Perform actual evolution from existing 4-star v7 save; use source catalysts.
 for id in sorted(IDS):
  rec=M['records'][str(id)];base=rec['ownedBaseId'];previous=rec['fromId']
  before=page.evaluate('''({base,previous,mats})=>{
   BF_debug.reset();P.roster=[...new Set([...P.roster,base])];P.squad=[base];P.evolutions={};P.evolutions[base]=previous;
   P.unitExp[base]=50;P.zel=300000;P.materials={};for(const [mid,n] of Object.entries(mats))P.materials[mid]=n;
   renderEvolutionPanel();let card=[...document.querySelectorAll('.evocard')].find(x=>x.innerText.includes(UNIT_BY_ID.get(previous).name));
   return {current:effectiveUnit(base)?.id,button:card?.querySelector('button.evoaction')?.textContent,
     disabled:card?.querySelector('button.evoaction')?.disabled,text:card?.innerText};
  }''',{'base':base,'previous':previous,'mats':rec['sourceRecipe']['materials']})
  assert before['current']==previous and before['button']=='Evolve' and before['disabled'] is False,before
  assert '200,000' in before['text'] and '7,500' in before['text'],before
  out=page.evaluate('''({base,previous})=>{
    let card=[...document.querySelectorAll('.evocard')].find(x=>x.innerText.includes(UNIT_BY_ID.get(previous).name));
    card.querySelector('button.evoaction').click();
    return {form:P.evolutions[base],active:effectiveUnit(base)?.id,party:S.party[0]?.unitId,
      zel:P.zel,saved:JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'))};
  }''',{'base':base,'previous':previous})
  assert (out['form'],out['active'],out['party'],out['zel'])==(id,id,id,292500),out
  assert out['saved']['version']==7 and out['saved']['evolutions'][str(base)]==id,out
  assert not errors,errors
  print('PASS playable 5-star source evolution',previous,'→',id,rec['name'],flush=True)
 # BB types: 2 single, 3 all enemy, 1 ATK buff, with NO guessed formula for code 1600/2300/3300/3400.
 out=page.evaluate('''async()=>{
  BF_debug.reset();wait=()=>Promise.resolve();
  S.enemies=[0,1,2].map(slot=>({id:1001+slot,slot,name:'Foe',hp:100000,maxHp:100000,atk:100,def:20}));
  const p=S.party[0];p.active=true;p.hp=Math.max(1,p.hp);S.target=1;
  p.unitId=10024;p.bb=100;p.action={kind:'burst',target:1};await performUnit(p,epoch);
  const single=S.enemies.map(e=>100000-e.hp);
  for(const e of S.enemies)e.hp=100000;
  p.unitId=30024;p.bb=100;p.action={kind:'burst',target:1};await performUnit(p,epoch);
  const all=S.enemies.map(e=>100000-e.hp);
  for(const e of S.enemies)e.hp=100000;
  p.unitId=40024;p.bb=100;p.action={kind:'burst',target:1};await performUnit(p,epoch);
  return {single,all,atkBuff:currentAtkBoost(p),foes:S.enemies.map(e=>e.hp),bb:p.bb,
    power:BFOriginalBBPower.forUnit(10024),source:BFOriginalFiveStarOther.sourceLevelsFor(10024)?.length};
 }''')
 assert out['single'][0]==0 and out['single'][1]>0 and out['single'][2]==0,out
 assert len(out['all'])==3 and all(v>0 for v in out['all']),out
 assert out['atkBuff']==80 and out['foes']==[100000]*3 and out['bb']==0,out
 assert out['power'] is None and out['source']==10,out
 print('PASS authentic single/all/support targeting, source Lv1 80-point ATK buff, unknown offensive codes remain demo damage',flush=True)
 # Special catalyst comes from explicitly DEMO milestones, retaining previous tier rewards.
 reward=page.evaluate('''()=>{
  BF_debug.reset();const missionIdx=0;QUEST=QUESTS[missionIdx];P.questClears[QUEST.missionId]=17;P.materials={};
  awardDemoRewards();return {clears:P.questClears[QUEST.missionId],mats:{...P.materials},save:P.version};
 }''')
 assert reward['clears']==18 and reward['mats'].get('10191')==1 and reward['mats'].get('10132')==1,reward
 assert reward['save']==7
 print('PASS DEMO milestone generates special original recipe catalyst and retains lower-tier reward',flush=True)
 # Reload a saved new 5-star form, and reject fabricated units.
 ending=page.evaluate('''()=>{
  BF_debug.reset();P.roster=[...new Set([...P.roster,10021])];P.squad=[10021];P.evolutions={'10021':10024};saveProgress();reset();
  const original=JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'));const valid=parseProgress(original).evolutions['10021'];
  original.evolutions={'10021':99999};let rejected=false;try{parseProgress(original)}catch(e){rejected=true}
  return {form:S.party[0].unitId,valid,rejected};
 }''')
 assert ending=={'form':10024,'valid':10024,'rejected':True},ending
 saved=page.evaluate('window.__saved');page.close()
 page=browser.new_page(viewport={'width':390,'height':844});page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('http://bf-assets.test/**',serve)
 page.evaluate('''saved=>{window.__saved=saved;Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem(k){return saved[k]??null},setItem(k,v){saved[k]=String(v)},removeItem(k){delete saved[k]},
 key(n){return Object.keys(saved)[n]??null},get length(){return Object.keys(saved).length}}});window.confirm=()=>true;window.alert=()=>{};}''',saved)
 page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=90000)
 recovered=page.evaluate('''()=>({version:P.version,unit:P.evolutions['10021'],battle:S.party[0]?.unitId,ok:!saveRecoveryPending})''')
 assert recovered=={'version':7,'unit':10024,'battle':10024,'ok':True},recovered
 assert not errors,errors
 print('PASS original v7 save reload and rejection of unknown evolution IDs',flush=True)
 browser.close()
