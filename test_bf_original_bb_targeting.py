"""v0.28: archived Global BB target scope in the existing DEMO battle engine.

Original English descriptions and master-table scopes determine which enemies
receive DEMO damage; the damage formula, support healing and charge rate are
still explicitly unverified demo features. No extra unlocks or save writes.
"""
from __future__ import annotations
import base64, gzip, hashlib, json, re, shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
A=ROOT/'app/src/main/assets'
M=json.loads((ROOT/'source_data/bf_global_original_bb_targeting.json').read_text('utf-8'))
rows=M['targets']
assert len(rows)==30
assert sum(x['target']=='all_enemies' for x in rows.values())==19
assert sum(x['target']=='single_enemy' for x in rows.values())==5
assert sum(x['target']=='support' for x in rows.values())==6
meta=json.loads((ROOT/'source_data/bf_global_original_lore_meta.json').read_text('utf-8'))
compressed=base64.b64decode((ROOT/'source_data/bf_global_original_lore_codex.json.gz.b64').read_text('ascii'))
assert hashlib.sha256(compressed).hexdigest()==meta['payloadGzipSha256']==M['provenance']['loreGzipSha256']
raw=gzip.decompress(compressed)
assert hashlib.sha256(raw).hexdigest()==meta['payloadJsonSha256']==M['provenance']['loreJsonSha256']
codex={str(u['id']):u for u in json.loads(raw)['units']}
for uid,row in rows.items():
    assert row['name']==codex[uid]['bb']['name']
    assert row['description']==codex[uid]['bb']['description']
assert rows['10011']['name']=='Flare Ride'
assert rows['10021']['target']=='single_enemy'
assert rows['40021']['target']=='support'

html=(A/'index.html').read_text('utf-8')
assert html.count('/* BF_GLOBAL_BB_TARGETING_V028 */')==1
assert html.count('const BF_VERIFIED_BB_SCOPES=')==1
assert html.count('const attackTargets=allEnemyBB?livingEnemies():[target];')==1
assert "bbOriginal?.target==='single_enemy'" in html
assert "bf_global_offline_demo_v7" in html
print('PASS 30 original Global skill names and target scopes match 2022 archives; 19 AoE, 5 single, 6 support')

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
        executable_path=shutil.which('google-chrome') or shutil.which('google-chrome-stable') or shutil.which('chromium'),
        args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.evaluate('''() => {
      const store={};window.__testStorage=store;
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem(k){return store[k]??null}, setItem(k,v){store[k]=String(v)},
        removeItem(k){delete store[k]},key(i){return Object.keys(store)[i]??null},
        get length(){return Object.keys(store).length}
      }});
      window.alert=()=>{};window.confirm=()=>true;
    }''')
    page.route('http://bf-assets.test/**',lambda route:route.fulfill(status=404,body=b''))
    page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=60000)
    scopes=page.evaluate('''() => ({n:BFOriginalBBTargets.count,a:BFOriginalBBTargets.allEnemyCount,
      aScope:BFOriginalBBTargets.scopeFor(10011),single:BFOriginalBBTargets.scopeFor(10021),
      support:BFOriginalBBTargets.scopeFor(40021),unknown:BFOriginalBBTargets.scopeFor(999999)})''')
    assert scopes=={'n':30,'a':19,'aScope':'all_enemies','single':'single_enemy','support':'support','unknown':None}
    before=page.evaluate("JSON.stringify(P)")
    before_saved=page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
    # Accelerate in-memory demo animations only for deterministic regression.
    # Never patch the shipped timer/AI/animation functions.
    for uid,kind in [(10011,'all_enemies'),(10021,'single_enemy'),(40021,'support'),(20011,'all_enemies')]:
        out=page.evaluate('''async ({uid}) => {
          BF_debug.reset();wait=()=>Promise.resolve();
          S.enemies=[
            {slot:0,name:'Foe A',hp:10000,maxHp:10000,def:80,atk:9},
            {slot:1,name:'Foe B',hp:10000,maxHp:10000,def:450,atk:9},
            {slot:2,name:'Foe C',hp:10000,maxHp:10000,def:160,atk:9}
          ];
          const p=S.party[0];p.unitId=uid;p.name='Test';p.bb=100;
          p.hp=Math.max(1,p.maxHp-210);p.action={kind:'burst',target:1};
          const old=S.enemies.map(e=>e.hp),oldHp=p.hp;
          await performUnit(p,epoch);
          return {old,after:S.enemies.map(e=>e.hp),bb:p.bb,
            hpBefore:oldHp,hpAfter:p.hp,atkBoost:BFOriginalSupportEffects.boostForSlot(0),log:E.log.textContent};
        }''',{'uid':uid})
        damage=[x-y for x,y in zip(out['old'],out['after'])]
        assert out['bb']==0,(uid,out)
        if kind=='all_enemies':
            assert all(x>0 for x in damage),(uid,damage)
            assert 'original all-enemy targeting' in out['log'],(uid,out['log'])
        elif kind=='single_enemy':
            assert damage[0]==0 and damage[1]>0 and damage[2]==0,damage
            assert 'original single-enemy targeting' in out['log']
        else:
            assert damage==[0,0,0],damage
            assert out['hpAfter']==out['hpBefore'],out
            assert out['atkBoost']==30,out
            assert 'ORIGINAL ATK BOOST BASE' in out['log']
    print('PASS original Global AoE hits all foes, single targets only selected foe, support hits none; demo effects disclosed')
    # Ordinary Attack is not converted into all-enemy damage by this BB change.
    out=page.evaluate('''async()=>{
      BF_debug.reset();wait=()=>Promise.resolve();
      S.enemies=[{slot:0,name:'A',hp:10000,maxHp:10000,def:100},
                 {slot:1,name:'B',hp:10000,maxHp:10000,def:100},
                 {slot:2,name:'C',hp:10000,maxHp:10000,def:100}];
      const p=S.party[0];p.action={kind:'attack',target:1};p.bb=42;
      await performUnit(p,epoch);
      return {hp:S.enemies.map(e=>e.hp),bb:p.bb};
    }''')
    assert out['hp'][0]==10000 and out['hp'][1]<10000 and out['hp'][2]==10000,out
    assert out['bb']==76,out
    # New BB scope is used by standard queue actions as well.
    queued=page.evaluate('''() => {
      BF_debug.reset();S.party[0].bb=100;S.selected=0;
      const prior=S.party[0].action;queue('burst');
      return {prior:prior===null,action:S.party[0].action,
        log:E.log.textContent.includes('Flare Ride')};
    }''')
    assert queued['prior'] and queued['action']['kind']=='burst' and queued['log'],queued
    page.evaluate("BF_debug.reset()")
    assert page.evaluate('BF_debug.state().auto') is False
    assert page.evaluate('BF_debug.state().party[0].bb')==0
    assert page.evaluate("JSON.stringify(P)")==before,'BB testing altered player progression'
    assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==before_saved
    assert not errors,errors
    print('PASS normal attacks, 34%-gauge demo gain, native queue/reset/Auto state, unchanged player save and no page errors')
    browser.close()
