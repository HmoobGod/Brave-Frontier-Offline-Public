"""v190: discoverable Quest -> Personal Offline Gems shortcut, no reward logic changes."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
A=R/"app/src/main/assets"
js=(A/"bf17000_personal_gem_rewards_ui.js").read_text("utf8")
assert js.count("bf19000-open-gem-rewards")==1
assert "host.before(shortcut);" in js and "host.after(panel);" in js
assert "panel.open=true;" in js
assert "aria-controls" in js and "scrollIntoView" in js
assert "localStorage.setItem(" not in js and "saveProgress(" not in js
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
        executable_path=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable"),
        args=["--no-sandbox","--disable-dev-shm-usage"])
    page=browser.new_page(viewport={"width":390,"height":844})
    failures=[]
    page.on("pageerror",lambda e:failures.append(str(e)))
    page.evaluate("""() => {
        const db={};window.__v190Writes=[];
        Object.defineProperty(window,'localStorage',{configurable:true,value:{
            getItem:k=>db[k]??null,
            setItem:(k,v)=>{db[k]=String(v);__v190Writes.push(k)},
            removeItem:k=>delete db[k],
            key:i=>Object.keys(db)[i]??null,
            get length(){return Object.keys(db).length}
        }});
        window.alert=()=>{};window.confirm=()=>true;
        HTMLMediaElement.prototype.load=()=>{};
        HTMLMediaElement.prototype.pause=()=>{};
        HTMLMediaElement.prototype.play=()=>Promise.resolve();
    }""")
    page.set_content((A/"index.html").read_text("utf8"),wait_until="load",timeout=90000)
    page.add_style_tag(path=str(A/"bf_home_nav.css"))
    page.add_script_tag(path=str(A/"bf_home_nav.js"))
    page.add_script_tag(path=str(A/"bf17000_personal_gem_rewards_ui.js"))
    assert page.evaluate("P.version")==7
    assert page.evaluate("BFGlobalCustomGemsV17000.snapshot().mode")=="original"
    jump=page.locator("#bf19000-open-gem-rewards")
    panel=page.locator("#bf17000-gem-rewards")
    assert jump.count()==panel.count()==1
    assert page.evaluate("""()=>{
        const jump=document.querySelector('#bf19000-open-gem-rewards');
        const quests=document.querySelector('#questlist');
        const panel=document.querySelector('#bf17000-gem-rewards');
        return jump.nextElementSibling===quests && quests.nextElementSibling===panel &&
            jump.getAttribute('aria-controls')==='bf17000-gem-rewards';
    }""")
    assert not panel.evaluate("(e)=>e.open")
    page.locator('.bf-navbar [data-bf-goto="quest"]').click()
    assert jump.is_visible(), "Top-of-Quest shortcut must be visible in actual Quest route"
    before=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
       save:localStorage.getItem('bf_global_offline_demo_v7'),
       writes:[...__v190Writes]})""")
    jump.click()
    assert panel.evaluate("(e)=>e.open")
    assert "Gem balance: 0" in panel.locator("p").first.text_content()
    assert "ORIGINAL" in panel.locator("p").first.text_content()
    panel.locator("summary").click()
    assert not panel.evaluate("(e)=>e.open")
    jump.click()
    assert panel.evaluate("(e)=>e.open")
    assert page.locator("#bf19000-open-gem-rewards").count()==1
    page.add_script_tag(path=str(A/"bf17000_personal_gem_rewards_ui.js"))
    assert page.locator("#bf19000-open-gem-rewards").count()==1
    assert page.locator("#bf17000-gem-rewards").count()==1
    after=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
       save:localStorage.getItem('bf_global_offline_demo_v7'),
       writes:[...__v190Writes]})""")
    assert before==after,(before,after)
    assert not failures,failures
    browser.close()
print("PASS v190: Quest shortcut opens existing offline Gem panel; v7 wallet and combat state unchanged")
