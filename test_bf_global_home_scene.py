"""Browser smoke: Global-art hub, live squad preview, locked modes, and save safety.
Only this isolated browser profile is changed; never use a real Android save.
"""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        headless=True,
        executable_path=(shutil.which("google-chrome") or
                         shutil.which("google-chrome-stable") or
                         shutil.which("chromium")),
        args=["--no-sandbox", "--disable-dev-shm-usage"])
    page = browser.new_page(viewport={"width": 390, "height": 844})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    # Chromium's network/file navigation may be disabled by its sandbox.
    # Route original relative image requests to local verified PNGs with no network.
    def serve_asset(route):
        relative = route.request.url.split("bf-assets.test/", 1)[-1]
        asset = ASSETS / relative
        if asset.is_file() and asset.suffix == ".png" and asset.resolve().is_relative_to(ASSETS.resolve()):
            route.fulfill(status=200, body=asset.read_bytes(), content_type="image/png")
        else:
            route.fulfill(status=404, body=b"")
    page.route("http://bf-assets.test/**", serve_asset)
    page.evaluate("""() => {
      const store = {};
      Object.defineProperty(window, 'localStorage', {configurable:true,value:{
        getItem(k){return store[k] ?? null},
        setItem(k,v){store[k]=String(v)},
        removeItem(k){delete store[k]},
        key(i){return Object.keys(store)[i] ?? null},
        get length(){return Object.keys(store).length}
      }});
      window.alert = () => {};
      window.confirm = () => true;
    }""")
    html = (ASSETS / "index.html").read_text(encoding="utf-8")
    html = html.replace("<head>", '<head><base href="http://bf-assets.test/">', 1)
    page.set_content(html, wait_until="load", timeout=60000)
    before = page.evaluate("""() => ({
        save: localStorage.getItem('bf_global_offline_demo_v7'),
        squad: JSON.stringify(P.squad), zel: P.zel
    })""")
    page.add_style_tag(path=str(ASSETS / "bf_home_nav.css"))
    page.add_script_tag(path=str(ASSETS / "bf_home_nav.js"))
    assert page.evaluate("BF_homeNav.current") == "home"
    assert page.locator("#bf-scene-party .bf-scene-member").count() == 6
    assert page.locator("#bf-scene-party img").count() == 6
    actual = page.locator("#bf-scene-party strong").all_text_contents()
    expected = page.evaluate("P.squad.map(id => effectiveUnit(id).name)")
    assert actual == expected, (actual, expected)
    assert page.locator(".bf-scene-places .bf-scene-place").count() == 6
    assert page.locator(".bf-scene-places button[data-bf-goto]").count() == 2
    assert page.locator(".bf-scene-places .bf-scene-locked").count() == 4
    assert page.locator(".bf-scene-toolrow button").count() == 4
    assert page.locator(".bf-scene-toolrow .bf-scene-tool-locked").count() == 1
    assert page.locator(".bf-scene-tool-box[data-bf-open-box]").count() == 1
    # Check actual locally packaged files resolve, rather than accepting broken img tags.
    page.wait_for_function("""() => [...document.querySelectorAll('.bf-scene-place img, .bf-scene-toolrow img')]
        .every(img => img.complete && img.naturalWidth > 0)""", timeout=15000)
    assert page.evaluate("""() => ({
        save: localStorage.getItem('bf_global_offline_demo_v7'),
        squad: JSON.stringify(P.squad), zel: P.zel
    })""") == before
    print("PASS original art loads, real party appears, unavailable modes stay locked")

    page.locator('.bf-scene-place[data-bf-goto="quest"]').click()
    assert page.evaluate("BF_homeNav.current") == "quest"
    assert page.locator("#battle").is_visible()
    page.locator('.bf-navbar button[data-bf-goto="home"]').click()
    page.locator('.bf-scene-place[data-bf-goto="summon"]').click()
    assert page.evaluate("BF_homeNav.current") == "summon"
    assert page.locator("#summonbutton").is_visible()
    page.locator('.bf-navbar button[data-bf-goto="units"]').click()
    assert page.locator("#squadpicker").is_visible()
    # A real in-app squad edit should refresh the Home preview; this browser
    # test is deliberately allowed to mutate its own isolated localStorage.
    page.locator('#squadpicker .squadpick.picked input').first.click()
    page.wait_for_function('P.squad.length === 5')
    page.locator('.bf-navbar button[data-bf-goto="home"]').click()
    page.wait_for_function("""() => document.querySelectorAll('#bf-scene-party .bf-scene-member img').length === 5""")
    assert page.locator("#bf-scene-party .bf-scene-member").count() == 6
    assert page.evaluate("BF_homeNav.current") == "home"
    assert not errors, errors
    print("PASS routes, live squad editing, and no JavaScript errors")
    browser.close()
