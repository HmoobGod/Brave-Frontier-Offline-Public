"""v0.34 archived BF Global second-stage forms: source and live browser tests."""
from __future__ import annotations
from pathlib import Path
import base64, hashlib, io, json, shutil, struct, zipfile
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
A=ROOT/'app/src/main/assets'
MAN=json.loads((ROOT/'source_data/bf_global_more_second_stage_v034.json').read_text())
IDS={60013,10023,20023,30023,40023,50023}
assert {int(k) for k in MAN['records']}==IDS
pack=base64.b64decode((ROOT/'source_assets/bf1/BF1_Global_2022_More_Second_Stage.zip.b64').read_text('ascii'))
assert hashlib.sha256(pack).hexdigest()==MAN['sourcePackSha256']
with zipfile.ZipFile(io.BytesIO(pack)) as z:
 for uid,rec in MAN['records'].items():
  for p,expected in rec['sourceFilesSha256'].items():
   assert hashlib.sha256(z.read(p)).hexdigest()==expected,(uid,p)
html=(A/'index.html').read_text('utf8')
assert html.count('/* BF_GLOBAL_MORE_SECOND_EVOLUTIONS_V034 */')==1
for uid in IDS:
 for name in (f'unit_anime_atlas_{uid}.png',f'unit_ills_thum_{uid}.png'):
  assert (A/'content/more_second_evolution'/name).is_file(),name
print('PASS source: six additional original Global 4-star forms, source file hashes and original scope/recipe references',flush=True)

with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
   executable_path=shutil.which('google-chrome') or shutil.which('google-chrome-stable') or shutil.which('chromium'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 def serve(route):
  from urllib.parse import urlsplit
  rel=urlsplit(route.request.url).path.lstrip('/') or 'index.html'
  p=(A/rel).resolve()
  if not p.is_relative_to(A.resolve()) or not p.is_file():
   route.fulfill(status=404,body=b'');return
  mim='image/png' if rel.endswith('.png') else 'text/html' if rel.endswith('.html') else 'text/plain'
  route.fulfill(status=200,content_type=mim,body=p.read_bytes())
 page.route('http://bf-assets.test/**',serve)
 page.evaluate('''()=>{const saved={};window.__saved=saved;
  Object.defineProperty(window,'localStorage',{configurable:true,value:{
    getItem(k){return saved[k]??null},setItem(k,v){saved[k]=String(v)},removeItem(k){delete saved[k]},
    key(i){return Object.keys(saved)[i]??null},get length(){return Object.keys(saved).length}}});
  window.confirm=()=>true;window.alert=()=>{};}''')
 page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=90000)
 info=page.evaluate('''()=>({
   starters:STARTERS.length,evolved:window.BF_EVOLVED_UNITS.length,recipes:EVO_RECIPES.length,
   bbCount:Object.keys(window.BF_ARCHIVE_BB_HITS).length,save:P.version,
   records:[60013,10023,20023,30023,40023,50023].map(id=>({id,
       name:UNIT_BY_ID.get(id)?.name,rarity:UNIT_BY_ID.get(id)?.rarity,
       target:bfOriginalBB(id)?.target,skill:bfOriginalBB(id)?.name,
       power:bfOriginalBBPower(id)?.base||null,support:originalSupport(id)?.pct||null,
       frames:UNIT_BY_ID.get(id)?.frameCount,origCap:UNIT_BY_ID.get(id)?.originalMaxLevel}))})''')
 assert (info['starters'],info['evolved'],info['recipes'],info['bbCount'],info['save'])==(18,54,54,72,7),info
 for row in info['records']:
  ref=MAN['records'][str(row['id'])]
  assert row['name']==ref['name'] and row['rarity']==4 and row['origCap']==ref['originalMaxLevel']
  assert row['frames']==ref['frameCount'] and row['target']==ref['bb']['target'] and row['skill']==ref['bb']['name']
  assert row['support']==(50 if row['id']==40023 else None),row
  if row['support'] is None:assert row['power']==ref['bb']['levelPower'][0],row
 assert not errors,errors
 print('PASS live 54 playable forms; authentic 2022 skills, targets, source levels and 4-star identities',flush=True)
 page.wait_for_function('''()=>[60013,10023,20023,30023,40023,50023].every(id=>imagesById.get(id)?.naturalWidth>0)''',timeout=45000)
 print('PASS all six source-derived animation sprite atlases load through offline image paths',flush=True)
 # Actual two-step evolution from an existing first-stage saved unit, using no
 # new fields in the existing v7 record.
 for uid in sorted(IDS):
  record=MAN['records'][str(uid)];owned=record['ownedBaseId'];previous=record['fromId']
  prep=page.evaluate('''({owned,previous,mats})=>{
     BF_debug.reset();P.roster=[...new Set([...P.roster,owned])];P.squad=[owned];
     P.evolutions={};P.evolutions[owned]=previous;P.unitExp[owned]=50;P.zel=250000;
     P.materials={};for(const [id,n] of Object.entries(mats))P.materials[id]=n;
     renderEvolutionPanel();
     const card=[...document.querySelectorAll('.evocard')].find(e=>e.innerText.includes(UNIT_BY_ID.get(previous).name));
     const button=card?.querySelector('button.evoaction');
     return {before:effectiveUnit(owned)?.id,ok:button?.textContent,disabled:button?.disabled,card:card?.innerText};
  }''',{'owned':owned,'previous':previous,'mats':record['sourceRecipe']['materials']})
  assert prep['before']==previous and prep['ok']=='Evolve' and not prep['disabled'],prep
  assert '100,000' in prep['card'] and '5,000' in prep['card'],prep
  page.evaluate('''({previous})=>{const card=[...document.querySelectorAll('.evocard')].find(e=>e.innerText.includes(UNIT_BY_ID.get(previous).name));card.querySelector('button.evoaction').click();}''',{'previous':previous})
  after=page.evaluate('''({owned})=>({form:P.evolutions[owned],active:effectiveUnit(owned)?.id,
    party:S.party[0]?.unitId,save:JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'))})''',{'owned':owned})
  assert after['form']==uid and after['active']==uid and after['party']==uid,after
  assert after['save']['version']==7 and after['save']['evolutions'][str(owned)]==uid,after
  assert not errors,errors
  print('PASS second stage',previous,'→',uid,record['name'],flush=True)
 # Check all-enemy and single-enemy BB scopes with archive Level 1 modifiers;
 # original injury/weakening status effects are still NOT simulated.
 out=page.evaluate('''async()=>{
  BF_debug.reset();wait=()=>Promise.resolve();
  S.enemies=[0,1,2].map(slot=>({id:1000+slot,slot,name:'Demo foe',hp:90000,maxHp:90000,atk:100,def:20}));
  const p=S.party[0];p.active=true;p.hp=Math.max(1,p.hp);S.target=1;
  p.unitId=60013;p.bb=100;p.action={kind:'burst',target:1};await performUnit(p,epoch);
  const all=S.enemies.map(e=>90000-e.hp);
  for(const foe of S.enemies)foe.hp=90000;
  p.unitId=10023;p.bb=100;p.action={kind:'burst',target:1};await performUnit(p,epoch);
  const single=S.enemies.map(e=>90000-e.hp);
  for(const foe of S.enemies)foe.hp=90000;
  p.unitId=40023;p.bb=100;p.action={kind:'burst',target:1};await performUnit(p,epoch);
  return {all,single,support:currentAtkBoost(S.party[0]),enemy:S.enemies.map(e=>e.hp),bb:p.bb};
 }''')
 assert all(x>0 for x in out['all']),out
 assert out['single'][0]==0 and out['single'][1]>0 and out['single'][2]==0,out
 assert out['support']==50 and out['enemy']==[90000]*3 and out['bb']==0,out
 print('PASS combat: Black Magress all-enemy, Zegar single-target, Commander Weiss source Lv1 +50% ATK',flush=True)
 # Original unsupported bad v7 evolution IDs must still be rejected; older
 # valid first-step saves must load without any migration.
 parsed=page.evaluate('''()=>{
    const old=JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'));
    old.evolutions={'60011':60012};const legit=parseProgress(old).evolutions['60011'];
    old.evolutions={'60011':987654};let rejected=false;
    try{parseProgress(old)}catch(e){rejected=true;}
    return {legit,rejected};
 }''')
 assert parsed=={'legit':60012,'rejected':True},parsed
 # Explicit saved form restore for new Black Magress without replacing roster.
 final=page.evaluate('''()=>{BF_debug.reset();P.roster=[...new Set([...P.roster,60011])];
    P.squad=[60011];P.evolutions={'60011':60013};saveProgress();reset();
    return {form:S.party[0].unitId,stored:JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'))};}''')
 assert final['form']==60013 and final['stored']['evolutions']['60011']==60013
 saved=page.evaluate('window.__saved')
 page.close()
 page=browser.new_page(viewport={'width':390,'height':844})
 page.on('pageerror',lambda error:errors.append(str(error)))
 page.route('http://bf-assets.test/**',serve)
 page.evaluate('''saved=>{window.__saved=saved;
  Object.defineProperty(window,'localStorage',{configurable:true,value:{
  getItem(k){return saved[k]??null},setItem(k,v){saved[k]=String(v)},removeItem(k){delete saved[k]},
  key(i){return Object.keys(saved)[i]??null},get length(){return Object.keys(saved).length}}});
  window.confirm=()=>true;window.alert=()=>{};}''',saved)
 page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=90000)
 reloaded=page.evaluate('''()=>({version:P.version,form:P.evolutions['60011'],battle:S.party[0]?.unitId,safe:!saveRecoveryPending})''')
 assert reloaded=={'version':7,'form':60013,'battle':60013,'safe':True},reloaded
 assert not errors,errors
 print('PASS old v7 save parsing and new evolved-form save/Android WebView reload, no schema changes',flush=True)
 browser.close()
