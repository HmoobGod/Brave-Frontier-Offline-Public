"""v208: real prepared HTML + complete Java onPageFinished script-chain regression.

This is a desktop Chromium approximation, NOT a real Android WebView/device test.
No native 2022 enemy waves, AI, drops, or mobile save compatibility are inferred.
"""
from pathlib import Path
import json
import re
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT/"app/src/main/assets"
JAVA = ROOT/"app/src/main/java/org/bravefrontier/offline/MainActivity.java"
HTML = ASSETS/"index.html"
APP_ASSET = "bf20600_amdahl_source_quest_guide.js"
EXPECTED_ORDER = (
    "bf100_grand_gaia_campaign.js",
    "bf14900_original_amdahl_art.js",
    "bf10800_2022_encounter_reference_ledger.js",
    "bf10900_stlamia_encounter_refs.js",
    "bf15100_amdahl_encounter_evidence.js",
    APP_ASSET,
    "bf17400_original_2022_encounter_crossrefs.js",
)
MASTER = "d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83"
CANON = "f35a7b06bc9e6fae6facc1fd77422f74c04798da4fb87f64a2737a0483a572c3"
java = JAVA.read_text("utf8")
assert "onPageFinished(WebView view, String url)" in java
finish = java.split("onPageFinished(WebView view, String url)", 1)[1]
assert 'if (!"file:///android_asset/index.html".equals(url)) return;' in finish
chain = re.findall(r'readPackagedText\("([^"]+\.js)"\)', finish)
assert 130 <= len(chain) <= 160, ("Java injection chain changed", len(chain))
assert len(set(chain)) == len(chain), "Duplicate Java asset load"
assert chain[0] == "bf_home_nav.js"
assert all(chain.count(x) == 1 for x in EXPECTED_ORDER)
assert [chain.index(x) for x in EXPECTED_ORDER] == sorted(
    chain.index(x) for x in EXPECTED_ORDER)
assert chain.index("bf17400_original_2022_encounter_crossrefs.js") < chain.index(
    "bf19100_original_2022_dungeon_backdrops.js")
assert all((ASSETS/x).is_file() for x in chain), "Missing prepared Android JS"
html = HTML.read_text("utf8")
assert len(html) > 1_000_000, "Prepared application HTML was not built"
assert "const SAVE_KEY='bf_global_offline_demo_v7'" in html
assert html.count("localStorage.setItem(SAVE_KEY,JSON.stringify(P))") == 1
readiness = json.loads((ROOT/"source_data/bf_global_2022_amdahl_quest_readiness_v147.json").read_text("utf8"))
assert len(readiness["quests"]) == 36
assert readiness["provenance"]["questCanonSha256"] == CANON
assert readiness["provenance"]["missionTableSha256"] == MASTER
assert readiness["area"]["playableNow"] is False

with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=True,
        executable_path=shutil.which("chromium") or shutil.which("google-chrome") or
                        shutil.which("google-chrome-stable"),
        args=["--no-sandbox", "--disable-dev-shm-usage"])
    page = browser.new_page(viewport={"width": 390, "height": 844})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    # Playwright about:blank has no native localStorage; install a deterministic
    # implementation BEFORE executing the real app's prepared inline JS.
    page.evaluate("""() => {
      const store = new Map();
      let writes = 0;
      Object.defineProperty(window,"localStorage",{
        configurable:true,
        value: {
          getItem:k => store.has(String(k))?store.get(String(k)):null,
          setItem:(k,v) => {writes++;store.set(String(k),String(v));},
          removeItem:k => {writes++;store.delete(String(k));},
          clear:() => {writes++;store.clear();},
          key:i => Array.from(store.keys())[i]??null,
          get length(){return store.size;}
        }
      });
      window.__bf208Writes=()=>writes;
    }""")
    page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
    assert not errors, ("Prepared HTML execution threw", errors)
    assert page.evaluate("P.version") == 7
    assert page.evaluate("QUESTS.length") == 106
    initial = page.evaluate("""()=>({
      player:JSON.stringify(P),
      quests:JSON.stringify(QUESTS),
      saved:localStorage.getItem("bf_global_offline_demo_v7"),
      writes:__bf208Writes()
    })""")
    assert initial["writes"] == 0, "Unprompted save-write on app launch"
    for asset in chain:
        page.add_script_tag(path=str(ASSETS/asset))
    assert not errors, ("First Java-equivalent script chain threw", errors)
    assert page.evaluate("QUESTS.length") == 106
    assert page.evaluate("Boolean(window.BFAmdahlOriginalArtV14900)")
    assert page.evaluate("Boolean(window.BFGlobalEncounterReferencesV15100)")
    assert page.evaluate("Boolean(window.BFAmdahlSourceQuestGuideV20600)")
    assert page.evaluate("Boolean(window.BFGlobalEncounterCrossrefsV17400)")
    assert page.locator("#bf20600-amdahl-guide").count() == 1
    assert page.locator("#bf14900-amdahl-art").count() == 1
    assert page.locator("#bf20600-dungeon option").count() == 7
    assert page.locator("#bf20600-quest-list li").count() == 5
    assert page.evaluate("BFAmdahlSourceQuestGuideV20600.source.masterSha256") == MASTER
    assert page.evaluate("BFAmdahlSourceQuestGuideV20600.source.canonicalQuestSha256") == CANON
    after_first = page.evaluate("""()=>({
      player:JSON.stringify(P),
      quests:JSON.stringify(QUESTS),
      saved:localStorage.getItem("bf_global_offline_demo_v7"),
      writes:__bf208Writes()
    })""")
    assert initial == after_first, "Optional module chain unexpectedly changed save/player/quests"
    # Desktop approximation of onPageFinished firing twice (resume/reload);
    # repeated evaluations must never append another Amdahl guide, set up
    # additional Amdahl handlers or mutate game state.
    for asset in chain:
        page.add_script_tag(path=str(ASSETS/asset))
    assert not errors, ("Second Java-equivalent script chain threw", errors)
    assert page.locator("#bf20600-amdahl-guide").count() == 1
    assert page.locator("#bf14900-amdahl-art").count() == 1
    assert page.locator("#bf20600-dungeon option").count() == 7
    assert page.evaluate("QUESTS.length") == 106
    assert page.evaluate("Boolean(window.BFGlobalEncounterCrossrefsV17400)")
    after_second = page.evaluate("""()=>({
      player:JSON.stringify(P),
      quests:JSON.stringify(QUESTS),
      saved:localStorage.getItem("bf_global_offline_demo_v7"),
      writes:__bf208Writes()
    })""")
    assert initial == after_second, "Second onPageFinished chain changed player/save/catalog"
    page.locator("#bf14900-amdahl-art > summary").click()
    page.locator("#bf20600-amdahl-guide > summary").click()
    page.locator("#bf20600-dungeon").select_option("460")
    assert page.locator("#bf20600-quest-list li").count() == 6
    assert "Malevolent Ceremony" in page.locator("#bf20600-quest-list").inner_text()
    assert page.evaluate("__bf208Writes()") == 0
    browser.close()
print(f"PASS v208: real 106-quest HTML, {len(chain)} Java-ordered modules x2, v206 once, v174 loaded, v7 save untouched")
