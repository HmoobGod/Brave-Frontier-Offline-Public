"""Browser regression for BF1 Global Units/Quest/Summon artwork and UI tabs.

Runs with a disposable in-memory browser save. Does not read the user's Drive backup.
"""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"

with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=True,
        executable_path=(shutil.which("google-chrome") or
                         shutil.which("google-chrome-stable") or
                         shutil.which("chromium")),
        args=["--no-sandbox", "--disable-dev-shm-usage"])
    page = browser.new_page(viewport={"width": 390, "height": 844})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))

    def serve_asset(route):
        rel = route.request.url.split("bf-assets.test/", 1)[-1]
        asset = ASSETS / rel
        if asset.is_file() and asset.resolve().is_relative_to(ASSETS.resolve()) and asset.suffix == ".png":
            route.fulfill(status=200, body=asset.read_bytes(), content_type="image/png")
        else:
            route.fulfill(status=404, body=b"")
    page.route("http://bf-assets.test/**", serve_asset)
    page.evaluate("""() => {
      const items={};
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem(k){return items[k] ?? null},
        setItem(k,v){items[k]=String(v)},
        removeItem(k){delete items[k]},
        key(i){return Object.keys(items)[i] ?? null},
        get length(){return Object.keys(items).length}
      }});
      window.alert=()=>{};window.confirm=()=>true;
    }""")
    html = (ASSETS / "index.html").read_text(encoding="utf-8")
    html = html.replace("<head>", '<head><base href="http://bf-assets.test/">', 1)
    page.set_content(html, wait_until="load", timeout=60000)
    before = page.evaluate("""() => ({
      squad: JSON.stringify(P.squad), zel: P.zel,
      save: localStorage.getItem('bf_global_offline_demo_v7')
    })""")
    page.add_style_tag(path=str(ASSETS / "bf_home_nav.css"))
    page.add_script_tag(path=str(ASSETS / "bf_home_nav.js"))
    page.locator('.bf-navbar button[data-bf-goto="units"]').click()
    assert page.locator("#squadpicker").is_visible()
    assert not page.locator("#evolist").is_visible()
    assert not page.locator("#traininglist").is_visible()
    assert page.evaluate("BFInnerScreens.unitTab") == "squad"
    page.locator('[data-bf-unit-tab="evolve"]').click()
    assert not page.locator("#squadpicker").is_visible()
    assert page.locator("#evolist").is_visible()
    page.locator('[data-bf-unit-tab="training"]').click()
    assert page.locator("#traininglist").is_visible()
    assert not page.locator("#evolist").is_visible()
    page.locator('[data-bf-unit-tab="squad"]').click()
    assert page.locator("#squadpicker").is_visible()
    print("PASS original Units menu, real squad/evolution/training tabs")

    # All Global sprite buttons are present and load from bundled local PNGs.
    imgs = '.bf-unit-actions img, .bf-quest-archive-head img, .bf-summon-archive-head img'
    page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
    assert page.locator('.bf-quest-archive-head').is_visible()
    assert page.locator('#questlist').is_visible()
    page.locator('.bf-quest-manage').click()
    assert page.evaluate("BF_homeNav.current") == "units"
    assert page.evaluate("BFInnerScreens.unitTab") == "squad"
    page.locator('.bf-navbar button[data-bf-goto="summon"]').click()
    assert page.locator(".bf-summon-archive-head").is_visible()
    assert page.locator("#summonbutton").is_visible()
    page.wait_for_function("""() => [...document.querySelectorAll(
      '.bf-unit-actions img, .bf-quest-archive-head img, .bf-summon-archive-head img'
    )].every(img => img.complete && img.naturalWidth > 0)""", timeout=15000)
    print("PASS Quest Manage Squad, Summoning Hall artwork and existing recruitment controls")

    after = page.evaluate("""() => ({
      squad: JSON.stringify(P.squad), zel: P.zel,
      save: localStorage.getItem('bf_global_offline_demo_v7')
    })""")
    assert before == after, (before, after)
    assert not errors, errors
    print("PASS unchanged game state and no JavaScript errors")
    browser.close()
