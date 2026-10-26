"""Build #17 original-art Quest path + archive evolution preview regression.
Tests a disposable mocked browser save only, not the user's actual app/Drive.
"""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/"app/src/main/assets"
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,
        executable_path=shutil.which("google-chrome") or shutil.which("google-chrome-stable") or shutil.which("chromium"),
        args=["--no-sandbox","--disable-dev-shm-usage"])
    page=browser.new_page(viewport={"width":390,"height":844})
    errors=[]
    page.on("pageerror",lambda error: errors.append(str(error)))
    def local_png(route):
        rel=route.request.url.split("bf-assets.test/",1)[-1]
        path=ASSETS/rel
        if path.is_file() and path.suffix==".png" and path.resolve().is_relative_to(ASSETS.resolve()):
            route.fulfill(status=200,body=path.read_bytes(),content_type="image/png")
        else:route.fulfill(status=404,body=b"")
    page.route("http://bf-assets.test/**",local_png)
    page.evaluate("""() => {
      const saved={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem(k){return saved[k]??null},setItem(k,v){saved[k]=String(v)},
        removeItem(k){delete saved[k]},key(n){return Object.keys(saved)[n]??null},
        get length(){return Object.keys(saved).length}}});
      window.alert=()=>{};window.confirm=()=>true;
    }""")
    html=(ASSETS/"index.html").read_text(encoding="utf-8").replace(
        "<head>",'<head><base href="http://bf-assets.test/">',1)
    page.set_content(html,wait_until="load",timeout=60000)
    page.add_style_tag(path=str(ASSETS/"bf_home_nav.css"))
    page.add_script_tag(path=str(ASSETS/"bf_home_nav.js"))
    before=page.evaluate("""() => ({
      roster:JSON.stringify(P.roster),squad:JSON.stringify(P.squad),
      evo:JSON.stringify(P.evolutions),exp:JSON.stringify(P.unitExp),
      zel:P.zel,save:localStorage.getItem('bf_global_offline_demo_v7')})""")
    page.locator('.bf-navbar button[data-bf-goto="units"]').click()
    page.locator('[data-bf-unit-tab="box"]').click()
    page.locator('#bf-box-search').fill('vargas')
    assert page.locator('.bf-evo-preview').is_visible()
    assert "NEXT ARCHIVED FORM" in page.locator('.bf-evo-preview').inner_text()
    assert "Unit ID 10012" in page.locator('.bf-evo-preview').inner_text()
    assert "Archive catalyst IDs: 10130 ×1" in page.locator('.bf-evo-preview').inner_text()
    page.wait_for_function("""() => [...document.querySelectorAll('.bf-evo-preview img')].every(i=>i.complete&&i.naturalWidth>0)""")
    page.locator('.bf-evo-open').click()
    assert page.evaluate("BFInnerScreens.unitTab")=="evolve"
    assert page.locator("#evolist").is_visible()
    after=page.evaluate("""() => ({
      roster:JSON.stringify(P.roster),squad:JSON.stringify(P.squad),
      evo:JSON.stringify(P.evolutions),exp:JSON.stringify(P.unitExp),
      zel:P.zel,save:localStorage.getItem('bf_global_offline_demo_v7')})""")
    assert after==before,(before,after)
    print("PASS archive evolution form preview and real Evolution Lab navigation (read-only)")

    page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
    assert page.locator('.bf-mission-step-row button').count()==106
    assert page.locator('[data-bf-mission="1"]').get_attribute("aria-pressed")=="true"
    assert page.locator('[data-bf-mission="2"]').is_disabled()
    assert page.locator('[data-bf-mission="10"]').is_disabled()
    assert page.locator('#bf-quest-next').is_disabled()
    assert page.evaluate("BFQuestAreas.choose(QUESTS[2])") is False
    assert page.evaluate("QUEST.missionId")==1
    page.wait_for_function("""() => [...document.querySelectorAll(
      '.bf-mission-step-actions img,#bf-quest-battle-jump img')].every(i=>i.complete&&i.naturalWidth>0)""")
    print("PASS archived quest path blocks locked quest selection")

    # Simulate unlocking only within the disposable browser, not in real saves.
    page.evaluate("""() => {P.questClears[1]=1;renderQuestList();}""")
    page.wait_for_function("""() => {
      const next=document.getElementById('bf-quest-next');
      return !next.disabled && !document.querySelector('[data-bf-mission="2"]').disabled;
    }""")
    assert page.locator('[data-bf-mission="1"]').evaluate("(e)=>e.classList.contains('bf-step-clear')")
    page.locator('#bf-quest-next').click()
    assert page.evaluate("QUEST.missionId")==2
    assert page.evaluate("P.lastMission")==2
    assert page.locator('[data-bf-mission="2"]').get_attribute("aria-pressed")=="true"
    assert page.locator('#bf-quest-prev').is_enabled()
    assert page.locator('[data-bf-mission="10"]').is_disabled()
    assert page.locator('#bf-quest-next').is_disabled()
    assert "Mission 2" in page.locator("#bf-mission-name").inner_text()
    assert page.locator('#bf-quest-battle-jump').is_visible()
    after_select=page.evaluate("""() => ({
      roster:JSON.stringify(P.roster),squad:JSON.stringify(P.squad),
      evo:JSON.stringify(P.evolutions),exp:JSON.stringify(P.unitExp),zel:P.zel})""")
    for field in ("roster","squad","evo","exp","zel"):
        assert after_select[field]==before[field],field
    assert not errors,errors
    print("PASS unlocked quest navigation invokes original selection and saves only normal quest progress; no JS errors")
    browser.close()
