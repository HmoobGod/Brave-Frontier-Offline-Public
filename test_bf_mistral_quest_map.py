"""Build 24: archived Global Mistral world-map, interactive dungeon pins.

Verifies the original image hashes, exact decoded F_DUNGEON_MST coordinates,
no quest-lock bypass, and existing quest handler/save semantics using only
a disposable browser save. Does not access real user progress or Drive files.
"""
from pathlib import Path
import json,hashlib,shutil
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/"app/src/main/assets"
SOURCE=json.loads((ROOT/"source_data/bf_global_mistral_map.json").read_text("utf-8"))
assert SOURCE["schema"]=="bf-global-mistral-map-v1"
assert SOURCE["land"]["areaId"]==100 and SOURCE["land"]["name"]=="Mistral"
assert SOURCE["source"]["areaPackSha256"]=="17b7da1c4dc3e82a454571f5b4983e54ef95d1eff7eb19a808f1ea39ced98082"
assert [(x["id"],x["x"],x["y"],x["requires"]) for x in SOURCE["dungeons"]]==[
  (1,400,780,0),(10,378,829,0),(20,36,698,12)]
for source in SOURCE["art"]:
    original=ROOT/"source_assets/bf1/area"/source["file"]
    packaged=ASSETS/"content/area"/source["file"]
    assert original.read_bytes()==packaged.read_bytes()
    assert hashlib.sha256(packaged.read_bytes()).hexdigest()==source["sha256"]
    assert len(packaged.read_bytes())==source["bytes"]
print("PASS original source-hashed 2022 Mistral map and banner artwork, decoded dungeon locations")

with sync_playwright() as pw:
    browser=pw.chromium.launch(
      headless=True,
      executable_path=shutil.which("google-chrome") or shutil.which("google-chrome-stable") or shutil.which("chromium"),
      args=["--no-sandbox","--disable-dev-shm-usage"])
    page=browser.new_page(viewport={"width":390,"height":844})
    errors=[]
    page.on("pageerror",lambda exc:errors.append(str(exc)))
    def respond(route):
        part=route.request.url.split("bf-assets.test/",1)[-1]
        file=ASSETS/part
        mime="image/jpeg" if file.suffix in (".jpg",".jpeg") else "image/png"
        if file.is_file() and file.resolve().is_relative_to(ASSETS.resolve()) and file.suffix in (".png",".jpg",".jpeg"):
            route.fulfill(status=200,body=file.read_bytes(),content_type=mime)
        else:route.fulfill(status=404,body=b"")
    page.route("http://bf-assets.test/**",respond)
    page.evaluate("""() => {
      const saved={};
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem(k){return saved[k]??null},setItem(k,v){saved[k]=String(v)},
        removeItem(k){delete saved[k]},key(n){return Object.keys(saved)[n]??null},
        get length(){return Object.keys(saved).length}
      }});
      window.alert=()=>{};window.confirm=()=>true;
      HTMLMediaElement.prototype.load=()=>{};
      HTMLMediaElement.prototype.pause=()=>{};
      HTMLMediaElement.prototype.play=()=>Promise.resolve();
    }""")
    html=(ASSETS/"index.html").read_text("utf-8")
    html=html.replace("<head>",'<head><base href="http://bf-assets.test/">',1)
    page.set_content(html,wait_until="load",timeout=60000)
    initial=page.evaluate("""() => ({
      squad:JSON.stringify(P.squad),roster:JSON.stringify(P.roster),
      exp:JSON.stringify(P.unitExp),zel:P.zel,
      clears:JSON.stringify(P.questClears),
      save:localStorage.getItem('bf_global_offline_demo_v7')
    })""")
    page.add_style_tag(path=str(ASSETS/"bf_home_nav.css"))
    page.add_script_tag(path=str(ASSETS/"bf_home_nav.js"))
    page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
    assert page.evaluate("BF_homeNav.current")=="quest"
    assert page.locator(".bf-mistral-map").is_visible()
    assert page.locator(".bf-mistral-pin").count()==9
    assert page.locator(".bf-mistral-list-item").count()==9
    page.wait_for_function("""() => [...document.querySelectorAll(
      '.bf-mistral-map img')].every(img => img.complete && img.naturalWidth > 0)""")
    entries=page.evaluate("BFMistralMap.entries.map(x=>({id:x.id,x:x.x,y:x.y,required:x.required}))")
    assert entries==[
      {"id":1,"x":400,"y":780,"required":0},
      {"id":10,"x":378,"y":829,"required":0},
      {"id":20,"x":36,"y":698,"required":12},
      {"id":30,"x":344,"y":656,"required":23},
      {"id":40,"x":64,"y":502,"required":33},
      {"id":50,"x":252,"y":420,"required":43},
      {"id":60,"x":425,"y":343,"required":53},
      {"id":70,"x":49,"y":264,"required":63},
      {"id":80,"x":330,"y":193,"required":73}]
    assert page.evaluate("BFMistralMap.isUnlocked(1)") is True
    assert page.evaluate("BFMistralMap.isUnlocked(10)") is False
    assert page.evaluate("BFMistralMap.isUnlocked(20)") is False
    assert "LOCKED" in page.locator('[data-bf-map-list="20"]').inner_text()
    assert page.evaluate("BFMistralMap.reveal(20)") is False
    assert page.evaluate("QUEST.missionId")==1
    assert page.evaluate("P.lastMission")==1
    assert page.evaluate("BFGlobalAudio.playingMode") is None
    print("PASS original world map, three accessible locations, no locked cave bypass or sound autoplay")

    # Editing in-memory quest clear state is not writing the real save. These
    # fake clears are only used to validate the original unlock chain.
    page.evaluate("""() => {
      P.questClears[1]=1;P.questClears[2]=1;
      renderQuestList();
    }""")
    assert page.evaluate("BFMistralMap.isUnlocked(10)") is True
    page.locator('[data-bf-map-list="10"]').click()
    assert page.evaluate("QUEST.missionId")==10
    assert page.evaluate("P.lastMission")==10
    assert page.evaluate("BFQuestAreas.selectedDungeon")=="10"
    assert page.locator("#questlist button.questcard:visible").count()==3
    assert "Start of Adventure" in page.locator("#bf-mission-name").inner_text()

    page.evaluate("""() => {
      P.questClears[10]=1;P.questClears[11]=1;P.questClears[12]=1;
      renderQuestList();
    }""")
    assert page.evaluate("BFMistralMap.isUnlocked(20)") is True
    page.locator('[data-bf-map-dungeon="20"]').click()
    assert page.evaluate("QUEST.missionId")==20
    assert page.evaluate("P.lastMission")==20
    assert page.evaluate("BFQuestAreas.selectedDungeon")=="20"
    assert page.locator("#questlist button.questcard:visible").count()==4
    assert "Cave of Dancing Flames" in page.locator("#bf-mission-name").inner_text()
    assert "Cave of Flames" in page.locator("#bf-mistral-map-label").inner_text()
    assert page.evaluate("BFGlobalAudio.playingMode") is None
    saved=page.evaluate("""() => ({
      squad:JSON.stringify(P.squad),roster:JSON.stringify(P.roster),
      exp:JSON.stringify(P.unitExp),zel:P.zel
    })""")
    for k in ("squad","roster","exp","zel"):
        assert saved[k]==initial[k],(k,saved[k],initial[k])
    assert not errors,errors
    print("PASS original selection and unlocked Mistral maps route to working demo missions without changing roster, EXP or Zel")
    browser.close()
