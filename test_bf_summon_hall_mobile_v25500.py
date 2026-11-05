"""v255 archived Global Summoning Hall UI: responsive/readable and no gameplay changes."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
A = ROOT / "app/src/main/assets"
J = (A / "bf_home_nav.js").read_text("utf8")
C = (A / "bf_home_nav.css").read_text("utf8")
WF = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf8")
PRE = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
MAN = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf8")

assert J.count('role="heading" aria-level="2">SUMMONING HALL</strong>') == 1
assert "content/home/home_win_akras_smn_hall.png" in J
assert "Offline recruitment prototype" in J
assert "No original rates or gacha system are claimed." in J
assert "/* v255 UI:" in C
PATCH = C.split("/* v255 UI:",1)[1]
for text in (".summonpanel .bf-summon-archive-head",
             ".bf-summon-archive-head strong[role=\"heading\"]",
             "@media(max-width:359px)", "flex-direction:column",
             "overflow-wrap:anywhere", "object-fit:contain",
             "width:min(84%,240px)"):
    assert text in PATCH, text
for forbidden in ("localStorage.", "P.gems", "P.summon", "awardDemoRewards(",
                  "saveProgress(", "fetch(", "XMLHttpRequest(", "onclick"):
    assert forbidden not in PATCH, forbidden
assert "test_bf_summon_hall_mobile_v25500.py --source-only" in PRE
assert WF.count("python3 test_bf_summon_hall_mobile_v25500.py") == 1
assert "android.permission.INTERNET" not in MAN
assert len(J.encode("utf8")) < 128 * 1024
assert len(C.encode("utf8")) < 128 * 1024
print("PASS v255 source: archived summon banner, truthful offline labels, safe layout and CI registration")
if "--source-only" in sys.argv[1:]:
    raise SystemExit(0)

import shutil
from playwright.sync_api import sync_playwright
chrome = shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "Chromium required for v255 Summon screen UI review"
marker = "\n})();"
bootstrap = marker.join(J.split(marker)[:2]) + marker
fixture = """<!doctype html><html><head><meta charset="utf-8"></head><body>
<main class="wrap">
<section class="progresspanel">Saves</section>
<section class="squadsetup">Units</section>
<section class="questpanel">Quest</section>
<section class="summonpanel">
<div class="bf-summon-archive-head">
<img src="content/home/home_win_akras_smn_hall.png" alt="Akras Summoning Hall" />
<div><strong role="heading" aria-level="2">SUMMONING HALL</strong>
<span>Offline recruitment prototype</span>
<small>Archived Global art. No original rates or gacha system are claimed.</small></div>
</div>
<button id="demo-summon" type="button">Demo recruit</button>
</section></main></body></html>"""
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=chrome,
                                 args=["--no-sandbox","--disable-dev-shm-usage"])
    for width in (320,359,360,393,412,540):
        page=browser.new_page(viewport={"width":width,"height":760})
        errors=[]
        page.on("pageerror",lambda error:errors.append(str(error)))
        page.set_content(fixture)
        page.add_style_tag(content=C)
        page.add_script_tag(content=bootstrap)
        page.locator('.bf-navbar button[data-bf-goto="summon"]').click()
        banner=page.locator(".summonpanel .bf-summon-archive-head")
        title=banner.locator('strong[role="heading"]')
        image=banner.locator("img")
        assert banner.is_visible(), width
        assert title.inner_text()=="SUMMONING HALL" and title.get_attribute("aria-level")=="2",width
        assert "Offline recruitment prototype" in banner.inner_text()
        assert "No original rates" in banner.inner_text()
        assert image.get_attribute("src")=="content/home/home_win_akras_smn_hall.png"
        layout=banner.evaluate("""e=>{
          const cs=getComputedStyle(e),rect=e.getBoundingClientRect();
          const label=e.querySelector('strong'),s=getComputedStyle(label);
          const image=e.querySelector('img').getBoundingClientRect();
          return {direction:cs.flexDirection,left:rect.left,right:rect.right,
            font:parseFloat(s.fontSize),imgHeight:image.height,imgRight:image.right}
        }""")
        assert layout["direction"]==("column" if width<=359 else "row"),(width,layout)
        assert layout["font"]>=15,(width,layout)
        assert layout["imgHeight"]>=90,(width,layout)
        assert layout["left"]>=-1 and layout["right"]<=width+1,(width,layout)
        assert layout["imgRight"]<=width+1,(width,layout)
        assert page.locator("#demo-summon").is_visible(),width
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth+1"),width
        page.locator('.bf-navbar button[data-bf-goto="home"]').click()
        assert banner.is_hidden(),width
        assert page.locator("#bf-home").is_visible(),width
        assert not errors,(width,errors)
        page.close()
    browser.close()
print("PASS v255 browser: authentic archived Summon banner and offline labels at six mobile widths")
