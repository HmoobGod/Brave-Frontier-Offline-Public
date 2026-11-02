"""v256: Menu/Saves backup versus destructive reset visual safety, CSS only."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
A=ROOT/"app/src/main/assets"
C=(A/"bf_home_nav.css").read_text("utf8")
J=(A/"bf_home_nav.js").read_text("utf8")
WF=(ROOT/".github/workflows/build-debug-apk.yml").read_text("utf8")
PRE=(ROOT/".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
MAN=(ROOT/"app/src/main/AndroidManifest.xml").read_text("utf8")
MARKER="/* v256 UI safeguard:"
assert C.count(MARKER)==1
PATCH=C.split(MARKER,1)[1]
for required in (
  ".progresspanel .transferactions button",
  ".progresspanel .transferactions #downloadsave",
  ".progresspanel .transferactions #wipesave",
  ".progresspanel #recoverycontinue",
  "button:focus-visible",
  "min-height:48px",
  "min-height:50px",
  "@media(max-width:359px)",
  "grid-template-columns:minmax(0,1fr)",
  "touch-action:manipulation",
  "overflow-wrap:anywhere",
):
    assert required in PATCH,required
for prohibited in (
    "localStorage.", "saveProgress(", "P.gems", "P.squad",
    "wipesave.click", "document.", "fetch(", "XMLHttpRequest(",
):
    assert prohibited not in PATCH,prohibited
assert "test_bf_save_controls_mobile_v25600.py --source-only" in PRE
assert WF.count("python3 test_bf_save_controls_mobile_v25600.py")==1
assert "android.permission.INTERNET" not in MAN
assert len(C.encode("utf8")) < 128*1024
assert len(J.encode("utf8")) < 128*1024
print("PASS v256 source: CSS-only backup/destructive visual distinction; save handlers preserved")
if "--source-only" in sys.argv[1:]:
    raise SystemExit(0)

import shutil
from playwright.sync_api import sync_playwright
chrome=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome,"Chromium required for save controls mobile UI tests"
marker="\n})();"
bootstrap=marker.join(J.split(marker)[:2])+marker
fixture="""<!doctype html><html><head><meta charset="utf-8"></head><body>
<main class="wrap">
<section class="progresspanel">
<div id="savewarning" class="save-warning" role="alert">
<strong>Recovery notice</strong>
<button id="recoverycontinue" type="button">Continue with New Save</button></div>
<div class="progressactions transferactions">
<button id="downloadsave" type="button">Download Save File</button>
<button id="uploadsave" type="button">Import Save File</button>
<button id="exportsave" type="button">Show Save Code</button>
<button id="importsave" type="button">Import Pasted Code</button>
<button id="undosave" type="button">Undo Last Import</button>
<button id="wipesave" type="button">New Save</button>
</div></section>
<section class="squadsetup">Units</section>
<section class="questpanel">Quest</section>
<section class="summonpanel">Summon</section>
</main></body></html>"""
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=chrome,
                                args=["--no-sandbox","--disable-dev-shm-usage"])
    for width in (320,359,360,393,412,540):
        page=browser.new_page(viewport={"width":width,"height":760})
        errors=[]
        page.on("pageerror",lambda err:errors.append(str(err)))
        page.set_content(fixture)
        page.add_style_tag(content=C)
        page.add_script_tag(content=bootstrap)
        page.locator('.bf-navbar button[data-bf-goto="menu"]').click()
        export=page.locator("#downloadsave")
        reset=page.locator("#wipesave")
        recovery=page.locator("#recoverycontinue")
        assert export.is_visible() and reset.is_visible() and recovery.is_visible(),width
        assert export.inner_text()=="Download Save File"
        assert reset.inner_text()=="New Save"
        assert reset.get_attribute("onclick") is None
        for button in (export,reset,recovery):
            values=button.evaluate("""e=>{
              const c=getComputedStyle(e),r=e.getBoundingClientRect();
              return {height:r.height,left:r.left,right:r.right,wrap:c.whiteSpace,
                outline:c.outlineStyle,color:c.borderTopColor,minHeight:parseFloat(c.minHeight)}
            }""")
            assert values["height"]>=48 and values["minHeight"]>=48,(width,values)
            assert values["wrap"]=="normal",(width,values)
            assert values["left"]>=-1 and values["right"]<=width+1,(width,values)
        assert export.evaluate("e=>getComputedStyle(e).borderTopColor")!=reset.evaluate(
            "e=>getComputedStyle(e).borderTopColor"),width
        assert reset.evaluate("e=>getComputedStyle(e).borderTopColor")==recovery.evaluate(
            "e=>getComputedStyle(e).borderTopColor"),width
        if width<=359:
            assert page.locator(".transferactions").evaluate(
                "e=>getComputedStyle(e).gridTemplateColumns.split(/\\s+/).length")==1,width
        page.keyboard.press("Tab")
        reset.focus()
        assert reset.evaluate("e=>e.matches(':focus-visible')"),width
        assert reset.evaluate("e=>getComputedStyle(e).outlineStyle")!="none",width
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"),width
        page.locator('.bf-navbar button[data-bf-goto="home"]').click()
        assert reset.is_hidden() and page.locator("#bf-home").is_visible(),width
        assert not errors,(width,errors)
        page.close()
    browser.close()
print("PASS v256 browser: backup vs reset differentiation and responsive safe-save controls")
