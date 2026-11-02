"""v247: original Global Home shortcut controls remain legible and operable.

CSS-only responsive patch; preserve original sprites, navigation, gameplay,
offline manifest, v7 saves, APK identity, and all unavailable preview states.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
A = ROOT / "app/src/main/assets"
CSS = (A / "bf_home_nav.css").read_text("utf8")
JS = (A / "bf_home_nav.js").read_text("utf8")
WF = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf8")
PRE = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
MAN = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf8")

assert "/* v247: preserve original Home shortcut sprites" in CSS
section = CSS.split("/* v247: preserve original Home shortcut sprites", 1)[1]
assert re.search(r"@media\s*\(max-width:412px\)\s*\{", section)
assert re.search(r"\.bf-scene-toolrow\s*\{\s*grid-template-columns:repeat\(3,minmax\(0,1fr\)\)", section)
assert re.search(r"\.bf-scene-toolrow>button,.bf-scene-toolrow>\.bf-scene-tool-locked\s*\{[^}]*min-height:96px", section)
assert re.search(r"\.bf-scene-toolrow img\s*\{\s*height:60px\s*\}", section)
assert not any(x in section for x in (
    "animation", "transition-duration", "localStorage", "saveProgress", "#battle",
    "visibility:hidden", "display:none", "pointer-events:none",
))
assert WF.count("python3 test_bf_home_shortcuts_mobile_v24700.py") == 1
assert PRE.count("test_bf_home_shortcuts_mobile_v24700.py") == 2
assert "android.permission.INTERNET" not in MAN
assert len(CSS.encode("utf8")) <= 128 * 1024
assert len(JS.encode("utf8")) <= 128 * 1024
home = JS.split("/* Build #9: original Global home location hub", 1)[1].split(
    "/* Build #11 - recovered BF1 Global artwork", 1)[0]
for label in ("QUESTS", "UNITS", "SAVES", "UNIT BOX", "EXCHANGE · LATER"):
    assert f"<span>{label}</span>" in home
assert home.count('class="bf-scene-tool-locked"') == 1
assert 'aria-label="Exchange Hall not implemented" aria-disabled="true"' in home
print("PASS v247 source: 3-column narrow shortcuts, source art, routes and save safety")
if "--source-only" in sys.argv:
    raise SystemExit(0)

import shutil
from playwright.sync_api import sync_playwright

chrome = shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "Chromium required for full v247 browser regression"
marker = "\n})();"
bootstrap = marker.join(JS.split(marker)[:2]) + marker
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
        page.add_style_tag(content=CSS)
        page.add_script_tag(content=bootstrap)
        shortcuts = page.locator(".bf-scene-toolrow")
        assert shortcuts.locator("button").count() == 4
        assert shortcuts.locator(".bf-scene-tool-locked").count() == 1
        grid = shortcuts.evaluate("""el => ({
            cols: getComputedStyle(el).gridTemplateColumns.split(' ').length,
            scroll: el.scrollWidth, client: el.clientWidth
        })""")
        assert grid["cols"] == (3 if width <= 412 else 5), (width, grid)
        assert grid["scroll"] <= grid["client"] + 2, (width, grid)
        for button in shortcuts.locator("button").all():
            metrics = button.evaluate("""el => ({
                width: el.getBoundingClientRect().width,
                height: el.getBoundingClientRect().height,
                label: parseFloat(getComputedStyle(el.querySelector('span')).fontSize),
                visible: getComputedStyle(el).visibility
            })""")
            assert metrics["width"] >= 44 and metrics["height"] >= 88, (width, metrics)
            assert metrics["label"] >= 10, (width, metrics)
            assert metrics["visible"] == "visible", (width, metrics)
        locked = shortcuts.locator(".bf-scene-tool-locked")
        assert locked.get_attribute("aria-disabled") == "true"
        assert locked.locator("button, a[href], [tabindex]").count() == 0
        page.locator('.bf-scene-toolrow button[data-bf-goto="quest"]').click()
        assert page.evaluate("BF_homeNav.current") == "quest"
        page.locator('.bf-navbar button[data-bf-goto="home"]').click()
        page.locator('.bf-scene-toolrow button[data-bf-goto="units"]').first.click()
        assert page.evaluate("BF_homeNav.current") == "units"
        page.locator('.bf-navbar button[data-bf-goto="home"]').click()
        page.locator('.bf-scene-toolrow button[data-bf-goto="menu"]').click()
        assert page.evaluate("BF_homeNav.current") == "menu"
        assert not errors, (width, errors)
        page.close()
    browser.close()
print("PASS v247 browser: accessible Home shortcut widths, labels and routes at 320–540px")
