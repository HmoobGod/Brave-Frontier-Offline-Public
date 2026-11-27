"""Combined actual acquisition -> stack -> squad -> Imp feed -> battle test."""
import sys,pathlib,shutil,json
from playwright.sync_api import sync_playwright
A=pathlib.Path(sys.argv[1]);errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome'),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':390,'height':844});p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/*',lambda r:r.abort())
 p.evaluate('''()=>{const db={};window.__writes=0;Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>db[k]??null,setItem:(k,v)=>{db[k]=String(v);window.__writes++},removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});window.alert=()=>{};window.confirm=()=>true;HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};HTMLMediaElement.prototype.play=()=>Promise.resolve()}''')
 p.set_content((A/'index.html').read_text(),wait_until='load',timeout=45000)
 for f in (pathlib.Path(__file__).with_name('native-order.txt')).read_text().splitlines():p.add_script_tag(content=(A/f).read_text())
 n=0
 def check(v,name):
  global n
  assert v,name
  n+=1;print('PASS',name,flush=True)
 def ev(s):return p.evaluate(s)
 check(not errors,'full native module order clean')
 ev("P.summonTokens=2;saveProgress();renderProgress();BF_homeNav.go('summon');Math.random=()=>0")
 check(not p.locator('#bf-copy-summon-optin').is_checked(),'normal game default off')
 p.locator('#bf-copy-summon-optin').check(timeout=5000);p.locator('#bf-copy-token-summon').click(timeout=5000);p.locator('#bf-copy-token-summon').click(timeout=5000)
 check(ev('P.summonTokens===0&&P._bfUnitInstancesV1.baseById[1000000001]===RECRUIT_IDS[0]'),'normal acquisition creates distinct owned instance')
 ev("BF_homeNav.go('units');BFInnerScreens.setTab('box')");p.locator('#bf-copy-stack-toggle').check(timeout=5000);check('×2' in p.locator('.bf-copy-stack summary').inner_text(),'stack acquired copies')
 # Actual native squad picker, remove six default units down to one before adding two.
 ev("BFInnerScreens.setTab('squad')")
 for _ in range(5):
  el=p.locator('#squadpicker .squadpick input:checked').last
  count=ev('P.squad.length')
  if count>1:
   el.click(timeout=5000)
   assert ev('P.squad.length')==count-1,'native squad removal failed'
 p.locator('#squadpicker .squadpick').filter(has_text='Copy #1000000001').locator('input').check(timeout=5000)
 check(ev('P.squad.includes(1000000001)&&P.squad.length<=6'),'copy independently selectable in squad')
 # Use actual Imp API to opt in and provision existing materials; no fabricated ownership.
 check(ev('BFGlobalOptionalImpsV16900.activate()'),'existing Imp mode explicitly activated')
 ev('BFGlobalOptionalImpsV16900.refresh()');plan=ev('BFGlobalOptionalImpsV16900.planSquad()');check(bool(plan and plan['total']>0),'smart squad plan available')
 writes=ev('__writes');check(ev('!!BFGlobalOptionalImpsV16900.feedSquad()'),'combined squad feed succeeds');check(ev('__writes')==writes+1,'combined feed single canonical save')
 check(ev('JSON.stringify(parseProgress(JSON.parse(localStorage.getItem(SAVE_KEY))))===JSON.stringify(P)'),'copy and Imp save exact roundtrip')
 ev("document.getElementById('mode').value='archive';reset()")
 check(ev('S.party.some(u=>u.baseId===1000000001&&u.unitId===RECRUIT_IDS[0])'),'acquired copy reaches next actual archive battle')
 check(ev('BFGlobalOptionalImpsV16900.snapshot().rows.some(r=>r.baseId===1000000001)'),'Imp audit uses owned instance identity')
 check(not errors,'no uncaught errors');print('TOTAL',n,flush=True);b.close()
