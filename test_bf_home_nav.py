"""Browser regression for the additive portrait navigation shell.

This tests browser DOM behavior, not Android APK signing/install or original-game UI parity.
Run alongside test_bf_v0131.py with Playwright and local Chromium/Chrome installed.
"""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
HTML = (ROOT / "app/src/main/assets/index.html").read_text(encoding="utf-8")
ASSETS = ROOT / "app/src/main/assets"

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        headless=True,
        executable_path=(shutil.which("google-chrome") or
                         shutil.which("google-chrome-stable") or shutil.which("chromium")),
        args=["--no-sandbox", "--disable-dev-shm-usage"])
    page = browser.new_page(viewport={"width": 390, "height": 844})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.evaluate("""() => {
      const saved = {};
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem(k){return saved[k] ?? null;},
        setItem(k,v){saved[k]=String(v);},
        removeItem(k){delete saved[k];},
        key(n){return Object.keys(saved)[n] ?? null;},
        get length(){return Object.keys(saved).length;}
      }});
      window.alert=()=>{};window.confirm=()=>true;
    }""")
    page.set_content(HTML, wait_until="load", timeout=60000)
    state = page.evaluate("({squad:JSON.stringify(P.squad),zel:P.zel,save:localStorage.getItem('bf_global_offline_demo_v7')})")
    page.add_style_tag(path=str(ASSETS / "bf_home_nav.css"))
    page.add_script_tag(path=str(ASSETS / "bf_home_nav.js"))
    assert page.evaluate("BF_homeNav.current") == "home"
    assert page.locator("#bf-home").is_visible()
    assert not page.locator("#questlist").is_visible()
    assert page.locator('.bf-navbar button[aria-current="page"]').count() == 1
    print("PASS home starts with quest content hidden")
    page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
    assert page.evaluate("BF_homeNav.current") == "quest"
    assert page.locator("#questlist").is_visible()
    assert page.locator("#battle").is_visible()
    assert page.locator("#slots").is_visible()
    print("PASS quest opens existing quest/battle/squad without reset")
    page.locator('.bf-navbar button[data-bf-goto="units"]').click()
    assert page.locator("#squadpicker").is_visible()
    assert not page.locator("#traininglist").is_visible()  # Squad tab is selected
    page.locator('.bf-unit-actions button[data-bf-unit-tab="training"]').click()
    assert page.locator("#traininglist").is_visible()
    page.locator('.bf-unit-actions button[data-bf-unit-tab="evolve"]').click()
    assert page.locator("#evolist").is_visible()
    page.locator('.bf-unit-actions button[data-bf-unit-tab="squad"]').click()
    assert page.locator("#squadpicker").is_visible()
    assert not page.locator("#questlist").is_visible()
    print("PASS units opens existing squad and training")
    page.locator('.bf-navbar button[data-bf-goto="summon"]').click()
    assert page.locator("#summonbutton").is_visible()
    print("PASS summon opens existing demo recruitment")
    page.locator('.bf-navbar button[data-bf-goto="menu"]').click()
    assert page.locator("#downloadsave").is_visible()
    assert page.locator("#uploadsave").is_visible()
    assert page.locator("#savetc").is_visible()
    print("PASS menu preserves existing JSON save controls")
    page.locator('.bf-navbar button[data-bf-goto="home"]').click()
    assert page.locator("#bf-home").is_visible()
    assert page.evaluate("({squad:JSON.stringify(P.squad),zel:P.zel,save:localStorage.getItem('bf_global_offline_demo_v7')})") == state
    assert page.evaluate("BF_homeNav.routedPanels") >= 10
    assert not errors, errors
    print("PASS navigation changes no save, squad, or Zel and throws no JS errors")
    browser.close()
