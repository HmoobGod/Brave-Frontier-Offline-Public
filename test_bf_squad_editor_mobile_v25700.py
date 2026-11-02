"""v257 UI-only squad-editor readability; source and phone viewport checks."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/"app/src/main/assets"
CSS=(ASSETS/"bf_home_nav.css").read_text("utf8")
JS=(ASSETS/"bf_home_nav.js").read_text("utf8")
PRE=(ROOT/".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
WF=(ROOT/".github/workflows/build-debug-apk.yml").read_text("utf8")
MAN=(ROOT/"app/src/main/AndroidManifest.xml").read_text("utf8")
MARKER="/* v257 UI-only:"
assert CSS.count(MARKER)==1
PATCH=CSS.split(MARKER,1)[1]
for token in (".squadsetup .squadpicker .squadpick", ".squadpick strong",
              ".squadpick small", "overflow-wrap:anywhere",
              "white-space:normal", "min-height:100px",
              "min-height:85px", "@media(max-width:359px)",
              "grid-template-columns:minmax(0,1fr)",
              "@media(min-width:520px)",
              "grid-template-columns:repeat(2,minmax(0,1fr))",
              "touch-action:manipulation", ":focus-within"):
    assert token in PATCH,token
for forbidden in ("localStorage.", "P.squad", "saveProgress(",
                  "fetch(", "XMLHttpRequest(", "document.", "onclick"):
    assert forbidden not in PATCH,forbidden
assert "test_bf_squad_editor_mobile_v25700.py --source-only" in PRE
assert WF.count("python3 test_bf_squad_editor_mobile_v25700.py")==1
assert "android.permission.INTERNET" not in MAN
assert len(JS.encode("utf8"))<128*1024
assert len(CSS.encode("utf8"))<128*1024
print("PASS v257 source: UI-only squad picker typography and mobile spacing, no save/game edits")
if "--source-only" in sys.argv[1:]:
    raise SystemExit(0)

import shutil
from playwright.sync_api import sync_playwright
chrome=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "Chromium required for v257 responsive squad-editor test"
marker="\n})();"
bootstrap=marker.join(JS.split(marker)[:2])+marker
fixture="""<!doctype html><html><head><meta charset="utf-8"></head><body>
<main class="wrap">
<section class="progresspanel">Saves</section>
<section class="questpanel">Quests</section>
<section class="summonpanel">Summon</section>
<section class="squadsetup">
<div id="squadpicker" class="squadpicker">
<label class="squadpick picked"><input type="checkbox" checked/><img alt="" />
<span><strong>Original Global Fencer Character with Long Name</strong><small>Fire · ★2 · Demo Lv.1 · Original cap Lv.30 · Original cost 2 · 1030 source base HP</small></span></label>
<label class="squadpick unowned"><input type="checkbox" disabled/><img alt="" />
<span><strong>Locked Archived Unit</strong><small>Not owned · Dark · ★2 · Original HP 1500</small></span></label>
<label class="squadpick picked"><input type="checkbox" checked/><img alt="" />
<span><strong>Another Long Original Global Character Name</strong><small>Earth · ★2 · Original cap Lv.30</small></span></label>
</div></section></main></body></html>"""
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True, executable_path=chrome,
                                args=["--no-sandbox","--disable-dev-shm-usage"])
    for width in (320,359,360,393,412,540):
        page=browser.new_page(viewport={"width":width,"height":760})
        errors=[]
        page.on("pageerror",lambda error:errors.append(str(error)))
        page.set_content(fixture)
        page.add_style_tag(content=CSS)
        page.add_script_tag(content=bootstrap)
        page.locator('.bf-navbar button[data-bf-goto="units"]').click()
        picker=page.locator("#squadpicker")
        cards=picker.locator(".squadpick")
        assert cards.count()==3 and cards.first.is_visible(),width
        columns=picker.evaluate("e=>getComputedStyle(e).gridTemplateColumns.trim().split(/\\s+/).length")
        assert columns==(1 if width<=359 else 2),(width,columns)
        for card in cards.all():
            v=card.evaluate("""e=>{
               const r=e.getBoundingClientRect();
               const s=getComputedStyle(e.querySelector('small'));
               const t=getComputedStyle(e.querySelector('strong'));
               return {left:r.left,right:r.right,height:r.height,
                 strongWhite:t.whiteSpace,smallWhite:s.whiteSpace,
                 wrap:s.overflowWrap,size:parseFloat(s.fontSize)}
            }""")
            assert v["height"] >= (85 if width<=359 else 100),(width,v)
            assert v["left"]>=-1 and v["right"]<=width+1,(width,v)
            assert v["strongWhite"]=="normal" and v["smallWhite"]=="normal",(width,v)
            assert v["wrap"]=="anywhere" and v["size"]>=10,(width,v)
        assert cards.nth(0).locator("input").is_checked(),width
        assert cards.nth(1).locator("input").is_disabled(),width
        page.keyboard.press("Tab")
        cards.nth(0).locator("input").focus()
        assert cards.nth(0).evaluate("e=>e.matches(':focus-within')"),width
        assert cards.nth(0).evaluate("e=>getComputedStyle(e).outlineStyle")!="none",width
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"),width
        page.locator('.bf-navbar button[data-bf-goto="home"]').click()
        assert cards.first.is_hidden() and page.locator("#bf-home").is_visible(),width
        assert not errors,(width,errors)
        page.close()
    browser.close()
print("PASS v257 Chromium: squad editor columns, text wrapping, focus, selection, no overflow")
