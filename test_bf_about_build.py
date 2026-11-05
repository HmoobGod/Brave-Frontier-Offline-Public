"""About UI with mocked public metadata; native implementation compiles in Android CI."""
from pathlib import Path
import re,sys,shutil
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
J=(A/'bf_home_nav.js').read_text();C=(A/'bf_home_nav.css').read_text();java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text()
MARK='/* About uses public installed-app metadata only,';MODULE=MARK+J.split(MARK,1)[1].split('\n})();',1)[0]+'\n})();'
method=java.split('@JavascriptInterface public String getBuildInfo()',1)[1].split('@JavascriptInterface public void importSaveFile()',1)[0]
assert all(x in method for x in ('getPackageInfo(getPackageName(), 0)','info.versionName','info.versionCode','"packageName"','return "{}"'))
assert all(x not in method for x in ('saveToWrite','getSigning','getDeviceId','getAndroidId','openInputStream','startActivity','getSharedPreferences'))
assert all(x not in MODULE for x in ('localStorage','saveProgress','P.','S.','importSaveFile(','exportSaveFile(','fetch('))
assert len(J.encode())<128*1024 and len(C.encode())<128*1024
assert 'test_bf_about_build.py --source-only' in (R/'.github/workflows/android-back-ui-source-preflight.yml').read_text()
assert 'python3 test_bf_about_build.py' in (R/'.github/workflows/build-debug-apk.yml').read_text()
if '--source-only' in sys.argv:print('PASS About source: public app metadata getter, bounded UI/no saves');raise SystemExit(0)
from playwright.sync_api import sync_playwright
from bf_capture_progress_audit import INSTALL_STORAGE,SNAPSHOT,assert_unchanged
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=shutil.which('chromium') or shutil.which('google-chrome'),args=['--no-sandbox'])
 for w in (320,393,540):
  p=b.new_page(viewport={'width':w,'height':852});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/*',lambda r:r.abort());p.evaluate(INSTALL_STORAGE);p.set_content((A/'index.html').read_text());p.add_style_tag(content=C);p.add_script_tag(content=J)
  before=p.evaluate(SNAPSHOT);s=p.evaluate('JSON.stringify(S)');p.locator('.bf-navbar [data-bf-goto="menu"]').click();panel=p.locator('#bf-about-build');summary=panel.locator('summary');summary.click();assert p.locator('#bf-about-version').inner_text()=='Unavailable'
  cases=[({'packageName':'org.example.fixture','versionName':'0.1-test','versionCode':123},True),({'packageName':'org.example.fixture','versionName':'<b>fixture</b>','versionCode':124},True),({'packageName':'org.example.fixture','versionName':'bad','versionCode':-1},False),({'packageName':'bad/package','versionName':'x','versionCode':1},False),({'versionCode':123},False)]
  for info,valid in cases:
   p.evaluate('(v)=>{window.__info=v;window.BFAndroid={getBuildInfo:()=>JSON.stringify(__info),importSaveFile:()=>{throw Error("must not import")},exportSaveFile:()=>{throw Error("must not export")}}}',info)
   summary.click();summary.click();p.wait_for_function('(v)=>document.getElementById("bf-about-version").textContent===v',arg=info['versionName'] if valid else 'Unavailable')
   assert panel.locator('dd b, dd img').count()==0
  p.evaluate('()=>{window.BFAndroid.getBuildInfo=()=>{throw Error("unavailable")};}');summary.click();summary.click();assert p.locator('#bf-about-version').inner_text()=='Unavailable'
  assert p.evaluate('document.documentElement.scrollWidth<=innerWidth+1');assert summary.bounding_box()['height']>=44
  assert_unchanged(p,before,w);assert p.evaluate('JSON.stringify(S)')==s
  p.locator('.bf-navbar [data-bf-goto="home"]').click();assert not panel.is_visible();p.add_script_tag(content=MODULE);assert p.locator('#bf-about-build').count()==1;assert not errors,errors
  print('PASS',w,'browser/mocked metadata/invalid/throw/text safety, routes and P/S/storage isolation');p.close()
 b.close()
