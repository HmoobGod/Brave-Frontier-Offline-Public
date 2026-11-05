"""v272: capture additional reconstructed source UI views, not Android or 2022 parity.

Disposable browser sessions, intercepted local source assets, no owner save access.
"""
from pathlib import Path
import sys
from bf_capture_progress_audit import INSTALL_STORAGE, SNAPSHOT, assert_unchanged
import hashlib
import json
import mimetypes
import shutil
from urllib.parse import urlsplit, unquote

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/"app/src/main/assets"
OUTPUT=ROOT/"source_audit_reports/v272_nested_ui_capture"
NAV=(ASSETS/"bf_home_nav.js").read_text("utf8")
CSS=(ASSETS/"bf_home_nav.css").read_text("utf8")
if "--capture-local" not in sys.argv:
    PRE=(ROOT/".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
    BUILD=(ROOT/".github/workflows/build-debug-apk.yml").read_text("utf8")
    MAN=(ROOT/"app/src/main/AndroidManifest.xml").read_text("utf8")
    assert "test_bf_nested_ui_capture_v27200.py --source-only" in PRE
    assert BUILD.count("python3 test_bf_nested_ui_capture_v27200.py --capture")==1
    assert "BraveFrontier-v272-nested-ui-screen-receipts" in BUILD
    assert "source_audit_reports/v272_nested_ui_capture/" in BUILD
    assert "android.permission.INTERNET" not in MAN
assert "window.BF_homeNav" in NAV and "window.BFInnerScreens" in NAV
assert "window.BFUnitBox" in NAV
assert len(NAV.encode())<128*1024 and len(CSS.encode())<128*1024
if "--source-only" in sys.argv:
    print("PASS v272 source: nested UI screenshot audit registered, no network permission")
    raise SystemExit(0)
assert "--capture" in sys.argv or "--capture-local" in sys.argv
from playwright.sync_api import sync_playwright
chrome=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "Chromium required for screenshot capture"
html=(ASSETS/"index.html").read_text("utf8")
assert "<head>" in html
html=html.replace("<head>",'<head><base href="http://bf-v272-assets.test/">',1)
OUTPUT.mkdir(parents=True,exist_ok=True)
VIEWS=(
    ("squad-editor","units","squad","#squadpicker"),
    ("unit-box","units","box","#bf-owned-box"),
    ("evolution","units","evolve","#evolist"),
    ("training","units","training",".training-panel"),
    ("quest-details","quest",None,"#bf-quest-details"),
    ("save-controls","menu",None,"#downloadsave"),
)
assert len(VIEWS)==6
missing=set()
external=set()
def serve(route):
    u=urlsplit(route.request.url)
    if u.hostname!="bf-v272-assets.test" or u.scheme!="http":
        external.add(u.hostname or u.scheme)
        route.abort()
        return
    rel=unquote(u.path).lstrip("/")
    parts=Path(rel).parts
    if not rel or ".." in parts or rel.startswith(".") or "\\" in rel:
        external.add("invalid-local-path")
        route.abort()
        return
    path=ASSETS.joinpath(*parts)
    if not path.is_file() or not path.resolve().is_relative_to(ASSETS.resolve()):
        missing.add(rel)
        route.abort()
        return
    route.fulfill(status=200,
                  content_type=mimetypes.guess_type(str(path))[0] or "application/octet-stream",
                  body=path.read_bytes())

SAVE_CONTROLS=('downloadsave','uploadsave','exportsave','importsave','undosave','wipesave')
receipts=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=chrome,
                               args=["--no-sandbox","--disable-dev-shm-usage"])
    for width,height in ((320,740),(393,852)):
        ctx=browser.new_context(viewport={"width":width,"height":height},
                                device_scale_factor=2,service_workers="block",
                                accept_downloads=False,reduced_motion="reduce",
                                color_scheme="dark")
        page=ctx.new_page()
        errors=[]
        page.on("pageerror",lambda err:errors.append(str(err)))
        page.on("dialog",lambda dialog:dialog.dismiss())
        page.route("**/*",serve)
        page.evaluate(INSTALL_STORAGE)
        page.set_content(html,wait_until="load",timeout=120000)
        page.add_style_tag(content=CSS)
        page.add_script_tag(content=NAV)
        page.locator("#bf-home").wait_for(state="visible",timeout=15000)
        baseline=page.evaluate(SNAPSHOT)
        for name,route,tab,selector in VIEWS:
            assert page.evaluate("(r)=>BF_homeNav.go(r)",route)
            if tab is not None:page.evaluate("(t)=>BFInnerScreens.setTab(t)",tab)
            subject=page.locator(selector)
            subject.wait_for(state="visible",timeout=12000)
            assert page.evaluate("BF_homeNav.current")==route
            if tab is not None:assert page.evaluate("BFInnerScreens.unitTab")==tab
            subject.scroll_into_view_if_needed(timeout=12000)
            save_visibility=[]
            if name=='save-controls':
                # Reconcile the tracked v278.1 defect: menu top is not a save-control view.
                # Find an unobscured position without clicking any save action.
                first_top=page.locator('#downloadsave').evaluate('(e)=>e.getBoundingClientRect().top+scrollY')
                for safe_top in range(16,273,16):
                    page.evaluate('(y)=>window.scrollTo({top:y,behavior:"instant"})',max(0,first_top-safe_top))
                    page.wait_for_timeout(80)
                    save_visibility=page.evaluate("""ids=>ids.map(id=>{
                      const e=document.getElementById(id),r=e.getBoundingClientRect();
                      const points=[[r.x+4,r.y+4],[r.right-4,r.y+4],
                                    [r.x+4,r.bottom-4],[r.right-4,r.bottom-4],
                                    [r.x+r.width/2,r.y+r.height/2]];
                      const clear=points.every(([x,y])=>{
                        const hit=document.elementFromPoint(x,y);return hit===e||e.contains(hit);
                      });
                      return {id,visible:r.top>=0&&r.bottom<=innerHeight&&r.left>=0&&r.right<=innerWidth,
                              unobscured:clear,sampleCount:points.length};
                    })""",list(SAVE_CONTROLS))
                    if all(x['visible'] and x['unobscured'] for x in save_visibility):break
                assert all(x['visible'] and x['unobscured'] for x in save_visibility),(width,save_visibility)
            page.wait_for_timeout(120)
            bounds=page.evaluate("""() => ({
               scrollWidth:document.documentElement.scrollWidth,
               scrollY:window.scrollY,innerWidth:window.innerWidth
            })""")
            assert bounds["scrollWidth"]<=width+1,(width,name,bounds)
            file=f"{width}x{height}-{name}.png"
            shot=OUTPUT/file
            page.screenshot(path=str(shot),full_page=False,animations="disabled",
                            caret="hide",timeout=20000)
            audit=assert_unchanged(page,baseline,(width,name))
            assert not errors,(width,name,errors[:3])
            receipts.append(dict(file=file,screen=name,route=route,unitTab=tab,
                viewport=[width,height],scrollY=bounds["scrollY"],
                scrollWidth=bounds["scrollWidth"],bytes=shot.stat().st_size,
                sha256=hashlib.sha256(shot.read_bytes()).hexdigest(),saveUnchanged=True,saveControlsVisibility=save_visibility,**audit))
        ctx.close()
    browser.close()
assert not external,sorted(external)
assert not missing,sorted(missing)[:20]
manifest=dict(version="v272",
   captureScope="nested source UI on packaged HTML and prepared assets",
   historical2022Parity="NOT TESTED",ownerDevice="NOT TESTED",
   fullAndroidWebView="NOT TESTED",personalSaveLoaded=False,
   sourceScreens=6,screenshots=receipts,missingAssetRequests=sorted(missing),
   externalRequestsBlocked=sorted(external))
(OUTPUT/"capture-manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
assert len(receipts)==12
print("PASS v272 12 nested UI screenshots, six views x two phone widths, save unchanged")
