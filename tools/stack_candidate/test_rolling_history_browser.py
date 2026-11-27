"""Disposable Chromium test with actual prepared game and native module order."""
import sys,pathlib,shutil
from playwright.sync_api import sync_playwright
A=pathlib.Path(sys.argv[1]);errors=[];n=0
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium'),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':390,'height':844});p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/*',lambda r:r.abort())
 p.evaluate('''()=>{const db={};window.__writes=0;window.__fail=false;Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>db[k]??null,setItem:(k,v)=>{if(window.__fail)throw Error('quota');db[k]=String(v);window.__writes++},removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});window.alert=()=>{};window.confirm=()=>true;HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};HTMLMediaElement.prototype.play=()=>Promise.resolve()}''')
 p.set_content((A/'index.html').read_text(),wait_until='load',timeout=45000)
 for f in pathlib.Path(__file__).with_name('native-order.txt').read_text().splitlines():p.add_script_tag(content=(A/f).read_text())
 def ev(s):return p.evaluate(s)
 def check(v,name):
  global n
  assert v,name
  n+=1;print('PASS',name,flush=True)
 check(not errors,'native order loaded')
 ev("P.summonTokens=4;P.summonHistory=Array.from({length:100},(_,i)=>RECRUIT_IDS[i%RECRUIT_IDS.length]);saveProgress();renderProgress();BF_homeNav.go('summon');Math.random=()=>0")
 p.locator('#bf-copy-summon-optin').check(timeout=5000)
 btn=p.locator('#bf-copy-token-summon');check(btn.is_enabled(),'full history does not block new summon')
 before=ev('JSON.parse(JSON.stringify(P))');writes=ev('__writes');btn.click(timeout=5000);after=ev('JSON.parse(JSON.stringify(P))')
 check(after['summonHistory']==before['summonHistory'][1:]+[ev('RECRUIT_IDS[0]')],'oldest history entry rotated out')
 check(after['summonTokens']==3 and len(after['roster'])==len(before['roster'])+1 and ev('__writes')==writes+1,'atomic first acquisition')
 for _ in range(3):btn.click(timeout=5000)
 check(ev('P.summonHistory.length===100&&P.summonTokens===0&&P.roster.length===('+str(len(before['roster']))+'+4)'),'four acquisitions at full history, no token or ownership loss')
 check(ev('Object.keys(P._bfUnitInstancesV1.baseById).length===3'),'three distinct copies retained')
 check(ev('JSON.stringify(parseProgress(JSON.parse(localStorage.getItem(SAVE_KEY))))===JSON.stringify(P)'),'v7 parser accepts rolling history')
 check(btn.is_disabled(),'zero token prevents further acquisition')
 ev('P.summonTokens=1;saveProgress();renderSummonPanel();window.__fail=true');before=ev('JSON.stringify(P)');raw=ev('localStorage.getItem(SAVE_KEY)');btn.click(timeout=5000);check(ev('JSON.stringify(P)')==before and ev('localStorage.getItem(SAVE_KEY)')==raw,'quota rollback preserves history and token')
 ev('window.__fail=false;saveProgress();P.summonHistory.push(RECRUIT_IDS[0]);renderSummonPanel()');check(btn.is_disabled() and ev('customDuplicateSummon().ok') is False,'invalid history length rejected')
 ev('P.summonHistory.pop();P.summonHistory[0]=999999999;renderSummonPanel()');check(btn.is_disabled() and ev('customDuplicateSummon().ok') is False,'invalid history record rejected')
 check(not errors,'no uncaught errors');print('TOTAL',n,flush=True);b.close()
