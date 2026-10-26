"""v0.42 optional Auto Battle coordination: positive, negative, and queue checks."""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
html=(ROOT/'app/src/main/assets/index.html').read_text('utf8')
assert html.count('/* BF_COORDINATED_AUTO_V042 */')==1
assert html.count('/* BF_SOURCE_AWARE_AUTO_V041 */')==1
assert html.count('/* BF_BATTLE_BB_GUIDE_V040 */')==1
assert html.count('/* BF_EVOLUTION_ROADMAP_V039 */')==1
assert html.count('window.BF042AutoCoordination?.plan(liveParty())')==1
assert html.count('window.BF041SmartAuto?.kindFor(p)')==1
assert 'bf_global_offline_demo_v7' in html
M=json.loads((ROOT/'source_data/bf_global_original_bb_support_v029.json').read_text())
assert M['skills']['40021']['level1DemoEffect']['pctAtLv1']==30
N=json.loads((ROOT/'source_data/bf_global_other_six_star_v038.json').read_text())
assert N['records']['40025']['bb']['levels'][0]['params'][1]==94
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
        executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
        args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.route('http://bf-assets.test/**',lambda route:route.fulfill(status=404,body=b''))
    page.evaluate("""() => {
      const cache={};window.__bf042storage=cache;
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem(k){return cache[k]??null},setItem(k,v){cache[k]=String(v)},
        removeItem(k){delete cache[k]},key(i){return Object.keys(cache)[i]??null},
        get length(){return Object.keys(cache).length}}});
      window.alert=()=>{};window.confirm=()=>true;
    }""")
    page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),
        wait_until='load',timeout=90000)
    assert page.locator('#bf041-smart-auto').count()==1
    assert page.locator('#bf040-bb-guide').count()==1
    assert page.evaluate('BF042AutoCoordination.enabled()') is False
    before=page.evaluate("""()=>({
      progress:JSON.stringify(P),
      saved:localStorage.getItem('bf_global_offline_demo_v7'),
      oldAuto:BF041SmartAuto.enabled()
    })""")
    out=page.evaluate("""()=>{
      BF_debug.reset();
      const [weak,strong,heal,damage]=S.party;
      weak.unitId=40021;strong.unitId=40025;heal.unitId=20041;damage.unitId=10011;
      for(const p of liveParty()){p.bb=100;p.hp=p.maxHp;p.atkBuff=null;}
      S.enemies=[{slot:0,name:'Low absolute',hp:70,maxHp:100,atk:10,def:20},
        {slot:1,name:'Low percent',hp:120,maxHp:1000,atk:10,def:20}];
      const inactive={target:BF042AutoCoordination.chooseTarget(livingEnemies()),
        plan:BF042AutoCoordination.plan(liveParty())};
      document.getElementById('bf041-smart-auto').checked=true;
      const target=BF042AutoCoordination.chooseTarget(livingEnemies());
      const planned=BF042AutoCoordination.plan(liveParty());
      const initial=[weak,strong,heal,damage].map(p=>planned.get(p));
      const originalKinds=[weak,strong,heal,damage].map(p=>BF041SmartAuto.kindFor(p));
      S.party[4].hp=Math.floor(S.party[4].maxHp*.5);
      const injured=BF042AutoCoordination.plan(liveParty()).get(heal);
      S.party[4].hp=S.party[4].maxHp;
      strong.bb=30;
      const weakerOnly=BF042AutoCoordination.plan(liveParty());
      strong.bb=100;
      weak.unitId=40025; // equal power tie must prefer earlier squad slot
      const tie=BF042AutoCoordination.plan(liveParty());
      weak.unitId=40021;
      for(const p of liveParty())p.atkBuff={pct:94,untilRound:S.round+1};
      const buffActive=BF042AutoCoordination.plan(liveParty());
      for(const p of liveParty())p.atkBuff=null;
      const invalid=BF042AutoCoordination.chooseTarget([{slot:5,hp:2,maxHp:0},
        {slot:4,hp:-3,maxHp:10},{slot:2,hp:1,maxHp:10}]);
      document.getElementById('bf041-smart-auto').checked=false;
      return {inactive:{target:inactive.target,plan:inactive.plan},target:target?.slot,
        initial,originalKinds,injured,weakerOnly:[weakerOnly.get(weak),weakerOnly.get(strong)],
        tie:[tie.get(weak),tie.get(strong)],
        buffActive:[buffActive.get(weak),buffActive.get(strong)],invalid:invalid?.slot,
        disabledAfter:BF042AutoCoordination.plan(liveParty()),
        schema:P.version,buttons:[!!document.getElementById('attack'),
          !!document.getElementById('burst'),!!document.getElementById('auto')]
      };
    }""")
    assert out['inactive']=={'target':None,'plan':None},out
    assert out['target']==1 and out['initial']==['attack','burst','attack','burst'],out
    assert out['originalKinds']==['burst','burst','attack','burst'],out
    assert out['injured']=='burst',out
    assert out['weakerOnly']==['burst','attack'],out
    assert out['tie']==['burst','attack'],out
    assert out['buffActive']==['attack','attack'],out
    assert out['invalid']==2 and out['disabledAfter'] is None,out
    assert out['schema']==7 and out['buttons']==[True,True,True],out
    # Test actual existing 350ms Auto queue with smart enabled.
    page.evaluate("""()=>{
      BF_debug.reset();const [p,q]=S.party;
      p.unitId=40021;q.unitId=40025;
      for(const a of liveParty()){a.hp=a.maxHp;a.bb=100;a.atkBuff=null;}
      S.enemies=[{slot:0,name:'A',hp:70,maxHp:100,def:20},
        {slot:1,name:'B',hp:120,maxHp:1000,def:20}];
      document.getElementById('bf041-smart-auto').checked=true;
      execute=()=>{window.__bf042queued={
        actions:liveParty().map(p=>({slot:p.id,kind:p.action.kind,target:p.action.target})),
        visualTarget:S.target
      }};
      S.auto=true;scheduleAuto();
    }""")
    page.wait_for_function("()=>!!window.__bf042queued",timeout=5500)
    queued=page.evaluate('window.__bf042queued')
    assert queued['visualTarget']==1 and all(a['target']==1 for a in queued['actions']),queued
    assert [a['kind'] for a in queued['actions'][:2]]==['attack','burst'],queued
    # Disable option -> old lowest absolute-HP targeting and both ready buffs cast.
    page.evaluate("""()=>{
      S.auto=false;
      document.getElementById('bf041-smart-auto').checked=false;
      window.__bf042queued=null;S.auto=true;scheduleAuto();
    }""")
    page.wait_for_function("()=>!!window.__bf042queued",timeout=5500)
    legacy=page.evaluate('window.__bf042queued')
    assert all(a['target']==0 for a in legacy['actions']),legacy
    assert [a['kind'] for a in legacy['actions'][:2]]==['burst','burst'],legacy
    page.evaluate("()=>{S.auto=false;document.getElementById('bf041-smart-auto').checked=false;}")
    assert page.evaluate("JSON.stringify(P)")==before['progress'],'P changed'
    assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==before['saved'],'save changed'
    assert not errors,errors
    print('PASS v0.42: original Lv1 buff sources; smart percentage targets, strongest one buff; legacy queue, v7 and nav unchanged',flush=True)
    browser.close()
