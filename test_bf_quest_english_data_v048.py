"""v0.48: browser regression for all 21 source-verified Global quest texts."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
base = json.loads((ROOT / "source_data/bf_global_quest_en_2022.json").read_text("utf-8"))
missions = list(base["missions"])
dungeons = list(base["dungeons"])
for file in ("bf_global_egor_snowfield_v045.json",
             "bf_global_forest_of_beasts_v046.json",
             "bf_global_magutagal_v047.json"):
    obj = json.loads((ROOT / "source_data" / file).read_text("utf-8"))
    missions.extend(obj["english"])
    row = obj["dungeon"]
    dungeons.append({"id": row["id"], "key": row["nameKey"], "name": row["name"]})
assert len(missions) == 21 and len(dungeons) == 6
assert [m["id"] for m in missions] == [
    1, 2, 10, 11, 12, 20, 21, 22, 23, 30, 31, 32, 33,
    40, 41, 42, 43, 50, 51, 52, 53]
source = {str(m["id"]): m["description"] for m in missions}
html_file = ASSETS / "index.html"
html = html_file.read_text("utf-8")
assert html.count("/* BF_GLOBAL_QUEST_TEXT_DATA_V048 */") == 1
assert "bf_global_offline_demo_v7" in html
nav = (ASSETS / "bf_home_nav.js").read_bytes()
assert len(nav) < 65536
assert b"BF_GLOBAL_QUEST_TEXT_DATA_V048" in nav
before = hashlib.sha256(html.encode()).digest()
subprocess.run([sys.executable, str(ROOT / "prepare_quest_english_data_v048.py")],
               check=True, cwd=ROOT)
assert hashlib.sha256(html_file.read_bytes()).digest() == before, "not idempotent"

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True,
        executable_path=shutil.which("chromium") or shutil.which("google-chrome")
                        or shutil.which("google-chrome-stable"),
        args=["--no-sandbox", "--disable-dev-shm-usage"])
    page = browser.new_page(viewport={"width": 390, "height": 844})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    def serve(route):
        relative = route.request.url.split("bf-assets.test/", 1)[-1]
        local = ASSETS / relative
        if local.is_file() and local.resolve().is_relative_to(ASSETS.resolve()) \
           and local.suffix in (".png", ".jpg"):
            route.fulfill(status=200, body=local.read_bytes(),
                          content_type="image/jpeg" if local.suffix == ".jpg" else "image/png")
        else:
            route.fulfill(status=404, body=b"")
    page.route("http://bf-assets.test/**", serve)
    page.evaluate("""() => {
      const store = {};
      Object.defineProperty(window, 'localStorage', {configurable:true, value:{
        getItem:k=>store[k]??null, setItem:(k,v)=>{store[k]=String(v)},
        removeItem:k=>{delete store[k]}, key:i=>Object.keys(store)[i]??null,
        get length(){return Object.keys(store).length}
      }});
      window.alert=()=>{}; window.confirm=()=>true;
      HTMLMediaElement.prototype.load=()=>{};
      HTMLMediaElement.prototype.pause=()=>{};
      HTMLMediaElement.prototype.play=()=>Promise.resolve();
    }""")
    page.set_content(html.replace("<head>", '<head><base href="http://bf-assets.test/">', 1),
                     wait_until="load", timeout=90000)
    assert page.evaluate("window.BF_QUEST_ENGLISH_DESCRIPTIONS") == source
    initial = page.evaluate("""() => ({
      version:P.version, roster:JSON.stringify(P.roster),
      squad:JSON.stringify(P.squad), exp:JSON.stringify(P.unitExp),
      clears:JSON.stringify(P.questClears),
      storage:localStorage.getItem('bf_global_offline_demo_v7')
    })""")
    page.add_style_tag(path=str(ASSETS / "bf_home_nav.css"))
    page.add_script_tag(path=str(ASSETS / "bf_home_nav.js"))
    assert page.evaluate("BFGlobalQuestText.missions.slice(0,21)") == missions
    assert page.evaluate("BFGlobalQuestText.dungeons.slice(0,6)") == dungeons
    assert page.evaluate("QUESTS.length") == 106
    assert page.evaluate("BFMistralMap.entries.length") == 9
    assert page.evaluate("""() => BFGlobalQuestText.sourceFor({
      ...QUESTS[0], missionNameKey:'UNVERIFIED'})""") is None
    for row in missions:
        quest = page.evaluate("(id) => QUESTS.find(q=>q.missionId===id)", row["id"])
        matched = page.evaluate("(q)=>BFGlobalQuestText.sourceFor(q)", quest)
        assert matched["mission"] == row, (row, matched)
    page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
    assert page.locator('.bf-mission-step-row [data-bf-mission]').count() == 106
    assert page.locator(".bf-mistral-pin").count() == 9
    assert page.evaluate("BFMistralMap.reveal(50)") is False
    page.evaluate("()=>{P.questClears[43]=1;renderQuestList()}")
    assert page.evaluate("BFMistralMap.isUnlocked(50)") is True
    page.locator('[data-bf-map-list="50"]').click()
    assert page.evaluate("QUEST.missionId") == 50
    assert page.locator(".bf-global-mission-description p").inner_text() == missions[17]["description"]
    final = page.evaluate("""() => ({
      version:P.version, roster:JSON.stringify(P.roster),
      squad:JSON.stringify(P.squad), exp:JSON.stringify(P.unitExp)
    })""")
    for field in ("version","roster","squad","exp"):
        assert final[field] == initial[field], field
    assert initial["version"] == 7
    assert not errors, errors
    browser.close()
print("PASS v0.48: source-exact 21 descriptions, fail-closed join, map locks, v7, idempotency")
