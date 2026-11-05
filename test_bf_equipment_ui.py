"""Read-only Equipment tab on actual prepared HTML; no owner data."""
from pathlib import Path
import hashlib,json,mimetypes,re,shutil,sys
from urllib.parse import unquote,urlsplit
from bf_capture_progress_audit import INSTALL_STORAGE,SNAPSHOT,assert_unchanged
ROOT=Path(__file__).resolve().parent;A=ROOT/'app/src/main/assets'
NAV=(A/'bf_home_nav.js').read_text();CSS=(A/'bf_home_nav.css').read_text()
MODULE=NAV.split('/* UI-first equipment inspector:',1)[1].split('\n})();',1)[0]+'\n})();'
assert all(term not in MODULE for term in ('localStorage','saveProgress','awardDemoRewards','BFAndroid','fetch(','P.roster=','P.squad='))
assert 'data-bf-unit-tab="equipment"' in NAV and 'equipment.hidden = next' in NAV
assert len(NAV.encode())<128*1024 and len(CSS.encode())<128*1024
assert 'python3 test_bf_equipment_ui.py --source-only' in (ROOT/'.github/workflows/android-back-ui-source-preflight.yml').read_text()
assert 'python3 test_bf_equipment_ui.py --capture' in (ROOT/'.github/workflows/build-debug-apk.yml').read_text()
if '--source-only' in sys.argv:
 print('PASS Equipment UI source: read-only preview, tab integration and bounded existing resources');raise SystemExit(0)
assert (A/'content/home/home_win_quest.png').is_file(),'Run bundled asset preparation first'
from playwright.sync_api import sync_playwright
chrome=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable');assert chrome
html=(A/'index.html').read_text().replace('<head>','<head><base href="http://bf-equipment-ui.test/">',1)
output=ROOT/'source_audit_reports/equipment-ui';output.mkdir(parents=True,exist_ok=True)
receipts=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=chrome,args=['--no-sandbox','--disable-dev-shm-usage'])
 for width,height in ((320,740),(393,852),(540,900),(740,360)):
  ctx=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce',service_workers='block')
  page=ctx.new_page();errors=[];bad=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  def serve(route):
   u=urlsplit(route.request.url);path=(A/unquote(u.path).lstrip('/')).resolve()
   if u.hostname!='bf-equipment-ui.test' or not path.is_relative_to(A.resolve()) or not path.is_file():bad.append(route.request.url);route.abort();return
   route.fulfill(body=path.read_bytes(),content_type=mimetypes.guess_type(str(path))[0] or 'application/octet-stream')
  page.route('**/*',serve);page.evaluate(INSTALL_STORAGE)
  page.set_content(html,wait_until='load',timeout=90000);page.add_style_tag(content=CSS);page.add_script_tag(content=NAV)
  baseline=page.evaluate(SNAPSHOT);battle=page.evaluate('JSON.stringify(S)')
  page.locator('.bf-navbar [data-bf-goto="units"]').click()
  tab=page.locator('button[data-bf-unit-tab="equipment"]');tab.click()
  panel=page.locator('#bf-equipment-screen')
  assert panel.is_visible() and page.evaluate('BFInnerScreens.unitTab')=='equipment'
  assert tab.get_attribute('aria-pressed')=='true'
  assert not page.locator('#squadpicker').is_visible()
  assert not page.locator('.evo-panel').is_visible() and not page.locator('.training-panel').is_visible()
  select=page.locator('#bf-equipment-unit');options=select.locator('option').evaluate_all('(es)=>es.map(e=>({id:e.value,text:e.textContent}))')
  assert len(options)>1
  select.select_option(options[1]['id'])
  assert options[1]['text'].split(' · #')[0] in page.locator('#bf-equipment-unit-card').inner_text()
  assert panel.locator('button:disabled').count()==4 # clear + 3 unavailable services
  def capture(name):
   panel.scroll_into_view_if_needed()
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(width,name)
   assert panel.evaluate('(e)=>e.scrollWidth<=e.clientWidth+1'),(width,name)
   for control in panel.locator('input,select,button').all():
    if control.is_visible():assert control.bounding_box()['height']>=44,(width,name,control.get_attribute('id'))
   assert_unchanged(page,baseline,(width,name));assert page.evaluate('JSON.stringify(S)')==battle
   if '--capture' in sys.argv:
    # Align the top of this full scrollable screen; viewport captures are not full-screen coverage.
    panel.evaluate('(e)=>e.scrollIntoView({block:"start"})')
    heading=panel.locator('.bf-equipment-header h2')
    assert heading.evaluate('e=>{const r=e.getBoundingClientRect();const hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return hit===e||e.contains(hit)}'),(width,name,'heading obscured')
    p=output/f'{width}x{height}-{name}.png';page.screenshot(path=str(p),animations='disabled')
    receipts.append({'view':name,'width':width,'height':height,'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    if name=='owned-unit':
     p=output/f'{width}x{height}-full-panel.png'
     # Component-only image: omit the fixed toolbar that would otherwise be
     # painted across this tall element. Viewport captures stay unmodified.
     panel.screenshot(path=str(p),animations='disabled',style='.bf-navbar{visibility:hidden!important}')
     data=p.read_bytes()
     receipts.append({'view':'full-panel','width':int.from_bytes(data[16:20],'big'),'height':int.from_bytes(data[20:24],'big'),
                      'viewportWidth':width,'viewportHeight':height,'fixedToolbarHiddenForComponentCapture':True,
                      'file':p.name,'sha256':hashlib.sha256(data).hexdigest()})
  capture('owned-unit')
  # Long display names are a synthetic UI fixture, not a new owned unit.
  page.evaluate("""()=>{window.__equipmentEffective=effectiveUnit;effectiveUnit=id=>{const u=__equipmentEffective(id);return u?{...u,name:'A Very Long Archived Unit Name With An Extended Title '.repeat(4)}:u};BFEquipmentUI.refresh()}""")
  capture('long-name')
  page.evaluate('effectiveUnit=window.__equipmentEffective;BFEquipmentUI.refresh()')
  page.locator('#bf-equipment-search').fill('no-such-owned-unit-xyz')
  assert select.is_disabled() and not page.locator('#bf-equipment-slots').is_visible()
  capture('no-matches')
  page.locator('#bf-equipment-clear').click()
  assert not select.is_disabled() and page.locator('#bf-equipment-search').evaluate('(e)=>e===document.activeElement')
  page.locator('#bf-equipment-search').focus();page.keyboard.press('Tab')
  assert select.evaluate('(e)=>e===document.activeElement')
  assert select.evaluate('(e)=>getComputedStyle(e).outlineWidth')=='3px'
  # Empty/unresolved roster fixtures must not be normalized or rewritten by the UI.
  original=page.evaluate('({roster:[...P.roster],squad:[...P.squad]})')
  for roster,squad,name in [([],[],'empty-roster'),([999999999],[999999999],'unresolved-roster')]:
   page.evaluate('(f)=>{P.roster=f.roster;P.squad=f.squad}',{'roster':roster,'squad':squad})
   fixture=page.evaluate(SNAPSHOT);page.evaluate('BFEquipmentUI.refresh()')
   assert select.is_disabled()
   if name=='unresolved-roster':assert '1 saved profile unavailable' in page.locator('#bf-equipment-status').inner_text()
   baseline_original=baseline;baseline=fixture;capture(name);baseline=baseline_original
  page.evaluate('(f)=>{P.roster=f.roster;P.squad=f.squad;BFEquipmentUI.refresh()}',original)
  assert_unchanged(page,baseline,width)
  # Portrait failure remains readable through the existing fallback helper.
  page.locator('#bf-equipment-unit-card img').evaluate('(e)=>e.dispatchEvent(new Event("error"))')
  assert page.locator('#bf-equipment-unit-card .bf-portrait-fallback').is_visible()
  page.locator('#bf-equipment-box').click()
  assert page.evaluate('BFInnerScreens.unitTab')=='box' and not panel.is_visible()
  page.locator('button[data-bf-unit-tab="equipment"]').click()
  page.locator('.bf-navbar [data-bf-goto="home"]').click();assert not panel.is_visible()
  page.locator('.bf-navbar [data-bf-goto="units"]').click();assert panel.is_visible()
  page.add_script_tag(content='/* UI-first equipment inspector:'+MODULE)
  assert page.locator('#bf-equipment-screen').count()==1 and page.locator('#bf-equipment-unit').count()==1
  assert_unchanged(page,baseline,width);assert page.evaluate('JSON.stringify(S)')==battle
  assert not errors,(width,errors);assert not bad,(width,bad[:5])
  print('PASS',width,height,'Equipment tab, owned/empty/unresolved/long/search/fallback states, routing and P/S/storage isolation',flush=True)
  ctx.close()
 browser.close()
if '--capture' in sys.argv:
 (output/'receipts.json').write_text(json.dumps(receipts,indent=2)+'\n');print('CAPTURED',len(receipts),'browser screenshots')
