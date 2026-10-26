"""Build #16: source-based dungeon group filters and nonmutating Unit Box browsing.
Disposable in-memory browser, no real saves or Drive files.
"""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

ASSETS=Path(__file__).resolve().parent / "app/src/main/assets"
with sync_playwright() as pw:
    browser=pw.chromium.launch(
        headless=True,
        executable_path=shutil.which("google-chrome") or shutil.which("google-chrome-stable") or shutil.which("chromium"),
        args=["--no-sandbox","--disable-dev-shm-usage"])
    page=browser.new_page(viewport={"width":390,"height":844})
    errors=[]
    page.on("pageerror",lambda error: errors.append(str(error)))
    def route_png(route):
        rel=route.request.url.split("bf-assets.test/",1)[-1]
        file=ASSETS/rel
        if file.is_file() and file.suffix==".png" and file.resolve().is_relative_to(ASSETS.resolve()):
            route.fulfill(body=file.read_bytes(),content_type="image/png",status=200)
        else: route.fulfill(body=b"",status=404)
    page.route("http://bf-assets.test/**",route_png)
    page.evaluate("""() => {
      const cache={};
      Object.defineProperty(window,"localStorage",{configurable:true,value:{
        getItem(k){return cache[k]??null},
        setItem(k,v){cache[k]=String(v)},
        removeItem(k){delete cache[k]},
        key(n){return Object.keys(cache)[n]??null},
        get length(){return Object.keys(cache).length}
      }});
      window.alert=()=>{};window.confirm=()=>true;
    }""")
    html=(ASSETS/"index.html").read_text(encoding="utf-8").replace("<head>",'<head><base href="http://bf-assets.test/">',1)
    page.set_content(html,wait_until="load",timeout=60000)
    page.add_style_tag(path=str(ASSETS/"bf_home_nav.css"))
    page.add_script_tag(path=str(ASSETS/"bf_home_nav.js"))
    initial=page.evaluate("""() => ({
      save:localStorage.getItem('bf_global_offline_demo_v7'),
      squad:JSON.stringify(P.squad),roster:JSON.stringify(P.roster),
      exp:JSON.stringify(P.unitExp),evo:JSON.stringify(P.evolutions),
      lastMission:P.lastMission,zel:P.zel
    })""")
    assert page.evaluate("BF_homeNav.current")=="home"
    page.locator(".bf-scene-tool-box").click()
    assert page.evaluate("BF_homeNav.current")=="units"
    assert page.evaluate("BFInnerScreens.unitTab")=="box"
    assert page.locator("#bf-owned-box").is_visible()
    assert page.locator(".bf-box-card").count()==6
    page.locator("#bf-box-element").select_option("Fire")
    assert page.locator(".bf-box-card").count()==1
    assert "Vargas" in page.locator(".bf-box-card").inner_text()
    assert "1 shown / 6 owned" in page.locator("#bf-box-count").inner_text()
    page.locator("#bf-box-element").select_option("all")
    page.locator("#bf-box-rarity").select_option("2")
    assert page.locator(".bf-box-card").count()==6
    page.locator("#bf-box-rarity").select_option("all")
    page.locator("#bf-box-sort").select_option("element")
    actual=page.locator(".bf-box-card").evaluate_all("(cards) => cards.map(c => Number(c.dataset.bfUnitId))")
    expected=page.evaluate("""() => P.roster.slice().sort((a,b) =>
      effectiveUnit(a).element.localeCompare(effectiveUnit(b).element) ||
      effectiveUnit(a).name.localeCompare(effectiveUnit(b).name) || a-b)""")
    assert actual==expected,(actual,expected)
    page.locator("#bf-box-search").fill("20011")
    assert page.locator(".bf-box-card").count()==1
    page.locator("#bf-box-search").fill("")
    page.locator(".bf-box-manage").click()
    assert page.evaluate("BFInnerScreens.unitTab")=="squad"
    assert page.locator("#squadpicker").is_visible()
    print("PASS Home->Unit Box, real element/rarity/name filters, source sorting, edit-squad shortcut")

    page.locator('.bf-navbar [data-bf-goto="quest"]').click()
    assert page.locator("#bf-quest-details").is_visible()
    assert page.locator(".bf-quest-area-tabs button").count()==24
    assert page.locator('#questlist button.questcard:visible').count()==106
    page.locator('.bf-quest-area-tabs button[data-bf-dungeon="10"]').click()
    assert page.evaluate("BFQuestAreas.selectedDungeon")=="10"
    assert page.locator('#questlist button.questcard:visible').count()==3
    assert "3 archived missions" in page.locator(".bf-quest-area-hint").inner_text()
    page.locator('.bf-quest-area-tabs button[data-bf-dungeon="20"]').click()
    assert page.locator('#questlist button.questcard:visible').count()==4
    page.locator('.bf-quest-area-tabs button[data-bf-dungeon="all"]').click()
    assert page.locator('#questlist button.questcard:visible').count()==106
    assert "MST_DUNGEONS_MISSION_1_NAME" in page.locator("#bf-mission-key").inner_text()
    assert "Mission 1" in page.locator("#bf-mission-name").inner_text()
    assert page.evaluate("BF_homeNav.current")=="quest"
    print("PASS source-derived Dungeon 1/10/20 exploration, locked previews, no guessed Global titles")

    final=page.evaluate("""() => ({
      save:localStorage.getItem('bf_global_offline_demo_v7'),
      squad:JSON.stringify(P.squad),roster:JSON.stringify(P.roster),
      exp:JSON.stringify(P.unitExp),evo:JSON.stringify(P.evolutions),
      lastMission:P.lastMission,zel:P.zel
    })""")
    assert final==initial,(initial,final)
    assert not errors,errors
    print("PASS all filters are read-only, save remains unchanged, no script errors")
    browser.close()
