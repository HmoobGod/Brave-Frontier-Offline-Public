"""Disposable browser DOM integration, based on v198 set_content fixture. No navigation, network, Android, or owner saves."""
import sys, pathlib, shutil
from playwright.sync_api import sync_playwright
A=pathlib.Path(sys.argv[1]); html=(A/'index.html').read_text(); errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage']); p=b.new_page(viewport={'width':390,'height':844});p.on('pageerror',lambda e:errors.append(e.stack or str(e)));p.route('**/*',lambda r:r.abort())
 p.evaluate('''()=>{const db={};window.__db=db;window.__fault=null;Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>db[k]??null,setItem:(k,v)=>{if(k===window.__fault)throw Error('fixture quota');db[k]=String(v)},removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});window.alert=()=>{};window.confirm=()=>true;HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};HTMLMediaElement.prototype.play=()=>Promise.resolve();}''')
 p.set_content(html,wait_until='load',timeout=45000)
 print('boot',p.evaluate('typeof P'),errors[:10],flush=True)
 for f in ['bf_stack_copies.js','bf_home_nav.js','bf10200_qol_unit_flags.js','bf10000_qol_squad_presets.js']:
  p.add_script_tag(content=(A/f).read_text());print('loaded',f,errors[:8],flush=True)
 print('apis',p.evaluate('({home:typeof BF_homeNav,inner:typeof BFInnerScreens,box:typeof BFUnitBox,flags:typeof BFGlobalQoLUnitFlagsV10200,presets:typeof BFGlobalQoLSquadPresetsV10000})'),flush=True)
 n=0
 def check(v,name):
  global n
  assert v,name
  n+=1;print('PASS',name,flush=True)
 check(not errors,'boot and relevant UI scripts without errors')
 check(p.locator('#bf-copy-token-summon').count()==0,'default duplicate button absent')
 p.evaluate("()=>{P.summonTokens=5;saveProgress();window.BF_STACK_DISPOSABLE_UI=true;Math.random=()=>0;renderProgress();BF_homeNav.go('summon');}")
 print('summon',p.locator('#bf-copy-token-summon').is_visible(),flush=True)
 p.locator('#bf-copy-token-summon').click(timeout=3000)
 p.locator('#bf-copy-token-summon').click(timeout=3000)
 check(p.evaluate('P.summonTokens===3&&P.roster.includes(1000000001)&&P._bfUnitInstancesV1.baseById[1000000001]===RECRUIT_IDS[0]'),'two user button clicks exact token and copy ownership')
 check(p.evaluate('localStorage.getItem(SAVE_KEY)===JSON.stringify(P)'),'canonical receipt')
 p.evaluate("BF_homeNav.go('units');BFInnerScreens.setTab('box')")
 p.locator('#bf-copy-stack-toggle').check(timeout=3000)
 check(p.locator('.bf-copy-stack summary').count()==1,'one matching-form group')
 check('×2' in p.locator('.bf-copy-stack summary').inner_text(),'quantity two')
 if not p.locator('.bf-copy-stack').evaluate('(e)=>e.open'):p.locator('.bf-copy-stack summary').click(timeout=3000)
 p.locator('[data-bf-unit-id="1000000001"]').click(timeout=3000)
 check(p.locator('[data-bf-unit-id="1000000001"]').get_attribute('aria-pressed')=='true','individual copy selection')
 print('flag panel',p.locator('#bf10200-favorite').is_visible(),flush=True)
 p.locator('#bf10200-favorite').click(timeout=3000)
 check(p.evaluate('copyOrgRead().favorites.includes(1000000001)'),'favorite button commits selected copy')
 # Reset and undo use actual existing event handlers, not test substitutes.
 p.evaluate("BF_homeNav.go('menu')")
 before=p.evaluate('localStorage.getItem(SAVE_KEY)')
 p.evaluate('__fault=SAVE_KEY;document.getElementById("wipesave").click();__fault=null')
 check(p.evaluate('localStorage.getItem(SAVE_KEY)')==before,'failed reset preserves canonical bytes')
 p.evaluate('document.getElementById("wipesave").click()')
 check(p.evaluate('!P._bfUnitInstancesV1&&localStorage.getItem(SAVE_KEY)===JSON.stringify(P)'),'successful reset saved fresh canonical progress')
 check(p.evaluate('localStorage.getItem(BF_IMPORT_UNDO_KEY)')==before,'reset retained exact undo backup')
 p.evaluate('document.getElementById("undosave").click()')
 check(p.evaluate('P.roster.includes(1000000001)&&copyOrgRead().favorites.includes(1000000001)'),'undo restores exact copy and marker')
 check(not errors,'no uncaught browser exceptions')
 print('TOTAL',n,flush=True)
 b.close()
