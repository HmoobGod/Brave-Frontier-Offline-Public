"""v267 missing-art readability; disposable offline browser only."""
from pathlib import Path
import shutil,sys
ROOT=Path(__file__).resolve().parent
A=ROOT/'app/src/main/assets'
HTML=(A/'index.html').read_text()
CSS=(A/'bf_home_nav.css').read_text()
NAV=(A/'bf_home_nav.js').read_text()
SRC=(ROOT/'.github/workflows/android-back-ui-source-preflight.yml').read_text()
BUILD=(ROOT/'.github/workflows/build-debug-apk.yml').read_text()
assert "fallback.textContent = 'NO ART'" in NAV
assert '/* v267 narrow-screen fallback readability;' in CSS
assert 'test_bf_unit_portrait_readability_v26700.py --source-only' in SRC
assert BUILD.count('python3 test_bf_unit_portrait_readability_v26700.py') == 1
assert 'android.permission.INTERNET' not in (ROOT/'app/src/main/AndroidManifest.xml').read_text()
print('PASS v267 source safeguards')
if '--source-only' in sys.argv[1:]:raise SystemExit(0)
from playwright.sync_api import sync_playwright
exe=shutil.which('chromium') or shutil.which('google-chrome')
assert exe
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=exe,args=['--no-sandbox','--disable-dev-shm-usage'])
 for width in (320,359,393,540):
  ctx=browser.new_context(viewport={'width':width,'height':790},service_workers='block')
  page=ctx.new_page()
  page.route('http://**/*',lambda r:r.abort())
  page.route('https://**/*',lambda r:r.abort())
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('dialog',lambda d:d.dismiss())
  page.evaluate("""() => {let s=Object.create(null);window.__t=s;Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>s[k]??null,setItem:(k,v)=>s[k]=String(v),removeItem:k=>delete s[k],clear:()=>Object.keys(s).forEach(k=>delete s[k]),key:n=>Object.keys(s)[n]??null,get length(){return Object.keys(s).length}}})}""")
  page.set_content(HTML,wait_until='load',timeout=90000)
  page.add_style_tag(content=CSS)
  page.evaluate("""() => {const f=window.effectiveUnit;window.effectiveUnit=id=>{const u=f(id);return u?{...u,portrait:''}:u};for(const recipe of EVO_RECIPES){const u=UNIT_BY_ID.get(recipe.evolvedId);if(u)UNIT_BY_ID.set(recipe.evolvedId,{...u,portrait:''})}}""")
  before=page.evaluate("""()=>JSON.stringify({s:P.squad,r:P.roster,e:P.evolutions,g:P.gems,z:P.zel,k:P.karma,save:localStorage.getItem('bf_global_offline_demo_v7'),storage:window.__t})""")
  page.add_script_tag(content=NAV)
  home=page.locator('#bf-scene-party .bf-portrait-fallback')
  assert home.count()==6
  page.evaluate("BF_homeNav.go('units');BFInnerScreens.setTab('box');BFUnitBox.refresh()")
  box=page.locator('#bf-box-results .bf-portrait-fallback')
  assert box.count()==6
  for selector in ('#bf-box-detail>.bf-portrait-fallback','#bf-box-detail .bf-evo-preview>.bf-portrait-fallback'):
   e=page.locator(selector)
   assert e.count()==1 and e.is_visible()
   assert e.inner_text()=='NO ART' and e.get_attribute('role')=='img'
   assert e.get_attribute('aria-label').startswith('Portrait unavailable for ')
   d=e.evaluate("""e=>{const t=e.firstChild,y=[];for(let i=3;i<=5;i++){let r=document.createRange();r.setStart(t,i);r.setEnd(t,i+1);y.push(Math.round(r.getBoundingClientRect().top))}const rect=e.getBoundingClientRect();return {font:parseFloat(getComputedStyle(e).fontSize),y,x:rect.x,right:rect.right,sw:e.scrollWidth,cw:e.clientWidth}}""")
   assert d['font']>=11 and len(set(d['y']))==1 and d['sw']<=d['cw']+1
   assert d['x']>=-1 and d['right']<=width+1
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  after=page.evaluate("""()=>JSON.stringify({s:P.squad,r:P.roster,e:P.evolutions,g:P.gems,z:P.zel,k:P.karma,save:localStorage.getItem('bf_global_offline_demo_v7'),storage:window.__t})""")
  assert before==after and not errors
  ctx.close();print('PASS v267',width)
 browser.close()
