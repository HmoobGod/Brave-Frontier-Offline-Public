"""v249: consolidated original Global Home UI release-readiness regression.

Pre-v250 source and browser verification only. No APK installation/device sign-off;
no modifications to gameplay, network, signing, rewards, v7 save or Current.
"""
from pathlib import Path
import sys
import re

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
J = (ASSETS / "bf_home_nav.js").read_text("utf8")
C = (ASSETS / "bf_home_nav.css").read_text("utf8")
WF = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf8")
PRE = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
MAN = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf8")
HOME = J.split("/* Build #9: original Global home location hub", 1)[1].split(
    "/* Build #11 - recovered BF1 Global artwork", 1)[0]
PREVIEWS = (
    ("Vortex Gate", "VORTEX GATE", "home_win_gate.png"),
    ("Arena", "ARENA", "home_win_arena.png"),
    ("Raid Battle", "RAID BATTLE", "home_win_raid_open.png"),
    ("Capital Randall", "CAPITAL RANDALL", "home_win_randall.png"),
)
assert HOME.count('role="heading" aria-level="1"') == 1
assert HOME.count('role="heading" aria-level="2"') == 3
assert HOME.count('role="heading" aria-level="3"') == 2
assert HOME.count('class="bf-scene-place bf-scene-active bf-scene-featured"') == 2
assert HOME.count('class="bf-scene-place bf-scene-locked"') == 4
assert HOME.count('<span class="bf-scene-status">NOT YET AVAILABLE</span>') == 4
assert HOME.count('class="bf-scene-location-name" aria-hidden="true"') == 4
for name, visible, filename in PREVIEWS:
    assert f'aria-label="{name} not implemented" aria-disabled="true"' in HOME
    assert f'<strong class="bf-scene-location-name" aria-hidden="true">{visible}</strong>' in HOME
    assert filename in HOME
for marker in ("/* v247: preserve original Home shortcut sprites",
               "/* v248: original six-unit Home squad preview"):
    assert marker in C
assert WF.count("python3 test_bf_home_ui_release_readiness_v24900.py") == 1
assert PRE.count("test_bf_home_ui_release_readiness_v24900.py") == 2
assert not any(term in HOME for term in (
    "localStorage.setItem(", "saveProgress(", "awardDemoRewards(", "P.squad =",
    "P.questClears ="
))
assert "android.permission.INTERNET" not in MAN
assert 0 < len(J.encode("utf8")) <= 128 * 1024
assert 0 < len(C.encode("utf8")) <= 128 * 1024
print("PASS v249 source: UI-only release readiness, 6 headings, 4 locked previews, asset budgets and routing")
if "--source-only" in sys.argv:
    raise SystemExit(0)

import shutil
from playwright.sync_api import sync_playwright

chrome = shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "Chromium required for v249 release-readiness browser checks"
marker = "\n})();"
bootstrap = marker.join(J.split(marker)[:2]) + marker
html = """<!doctype html><html><head><meta charset="utf-8"></head><body>
<main class="wrap"><section class="progresspanel">Saves</section>
<section class="questpanel">Quests</section>
<section class="squadsetup">Units</section>
<section class="summonpanel">Summon</section></main></body></html>"""

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=chrome,
        args=["--no-sandbox", "--disable-dev-shm-usage"])
    for width in (320, 360, 393, 412, 540):
        page = browser.new_page(viewport={"width": width, "height": 760})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content(html)
        page.add_style_tag(content=C)
        page.add_script_tag(content=bootstrap)

        headings = page.locator("#bf-home [role=heading]").evaluate_all(
            "(nodes) => nodes.map(n => [Number(n.getAttribute('aria-level')), n.textContent.trim()])")
        assert [level for level, _ in headings] == [1, 2, 2, 3, 3, 2], (width, headings)

        squad = page.locator("#bf-scene-party")
        assert squad.locator(".bf-scene-member").count() == 6
        assert squad.evaluate(
            "(el) => getComputedStyle(el).gridTemplateColumns.split(' ').length"
        ) == (3 if width <= 412 else 6), width

        shortcut = page.locator(".bf-scene-toolrow")
        assert shortcut.locator("button").count() == 4
        assert shortcut.evaluate(
            "(el) => getComputedStyle(el).gridTemplateColumns.split(' ').length"
        ) == (3 if width <= 412 else 5), width

        previews = page.locator(".bf-scene-places .bf-scene-locked")
        assert previews.count() == 4
        for index, (name, visible, image) in enumerate(PREVIEWS):
            card = previews.nth(index)
            assert card.get_attribute("aria-disabled") == "true"
            assert card.get_attribute("role") == "group"
            assert card.get_attribute("aria-label") == name + " not implemented"
            assert card.locator(".bf-scene-location-name").inner_text() == visible
            assert card.locator(".bf-scene-location-name").get_attribute("aria-hidden") == "true"
            assert card.locator(".bf-scene-status").inner_text() == "NOT YET AVAILABLE"
            assert image in card.locator("img").get_attribute("src")
            assert card.locator("button, a[href], [tabindex]").count() == 0

        exchange = page.locator(".bf-scene-tool-locked")
        assert exchange.get_attribute("aria-disabled") == "true"
        assert exchange.locator("button, a[href], [tabindex]").count() == 0
        assert page.locator(".bf-scene-places button").count() == 2
        for selector in ("#bf-scene-party", ".bf-scene-places", ".bf-scene-toolrow"):
            sizes = page.locator(selector).evaluate(
                "(el) => ({scroll:el.scrollWidth,client:el.clientWidth})")
            assert sizes["scroll"] <= sizes["client"] + 2, (width, selector, sizes)

        for selector, target in (
            ('.bf-scene-featured[data-bf-goto="quest"]', "quest"),
            ('.bf-scene-featured[data-bf-goto="summon"]', "summon"),
            ('.bf-scene-toolrow button[data-bf-goto="units"]:not([data-bf-open-box])', "units"),
            ('.bf-scene-toolrow button[data-bf-goto="menu"]', "menu"),
        ):
            assert page.locator(selector).count() == 1, (width, selector)
            page.locator(selector).click()
            assert page.evaluate("BF_homeNav.current") == target, (width, target)
            page.locator('.bf-navbar button[data-bf-goto="home"]').click()
        assert not errors, (width, errors)
        page.close()
    browser.close()
print("PASS v249 browser: complete original Home UI/route/locked-state matrix at five widths")
