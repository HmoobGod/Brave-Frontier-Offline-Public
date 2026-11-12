"""v391: real Home route shortcut; Chromium only, never an owner's Android save.
The reconstructed shortcut uses a byte-verified original Global PNG, but its
session navigation behavior is an offline convenience, not claimed 2022 parity.
"""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
A = ROOT / "app/src/main/assets"
SCRIPT = A / "bf39100_global_home_session_return.js"
JAVA = ROOT / "app/src/main/java/org/bravefrontier/offline/MainActivity.java"

js = SCRIPT.read_text(encoding="utf-8")
native = JAVA.read_text(encoding="utf-8")
assert 'readPackagedText("bf39100_global_home_session_return.js")' in native
assert "bf_global_offline_demo_v7" not in js
for forbidden in ("localStorage", "saveProgress(", "awardDemoRewards(", "P.squad", "P.questClears"):
    assert forbidden not in js, forbidden
assert "BF_homeNav" in js and "bf-route-change" in js
assert "content/home/home_new_btn_shortcut1.png" in js
assert len(js.encode("utf-8")) < 65536
chrome = (shutil.which("google-chrome") or shutil.which("google-chrome-stable")
          or shutil.which("chromium"))
assert chrome, "Chromium required for native Home navigation regression"

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=chrome,
                                 args=["--no-sandbox", "--disable-dev-shm-usage"])
    page = browser.new_page(viewport={"width": 390, "height": 844})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.evaluate("""() => {
      const data = {};
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem(k){return data[k]??null},
        setItem(k,v){data[k]=String(v)},
        removeItem(k){delete data[k]},
        key(i){return Object.keys(data)[i]??null},
        get length(){return Object.keys(data).length}
      }});
      window.alert=()=>{};window.confirm=()=>true;
    }""")
    page.set_content((A / "index.html").read_text(encoding="utf-8"),
                     wait_until="load", timeout=60000)
    page.add_style_tag(path=str(A / "bf_home_nav.css"))
    page.add_script_tag(path=str(A / "bf_home_nav.js"))
    state = page.evaluate("""() => ({
      save:localStorage.getItem('bf_global_offline_demo_v7'),
      player:JSON.stringify(P),
      battle:typeof S==='undefined'?null:JSON.stringify(S)
    })""")
    page.add_script_tag(path=str(SCRIPT))
    page.add_script_tag(path=str(SCRIPT))
    assert page.locator("#bf-home-session-return").count() == 1
    assert not page.locator("#bf-home-session-return").is_visible()
    assert page.evaluate("BFHomeSessionReturnV39100.lastRoute") is None
    assert page.evaluate("BF_homeNav.current") == "home"

    for dest,label in (("quest","QUEST"), ("units","UNITS"),
                       ("summon","SUMMON"), ("menu","MENU")):
        page.locator(f'.bf-navbar button[data-bf-goto="{dest}"]').click()
        assert page.evaluate("BF_homeNav.current") == dest
        assert not page.locator("#bf-home-session-return").is_visible()
        page.locator('.bf-navbar button[data-bf-goto="home"]').click()
        assert page.evaluate("BF_homeNav.current") == "home"
        button = page.locator("#bf-home-return-button")
        assert button.is_visible()
        assert f"RETURN TO {label}" in button.inner_text()
        assert page.evaluate("BF_homeNav.current") == "home", "No automatic resume"
        # Revisit only via the original Home router on an actual button click.
        button.click()
        assert page.evaluate("BF_homeNav.current") == dest
        page.locator('.bf-navbar button[data-bf-goto="home"]').click()

    assert page.evaluate("BF_homeNav.go('not-a-route')") is False
    assert page.evaluate("BFHomeSessionReturnV39100.lastRoute") == "menu"
    for width in (320,390,540):
        page.set_viewport_size({"width":width,"height":844})
        bounds = page.locator("#bf-home-session-return").evaluate("""el => ({
          left:el.getBoundingClientRect().left,
          right:el.getBoundingClientRect().right,
          buttonRight:el.querySelector('button').getBoundingClientRect().right,
          viewport:innerWidth,
          minHeight:el.querySelector('button').getBoundingClientRect().height
        })""")
        assert 0 <= bounds["left"] and bounds["right"] <= width + 1, (width,bounds)
        assert bounds["buttonRight"] <= bounds["right"] + 1, (width,bounds)
        assert bounds["minHeight"] >= 44, (width,bounds)
    assert page.locator("#bf-home-return-button img").get_attribute("src") == (
        "content/home/home_new_btn_shortcut1.png")
    after = page.evaluate("""() => ({
      save:localStorage.getItem('bf_global_offline_demo_v7'),
      player:JSON.stringify(P),
      battle:typeof S==='undefined'?null:JSON.stringify(S)
    })""")
    assert after == state, (state,after)
    assert not errors, errors
    browser.close()
print("PASS v391 Home session-return original art, four explicit routes, 320/390/540px, no save/player/battle mutations")
