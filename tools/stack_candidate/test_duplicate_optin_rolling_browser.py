"""Real prepared-game UI; isolated storage and deterministic draws; no device save."""
import sys,pathlib,shutil
from playwright.sync_api import sync_playwright
A=pathlib.Path(sys.argv[1]); errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome'),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':390,'height':844});p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/*',lambda r:r.abort())
 p.evaluate('''()=>{const db={};window.__db=db;window.__fault=null;window.__allow=true;window.__writes=0;Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>db[k]??null,setItem:(k,v)=>{if(k===window.__fault)throw Error('fixture quota');db[k]=String(v);window.__writes++},removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});window.alert=()=>{};window.confirm=()=>window.__allow;HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};HTMLMediaElement.prototype.play=()=>Promise.resolve();}''')
 p.set_content((A/'index.html').read_text(),wait_until='load',timeout=45000)
 for f in ['bf_stack_copies.js','bf_home_nav.js','bf10200_qol_unit_flags.js','bf10000_qol_squad_presets.js']:
  p.add_script_tag(content=(A/f).read_text())
 p.evaluate("P.summonTokens=8;saveProgress();renderProgress();BF_homeNav.go('summon');Math.random=()=>0")
 n=0
 def check(v,name):
  global n
  assert v,name
  n+=1;print('PASS',name,flush=True)
 def ev(s):return p.evaluate(s)
 def click():p.locator('#bf-copy-token-summon').click(timeout=5000)
 toggle=p.locator('#bf-copy-summon-optin'); button=p.locator('#bf-copy-token-summon')
 check(not errors,'boot without page errors');check(toggle.is_visible(),'player toggle visible in Summon');check(not toggle.is_checked(),'default off');check(button.count()==0,'default duplicate button absent');check(ev('typeof window.BF_STACK_DISPOSABLE_UI==="undefined"'),'no test flag');
 before=ev('JSON.stringify(P)');writes=ev('__writes');toggle.check(timeout=5000);check(button.is_visible(),'opt-in exposes real summon');check(ev('JSON.stringify(P)')==before and ev('__writes')==writes,'opt-in makes no save or cost mutation')
 ev('__allow=false');click();check(ev('JSON.stringify(P)')==before,'cancel leaves save unchanged');ev('__allow=true');click();check(ev('P.summonTokens===7&&P.roster.includes(RECRUIT_IDS[0])&&!P._bfUnitInstancesV1'),'first summon obtains base, spends one token');check(ev('__writes')==writes+1,'first summon one canonical write');click();check(ev('P.summonTokens===6&&P.roster.includes(1000000001)&&P._bfUnitInstancesV1.baseById[1000000001]===RECRUIT_IDS[0]'),'second summon gets separate owned duplicate');check(ev('__writes')==writes+2,'duplicate summon one canonical write');check(ev('P.unitExp[1000000001]===0&&P.summonHistory.length===2'),'copy starts zero EXP with source history');check(ev('JSON.stringify(parseProgress(JSON.parse(localStorage.getItem(SAVE_KEY))))===JSON.stringify(P)'),'v7 parser roundtrip exact');
 # Capture detached stale button and make sure disabling consent also invalidates its handler.
 ev("window.__stale=document.getElementById('bf-copy-token-summon')");toggle.uncheck();check(button.count()==0,'off removes button');before=ev('JSON.stringify(P)');ev('__stale.click()');check(ev('JSON.stringify(P)')==before,'stale click cannot acquire');check(ev('P.roster.includes(1000000001)'),'off preserves owned copy');
 # Ordinary token draw still excludes all owned recruit bases.
 ev('E.summonbutton.click()');check(ev('P.summonTokens===5&&P.roster.includes(RECRUIT_IDS[1])&&P._bfUnitInstancesV1.nextId===1000000002'),'ordinary summon unchanged and unowned-only');
 # UI grouping and individual identity remain functional with no test flag.
 ev("BF_homeNav.go('units');BFInnerScreens.setTab('box')");p.locator('#bf-copy-stack-toggle').check(timeout=5000);check(p.locator('.bf-copy-stack summary').count()==1,'stack group visible');check('×2' in p.locator('.bf-copy-stack summary').inner_text(),'group count two');ev("BF_homeNav.go('summon')");toggle.check();
 # No stale clicks while busy, recovery lock, auto, or at limit.
 for cond,restore,name in [('S.busy=true','S.busy=false','busy'),('S.auto=true;S.over=false','S.auto=false','auto active'),('saveRecoveryPending=true','saveRecoveryPending=false','recovery')]:
  before=ev('JSON.stringify(P)');ev(cond+";document.getElementById('bf-copy-token-summon').click();"+restore);check(ev('JSON.stringify(P)')==before,name+' blocks stale click')
 before=ev('JSON.stringify(P)');ev("window.BFGlobalQoLQuestRepeatV9800={statusSnapshot:()=>({active:true})};document.getElementById('bf-copy-token-summon').click();delete window.BFGlobalQoLQuestRepeatV9800");check(ev('JSON.stringify(P)')==before,'repeat transition blocks stale click (simulated status)');
 ev('P.summonTokens=0;saveProgress();renderProgress()');check(button.is_disabled(),'no tokens disables button');ev('P.summonTokens=5;P.summonHistory=Array(100).fill(RECRUIT_IDS[0]);saveProgress();renderProgress()');check(button.is_enabled(),'rolling history permits new summons at 100 entries');ev('P.summonHistory=[RECRUIT_IDS[0],RECRUIT_IDS[0],RECRUIT_IDS[1]];saveProgress();renderProgress()');
 before=ev('JSON.stringify(P)');raw=ev('localStorage.getItem(SAVE_KEY)');ev('__fault=SAVE_KEY');click();ev('__fault=null');check(ev('JSON.stringify(P)')==before and ev('localStorage.getItem(SAVE_KEY)')==raw,'quota failure preserves memory and saved bytes');check(button.is_disabled(),'failed save disables acquisition');ev('saveProgress();renderProgress()');check(not button.is_disabled(),'successful save restores eligibility');
 # New save and undo use actual save controls, both revoke opt-in.
 ev("BF_homeNav.go('menu');document.getElementById('wipesave').click();BF_homeNav.go('summon')");check(not toggle.is_checked() and button.count()==0,'new save revokes opt-in');check(ev('!P._bfUnitInstancesV1'),'fresh save no copy');ev("BF_homeNav.go('menu');document.getElementById('undosave').click();BF_homeNav.go('summon')");check(ev('P.roster.includes(1000000001)'),'undo retains owned copy');check(not toggle.is_checked() and button.count()==0,'undo stays off');
 # Confirmed copy-bearing import, legacy-only import and legacy wipe revoke consent too.
 toggle.check();ev('window.__copySave=JSON.stringify(P)');check(ev("bfImportSaveText(__copySave,'disposable copy save')"),'copy save import');check(not toggle.is_checked() and button.count()==0,'copy import revokes opt-in')
 toggle.check();check(ev("bfImportSaveText(JSON.stringify(defaultProgress()),'disposable legacy save')"),'copy-to-legacy import');check(not toggle.is_checked() and button.count()==0,'copy-to-legacy import revokes opt-in')
 toggle.check();check(ev("bfImportSaveText(JSON.stringify(defaultProgress()),'disposable legacy save')"),'legacy-to-legacy import');check(not toggle.is_checked() and button.count()==0,'legacy import revokes opt-in')
 toggle.check();ev("BF_homeNav.go('menu');document.getElementById('wipesave').click();BF_homeNav.go('summon')");check(not toggle.is_checked() and button.count()==0,'legacy wipe revokes opt-in')
 check(not errors,'no uncaught browser errors');print('TOTAL',n,flush=True);b.close()
