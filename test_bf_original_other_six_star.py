"""v0.38 original 2022 Global alternate six-star source/live regression."""
from pathlib import Path
import base64,hashlib,io,json,shutil,zipfile
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent; A=ROOT/'app/src/main/assets';M=json.loads((ROOT/'source_data/bf_global_other_six_star_v038.json').read_text())
IDS={10025,20025,30025,40025,50025,60025}
assert set(map(int,M['records']))==IDS
zbytes=base64.b64decode((ROOT/'source_assets/bf1/BF1_Global_2022_Other_Six_Star.zip.b64').read_text())
assert hashlib.sha256(zbytes).hexdigest()==M['sourcePackSha256']
with zipfile.ZipFile(io.BytesIO(zbytes)) as z:
 for row in M['records'].values():
  for name,sha in row['sourceFilesSha256'].items():assert hashlib.sha256(z.read(name)).hexdigest()==sha
for uid in IDS:
 for pre in ('unit_anime_atlas_','unit_ills_thum_'):assert (A/'content/other_six_star'/f'{pre}{uid}.png').is_file()
html=(A/'index.html').read_text('utf8')
assert html.count('/* BF_GLOBAL_OTHER_SIX_STAR_V038 */')==1
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844});errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 def serve(route):
  from urllib.parse import urlsplit
  file=(A/urlsplit(route.request.url).path.lstrip('/')).resolve()
  if not file.is_relative_to(A.resolve()) or not file.is_file():route.fulfill(status=404,body=b'');return
  route.fulfill(status=200,content_type='image/png' if file.suffix=='.png' else 'text/plain',body=file.read_bytes())
 page.route('http://bf-assets.test/**',serve)
 setup='''(old)=>{const s=old||{};window.__save=s;Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem(k){return s[k]??null},setItem(k,v){s[k]=String(v)},removeItem(k){delete s[k]},key(i){return Object.keys(s)[i]??null},get length(){return Object.keys(s).length}}});window.confirm=()=>true;window.alert=()=>{}}'''
 page.evaluate(setup,None)
 page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=90000)
 state=page.evaluate('''()=>({base:STARTERS.length,evolved:window.BF_EVOLVED_UNITS.length,recipes:EVO_RECIPES.length,skills:Object.keys(window.BF_ARCHIVE_BB_HITS).length,version:P.version,
   entries:[10025,20025,30025,40025,50025,60025].map(id=>({id,name:UNIT_BY_ID.get(id)?.name,cap:UNIT_BY_ID.get(id)?.originalMaxLevel,rarity:UNIT_BY_ID.get(id)?.rarity,scope:bfOriginalBB(id)?.target,skill:bfOriginalBB(id)?.name,power:bfOriginalBBPower(id)?.base??null,support:originalSupport(id)?.pct??null,raw:BFOriginalOtherSixStar.sourceLevelsFor(id),frames:UNIT_BY_ID.get(id)?.frameCount}))})''')
 assert (state['base'],state['evolved'],state['recipes'],state['skills'],state['version'])==(18,54,54,72,7),state
 for x in state['entries']:
  row=M['records'][str(x['id'])]
  assert x['name']==row['name'] and x['cap']==100 and x['rarity']==6 and x['scope']==row['bb']['target'] and x['skill']==row['bb']['name'],x
  assert x['raw']==row['bb']['levels'] and x['frames']==row['frameCount']
  assert x['power'] is None and x['support']==(94 if x['id']==40025 else None),x
 assert not errors,errors
 page.wait_for_function('''()=>[10025,20025,30025,40025,50025,60025].every(id=>imagesById.get(id)?.naturalWidth>0)''',timeout=45000)
 print('PASS original 72 playable forms, 54 evolution recipes and six source-hashed 6-star animated assets',flush=True)
 # Each owned base ID is not replaced by a newly summoned unit.
 for uid in sorted(IDS):
  row=M['records'][str(uid)];base=row['ownedBaseId'];prev=row['fromId']
  before=page.evaluate('''({base,prev,mats})=>{BF_debug.reset();P.roster=[...new Set([...P.roster,base])];P.squad=[base];P.evolutions={};P.evolutions[base]=prev;P.unitExp[base]=100;P.materials={};P.zel=90000;
    for(const [id,count] of Object.entries(mats))P.materials[id]=count;
    renderEvolutionPanel();const card=[...document.querySelectorAll('.evocard')].find(c=>c.textContent.includes(UNIT_BY_ID.get(prev).name));const btn=card?.querySelector('.evoaction');
    return {form:effectiveUnit(base)?.id,canEvolve:btn?.textContent,disabled:btn?.disabled,display:card?.textContent};}''',{'base':base,'prev':prev,'mats':row['sourceRecipe']['materials']})
  assert before['form']==prev and before['canEvolve']=='Evolve' and before['disabled'] is False and '500,000' in before['display'] and '10,000' in before['display'],before
  page.evaluate('''(prev)=>{const card=[...document.querySelectorAll('.evocard')].find(c=>c.textContent.includes(UNIT_BY_ID.get(prev).name));card.querySelector('.evoaction').click()}''',prev)
  after=page.evaluate('''(base)=>({form:P.evolutions[base],current:effectiveUnit(base)?.id,party:S.party[0]?.unitId,zel:P.zel,exp:P.unitExp[base],saved:JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'))})''',base)
  assert after['form']==uid and after['current']==uid and after['party']==uid and after['zel']==80000 and after['exp']==0,after
  assert after['saved']['version']==7 and after['saved']['evolutions'][str(base)]==uid,after
  assert not errors,errors
  print('PASS real evolution',prev,'->',uid,row['name'],flush=True)
 # Distinguish 5 damage skills from the authentic support scope; native offensive
 # effect codes 1800/2300/3300/3400 remain DEMO 2.1x, not invented percentages.
 combat=page.evaluate('''async()=>{BF_debug.reset();wait=()=>Promise.resolve();const p=S.party[0];p.active=true;p.hp=p.maxHp;
  S.enemies=[0,1,2].map(slot=>({slot,name:'Dummy',hp:100000,maxHp:100000,def:20,atk:10}));S.target=1;
  p.unitId=10025;p.bb=100;p.action={kind:'burst',target:1};await performUnit(p,epoch);
  const single=S.enemies.map(e=>100000-e.hp);
  for(const e of S.enemies)e.hp=100000;
  p.unitId=30025;p.bb=100;p.action={kind:'burst',target:1};await performUnit(p,epoch);
  const all=S.enemies.map(e=>100000-e.hp);
  for(const e of S.enemies)e.hp=100000;
  p.unitId=40025;p.bb=100;p.action={kind:'burst',target:1};await performUnit(p,epoch);
  return {single,all,boost:currentAtkBoost(S.party[0]),enemies:S.enemies.map(e=>e.hp),bb:p.bb,fallback:bbDamageMultiplier({...p,unitId:10025},true)};
 }''')
 assert combat['single'][0]==combat['single'][2]==0 and combat['single'][1]>0,combat
 assert all(x>0 for x in combat['all']) and combat['enemies']==[100000]*3 and combat['boost']==94 and combat['bb']==0 and abs(combat['fallback']-2.1)<0.0001,combat
 print('PASS source BB single/all/support targeting; demo 94-point ATK buff and unproven damage formula fallback',flush=True)
 # Every 30th and 36th quest clear grants the two original catalyst IDs, as
 # clearly DEMO awards while preserving 24th 50354 schedule.
 rewards=page.evaluate('''()=>{const out={};for(const n of [24,30,36]){BF_debug.reset();QUEST=QUESTS[0];P.questClears[QUEST.missionId]=n-1;P.materials={};awardDemoRewards();out[n]={...P.materials}}return out}''')
 assert rewards['24'].get('50354')==1 and rewards['30'].get('60144')==1 and rewards['36'].get('60224')==1,rewards
 print('PASS 24th / 30th / 36th clear distinct demo catalyst schedules',flush=True)
 parsed=page.evaluate('''()=>{const orig=JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'));
   orig.evolutions={'10021':10024};const prev=parseProgress(orig).evolutions['10021'];
   orig.evolutions={'10021':10025};const current=parseProgress(orig).evolutions['10021'];
   orig.evolutions={'10021':987654};let refused=false;try{parseProgress(orig)}catch(e){refused=true};return {prev,current,refused}}''')
 assert parsed=={'prev':10024,'current':10025,'refused':True},parsed
 page.evaluate('''()=>{BF_debug.reset();P.roster=[...new Set([...P.roster,10021])];P.squad=[10021];P.evolutions={'10021':10025};saveProgress();reset()}''')
 saved=page.evaluate('window.__save');page.close();page=browser.new_page(viewport={'width':390,'height':844})
 page.on('pageerror',lambda e:errors.append(str(e)));page.route('http://bf-assets.test/**',serve);page.evaluate(setup,saved)
 page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=90000)
 final=page.evaluate('''()=>({schema:P.version,key:SAVE_KEY,form:P.evolutions[10021],party:S.party[0]?.unitId,recovery:saveRecoveryPending})''')
 assert final=={'schema':7,'key':'bf_global_offline_demo_v7','form':10025,'party':10025,'recovery':False},final
 assert not errors,errors
 print('PASS legacy v7 save imports, forged forms refused, restored 6-star battle asset and party',flush=True)
 browser.close()
