"""v264 presentation-only safe-save hierarchy follow-up to Claude v256 N2-N4.

No reset, export, confirm, import, local storage or Android code is changed.
An isolated Chromium fixture includes the real inherited flex CSS declaration.
"""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
A=ROOT/"app/src/main/assets"
CSS=(A/"bf_home_nav.css").read_text("utf8")
NAV=(A/"bf_home_nav.js").read_text("utf8")
HTML=(A/"index.html").read_text("utf8")
PRE=(ROOT/".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
WF=(ROOT/".github/workflows/build-debug-apk.yml").read_text("utf8")
MAN=(ROOT/"app/src/main/AndroidManifest.xml").read_text("utf8")

MARKER="/* v264 safe-save visual hierarchy:"
assert CSS.count(MARKER)==1
PATCH=CSS.split(MARKER,1)[1]
for need in (
    ".transferactions #downloadsave", "#quarantineexport",
    "#quarantineexport:focus-visible", "#wipesave",
    "min-height:48px", "min-height:50px", "flex:1 1 100%",
    "margin-top:8px", "background:linear-gradient(#6b592d,#253e34)",
    "color:#fff4cf", "touch-action:manipulation",
    "overflow-wrap:anywhere", "@media(max-width:359px)",
    "@media(min-width:360px)",
):
    assert need in PATCH,need
for forbidden in (
    "localStorage.", "saveProgress(", "P.gems", "P.squad",
    "P.questClears", "S.", "window.", "document.",
    "confirm(", "fetch(", "XMLHttpRequest(", "onclick=",
    "visibility:hidden", "display:none", "pointer-events:none",
):
    assert forbidden not in PATCH,forbidden
for element in ("quarantineexport","recoverycontinue","downloadsave","wipesave","undosave"):
    assert ('id="'+element+'"') in HTML,element
assert "test_bf_recovery_backup_hierarchy_v26400.py --source-only" in PRE
assert WF.count("python3 test_bf_recovery_backup_hierarchy_v26400.py")==1
assert "android.permission.INTERNET" not in MAN
assert len(CSS.encode("utf8")) < 128*1024
assert len(NAV.encode("utf8")) < 128*1024
print("PASS v264 source: original save control IDs, CSS-only styling and registration")
if "--source-only" in sys.argv[1:]:
    raise SystemExit(0)

import shutil
from playwright.sync_api import sync_playwright
chrome=(shutil.which("chromium") or shutil.which("google-chrome") or
        shutil.which("google-chrome-stable"))
assert chrome,"Chromium required"
marker="\n})();"
bootstrap=marker.join(NAV.split(marker)[:2])+marker
fixture="""<!doctype html><html><head><meta charset="utf-8">
<style>
/* Reproduce real index.html layout flex rule, not just navigation stylesheet. */
.transferactions{display:flex;flex-wrap:wrap;gap:7px}
.transferactions button{flex:1 1 140px;min-height:36px}
#quarantineexport{min-height:36px}
</style></head><body><main class="wrap">
<section class="progresspanel panel">
<div id="savewarning" class="save-warning" role="alert">
<button id="quarantineexport" type="button">Download Unreadable Save Backup</button>
<button id="recoverycontinue" type="button">Continue with New Save</button>
</div>
<div class="progressactions transferactions">
<button id="downloadsave">Download Save File</button>
<button id="uploadsave">Import Save File</button>
<button id="exportsave">Show Save Code</button>
<button id="importsave">Import Pasted Code</button>
<button id="undosave">Undo Last Import</button>
<button id="wipesave">New Save</button>
</div></section>
<section class="squadsetup">Units</section>
<section class="questpanel"><div id="questlist">Quests</div></section>
<section class="summonpanel">Summon</section>
</main></body></html>"""
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path=chrome,
                              args=["--no-sandbox","--disable-dev-shm-usage"])
    for width in (320,359,360,393,412,540):
        page=browser.new_page(viewport={"width":width,"height":760})
        errors=[]
        page.on("pageerror",lambda err:errors.append(str(err)))
        page.set_content(fixture)
        page.add_style_tag(content=CSS)
        page.add_script_tag(content=bootstrap)
        page.locator('.bf-navbar button[data-bf-goto="menu"]').click()
        dl=page.locator("#downloadsave")
        recovery=page.locator("#quarantineexport")
        dangerous=page.locator("#wipesave")
        assert dl.is_visible() and recovery.is_visible() and dangerous.is_visible(),width
        for button in (dl,recovery,dangerous):
            m=button.evaluate("""e=>{
              const c=getComputedStyle(e),r=e.getBoundingClientRect();
              return {height:r.height,left:r.left,right:r.right,
                color:c.color,border:c.borderTopColor,
                minHeight:parseFloat(c.minHeight),background:c.backgroundImage,
                wrap:c.whiteSpace}
            }""")
            assert m["height"]>=48 and m["left"]>=-1 and m["right"]<=width+1,(width,m)
            assert m["wrap"]=="normal",(width,m)
        assert dl.evaluate("e=>getComputedStyle(e).backgroundImage")==recovery.evaluate(
            "e=>getComputedStyle(e).backgroundImage"),width
        assert dl.evaluate("e=>getComputedStyle(e).backgroundImage")!=dangerous.evaluate(
            "e=>getComputedStyle(e).backgroundImage"),width
        if width<=359:
            assert recovery.evaluate("e=>e.getBoundingClientRect().height")>=50,width
            assert page.locator(".transferactions").evaluate(
                "e=>getComputedStyle(e).gridTemplateColumns.trim().split(/\\s+/).length")==1,width
        else:
            # New Save must be on its own flex row, not beside Undo Last Import.
            wipe=dangerous.bounding_box()
            undo=page.locator("#undosave").bounding_box()
            assert wipe and undo and wipe["y"]>=undo["y"]+undo["height"]+7,(width,wipe,undo)
            assert dangerous.evaluate("e=>getComputedStyle(e).flexBasis")=="100%",width
        page.keyboard.press("Tab")
        recovery.focus()
        assert recovery.evaluate("e=>e.matches(':focus-visible')"),width
        assert recovery.evaluate("e=>getComputedStyle(e).outlineStyle")!="none",width
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"),width
        page.locator('.bf-navbar button[data-bf-goto="home"]').click()
        assert recovery.is_hidden() and dangerous.is_hidden(),width
        assert page.locator("#bf-home").is_visible(),width
        assert not errors,(width,errors)
        page.close()
    browser.close()
print("PASS v264 Chromium: recovery backup touch/contrast distinction and separate reset row")
