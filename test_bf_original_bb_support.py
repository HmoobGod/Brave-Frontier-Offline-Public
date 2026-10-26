"""Brave Frontier Global v0.29 original BB Lv1 source and real runtime regressions."""
import json,shutil,re
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
source=json.loads((ROOT/'source_data/bf_global_original_bb_support_v029.json').read_text())
assert source['schema']=='bf-global-original-bb-support-v029'
assert set(source['skills'])=={'20041','30041','40021','40022','40041','50041'}
assert source['skills']['40021']['level1DemoEffect']['pctAtLv1']==30
assert source['skills']['40022']['level1DemoEffect']['pctAtLv1']==40
assert all(source['skills'][i]['level1DemoEffect']['lowAtLv1']==600 for i in ['20041','30041','40041','50041'])
html=(ASSETS/'index.html').read_text('utf-8')
assert html.count('/* BF_GLOBAL_BB_SUPPORT_V029 */')==1
assert html.count('function effectivePlayerAtk(p)')==1
assert 'bf_global_offline_demo_v7' in html
print('PASS 6 archived Global support BBs source-verified; code injected exactly once',flush=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=shutil.which('google-chrome') or shutil.which('chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[]
 page.on('pageerror',lambda err:errors.append(str(err)))
 page.evaluate('''() => {
   const store={};window.__testStorage=store;
   Object.defineProperty(window,'localStorage',{configurable:true,value:{
     getItem(k){return store[k]??null;},setItem(k,v){store[k]=String(v);},
     removeItem(k){delete store[k];},key(i){return Object.keys(store)[i]??null},
     get length(){return Object.keys(store).length}
   }});window.alert=()=>{};window.confirm=()=>true;
 }''')
 page.route('http://bf-assets.test/**',lambda route:route.fulfill(status=404,body=b''))
 page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=60000)
 before=page.evaluate("JSON.stringify(P)")
 before_stored=page.evaluate("JSON.stringify(window.__testStorage)")
 assert page.evaluate("BFOriginalSupportEffects.ids.length")==6
 assert page.evaluate("BFOriginalSupportEffects.forUnit(40022).pct")==40
 assert page.evaluate("BFOriginalSupportEffects.forUnit(20041).kind")=='heal_all'
 # Source levels affect ONLY ally attack. Two buffs, stronger replaces weaker,
 # weaker does not erase stronger, attack damage multiplies via effective atk.
 out=page.evaluate('''async () => {
  BF_debug.reset();wait=()=>Promise.resolve();
  const ally=S.party[0];ally.hp=ally.maxHp-200;
  let foes=[{slot:0,name:'Target',hp:99999,maxHp:99999,atk:300,def:5}];
  S.enemies=foes;
  const beforeAtks=S.party.map(p=>p.atk),beforeHps=S.party.map(p=>p.hp),enemyHp=foes[0].hp;
  const buff=S.party[0];buff.unitId=40021;buff.bb=100;buff.action={kind:'burst',target:0};
  await performUnit(buff,epoch);
  const first=S.party.map(p=>p.atkBuff?.pct||0),hit1=foes[0].hp;
  const actual=effectivePlayerAtk(S.party[1]);
  const label=E.slots.textContent.includes('ATK +30%');
  S.round=2;update();const turns2=E.slots.textContent.includes('2 turns');
  S.round=3;update();const turns3=E.slots.textContent.includes('1 turn');
  S.round=4;update();const expired=S.party.map(p=>currentAtkBoost(p));
  S.round=5;
  buff.unitId=40022;buff.bb=100;buff.action={kind:'burst',target:0};await performUnit(buff,epoch);
  const stronger=S.party[1].atkBuff.pct;
  buff.unitId=40021;buff.bb=100;buff.action={kind:'burst',target:0};await performUnit(buff,epoch);
  const afterWeaker=S.party[1].atkBuff.pct;
  const alive=S.party.filter(p=>p.active&&p.hp>0).length;
  return {beforeAtks,beforeHps,afterHps:S.party.map(p=>p.hp),enemyHp,hit1,first,actual,
          label,turns2,turns3,expired,stronger,afterWeaker,alive};
 }''')
 assert out['enemyHp']==out['hit1'],out
 assert out['afterHps']==out['beforeHps'],out
 assert out['first']==[30]*out['alive'],out
 assert out['actual']==round(out['beforeAtks'][1]*1.3),out
 assert out['label'] and out['turns2'] and out['turns3'],out
 assert all(v==0 for v in out['expired']),out
 assert out['stronger']==40 and out['afterWeaker']==40,out
 print('PASS original source ATK +30/+40 party boosts, 3 turns, visible indicators, no stacks/no enemy healing',flush=True)
 # Stronger buff affects outgoing allies' attack only; never modifies the
 # base stats themselves or enemy attack formula. Verify damage difference by
 # restoring deterministic PRNG seed for each hit and same source unit.
 out=page.evaluate('''async () => {
  BF_debug.reset();wait=()=>Promise.resolve();
  S.enemies=[{slot:0,name:'Foe',hp:99999,maxHp:99999,atk:50,def:25}];
  const p=S.party[0];p.unitId=10011;
  p.action={kind:'attack',target:0};seed=123;await performUnit(p,epoch);
  const plain=99999-S.enemies[0].hp;
  S.enemies[0].hp=99999;
  p.action={kind:'attack',target:0};p.atkBuff={pct:40,untilRound:S.round+2};seed=123;
  await performUnit(p,epoch);
  const boosted=99999-S.enemies[0].hp;
  return {plain,boosted,baseAtk:p.atk,boost:currentAtkBoost(p),enemy:S.enemies[0].atk};
 }''')
 assert out['boosted']>out['plain']>0,out
 assert out['boost']==40 and out['baseAtk']>0 and out['enemy']==50,out
 print('PASS same attack seed deals more damage only with active ally ATK buff; source unit base stat preserved',flush=True)
 # All four archived healers: cap to max, KO exclusion, zero enemy damage,
 # original base 600..800, no invented REC component or resurrection.
 for uid in [20041,30041,40041,50041]:
  out=page.evaluate('''async ({uid})=>{
   BF_debug.reset();wait=()=>Promise.resolve();
   S.enemies=[{slot:0,name:'Foe',hp:10000,maxHp:10000,atk:200,def:10}];
   const healer=S.party[0];healer.unitId=uid;healer.bb=100;healer.action={kind:'burst',target:0};
   const healthy=S.party[1];healthy.maxHp=healthy.maxHp+1500;healthy.hp=healthy.maxHp-1200;
   const capped=S.party[2];capped.hp=capped.maxHp-4;
   const ko=S.party[3];ko.hp=0;
   const old=[healthy.hp,capped.hp,ko.hp],max=[healthy.maxHp,capped.maxHp,ko.maxHp];
   await performUnit(healer,epoch);
   return {bb:healer.bb,old,max,after:[healthy.hp,capped.hp,ko.hp],enemyHp:S.enemies[0].hp,
     buff:S.party.map(p=>p.atkBuff||null),log:E.log.textContent};
  }''',{'uid':uid})
  actual=out['after'][0]-out['old'][0]
  assert 600<=actual<=800,(uid,out)
  assert out['after'][1]==out['max'][1] and out['after'][2]==0,(uid,out)
  assert out['bb']==0 and out['enemyHp']==10000,(uid,out)
  assert all(x is None for x in out['buff']),(uid,out)
  assert 'source Lv1 base healing range' in out['log'],(uid,out)
 print('PASS 4 original Global Lv1 600–800 base heals: correct HP caps, no KO revival, no enemy damage',flush=True)
 # Reset clears buffs, store remains unchanged; Auto stays off by default.
 final=page.evaluate('''()=>{BF_debug.reset();return {
  boosts:S.party.map(p=>currentAtkBoost(p)),auto:S.auto,stored:JSON.stringify(window.__testStorage),
  hasSaveKey:SAVE_KEY==='bf_global_offline_demo_v7', progress:JSON.stringify(P)};}''')
 assert all(b==0 for b in final['boosts'])
 assert not final['auto'] and final['hasSaveKey']
 assert final['progress']==before
 assert final['stored']==before_stored
 assert not errors,errors
 print('PASS reset/Auto unchanged, source support effects never persist to save, no browser errors',flush=True)
 browser.close()
