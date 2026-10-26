"""v0.13.1 first-APK browser regressions (not an Android device test).

Run: python3 -m pip install playwright && python3 test_bf_v0131.py
Uses Google Chrome on CI, Chromium locally; does not download a browser.
"""
import json, shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML = (Path(__file__).parent / 'app/src/main/assets/index.html').read_text(encoding='utf-8')
BASE={'format':'bf-global-offline-demo','version':6,'exp':0,'zel':777,'karma':0,'clears':0,
      'squad':[10011,20011,30011,40011,50011,60011],
      'roster':[10011,20011,30011,40011,50011,60011],
      'unitExp':{},'questClears':{},'lastMission':1,'materials':{},'evolutions':{},'summonTokens':0,'summonHistory':[],'trainingShards':0,'trainingSpent':0}

checks=[]
def passed(s):
    checks.append(s)
    print('PASS',s,flush=True)

def new_page(browser,store=None):
    page=browser.new_page(viewport={'width':390,'height':844},accept_downloads=True)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    # Own mock localStorage, deterministic over reload and independent across tests.
    page.evaluate('''(store) => {
      const saved=store;
      window.__saved=saved;
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
       get length(){return Object.keys(saved).length},
       key(n){return Object.keys(saved)[n]??null},
       getItem(k){return Object.prototype.hasOwnProperty.call(saved,k)?saved[k]:null},
       setItem(k,v){saved[k]=String(v)}, removeItem(k){delete saved[k]}
      }});
      window.confirm=()=>true;window.alert=()=>{};
    }''',store or {})
    page.set_content(HTML,wait_until='load',timeout=60000)
    return page,errors

with sync_playwright() as p:
    chrome = shutil.which('google-chrome') or shutil.which('google-chrome-stable')
    chromium = shutil.which('chromium')
    browser = p.chromium.launch(headless=True,executable_path=chrome or chromium,
        args=['--no-sandbox','--disable-dev-shm-usage'])
    # A: corruption fallback, deduped quarantine.
    store={'bf_global_offline_demo_v7':'{bad','bf_global_offline_demo_v6':json.dumps(BASE)}
    page,errors=new_page(browser,store)
    assert page.evaluate('P.zel')==777
    assert page.evaluate('saveRecoveryPending') is False
    store=page.evaluate('window.__saved')
    qkeys=lambda: [k for k in store if k.startswith('bf_global_offline_quarantine_')]
    assert len(qkeys())==1,store.keys()
    # Reload same JS realm (the already-running RAF is stopped by closing after assertions).
    backup_key=qkeys()[0]
    page.close()
    page,errors=new_page(browser,store)
    assert len(qkeys())==1 and backup_key==qkeys()[0]
    assert store['bf_global_offline_demo_v7']=='{bad'
    assert page.evaluate('P.zel')==777 and not errors, errors
    passed('A: corrupt v7 falls back to valid v6; repeated load deduplicates backup')
    page.close()

    # B: corrupt only -> block writes and rewards from overwriting raw data.
    raw='{bad';store={'bf_global_offline_demo_v7':raw}
    page,errors=new_page(browser,store)
    state=page.evaluate('''() => {const before=P.zel;
       const saved=saveProgress(); awardDemoRewards();
       return {pending:saveRecoveryPending,saved,before,after:P.zel,
               warning:!document.getElementById('savewarning').hidden};}''')
    assert state['pending'] and not state['saved'] and state['warning']
    assert page.evaluate('window.__saved.bf_global_offline_demo_v7')==raw and not errors,(state,errors)
    passed('B: unrecoverable save blocks persistence; original corrupt bytes retained')
    page.close()

    # C: original Thunder's Command grants ATK to allies (not healing); no enemy damage, gauge consumed.
    page,errors=new_page(browser)
    page.evaluate('''() => {P.roster=[...new Set([...P.roster,40021])];
      P.squad=[40021,10011];saveProgress();reset();E.speed.value='5';
      for(const e of S.enemies){e.hp=e.maxHp=700;}for(const p of S.party){if(p&&p.hp>0)p.hp=Math.max(1,p.maxHp-500);}
      const a=S.party.find(x=>x&&x.unitId===40021||x&&x.sourceId===40021||x&&x.id===40021);
      if(!a)throw new Error('Cannot find support in squad');
      a.bb=100; a.action={kind:'burst',target:0};
      for(const p of S.party){if(p&&p.hp>0&&p!==a)p.action={kind:'guard'};}
      window.__support=a;
    }''')
    before=page.evaluate('S.enemies[0].hp')
    page.evaluate('execute()')
    page.wait_for_function('!S.busy',timeout=25000)
    assert page.evaluate('S.enemies[0].hp')==before
    assert page.evaluate('window.__support.bb')==0
    assert page.evaluate('window.__support.atkBuff.pct')==30
    print('SUPPORT_LOG', repr(page.locator('#log').text_content()[:1000]),flush=True)
    assert 'dealt 0 enemy damage' in page.locator('#log').text_content()
    assert not errors,errors
    passed('C: Thunder BB boosts ally ATK, deals no enemy damage; gauge consumed')
    page.close()

    # D: support party still clears with Auto Battle.
    page,errors=new_page(browser)
    page.evaluate('''() => {P.roster=[...new Set([...P.roster,40021])];
       P.squad=[10011,20011,30011,40011,50011,40021]; saveProgress();reset();
       E.speed.value='5'; for(const e of S.enemies)e.hp=1;
       const a=S.party.find(p=>p&&p.id===40021||p&&p.unitId===40021||p&&p.sourceId===40021);
       if(a)a.bb=100;
       }''')
    page.locator('#auto').check()
    # Keep training enemy health minimal on each new wave to reduce runtime.
    for wave in (1,2):
        page.wait_for_function('(n)=>S.wave>=n',arg=wave,timeout=50000)
        page.evaluate('for(const e of S.enemies)e.hp=1')
    page.wait_for_function('S.over',timeout=50000)
    assert page.evaluate('S.phase')=='Victory' and not errors,(page.evaluate('S.phase'),errors)
    passed('D: Auto Battle with support unit completes all waves')
    page.close()

    # E: restarting mid-BB never damages enemies after the reset.
    page,errors=new_page(browser)
    page.evaluate('''() => {P.squad=[10011];saveProgress();reset();E.speed.value='2';
      for(const e of S.enemies)e.hp=e.maxHp=30000;
      S.party[0].bb=100;S.party[0].action={kind:'burst',target:0};
      execute();setTimeout(()=>reset(),40);}''')
    page.wait_for_timeout(1200)
    assert page.evaluate('S.enemies[0].hp===S.enemies[0].maxHp && !S.busy') and not errors,errors
    passed('E: mid-BB reset cancels future hits and returns to idle')
    page.close();browser.close()

print(f'{len(checks)} browser checks passed. Android install, signing updates and force-stop persistence still require device tests.')
