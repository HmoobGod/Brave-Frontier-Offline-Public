"""Read-only Unit Box and archive-backed Quest details regression.

Never reads or modifies a real Android or Drive save. 390px portrait browser.
"""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

ASSETS = Path(__file__).resolve().parent / "app/src/main/assets"

with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=True,
        executable_path=shutil.which("google-chrome") or shutil.which("google-chrome-stable") or shutil.which("chromium"),
        args=["--no-sandbox", "--disable-dev-shm-usage"])
    page = browser.new_page(viewport={"width":390,"height":844})
    errors=[]
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    def route_local(route):
        rel=route.request.url.split("bf-assets.test/",1)[-1]
        path=ASSETS/rel
        if path.is_file() and path.suffix==".png" and path.resolve().is_relative_to(ASSETS.resolve()):
            route.fulfill(status=200,body=path.read_bytes(),content_type="image/png")
        else:route.fulfill(status=404,body=b"")
    page.route("http://bf-assets.test/**",route_local)
    page.evaluate("""() => {
      const values={};
      Object.defineProperty(window,"localStorage",{configurable:true,value:{
        getItem(k){return values[k]??null},setItem(k,v){values[k]=String(v)},
        removeItem(k){delete values[k]},key(i){return Object.keys(values)[i]??null},
        get length(){return Object.keys(values).length}
      }});
      window.alert=()=>{};window.confirm=()=>true;
    }""")
    html=(ASSETS/"index.html").read_text(encoding="utf-8")
    html=html.replace("<head>",'<head><base href="http://bf-assets.test/">',1)
    page.set_content(html,wait_until="load",timeout=60000)
    page.add_style_tag(path=str(ASSETS/"bf_home_nav.css"))
    page.add_script_tag(path=str(ASSETS/"bf_home_nav.js"))
    initial=page.evaluate("""() => ({
      squad: JSON.stringify(P.squad),roster:JSON.stringify(P.roster),
      exp:JSON.stringify(P.unitExp),save:localStorage.getItem('bf_global_offline_demo_v7'),
      zel:P.zel
    })""")

    page.locator('.bf-navbar [data-bf-goto="units"]').click()
    page.locator('.bf-unit-actions [data-bf-unit-tab="box"]').click()
    assert page.evaluate("BFInnerScreens.unitTab")=="box"
    assert page.locator("#bf-owned-box").is_visible()
    assert not page.locator("#squadpicker").is_visible()
    assert not page.locator("#evolist").is_visible()
    assert page.locator(".bf-box-card").count()==page.evaluate("P.roster.length")==6
    assert page.locator("#bf-box-detail h3").is_visible()
    page.locator("#bf-box-filter").select_option("reserve")
    assert page.locator(".bf-box-card").count()==0
    page.locator("#bf-box-filter").select_option("all")
    page.locator("#bf-box-sort").select_option("rarity")
    page.locator("#bf-box-search").fill("vargas")
    assert page.locator(".bf-box-card").count()==1
    assert "Vargas" in page.locator("#bf-box-detail h3").inner_text()
    page.locator("#bf-box-search").fill("")
    assert page.locator(".bf-box-card").count()==6
    page.wait_for_function("""() => [...document.querySelectorAll(
      '#bf-owned-box .bf-box-card img, .bf-unit-actions img')].every(img=>img.complete&&img.naturalWidth>0)""")
    print("PASS live owned Unit Box, base-stat detail, name filter and sort, 6 actual owned")

    page.locator('.bf-navbar [data-bf-goto="quest"]').click()
    assert not page.locator("#bf-owned-box").is_visible()
    assert page.locator("#bf-quest-details").is_visible()
    assert "Mission 1" in page.locator("#bf-mission-name").inner_text()
    assert page.locator(".bf-mission-stats span").count()==6
    assert page.locator(".bf-mission-stats span").nth(0).locator("strong").inner_text()=="3"
    assert page.locator(".bf-mission-stats span").nth(3).locator("strong").inner_text()=="500"
    assert "MST_DUNGEONS_MISSION_1_NAME" in page.locator("#bf-mission-key").inner_text()
    # Exercise selecting a second mission in the disposable browser without saving.
    page.evaluate("""() => {
      P.questClears[1]=1;
      QUEST=QUESTS.find(q=>q.missionId===2);
      renderQuestList();
    }""")
    page.wait_for_function("document.querySelector('#bf-mission-name').textContent.includes('Mission 2')")
    assert page.locator(".bf-mission-stats span").nth(3).locator("strong").inner_text()=="1000"
    page.locator("#bf-quest-battle-jump").click()
    assert page.locator("#battle").is_visible()
    print("PASS archived quest IDs/rewards, live mission changes, battle shortcut")

    result=page.evaluate("""() => ({
      squad: JSON.stringify(P.squad),roster:JSON.stringify(P.roster),
      exp:JSON.stringify(P.unitExp),save:localStorage.getItem('bf_global_offline_demo_v7'),
      zel:P.zel
    })""")
    assert result==initial,(initial,result)
    assert not errors,errors
    print("PASS no saved progress, squad, XP, Zel changes; no JS errors")
    browser.close()
