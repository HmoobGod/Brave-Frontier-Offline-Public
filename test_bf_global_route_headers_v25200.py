"""v252: actual original-art route header/accessibility and mobile UI regression.

Non-Home route presentation only; no gameplay, save, reward, signing or
original source artwork changes. Full browser test runs in signed APK CI.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
A = ROOT / "app/src/main/assets"
J = (A / "bf_home_nav.js").read_text("utf8")
C = (A / "bf_home_nav.css").read_text("utf8")
WF = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf8")
PRE = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
MAN = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf8")
PREFIX = J.split("/* Build #9: original Global home location hub", 1)[0]
HEADER = PREFIX.split("  const heading = document.createElement('div');", 1)[1].split(
    "  home.insertAdjacentElement('afterend', heading);", 1
)[0]
assert "heading.setAttribute('role', 'heading');" in HEADER
assert "heading.setAttribute('aria-level', '1');" in HEADER
assert "heading.setAttribute('aria-live', 'polite');" in HEADER
assert "heading.hidden = true;" in HEADER
assert "heading.textContent = names[route];" in PREFIX
assert "heading.hidden = route === 'home';" in PREFIX
assert "/* v252 UI focus:" in C
assert "body.bf-menu-mode .bf-route-title:not([hidden])" in C
assert "content/battle/battle_dungeon_name_deco.png" in C
assert (A / "content/battle/battle_dungeon_name_deco.png").is_file()
assert "aria-current','page'" in PREFIX
assert "test_bf_global_route_headers_v25200.py --source-only" in PRE
assert WF.count("python3 test_bf_global_route_headers_v25200.py") == 1
assert "android.permission.INTERNET" not in MAN
assert 0 < len(J.encode("utf8")) < 128 * 1024
assert 0 < len(C.encode("utf8")) < 128 * 1024
assert not any(token in HEADER for token in (
    "saveProgress(", "localStorage.", "P.gems", "P.questClears",
    "awardDemoRewards(", "fetch(", "XMLHttpRequest("
))
print("PASS v252 source: original art route headers, 128KiB resource limits, no save writes")
if "--source-only" in sys.argv:
    raise SystemExit(0)

import shutil
from playwright.sync_api import sync_playwright

chrome = shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "Chromium required for v252 route header verification"
marker = "\n})();"
bootstrap = marker.join(J.split(marker)[:2]) + marker
html = """<!doctype html><html><head><meta charset="utf-8"></head><body>
<main class="wrap"><section class="progresspanel">Saves</section>
<section class="questpanel">Quests</section>
<section class="squadsetup">Units</section>
<section class="summonpanel">Summons</section></main></body></html>"""
routes = {
    "units": "UNITS · SQUAD",
    "quest": "QUEST · BATTLE",
    "summon": "SUMMON GATE · DEMO",
    "menu": "MENU · SAVES",
}
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=chrome, args=[
        "--no-sandbox", "--disable-dev-shm-usage"
    ])
    for width in (320, 360, 393, 412, 540):
        page = browser.new_page(viewport={"width":width,"height":760})
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.set_content(html)
        page.add_style_tag(content=C)
        page.add_script_tag(content=bootstrap)
        title = page.locator("#bf-route-title")
        assert title.get_attribute("role") == "heading"
        assert title.get_attribute("aria-level") == "1"
        assert title.get_attribute("aria-live") == "polite"
        assert title.is_hidden(), width
        for route, expected in routes.items():
            page.locator(f'.bf-navbar button[data-bf-goto="{route}"]').click()
            assert title.is_visible(), (width, route)
            assert title.inner_text() == expected, (width, route)
            assert page.locator(f'.bf-navbar button[data-bf-goto="{route}"]').get_attribute("aria-current") == "page"
            computed = title.evaluate("""e=>{
              const c=getComputedStyle(e),r=e.getBoundingClientRect();
              return {display:c.display,fontSize:parseFloat(c.fontSize),
                minHeight:parseFloat(c.minHeight),left:r.left,right:r.right,
                art:c.backgroundImage.includes('battle_dungeon_name_deco.png')}
            }""")
            assert computed["art"], (width,route,computed)
            assert computed["fontSize"] >= 14, (width,route,computed)
            assert computed["minHeight"] >= 49, (width,route,computed)
            assert computed["left"] >= -1 and computed["right"] <= width+1, (width,route,computed)
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), (width,route)
        page.locator('.bf-navbar button[data-bf-goto="home"]').click()
        assert title.is_hidden() and page.locator("#bf-home").is_visible(), width
        assert not errors, (width,errors)
        page.close()
    browser.close()
print("PASS v252 browser: visible original-art route headings and safe navigation at five phone widths")
