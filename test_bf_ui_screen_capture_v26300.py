"""v263 — deterministic, navigation-shell screenshot evidence for UI review.

Never touches Android or owner storage. Chromium loads only the checked-out
repository's prepared assets and a fresh, empty profile. The navigation shell
is a subset of Android's additional injected modules, not full APK parity.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
NAV = (ASSETS / "bf_home_nav.js").read_text("utf8")
CSS = (ASSETS / "bf_home_nav.css").read_text("utf8")
WF = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf8")
PRE = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
MAN = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf8")
DOC = (ROOT / "V263_UI_SCREEN_CAPTURE_EVIDENCE.md").read_text("utf8")
OUTPUT = ROOT / "source_audit_reports/v263_ui_screen_capture"

assert "window.BF_homeNav = {go,get current()" in NAV
assert "/* v262 battle tactical focus/status mobile controls" in CSS
assert "test_bf_ui_screen_capture_v26300.py --source-only" in PRE
assert WF.count("python3 test_bf_ui_screen_capture_v26300.py --capture") == 1
assert WF.count("python3 test_bf_ui_screen_capture_v26300.py --source-only") == 0
assert "BraveFrontier-v263-navigation-screen-receipts" in WF
assert "source_audit_reports/v263_ui_screen_capture/" in WF
assert "navigation-only Chromium" in DOC
assert "android.permission.INTERNET" not in MAN
assert len(NAV.encode("utf8")) < 128*1024
assert len(CSS.encode("utf8")) < 128*1024
SCREENS = (
    ("home", "#bf-home"),
    ("units", "#squadpicker"),
    ("quest", "#questlist"),
    ("summon", "#summonbutton"),
    ("menu", "#downloadsave"),
)
assert len({s for s, _ in SCREENS}) == 5
print("PASS v263 source: navigation screenshot evidence registration and no app changes")
if "--source-only" in sys.argv:
    raise SystemExit(0)
assert "--capture" in sys.argv, "Explicit --capture required; no silent screenshot action"

import hashlib
import json
import mimetypes
import shutil
from urllib.parse import urlsplit, unquote
from playwright.sync_api import sync_playwright

assert (ASSETS / "index.html").is_file(), "Packaged index source not found"
chrome = (shutil.which("chromium") or shutil.which("google-chrome") or
          shutil.which("google-chrome-stable"))
assert chrome, "Chromium required for capture receipts"
OUTPUT.mkdir(parents=True, exist_ok=True)

# All URLs are intercepted; there is no external network or personal storage.
BASE = "https://bf-v263-local.test/"
blocked = set()
missing = set()

def serve(route):
    address = urlsplit(route.request.url)
    if address.scheme != "https" or address.hostname != "bf-v263-local.test":
        blocked.add(address.hostname or address.scheme)
        route.abort()
        return
    relative = unquote(address.path).lstrip("/") or "index.html"
    parts = Path(relative).parts
    if ".." in parts or relative.startswith(".") or "\\" in relative:
        blocked.add("path traversal")
        route.abort()
        return
    item = ASSETS.joinpath(*parts)
    if not item.is_file() or not item.resolve().is_relative_to(ASSETS.resolve()):
        missing.add(relative)
        route.abort()
        return
    content_type = mimetypes.guess_type(str(item))[0] or "application/octet-stream"
    route.fulfill(status=200, content_type=content_type, body=item.read_bytes())

receipts = []
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=chrome,
                                 args=["--no-sandbox", "--disable-dev-shm-usage"])
    for width, height in ((320, 740), (393, 852)):
        # New isolated context per viewport; no owner save or browser profile.
        context = browser.new_context(
            viewport={"width": width, "height": height}, device_scale_factor=2,
            service_workers="block", accept_downloads=False,
            reduced_motion="reduce", color_scheme="dark",
        )
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("dialog", lambda dialog: dialog.dismiss())
        page.route("**/*", serve)
        page.goto(BASE + "index.html", wait_until="load", timeout=90000)
        page.add_style_tag(path=str(ASSETS / "bf_home_nav.css"))
        page.add_script_tag(path=str(ASSETS / "bf_home_nav.js"))
        page.locator("#bf-home").wait_for(state="visible", timeout=15000)
        assert page.locator(".bf-navbar button").count() == 5
        initial = page.evaluate("""() => ({
            squad: JSON.stringify(P.squad), zel: P.zel, gems: P.gems,
            save: localStorage.getItem('bf_global_offline_demo_v7')
        })""")
        assert initial["save"] is None, "Capture profile must start with no v7 save"
        for screen, selector in SCREENS:
            page.locator(f'.bf-navbar button[data-bf-goto="{screen}"]').click()
            page.locator(selector).wait_for(state="visible", timeout=12000)
            assert page.evaluate("BF_homeNav.current") == screen
            assert page.locator('.bf-navbar button[aria-current="page"]').count() == 1
            page.evaluate("window.scrollTo({top:0,left:0,behavior:'instant'})")
            page.wait_for_timeout(120)
            bounds = page.evaluate("""() => ({
                width:innerWidth,
                scrollWidth:document.documentElement.scrollWidth,
                active:document.activeElement?.tagName || null
            })""")
            filename = f"{width}x{height}-{screen}.png"
            path = OUTPUT / filename
            page.screenshot(path=str(path), full_page=False,
                            animations="disabled", caret="hide", timeout=15000)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            current = page.evaluate("""() => ({
                squad: JSON.stringify(P.squad), zel:P.zel, gems:P.gems,
                save:localStorage.getItem('bf_global_offline_demo_v7')
            })""")
            assert current == initial, (width, screen, "Navigation changed demo state")
            assert bounds["scrollWidth"] <= width + 2, (width, screen, bounds)
            receipts.append({
                "screen": screen,
                "viewport": [width, height], "deviceScaleFactor": 2,
                "file": filename, "sha256": digest,
                "bytes": path.stat().st_size,
                "documentScrollWidth": bounds["scrollWidth"],
                "navigatorCurrent": screen,
                "saveUnchanged": True,
            })
        assert not errors, (width, errors)
        context.close()
    browser.close()

# Receipts are review artifacts, not authoritative original 2022 screenshots.
assert not blocked, f"Unexpected external requests: {sorted(blocked)[:10]}"
data = {
    "version": "v263",
    "captureScope": "navigation-shell-only, source-served Chromium; not full Android module injection",
    "historical2022Parity": "NOT TESTED",
    "ownerDevice": "NOT TESTED",
    "personalSaveLoaded": False,
    "originalArt": "repository-prepared asset references; no original screenshot comparison",
    "routes": 5,
    "viewports": [[320, 740], [393, 852]],
    "screenshots": receipts,
    "missingAssetRequests": sorted(missing)[:100],
    "missingAssetCount": len(missing),
    "externalRequestsBlocked": sorted(blocked),
}
receipt = OUTPUT / "capture-manifest.json"
receipt.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf8")
assert len(receipts) == 10, len(receipts)
print("PASS v263 capture: 10 navigation-only PNG receipts, 5 routes, 2 phone widths, v7 isolation")
print("WARN v263: screenshots do not certify native Android screenshots or 2022 Global layout parity")
