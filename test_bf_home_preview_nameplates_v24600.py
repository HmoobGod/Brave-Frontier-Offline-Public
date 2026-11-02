"""v246: visible names on recovered original Global Home location previews.

Presentation-only; do not enable unavailable routes or change original image
bytes, saves, gameplay, economy, Android code or resource loader limits.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
J = (ASSETS / "bf_home_nav.js").read_text("utf8")
C = (ASSETS / "bf_home_nav.css").read_text("utf8")
WF = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf8")
PRE = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
MAN = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf8")
HOME = J.split("/* Build #9: original Global home location hub", 1)[1].split(
    "/* Build #11 - recovered BF1 Global artwork", 1)[0]

PLACES = (
    ("Vortex Gate", "VORTEX GATE", "home_win_gate.png"),
    ("Arena", "ARENA", "home_win_arena.png"),
    ("Raid Battle", "RAID BATTLE", "home_win_raid_open.png"),
    ("Capital Randall", "CAPITAL RANDALL", "home_win_randall.png"),
)
for name, visible, sprite in PLACES:
    assert f'aria-label="{name} not implemented" aria-disabled="true"' in HOME
    assert f'<strong class="bf-scene-location-name" aria-hidden="true">{visible}</strong>' in HOME
    assert sprite in HOME
assert HOME.count('class="bf-scene-location-name" aria-hidden="true"') == 4
assert HOME.count('class="bf-scene-place bf-scene-locked"') == 4
assert HOME.count('<span class="bf-scene-status">NOT YET AVAILABLE</span>') == 4
assert HOME.count('class="bf-scene-place bf-scene-active bf-scene-featured"') == 2
assert "/* v246: readable nameplates" in C
assert re.search(r"\.bf-scene-places \.bf-scene-locked \.bf-scene-location-name\s*\{[^}]*font:900 11px/1\.2", C)
assert not any(x in HOME for x in (
    "localStorage.setItem(", "saveProgress(", "awardDemoRewards(",
    "P.questClears =", "P.squad ="
))
assert "android.permission.INTERNET" not in MAN
assert len(J.encode("utf8")) <= 128 * 1024
assert len(C.encode("utf8")) <= 128 * 1024
assert WF.count("python3 test_bf_home_preview_nameplates_v24600.py") == 1
assert PRE.count("test_bf_home_preview_nameplates_v24600.py") == 2
print("PASS v246 source: all four original Global previews visibly named, no route/save changes")
if "--source-only" in sys.argv:
    raise SystemExit(0)

import shutil
from playwright.sync_api import sync_playwright

chrome = shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "Chromium required for v246 browser verification"
marker = "\n})();"
bootstrap = marker.join(J.split(marker)[:2]) + marker
html = """<!doctype html><html><head><meta charset="utf-8"></head><body>
<main class="wrap"><section class="progresspanel">Saves</section>
<section class="questpanel">Quest</section><section class="squadsetup">Units</section>
<section class="summonpanel">Summon</section></main></body></html>"""

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=chrome,
        args=["--no-sandbox", "--disable-dev-shm-usage"])
    for width in (320, 360, 393, 412, 540):
        page = browser.new_page(viewport={"width": width, "height": 760})
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.set_content(html)
        page.add_style_tag(content=C)
        page.add_script_tag(content=bootstrap)
        locked = page.locator(".bf-scene-places .bf-scene-locked")
        assert locked.count() == 4, (width, locked.count())
        for index, (name, visible, sprite) in enumerate(PLACES):
            card = locked.nth(index)
            assert card.get_attribute("aria-label") == name + " not implemented"
            assert card.get_attribute("aria-disabled") == "true"
            assert card.locator("button, a[href], [tabindex]").count() == 0
            label = card.locator(".bf-scene-location-name")
            assert label.count() == 1
            assert label.inner_text() == visible
            assert label.get_attribute("aria-hidden") == "true"
            assert sprite in card.locator("img").get_attribute("src")
            assert card.locator(".bf-scene-status").inner_text() == "NOT YET AVAILABLE"
            geom = card.evaluate("""el => ({
                height: el.scrollHeight, client: el.clientHeight,
                labelSize: parseFloat(getComputedStyle(el.querySelector('.bf-scene-location-name')).fontSize)
            })""")
            assert geom["height"] <= geom["client"] + 2, (width, name, geom)
            assert geom["labelSize"] >= 10, (width, name, geom)
        grid = page.locator(".bf-scene-places").evaluate(
            "(el)=>({scroll:el.scrollWidth,client:el.clientWidth})")
        assert grid["scroll"] <= grid["client"] + 2, (width, grid)
        assert page.locator(".bf-scene-places button").count() == 2
        page.locator('.bf-scene-featured[data-bf-goto="quest"]').click()
        assert page.evaluate("BF_homeNav.current") == "quest"
        page.locator('.bf-navbar button[data-bf-goto="home"]').click()
        page.locator('.bf-scene-featured[data-bf-goto="summon"]').click()
        assert page.evaluate("BF_homeNav.current") == "summon"
        assert not errors, (width, errors)
        page.close()
    browser.close()
print("PASS v246 browser: original Global nameplates legible, locked and noninteractive at five widths")
