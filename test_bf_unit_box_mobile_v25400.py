"""v254 Unit Box cards: CSS-only UI review, 320–540px and source safety."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
A = ROOT / "app/src/main/assets"
J = (A / "bf_home_nav.js").read_text("utf8")
C = (A / "bf_home_nav.css").read_text("utf8")
WF = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf8")
PRE = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
MAN = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf8")
MARKER = "/* v254 UI-only:"
assert MARKER in C
PATCH = C.split(MARKER,1)[1]
for token in (".bf-owned-box .bf-box-card", ".bf-box-card strong",
              "-webkit-line-clamp:2", "white-space:normal",
              "overflow-wrap:anywhere", '.bf-box-card[aria-pressed="true"]',
              ".bf-box-card:focus-visible", "max-width:100%",
              "grid-template-columns:repeat(2,minmax(0,1fr))",
              "touch-action:manipulation"):
    assert token in PATCH, token
assert "unitBox.className = 'bf-owned-box'" in J
assert "className='bf-box-card'" in J
assert "test_bf_unit_box_mobile_v25400.py --source-only" in PRE
assert WF.count("python3 test_bf_unit_box_mobile_v25400.py") == 1
assert "android.permission.INTERNET" not in MAN
assert len(J.encode("utf8")) < 128*1024
assert len(C.encode("utf8")) < 128*1024
for forbidden in ("localStorage.", "saveProgress(", "P.squad", "P.unitExp",
                  "P.gems", "fetch(", "XMLHttpRequest(", "importSave"):
    assert forbidden not in PATCH, forbidden
print("PASS v254 source: Unit Box long-name, responsive/focus/selection UI only; no game/save writes")
if "--source-only" in sys.argv[1:]:
    raise SystemExit(0)

import shutil
from playwright.sync_api import sync_playwright
browser_path = shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert browser_path, "Chromium needed for v254 Unit Box responsive tests"
closing = "\n})();"
bootstrap = closing.join(J.split(closing)[:2]) + closing
fixture = """<!doctype html><html><head><meta charset="utf-8"></head><body>
<main class="wrap">
<section class="progresspanel">Saves</section>
<section class="questpanel">Quest</section>
<section class="summonpanel">Summon</section>
<section class="squadsetup" data-bf-unit-tab="box">
<section id="bf-owned-box" class="bf-owned-box">
<div id="bf-box-results" class="bf-box-results">
<button type="button" class="bf-box-card" id="u1" aria-pressed="false"><img alt="" /><strong>Original Global Unit with an Extremely Long Name</strong><span>★7 · Lv.100</span><small>RESERVE</small></button>
<button type="button" class="bf-box-card" id="u2" aria-pressed="true"><img alt="" /><strong>Selected Owned Unit</strong><span>★6 · Lv.99</span><small>ACTIVE</small></button>
<button type="button" class="bf-box-card" id="u3" aria-pressed="false"><img alt="" /><strong>Third Unit</strong><span>★5 · Lv.55</span><small>RESERVE</small></button>
</div>
<section id="bf-box-detail" class="bf-box-detail" aria-label="Unit details">Archived unit detail and original stats</section>
</section></section></main></body></html>"""
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=browser_path,
                                 args=["--no-sandbox","--disable-dev-shm-usage"])
    for width in (320,359,360,393,412,540):
        page = browser.new_page(viewport={"width":width,"height":760})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.set_content(fixture)
        page.add_style_tag(content=C)
        page.add_script_tag(content=bootstrap)
        page.locator('.bf-navbar button[data-bf-goto="units"]').click()
        card=page.locator("#u1")
        selected=page.locator("#u2")
        assert card.is_visible() and selected.is_visible(),width
        grid=page.locator("#bf-box-results")
        columns=grid.evaluate("e=>getComputedStyle(e).gridTemplateColumns.trim().split(/\\s+/).length")
        assert columns == (2 if width<=359 else 4 if width>=520 else 3),(width,columns)
        text=card.locator("strong").evaluate("""e=>{const c=getComputedStyle(e);return{
             white:c.whiteSpace,wrap:c.overflowWrap,clamp:c.webkitLineClamp,
             height:e.getBoundingClientRect().height
        }}""")
        assert text["white"]=="normal" and text["wrap"]=="anywhere", (width,text)
        assert text["clamp"]=="2" and text["height"]>0, (width,text)
        for item in (card,selected):
            rect=item.evaluate("""e=>{const r=e.getBoundingClientRect();return{
              left:r.left,right:r.right,height:r.height}}""")
            assert rect["height"]>=146, (width,rect)
            assert rect["left"]>=-1 and rect["right"]<=width+1, (width,rect)
        assert selected.get_attribute("aria-pressed")=="true"
        assert card.get_attribute("aria-pressed")=="false"
        pressed=selected.evaluate("e=>getComputedStyle(e).borderTopColor")
        unpressed=card.evaluate("e=>getComputedStyle(e).borderTopColor")
        assert pressed != unpressed,(width,pressed,unpressed)
        page.keyboard.press("Tab")
        card.focus()
        assert card.evaluate("e=>e.matches(':focus-visible')"),width
        assert card.evaluate("e=>getComputedStyle(e).outlineStyle")!="none",width
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth+1"), width
        page.locator('.bf-navbar button[data-bf-goto="home"]').click()
        assert card.is_hidden(),width
        assert page.locator("#bf-home").is_visible(),width
        assert not errors,(width,errors)
        page.close()
    browser.close()
print("PASS v254 Chromium: responsive Unit Box columns, card wrapping, active state, keyboard focus and safe routing")
