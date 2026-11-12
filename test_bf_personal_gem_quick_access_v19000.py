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
# Header Gem readout: one read-only element, never interactive.
assert js.count("bf17000-header-gems")==2 and "pointer-events:none" in js
assert "addEventListener('click'" in js and "headGems.addEventListener" not in js
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
    # Home header: the recovered Global header's empty Gem row now carries a
    # read-only personal balance. Original reward mode shows a dash.
    head_gems=page.locator(".bf-shell-head > #bf17000-header-gems")
    assert head_gems.count()==1 and head_gems.is_visible()
    assert head_gems.inner_text()=="Gems \u2014"
    assert head_gems.get_attribute("aria-label")=="Personal offline Gems not shown in original reward mode"
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
    assert page.locator("#bf17000-header-gems").count()==1
    after=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
       save:localStorage.getItem('bf_global_offline_demo_v7'),
       writes:[...__v190Writes]})""")
    assert before==after,(before,after)
    # The shortcut is read-only; its displayed personal balance updates only
    # after the existing canonical v7 Gem/quest transactions commit.
    assert jump.inner_text() == 'GEMS · DAILY REWARDS'
    assert page.evaluate('BFGlobalCustomGemsV17000.setMode("custom")') is True
    assert jump.inner_text() == 'GEMS · DAILY REWARDS · 0'
    assert head_gems.inner_text() == 'Gems 0'
    assert page.evaluate('BFGlobalCustomGemsV17000.claimWelcome()') is True
    assert jump.inner_text() == 'GEMS · DAILY REWARDS · 1,000'
    assert head_gems.inner_text() == 'Gems 1,000'
    assert page.evaluate('BFGlobalCustomGemsV17000.claimDaily()') is True
    assert jump.inner_text() == 'GEMS · DAILY REWARDS · 1,100'
    page.evaluate('QUEST=QUESTS.find(q=>q.missionId===1);awardDemoRewards()')
    assert jump.inner_text() == 'GEMS · DAILY REWARDS · 1,125'
    page.evaluate('awardDemoRewards()')
    assert jump.inner_text() == 'GEMS · DAILY REWARDS · 1,126'
    assert head_gems.inner_text() == 'Gems 1,126'
    assert head_gems.get_attribute('aria-label') == 'Personal offline Gems 1,126'
    assert page.evaluate('P._bfGemV170Custom.balance') == 1126
    assert page.evaluate("""()=>{
        const raw=localStorage.getItem('bf_global_offline_demo_v7');
        return JSON.parse(raw)._bfGemV170Custom.balance===1126;
    }""")
    snapshot=page.evaluate('JSON.stringify(P)')
    saved=page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
    page.evaluate('BFGlobalPersonalGemUIV17000.refresh()')
    assert page.evaluate('JSON.stringify(P)') == snapshot
    assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')") == saved
    assert jump.get_attribute('aria-label') == 'Personal Gem balance 1,126. Open rewards'
    # The readout sits in the header art's Gem row at 320/390/540px: inside the
    # header, above the Zel row, right-aligned with it, and on every route.
    for width in (320,390,540):
        page.set_viewport_size({"width":width,"height":844})
        for route in ("home","quest","units","summon","menu"):
            page.evaluate("r=>BF_homeNav.go(r)",route)
            page.evaluate("BFGlobalPersonalGemUIV17000.refresh()")
            box=page.evaluate("""()=>{
                const rect=e=>e.getBoundingClientRect();
                const g=document.getElementById('bf17000-header-gems');
                const h=rect(g.parentElement),r=rect(g),
                  z=rect(document.querySelector('.bf-global-zel')),
                  k=rect(document.querySelector('.bf-global-karma'));
                return {inside:r.width>0&&r.left>=h.left&&r.right<=h.right&&r.top>=h.top,
                  aboveZel:r.bottom<=z.top+1,row:Math.abs((z.top-r.top)-(k.top-z.top))<=2,
                  aligned:Math.abs(r.right-z.right)<=1,
                  whole:g.scrollWidth<=g.clientWidth,
                  inert:getComputedStyle(g).pointerEvents==='none'&&g.tabIndex===-1};
            }""")
            assert all(box.values()),(width,route,box)
    page.set_viewport_size({"width":390,"height":844})
    page.evaluate("BF_homeNav.go('quest')")
    assert page.evaluate('JSON.stringify(P)') == snapshot
    assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')") == saved
    assert page.evaluate('BFGlobalCustomGemsV17000.setMode("original")') is True
    assert jump.inner_text() == 'GEMS · DAILY REWARDS'
    assert head_gems.inner_text() == 'Gems \u2014'
    assert page.evaluate('P._bfGemV170Custom.balance') == 1126
    assert page.evaluate('BFGlobalCustomGemsV17000.setMode("custom")') is True
    assert jump.inner_text() == 'GEMS · DAILY REWARDS · 1,126'
    assert page.locator('#bf19000-open-gem-rewards').count()==1
    assert page.locator('#bf17000-gem-rewards').count()==1
    assert not failures,failures
    browser.close()
print("PASS v190: Quest shortcut opens existing offline Gem panel; v7 wallet and combat state unchanged")
