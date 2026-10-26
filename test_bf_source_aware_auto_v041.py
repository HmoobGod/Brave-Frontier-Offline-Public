"""v0.41 Chrome: verified original BB types, optional DEMO AI, no save mutation."""
import json,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
html=(ROOT/'app/src/main/assets/index.html').read_text('utf-8')
src=json.loads((ROOT/'source_data/bf_global_original_bb_support_v029.json').read_text())
assert src['skills']['20041']['level1DemoEffect']['type']=='heal_all'
assert src['skills']['40021']['level1DemoEffect']['type']=='atk_buff_all'
assert html.count('/* BF_SOURCE_AWARE_AUTO_V041 */')==1
assert html.count('/* BF_BATTLE_BB_GUIDE_V040 */')==1
assert html.count('/* BF_EVOLUTION_ROADMAP_V039 */')==1
assert html.count("window.BF041SmartAuto?.kindFor(p)")==1
assert 'bf_global_offline_demo_v7' in html
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.route('http://bf-assets.test/**',lambda route:route.fulfill(status=404,body=b''))
    page.evaluate("""() => {
      const store={};window.__v041storage=store;
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem(k){return store[k]??null},setItem(k,v){store[k]=String(v)},
        removeItem(k){delete store[k]},key(i){return Object.keys(store)[i]??null},
        get length(){return Object.keys(store).length}}});
      window.confirm=()=>true;window.alert=()=>{};
    }""")
    page.set_content(html.replace('<head>','<head><base href="http://bf-assets.test/">',1),wait_until='load',timeout=90000)
    assert page.locator('#bf041-smart-auto').count()==1
    assert page.evaluate("BF041SmartAuto.enabled()") is False
    assert page.locator('#auto').count()==1
    assert page.locator('#bf040-bb-guide').count()==1
    before=page.evaluate("""()=>({progress:JSON.stringify(P),saved:localStorage.getItem('bf_global_offline_demo_v7')})""")
    result=page.evaluate("""()=>{
      BF_debug.reset();
      const healer=S.party[0],buffer=S.party[1],attacker=S.party[2];
      healer.unitId=20041;buffer.unitId=40025;attacker.unitId=10011;
      for(const p of S.party){if(p.active){p.bb=100;p.hp=p.maxHp;}}
      const decide=()=>[healer,buffer,attacker].map(p=>BF041SmartAuto.kindFor(p));
      const disabled=decide();
      document.getElementById('bf041-smart-auto').checked=true;
      const full=decide(); // healer should attack, unbuffed 94% ATK buff should cast
      S.party[3].hp=Math.floor(S.party[3].maxHp*0.5);
      const injured=decide();
      S.party[3].hp=S.party[3].maxHp;
      for(const p of liveParty())p.atkBuff={pct:94,untilRound:S.round+1};
      const alreadyBuffed=decide();
      healer.bb=0;const noGauge=decide();healer.bb=100;
      document.getElementById('bf041-smart-auto').checked=false;
      const disabledAgain=decide();
      return {disabled,full,injured,alreadyBuffed,noGauge,disabledAgain,
        roster:S.party.length,schema:P.version,saved:localStorage.getItem('bf_global_offline_demo_v7')};
    }""")
    assert result['disabled']==['burst']*3,result
    assert result['full']==['attack','burst','burst'],result
    assert result['injured']==['burst','burst','burst'],result
    assert result['alreadyBuffed']==['attack','attack','burst'],result
    assert result['noGauge']==['attack','attack','burst'],result
    assert result['disabledAgain']==['burst']*3,result
    assert result['roster']==6 and result['schema']==7,result
    # Test the real automated queue, not just the policy helper.
    page.evaluate("""()=>{
      BF_debug.reset();
      const p=S.party[0];p.unitId=20041;p.bb=100;p.hp=p.maxHp;
      for(const a of S.party)if(a.active){a.hp=a.maxHp;a.bb=0}
      p.bb=100;
      document.getElementById('bf041-smart-auto').checked=true;
      execute=()=>{window.__v041queued=S.party.filter(a=>a.active).map(a=>a.action?.kind||null);};
      S.auto=true;
      scheduleAuto();
    }""")
    page.wait_for_function("()=>Array.isArray(window.__v041queued)",timeout=5000)
    queued=page.evaluate("window.__v041queued")
    assert queued[0]=='attack' and all(k=='attack' for k in queued),queued
    page.evaluate("()=>{S.auto=false;document.getElementById('bf041-smart-auto').checked=false;}")
    assert page.evaluate("JSON.stringify(P)")==before['progress'],'AI modified save progress'
    assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==before['saved'],'AI wrote save'
    assert not errors,errors
    print('PASS v0.41 heal/buff/offense + default OFF, real Auto queue, original controls, 6-slot squad, save schema v7 unchanged',flush=True)
    browser.close()
