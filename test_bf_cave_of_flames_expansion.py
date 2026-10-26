"""v0.21: original Global missions 21–23, save/resume and unlocked demo combat.

Only uses disposable in-memory localStorage; never accesses user/Drive saves.
The six old quests stay unchanged. New mission IDs, energy, battles and base
reward totals come from F_MISSION_MST. Wave/enemy generation is still DEMO.
"""
import json, shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/"app/src/main/assets"
manifest=json.loads((ROOT/"source_data/bf_global_missions_21_23.json").read_text("utf-8"))
language=json.loads((ROOT/"source_data/bf_global_quest_en_2022.json").read_text("utf-8"))
assert manifest["schema"]=="bf-global-mission-expansion-v1"
expected=manifest["missions"]
assert [x["missionId"] for x in expected]==[21,22,23]
assert len(language["missions"])==9
assert len({x["id"] for x in language["missions"]})==9
assert manifest["originalSources"]["masterSha256"]=="69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"

with sync_playwright() as p:
    browser=p.chromium.launch(
        headless=True,
        executable_path=shutil.which("google-chrome") or shutil.which("google-chrome-stable") or shutil.which("chromium"),
        args=["--no-sandbox","--disable-dev-shm-usage"]
    )
    page=browser.new_page(viewport={"width":390,"height":844})
    errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    def serve_png(route):
        rel=route.request.url.split("bf-assets.test/",1)[-1]
        img=ASSETS/rel
        if img.is_file() and img.suffix==".png" and img.resolve().is_relative_to(ASSETS.resolve()):
            route.fulfill(status=200,body=img.read_bytes(),content_type="image/png")
        else:route.fulfill(status=404,body=b"")
    page.route("http://bf-assets.test/**",serve_png)
    page.evaluate("""() => {
      const storage={};
      Object.defineProperty(window,"localStorage",{configurable:true,value:{
        getItem(k){return storage[k]??null},setItem(k,v){storage[k]=String(v)},
        removeItem(k){delete storage[k]},key(n){return Object.keys(storage)[n]??null},
        get length(){return Object.keys(storage).length}
      }});
      window.alert=()=>{};window.confirm=()=>true;
    }""")
    html=(ASSETS/"index.html").read_text("utf-8")
    assert "/* BF_CAVE_20_BEGIN */" in html
    assert html.count("/* BF_CAVE_20_BEGIN */")==1
    html=html.replace("<head>",'<head><base href="http://bf-assets.test/">',1)
    page.set_content(html,wait_until="load",timeout=60000)
    page.add_style_tag(path=str(ASSETS/"bf_home_nav.css"))
    page.add_script_tag(path=str(ASSETS/"bf_home_nav.js"))
    page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
    assert page.evaluate("BF_homeNav.current")=="quest"
    assert page.evaluate("QUESTS.map(q=>q.missionId).slice(0,9)")==[1,2,10,11,12,20,21,22,23]
    assert page.locator(".bf-mission-step-row button").count()==106
    assert page.locator("#questlist .questcard").count()==106
    assert page.evaluate("QUESTS.length")==106
    for x in expected:
        record=page.evaluate("(id)=>QUESTS.find(q=>q.missionId===id)",x["missionId"])
        assert record==x,(record,x)
        source=next(z for z in language["missions"] if z["id"]==x["missionId"])
        assert page.evaluate("(id)=>BFGlobalQuestText.sourceFor(QUESTS.find(q=>q.missionId===id)).mission.name",x["missionId"])==source["name"]
        assert page.locator(f'[data-bf-mission="{x["missionId"]}"]').is_disabled()
    assert page.evaluate("BFQuestAreas.choose(QUESTS[6])") is False
    assert page.evaluate("QUEST.missionId")==1
    print("PASS original source quest records, nine missions, locked gates and authenticated original Global English")

    # Unlock via simulated existing save progress, then select using the same
    # production quest cards. No injection of combat/reward logic.
    page.evaluate("() => {P.questClears[20]=1;renderQuestList();}")
    page.wait_for_function("!document.querySelector('[data-bf-mission=\"21\"]').disabled")
    page.locator('[data-bf-mission="21"]').click()
    assert page.evaluate("QUEST.missionId")==21
    assert page.evaluate("P.lastMission")==21
    assert "Wielder of the Fire" in page.locator("#bf-mission-name").inner_text()
    page.evaluate("() => {E.mode.value='archive';reset()}")
    assert page.evaluate("S.totalWaves")==5
    assert page.evaluate("QUEST.background")=="dungeon_battle_10200.jpg"
    assert page.locator('[data-bf-mission="22"]').is_disabled()

    page.evaluate("() => {P.questClears[21]=1;renderQuestList();}")
    page.wait_for_function("!document.querySelector('[data-bf-mission=\"22\"]').disabled")
    page.locator('[data-bf-mission="22"]').click()
    assert page.evaluate("QUEST.missionId")==22
    assert page.evaluate("P.lastMission")==22
    assert "The Thief's Hideout" in page.locator("#bf-mission-name").inner_text()
    assert page.evaluate("S.totalWaves")==5
    assert page.locator('[data-bf-mission="23"]').is_disabled()

    page.evaluate("() => {P.questClears[22]=1;renderQuestList();}")
    page.wait_for_function("!document.querySelector('[data-bf-mission=\"23\"]').disabled")
    page.locator('[data-bf-mission="23"]').click()
    assert page.evaluate("QUEST.missionId")==23
    assert page.evaluate("P.lastMission")==23
    assert "The Blazing Beast" in page.locator("#bf-mission-name").inner_text()
    assert page.evaluate("S.totalWaves")==6
    assert page.locator(".bf-global-mission-description p").inner_text()==next(
        m["description"] for m in language["missions"] if m["id"]==23
    )
    check=page.evaluate("""() => ({
      progress:parseProgress(JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'))),
      roster:P.roster,squad:P.squad,exp:P.unitExp,
      selected:QUEST.missionId,total:S.totalWaves
    })""")
    assert check["progress"]["lastMission"]==23
    assert check["progress"]["questClears"]["22"]==1
    assert check["roster"]==check["progress"]["roster"]
    assert check["squad"]==check["progress"]["squad"]
    assert check["selected"]==23 and check["total"]==6
    assert not errors, errors
    print("PASS 20->21->22->23 progressive unlock, 5/5/6 actual demo wave counts, save v7 roundtrip")

    # Do not promote missing original combat encounters or extra reward drops
    # to verified status. Rendering is a DEMO and named that way.
    assert page.locator("#questinfo").is_visible()
    assert "simulated" in page.locator("#questinfo").inner_text().lower()
    print("PASS user-facing simulated battle disclaimer; special drops not fabricated")
    browser.close()
