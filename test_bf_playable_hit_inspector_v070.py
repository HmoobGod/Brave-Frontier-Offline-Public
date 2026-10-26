"""v0.70 browser: explore all 72 original attack profiles and keep owned roster intact."""
from pathlib import Path
import hashlib,shutil,subprocess,sys
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
f=ASSETS/'index.html'
s=f.read_text('utf-8')
assert s.count('/* BF_PLAYABLE_HIT_INSPECTOR_V070 */')==1
before=hashlib.sha256(s.encode()).hexdigest()
subprocess.run([sys.executable,str(ROOT/'prepare_playable_hit_inspector_v070.py')],check=True,cwd=ROOT)
assert hashlib.sha256(f.read_bytes()).hexdigest()==before
assert 'bf_global_offline_demo_v7' in s
with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,
    executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
    args=['--no-sandbox','--disable-dev-shm-usage'])
  page=browser.new_page(viewport={'width':390,'height':844})
  errors=[]
  page.on('pageerror',lambda error:errors.append(str(error)))
  page.evaluate("""() => {
    const files={};
    Object.defineProperty(window,'localStorage',{configurable:true,value:{
      getItem:k=>files[k]??null,setItem:(k,v)=>{files[k]=String(v)},
      removeItem:k=>{delete files[k]},key:i=>Object.keys(files)[i]??null,
      get length(){return Object.keys(files).length}}});
    window.alert=()=>{};window.confirm=()=>true;
    HTMLMediaElement.prototype.load=()=>{};
    HTMLMediaElement.prototype.pause=()=>{};
    HTMLMediaElement.prototype.play=()=>Promise.resolve();
  }""")
  page.set_content(s,wait_until='load',timeout=90000)
  assert page.evaluate('P.version')==7
  assert page.evaluate('BFPlayableAttackFramesV062.count')==72
  baseline=page.evaluate("""() => ({
    progress:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')
  })""")
  options=page.locator('#hitunit option')
  assert options.count()==72,options.count()
  allIds=page.evaluate("Array.from(document.querySelectorAll('#hitunit option')).map(x=>Number(x.value))")
  assert len(set(allIds))==72
  assert 10015 in allIds and 10023 in allIds and 60025 in allIds
  assert 'ARCHIVE ONLY' in page.locator('#hitunit option[value="10015"]').text_content()
  assert 'ARCHIVE ONLY' not in page.locator('#hitunit option[value="10011"]').text_content()
  page.locator('#hitunit').select_option('10015')
  assert '7 recorded normal hits' in page.locator('#hitevents').inner_text()
  assert page.locator('#hitevents .hit-dots span').count()==7
  page.locator('#hitunit').select_option('10023')
  assert '130 rather than 100' in page.locator('#hitevents').inner_text()
  assert 'not normalized' in page.locator('#hitevents').inner_text()
  page.locator('#hitunit').select_option('60025')
  assert '6 recorded normal hits' in page.locator('#hitevents').inner_text()
  assert page.locator('#hitevents .hit-dots span').count()==6
  final=page.evaluate("""() => ({
    progress:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')
  })""")
  assert final==baseline
  assert not errors,errors
  browser.close()
print('PASS v0.70 source 72 hit-inspector profiles, 130% warning and unowned flags, v7 state intact')
