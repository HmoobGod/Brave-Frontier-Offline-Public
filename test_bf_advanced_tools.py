"""Preserve live diagnostics nodes/handlers while collapsing their Menu presentation."""
from pathlib import Path
import sys,shutil
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
J=(A/'bf_home_nav.js').read_text();C=(A/'bf_home_nav.css').read_text()
MARK='/* Keep raw battle diagnostics';MODULE=MARK+J.split(MARK,1)[1].split('\n})();',1)[0]+'\n})();'
assert not any(s in MODULE for s in ('localStorage','saveProgress','P.','S.','cloneNode','fetch(','BFAndroid'))
assert 'tools.append(title,note,inspector)' in MODULE
assert len(J.encode())<128*1024 and len(C.encode())<128*1024
assert 'test_bf_advanced_tools.py --source-only' in (R/'.github/workflows/android-back-ui-source-preflight.yml').read_text()
assert 'python3 test_bf_advanced_tools.py' in (R/'.github/workflows/build-debug-apk.yml').read_text()
if '--source-only' in sys.argv:print('PASS Advanced Tools source: bounded UI-only relocation, no clone/data writes');raise SystemExit(0)
from playwright.sync_api import sync_playwright
from bf_capture_progress_audit import INSTALL_STORAGE,SNAPSHOT,assert_unchanged
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=shutil.which('chromium') or shutil.which('google-chrome'),args=['--no-sandbox'])
 for w,h in ((320,740),(393,852),(540,900),(740,360)):
  p=b.new_page(viewport={'width':w,'height':h});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.route('**/*',lambda r:r.abort());p.evaluate(INSTALL_STORAGE)
  p.set_content((A/'index.html').read_text());p.add_style_tag(content=C);p.add_script_tag(content=J.split(MARK,1)[0])
  p.evaluate('()=>{window.__hit=document.querySelector("section.hit-panel");window.__events=document.getElementById("hitevents");window.__saves=["downloadsave","uploadsave","exportsave","importsave","undosave","wipesave"].map(id=>document.getElementById(id))}')
  before=p.evaluate(SNAPSHOT);battle=p.evaluate('JSON.stringify(S)');p.add_script_tag(content=MODULE)
  p.locator('.bf-navbar [data-bf-goto="menu"]').click();tools=p.locator('#bf-advanced-tools');assert tools.is_visible() and not p.locator('.hit-panel').is_visible()
  summary=tools.locator(':scope > summary');summary.focus();p.keyboard.press('Enter');assert p.locator('.hit-panel').is_visible()
  assert p.evaluate('document.querySelector("#bf-advanced-tools .hit-panel")===__hit && document.getElementById("hitevents")===__events')
  original=p.locator('#hitevents').inner_text();p.locator('#hitmode').select_option('bb');p.locator('#hitunit').select_option(index=1);assert p.locator('#hitevents').inner_text()!=original
  assert p.evaluate('__saves.every(e=>e&&e===document.getElementById(e.id)&&document.querySelectorAll("#"+e.id).length===1)')
  assert summary.bounding_box()['height']>=44 and p.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  # v396: the opened unit chooser must stay inside the tools card (long names were clipped to 368px at 320px; synthetic option removed again).
  fit=p.evaluate('()=>{const long=document.createElement("option");long.textContent="Synthetic longest recovered Global unit display name · 999999";document.getElementById("hitunit").append(long);const r=document.getElementById("bf-advanced-tools").getBoundingClientRect();const out=["#hitunit",".hit-controls>.hit-choice"].map(q=>{const e=document.querySelector("#bf-advanced-tools "+q).getBoundingClientRect();return e.width>0&&e.left>=r.left-.5&&e.right<=r.right+.5&&e.right<=innerWidth});long.remove();return out}');assert fit==[True,True],(w,fit)
  summary.focus();assert summary.evaluate('(e)=>getComputedStyle(e).outlineWidth')=='3px';p.keyboard.press('Space');assert not p.locator('.hit-panel').is_visible()
  p.locator('.bf-navbar [data-bf-goto="home"]').click();assert not tools.is_visible();p.locator('.bf-navbar [data-bf-goto="menu"]').click();assert tools.is_visible()
  p.add_script_tag(content=MODULE);assert p.locator('#bf-advanced-tools').count()==1
  assert_unchanged(p,before,w);assert p.evaluate('JSON.stringify(S)')==battle;assert not errors,errors
  print('PASS',w,h,'same live inspector/events/save nodes, original handlers, keyboard/routes/P/S/storage');p.close()
 # Missing inspector is a no-op rather than an empty broken tool section.
 p=b.new_page();p.set_content('<section class="progresspanel"></section>');p.add_script_tag(content=MODULE);assert p.locator('#bf-advanced-tools').count()==0;p.close();b.close()
