#!/usr/bin/env python3
"""v423: Home shows only owned, nonduplicate live squad entries (read-only)."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
JS = (ASSETS / "bf_home_nav.js").read_text("utf8")
CSS = (ASSETS / "bf_home_nav.css").read_text("utf8")
assert "bf-scene-party-review" in JS and CSS
assert "roster.includes(baseId)" in JS and "!seen.has(baseId)" in JS
assert "saveProgress(" not in JS
with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=True,
        executable_path=shutil.which("chromium") or shutil.which("google-chrome")
                        or shutil.which("google-chrome-stable"),
        args=["--no-sandbox", "--disable-dev-shm-usage"])
    try:
        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.evaluate("""() => {
            const db={};let writes=0;
            Object.defineProperty(window, "localStorage", {configurable:true,value:{
              getItem:k=>db[k]??null,
              setItem:(k,v)=>{writes++;db[k]=String(v)},
              removeItem:k=>{writes++;delete db[k]},
              key:i=>Object.keys(db)[i]??null,
              get length(){return Object.keys(db).length}
            }});
            window.__v423Writes=()=>writes;
            window.alert=()=>{};window.confirm=()=>true;
            HTMLMediaElement.prototype.load=()=>{};
            HTMLMediaElement.prototype.pause=()=>{};
            HTMLMediaElement.prototype.play=()=>Promise.resolve();
        }""")
        page.set_content((ASSETS / "index.html").read_text("utf8"),
                         wait_until="load", timeout=90000)
        page.add_style_tag(path=str(ASSETS / "bf_home_nav.css"))
        page.add_script_tag(path=str(ASSETS / "bf_home_nav.js"))
        assert page.evaluate("P.version") == 7
        assert page.evaluate("BF_homeNav.current") == "home"
        assert page.locator("#bf-scene-party .bf-scene-member").count() == 6
        warning = page.locator("#bf-scene-party-review")
        assert warning.count() == 1 and warning.is_hidden()
        ids = page.evaluate("""() => {
           const owned = P.roster.find(id=>Number.isSafeInteger(id)&&id>0&&effectiveUnit(id));
           const unowned = [10012,20012,30012,40012,50012,60012,
                            10013,20013,30013,40013,50013,60013]
                .find(id=>!P.roster.includes(id)&&effectiveUnit(id));
           return {owned,unowned};
        }""")
        assert ids["owned"] is not None and ids["unowned"] is not None, ids
        page.evaluate("""({owned,unowned})=>{
           window.__v423Original=P.squad.slice();
           P.squad=[owned,unowned,owned,null,-1,{}];
        }""", ids)
        state = page.evaluate("""()=>({
           p:JSON.stringify(P),s:JSON.stringify(S),
           save:localStorage.getItem('bf_global_offline_demo_v7'),
           writes:__v423Writes()
        })""")
        for width in (320,370,390,540):
            page.set_viewport_size({"width":width,"height":844})
            page.evaluate("BFGlobalHome.refreshParty()")
            cards = page.locator("#bf-scene-party .bf-scene-member")
            assert cards.count() == 6
            assert "REVIEW" not in cards.nth(0).inner_text()
            for i in (1,2,4,5):
                assert cards.nth(i).inner_text() == "REVIEW", (width,i)
                assert "Unverified" in cards.nth(i).get_attribute("aria-label")
            assert "Empty squad slot" in cards.nth(3).get_attribute("aria-label")
            assert warning.is_visible()
            assert "4 squad entries need review" in warning.inner_text()
            bounds = warning.evaluate("""el=>{
              const r=el.getBoundingClientRect();
              return {left:r.left,right:r.right};
            }""")
            assert bounds["left"] >= -1 and bounds["right"] <= width+1, (width,bounds)
        after = page.evaluate("""()=>({
           p:JSON.stringify(P),s:JSON.stringify(S),
           save:localStorage.getItem('bf_global_offline_demo_v7'),
           writes:__v423Writes()
        })""")
        assert state == after, (state,after)
        page.evaluate("P.squad=window.__v423Original;delete window.__v423Original")
        page.evaluate("BFGlobalHome.refreshParty()")
        assert warning.is_hidden()
        assert page.locator("#bf-scene-party .bf-scene-member").count() == 6
        assert not errors, errors
    finally:
        browser.close()
print("PASS v423 Home owned squad validation, mobile REVIEW status, no save/Auto changes")
