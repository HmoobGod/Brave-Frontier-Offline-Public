"""Offline UI-only location screens, real prepared HTML; synthetic state only."""
from pathlib import Path
import hashlib
import json
import mimetypes
import re
import shutil
import sys
from urllib.parse import unquote,urlsplit
from bf_capture_progress_audit import INSTALL_STORAGE,SNAPSHOT,assert_unchanged

ROOT=Path(__file__).resolve().parent
A=ROOT/'app/src/main/assets'
NAV=(A/'bf_home_nav.js').read_text()
CSS=(A/'bf_home_nav.css').read_text()
MODULE=NAV.split('/* UI-first location screens:',1)[1]
assert len(NAV.encode())<128*1024 and len(CSS.encode())<128*1024
assert not any(x in MODULE for x in ('localStorage','saveProgress','awardDemoRewards','fetch(','BFAndroid','P.','S.'))
assert "return window.BFLocationPreview.back()" in NAV
assert 'window.BFLocationPreview?.isOpen' in NAV
assert 'test_bf_location_previews.py --source-only' in (ROOT/'.github/workflows/android-back-ui-source-preflight.yml').read_text()
assert 'python3 test_bf_location_previews.py --capture' in (ROOT/'.github/workflows/build-debug-apk.yml').read_text()
if '--source-only' in sys.argv:
    print('PASS location UI source: presentation-only, existing loader budgets and Back hook');raise SystemExit(0)
from playwright.sync_api import sync_playwright
chrome=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable')
assert chrome
html=(A/'index.html').read_text().replace('<head>','<head><base href="http://bf-location-ui.test/">',1)
java=(ROOT/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text()
back_js=re.search(r'private static final String UI_BACK_JS\s*=\s*"([^"]+)";',java).group(1)
output=ROOT/'source_audit_reports/location-ui-previews';output.mkdir(parents=True,exist_ok=True)
receipts=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=chrome,args=['--no-sandbox','--disable-dev-shm-usage'])
    for width,height in ((320,740),(393,852),(540,900),(740,360)):
        context=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce',service_workers='block')
        page=context.new_page();errors=[];missing=[];external=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        def serve(route):
            url=urlsplit(route.request.url)
            if url.hostname!='bf-location-ui.test':external.append(route.request.url);route.abort();return
            path=(A/unquote(url.path).lstrip('/')).resolve()
            if not path.is_relative_to(A.resolve()) or not path.is_file():missing.append(str(path));route.abort();return
            route.fulfill(body=path.read_bytes(),content_type=mimetypes.guess_type(str(path))[0] or 'application/octet-stream')
        page.route('**/*',serve)
        page.evaluate(INSTALL_STORAGE)
        page.set_content(html,wait_until='load',timeout=90000)
        page.add_style_tag(content=CSS);page.add_script_tag(content=NAV)
        baseline=page.evaluate(SNAPSHOT);battle=page.evaluate('JSON.stringify(S)')
        trigger=page.locator('#bf-location-launch');trigger.click()
        dialog=page.locator('#bf-location-dialog')
        assert dialog.is_visible() and page.evaluate("BF_homeNav.current")== 'location-preview'
        assert page.locator('#bf-location-title').evaluate('(e)=>e===document.activeElement')
        assert page.locator('.bf-location-directory button').count()==5
        assert page.evaluate('BFLocationPreview.open("unknown")') is False
        def capture(name):
            bounds=dialog.evaluate('(e)=>{const r=e.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,scroll:e.scrollWidth,client:e.clientWidth}}')
            assert bounds['left']>=0 and bounds['right']<=width+1 and bounds['top']>=0 and bounds['bottom']<=height+1,bounds
            assert bounds['scroll']<=bounds['client']+1,bounds
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            assert_unchanged(page,baseline,(width,name))
            assert page.evaluate('JSON.stringify(S)')==battle
            if '--capture' in sys.argv:
                file=output/f'{width}x{height}-{name}.png';page.screenshot(path=str(file),animations='disabled')
                receipts.append({'view':name,'width':width,'height':height,'file':file.name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
        capture('directory')
        for key,name in [('vortex','Vortex Gate'),('arena','Arena'),('raid','Raid Battle'),('randall','Capital Randall'),('exchange','Exchange Hall')]:
            page.locator(f'.bf-location-directory [data-bf-location="{key}"]').click()
            assert page.locator('#bf-location-title').inner_text()==name
            assert page.locator('.bf-location-unavailable').is_disabled()
            assert page.locator('.bf-location-services h2').count()>=2
            capture(key)
            if key=='randall':
                page.locator('.bf-location-exchange').click()
                assert page.locator('#bf-location-title').inner_text()=='Exchange Hall'
                assert page.evaluate(back_js) is True
                assert page.locator('#bf-location-title').inner_text()=='Capital Randall'
            assert page.evaluate(back_js) is True
            assert page.locator('#bf-location-title').inner_text()=='Global Locations'
        # Native modal containment: focus never reaches the inert Home page.
        for _ in range(9):
            page.keyboard.press('Tab')
            assert dialog.evaluate('(e)=>e.contains(document.activeElement)||e===document.activeElement')
        for _ in range(9):
            page.keyboard.press('Shift+Tab')
            assert dialog.evaluate('(e)=>e.contains(document.activeElement)||e===document.activeElement')
        assert page.evaluate(back_js) is True
        page.wait_for_function('!document.body.classList.contains("bf-location-preview-open")')
        assert not dialog.is_visible() and page.evaluate('BF_homeNav.current')=='home'
        assert trigger.evaluate('(e)=>document.activeElement===e')
        assert page.evaluate(back_js) is False
        trigger.click();page.keyboard.press('Escape')
        page.wait_for_function('!document.body.classList.contains("bf-location-preview-open")')
        assert trigger.evaluate('(e)=>document.activeElement===e')
        trigger.click();page.locator('#bf-location-close').click()
        page.wait_for_function('!document.body.classList.contains("bf-location-preview-open")')
        assert page.evaluate('BFLocationPreview.open("arena")') is True
        assert page.evaluate('BF_homeNav.go("units")') is True
        page.wait_for_function('!document.body.classList.contains("bf-location-preview-open")')
        assert not dialog.is_visible() and page.evaluate('BF_homeNav.current')=='units'
        assert_unchanged(page,baseline,width)
        assert page.evaluate('JSON.stringify(S)')==battle
        previous=page.evaluate('BFLocationPreview.isOpen')
        page.add_script_tag(content='/* UI-first location screens:'+MODULE)
        assert page.locator('#bf-location-dialog').count()==1 and page.locator('#bf-location-launch').count()==1
        assert page.evaluate('BFLocationPreview.isOpen')==previous
        assert not errors,(width,errors)
        assert not missing,(width,missing)
        assert not external,(width,external)
        print('PASS',width,height,'five location UIs; nested Back, close/Escape/focus/modal/route states; P/S/storage unchanged')
        context.close()
    browser.close()
if '--capture' in sys.argv:
    (output/'receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
    print('CAPTURED',len(receipts),'UI screenshots (browser evidence; no device acceptance)')
