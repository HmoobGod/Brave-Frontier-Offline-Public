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
    # v437: Home build-info shortcut opens only the already-existing Menu
    # metadata disclosure; browser previews must not invent APK identity.
    for width in (320,390,540):
        page.set_viewport_size({"width":width,"height":844})
        button = page.locator("#bf-home-build-info")
        assert button.is_visible()
        assert button.evaluate("(e)=>e.getBoundingClientRect().height") >= 44
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"),width
    page.set_viewport_size({"width":390,"height":844})
    before_build = page.evaluate("({p:JSON.stringify(P),s:JSON.stringify(S),quest:QUEST.missionId,save:localStorage.getItem('bf_global_offline_demo_v7')})")
    page.locator("#bf-home-build-info").click()
    assert page.evaluate("BF_homeNav.current") == "menu"
    assert page.locator("#bf-about-build").evaluate("(e)=>e.open")
    assert page.locator("#bf-about-version").inner_text() == "Unavailable"
    assert page.locator("#bf-about-package").inner_text() == "Unavailable"
    assert page.evaluate("({p:JSON.stringify(P),s:JSON.stringify(S),quest:QUEST.missionId,save:localStorage.getItem('bf_global_offline_demo_v7')})") == before_build
    page.locator('.bf-navbar button[data-bf-goto="home"]').click()
    assert page.evaluate("BF_homeNav.current") == "home"
    print("PASS Home build-info shortcut routes read-only without fabricated APK metadata")
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
    # v452: the read-only Training banner must not coerce malformed v7
    # resources to zero or to an apparent affordable purchase.
    training = page.evaluate("""() => {
      const keys=['trainingShards','zel','trainingSpent'];
      const original=keys.map(k=>({key:k,had:Object.prototype.hasOwnProperty.call(P,k),value:P[k]}));
      const before=JSON.stringify({P,S});
      const save=localStorage.getItem('bf_global_offline_demo_v7');
      const tab=document.querySelector('.bf-unit-actions button[data-bf-unit-tab="training"]');
      const note=document.querySelector('.bf-training-cost-note');
      const result={bad:[]};
      const show=(key,value)=>{
        P.trainingShards=5;P.zel=750;P.trainingSpent=0;
        if(key!==null)P[key]=value;
        tab.click();
        return note?.textContent || '';
      };
      try {
        result.noteFound=!!note;
        result.healthy=show(null,null);
        result.cap=show('trainingSpent',100000);
        for(const [key,value] of [
          ['trainingShards',-1],['trainingShards',2.5],['trainingShards','5'],
          ['trainingShards',null],['trainingShards',NaN],
          ['trainingShards',Infinity],['trainingShards',Number.MAX_SAFE_INTEGER+1],
          ['zel',-1],['zel','750'],['zel',750.5],
          ['trainingSpent',-1],['trainingSpent','0'],
          ['trainingSpent',0.5],['trainingSpent',Number.MAX_SAFE_INTEGER+1]
        ]) result.bad.push([key,show(key,value)]);
      } finally {
        for(const {key,had,value} of original) {
          if(had) P[key]=value; else delete P[key];
        }
        tab.click();
      }
      result.unchanged=JSON.stringify({P,S})===before &&
        localStorage.getItem('bf_global_offline_demo_v7')===save;
      return result;
    }""")
    assert training["noteFound"], training
    assert "Resources support +10 or +50" in training["healthy"], training
    assert "spending limit reached" in training["cap"], training
    assert len(training["bad"])==14 and all(
        "Training resource status unavailable" in message
        for _,message in training["bad"]),training
    assert training["unchanged"],training
    print("PASS fail-closed read-only training affordability with corrupt resources and unchanged v7")
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
