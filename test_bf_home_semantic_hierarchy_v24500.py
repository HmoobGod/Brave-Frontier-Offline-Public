"""v245: original Global Home headings and unavailable-preview semantics.

Presentation-only patch. Validate real Home DOM semantics at small viewports
without changing application routes, save data, original art or rewards.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
J = (ASSETS / "bf_home_nav.js").read_text("utf8")
C = (ASSETS / "bf_home_nav.css").read_text("utf8")
MANIFEST = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf8")
WF = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf8")
PREFLIGHT = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
HOME = J.split("/* Build #9: original Global home location hub", 1)[1].split(
    "/* Build #11 - recovered BF1 Global artwork", 1)[0]
assert HOME.count('role="heading" aria-level="1"') == 1
assert HOME.count('role="heading" aria-level="2"') == 3
assert HOME.count('role="heading" aria-level="3"') == 2
for title in ("GRAND GAIA", "CURRENT SQUAD", "ADVENTURE", "HOME SHORTCUTS"):
    assert title in HOME
for name in ("Vortex Gate", "Arena", "Raid Battle", "Capital Randall"):
    assert 'aria-label="' + name + ' not implemented" aria-disabled="true"' in HOME
assert 'role="group" aria-label="Exchange Hall not implemented" aria-disabled="true"' in HOME
assert HOME.count('class="bf-scene-place bf-scene-active bf-scene-featured"') == 2
assert HOME.count('class="bf-scene-place bf-scene-locked"') == 4
assert not any(x in HOME for x in (
    "localStorage.setItem(", "saveProgress(", "awardDemoRewards(",
    "P.squad =", "P.questClears ="
))
assert "android.permission.INTERNET" not in MANIFEST
assert WF.count("python3 test_bf_home_semantic_hierarchy_v24500.py") == 1
assert PREFLIGHT.count("test_bf_home_semantic_hierarchy_v24500.py") == 2
assert 0 < len(J.encode("utf8")) <= 128 * 1024
print("PASS v245 source: Home headings 1/2/3, disabled previews, no routes/save code touched")
if "--source-only" in sys.argv:
    raise SystemExit(0)

import shutil
from playwright.sync_api import sync_playwright
chrome = shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "Chromium required for full v245 browser checks"
marker = "\n})();"
bootstrap = marker.join(J.split(marker)[:2]) + marker
html = """<!doctype html><html><head><meta charset="utf-8"></head><body>
<main class="wrap"><section class="progresspanel">Saves</section>
<section class="questpanel">Quests</section><section class="squadsetup">Units</section>
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
        headings = page.locator("#bf-home [role=heading]").evaluate_all(
            "(nodes) => nodes.map(n => [Number(n.getAttribute('aria-level')), n.textContent.trim()])")
        assert [level for level, _ in headings] == [1, 2, 2, 3, 3, 2], (width, headings)
        assert headings[0][1] == "GRAND GAIA", (width, headings)
        for name in ("Vortex Gate", "Arena", "Raid Battle", "Capital Randall"):
            item = page.locator(f'.bf-scene-locked[aria-label="{name} not implemented"]')
            assert item.count() == 1, (width, name)
            assert item.get_attribute("role") == "group"
            assert item.get_attribute("aria-disabled") == "true"
            assert item.locator("button, a[href]").count() == 0
        box = page.locator(".bf-scene-tool-locked")
        assert box.get_attribute("role") == "group"
        assert box.get_attribute("aria-disabled") == "true"
        assert page.locator(".bf-scene-places button").count() == 2
        page.locator('.bf-scene-featured[data-bf-goto="quest"]').click()
        assert page.evaluate("BF_homeNav.current") == "quest"
        page.locator('.bf-navbar button[data-bf-goto="home"]').click()
        page.locator('.bf-scene-featured[data-bf-goto="summon"]').click()
        assert page.evaluate("BF_homeNav.current") == "summon"
        assert not errors, (width, errors)
        page.close()
    browser.close()
print("PASS v245 browser: semantic headings, disabled previews and unchanged routes at 5 widths")
