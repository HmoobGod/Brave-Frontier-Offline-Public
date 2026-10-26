"""v0.20: original Brave Frontier Global English localization regression.

The fixture is a verified extract from BF1_sgtext_part001.zip:
base64-decoded UTF-8 CSV, English column (index 1). Tests use a disposable
browser localStorage only and do not touch the real phone/Drive save.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
import shutil

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/"app/src/main/assets"
CATALOG=json.loads((ROOT/"source_data/bf_global_quest_en_2022.json").read_text("utf-8"))
assert CATALOG["schema"]=="bf-global-quest-sgtext-english-v1"
assert len(CATALOG["missions"])==9 and len(CATALOG["dungeons"])==3
assert CATALOG["provenance"]["archiveSha256"]=="4dccce4eeb6a89cc0cf5718badff7af95046c891882e42c05c6eaca81f9d6285"
assert len({m["id"] for m in CATALOG["missions"]})==9
assert len({d["id"] for d in CATALOG["dungeons"]})==3
for mission in CATALOG["missions"]:
    assert mission["key"]==f'MST_DUNGEONS_MISSION_{mission["id"]}_NAME'
    assert mission["descriptionKey"]==f'MST_DUNGEONS_MISSION_{mission["id"]}_DESCRIPTION'
    assert mission["description"] and mission["name"]
for dungeon in CATALOG["dungeons"]:
    assert dungeon["key"]==f'MST_DUNGEONS_DUNGEON_{dungeon["id"]}_NAME'
    assert dungeon["name"]
print("PASS preserved Global English sgtext catalog, source hashes and complete six-mission coverage")

with sync_playwright() as playwright:
    browser=playwright.chromium.launch(
        headless=True,
        executable_path=(shutil.which("google-chrome") or
                         shutil.which("google-chrome-stable") or
                         shutil.which("chromium")),
        args=["--no-sandbox","--disable-dev-shm-usage"])
    page=browser.new_page(viewport={"width":390,"height":844})
    errors=[]
    page.on("pageerror",lambda error: errors.append(str(error)))
    def local_assets(route):
        relative=route.request.url.split("bf-assets.test/",1)[-1]
        file=ASSETS/relative
        if file.is_file() and file.suffix==".png" and file.resolve().is_relative_to(ASSETS.resolve()):
            route.fulfill(status=200,body=file.read_bytes(),content_type="image/png")
        else:
            route.fulfill(status=404,body=b"")
    page.route("http://bf-assets.test/**",local_assets)
    page.evaluate("""() => {
      const items={};
      Object.defineProperty(window,"localStorage",{configurable:true,value:{
        getItem(k){return items[k]??null},setItem(k,v){items[k]=String(v)},
        removeItem(k){delete items[k]},key(i){return Object.keys(items)[i]??null},
        get length(){return Object.keys(items).length}
      }});
      window.alert=()=>{};window.confirm=()=>true;
    }""")
    html=(ASSETS/"index.html").read_text("utf-8").replace(
        "<head>",'<head><base href="http://bf-assets.test/">',1)
    page.set_content(html,wait_until="load",timeout=60000)
    snapshot=page.evaluate("""() => ({
      save:localStorage.getItem('bf_global_offline_demo_v7'),
      squad:JSON.stringify(P.squad),roster:JSON.stringify(P.roster),
      zel:P.zel,karma:P.karma,
      clears:JSON.stringify(P.questClears)
    })""")
    page.add_style_tag(path=str(ASSETS/"bf_home_nav.css"))
    page.add_script_tag(path=str(ASSETS/"bf_home_nav.js"))
    page.locator('.bf-navbar button[data-bf-goto="quest"]').click()

    live=page.evaluate("({missions: BFGlobalQuestText.missions, dungeons: BFGlobalQuestText.dungeons})")
    assert live["missions"][:len(CATALOG["missions"])]==CATALOG["missions"],"JavaScript English text is not identical to source fixture"
    assert live["dungeons"][:len(CATALOG["dungeons"])]==CATALOG["dungeons"],"JavaScript dungeon names differ from source fixture"
    for index,item in enumerate(CATALOG["missions"]):
        q=page.evaluate("(id) => QUESTS.find(q=>q.missionId===id)",item["id"])
        assert q["missionNameKey"]==item["key"],item["id"]
        heading=page.locator("#questlist button.questcard").nth(index).locator("strong").inner_text()
        assert item["name"] in heading,(item["name"],heading)
        path_button=page.locator(f'.bf-mission-step-row [data-bf-mission="{item["id"]}"]')
        assert item["name"] in path_button.inner_text()
        expected_locked=item["id"]!=1
        assert path_button.is_disabled()==expected_locked,(item["id"],expected_locked)
    for dungeon in CATALOG["dungeons"]:
        button=page.locator(f'.bf-quest-area-tabs [data-bf-dungeon="{dungeon["id"]}"]')
        assert button.inner_text()==dungeon["name"],dungeon

    assert "Basics of Battle" in page.locator("#bf-mission-name").inner_text()
    assert page.locator(".bf-global-mission-description p").inner_text()==CATALOG["missions"][0]["description"]
    assert page.locator(".bf-quest-scroll span").inner_text()=="Beginner's Prairie"
    assert page.locator("#bf-mission-key").inner_text().find("MST_DUNGEONS_MISSION_1_NAME")>=0

    malformed=page.evaluate("""() => BFGlobalQuestText.sourceFor({
      ...QUESTS[0],missionNameKey:"NOT_VERIFIED"
    })""")
    assert malformed is None,"Unverified localization joins should fail closed"
    unchanged=page.evaluate("""() => ({
      save:localStorage.getItem('bf_global_offline_demo_v7'),
      squad:JSON.stringify(P.squad),roster:JSON.stringify(P.roster),
      zel:P.zel,karma:P.karma,
      clears:JSON.stringify(P.questClears)
    })""")
    assert snapshot==unchanged,(snapshot,unchanged)
    print("PASS six original Global mission names, three dungeon labels and first quest description; zero save writes")

    # Work on disposable temporary quest progress to verify that switching
    # missions updates text and does not break core unlock/selection handling.
    page.evaluate("""() => {P.questClears[1]=1;renderQuestList();}""")
    page.locator('#bf-quest-next').click()
    page.wait_for_function("document.querySelector('#bf-mission-name').textContent.includes('Element & Skill')")
    assert page.locator(".bf-global-mission-description p").inner_text()==CATALOG["missions"][1]["description"]
    assert page.evaluate("QUEST.missionId")==2
    assert page.evaluate("P.lastMission")==2
    assert "Element & Skill" in page.locator("#bf-mission-name").inner_text()

    page.evaluate("""() => {
      P.questClears[2]=1;
      P.questClears[10]=1;
      P.questClears[11]=1;
      P.questClears[12]=1;
      renderQuestList();
    }""")
    page.locator('#bf-quest-next').click()
    page.wait_for_function("document.querySelector('#bf-mission-name').textContent.includes('Start of Adventure')")
    assert page.locator(".bf-quest-scroll span").inner_text()=="Adventurer's Prairie"
    page.locator('.bf-mission-step-row [data-bf-mission="20"]').click()
    page.wait_for_function("document.querySelector('#bf-mission-name').textContent.includes('Cave of Dancing Flames')")
    assert page.locator(".bf-quest-scroll span").inner_text()=="Cave of Flames"
    assert page.locator(".bf-global-mission-description p").inner_text()==CATALOG["missions"][5]["description"]
    assert not errors,errors
    print("PASS quest transitions preserve exact Global English names/descriptions and real original quest handlers")
    browser.close()
