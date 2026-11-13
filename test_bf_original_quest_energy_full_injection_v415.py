"""v415 R3: real MainActivity injection confirms translated Quest cards retain
correct original 2022 Energy references and an actually functional filter.

This is browser-only regression evidence; never alters canonical APK or owner save.
"""
from pathlib import Path
import json
import re
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
JAVA = (ROOT / "app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
MASTER = json.loads((ROOT / "source_data/bf_global_original_2022_live_quest_economy_v142.json").read_text("utf8"))
modules = re.findall(r'readPackagedText\("([^"]+\.(?:js|css))"\)', JAVA)
assert len(modules) >= 140 and modules[0] == "bf_home_nav.css", modules[:5]
assert modules.index("bf_home_nav.js") < modules.index("bf14300_original_quest_energy.js")
assert modules.index("bf14300_original_quest_energy.js") < modules.index("bf_home_battle_readiness_v420.js")
# Some generated source packs are absent from an unprepared checkout. The
# Android app loads them optionally, and its build step may produce them.
OPTIONAL_GENERATED = {
    "bf17400_original_2022_encounter_crossrefs.js",
    "bf19100_original_2022_dungeon_backdrops.js",
    "bf22000_original_2022_additional_dungeon_backdrops.js",
    "bf11600_original_lord_stats_data.js",
    "bf22300_original_2022_evolution_item_gallery.js",
}
assert MASTER["year"] == 2022 and MASTER["total"] == 106
rows = MASTER["records"]
expected = {
    "all": [r[0] for r in rows],
    "0": [r[0] for r in rows if r[4] == 0],
    "1-3": [r[0] for r in rows if 1 <= r[4] <= 3],
    "4-6": [r[0] for r in rows if 4 <= r[4] <= 6],
    "7+": [r[0] for r in rows if r[4] >= 7],
}
assert [len(expected[k]) for k in ("all", "0", "1-3", "4-6", "7+")] == [106, 2, 10, 31, 63]

def snapshot(p):
    return p.evaluate("""() => ({
      player:JSON.stringify(P),session:JSON.stringify(S),mission:QUEST.missionId,
      save:localStorage.getItem('bf_global_offline_demo_v7'),
      keys:Array.from({length:localStorage.length},(_,i)=>localStorage.key(i)).sort()
    })""")

with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=True,
        executable_path=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable"),
        args=["--no-sandbox", "--disable-dev-shm-usage"])
    try:
        p = browser.new_page(viewport={"width": 320, "height": 844})
        errors = []
        p.on("pageerror", lambda error: errors.append(str(error)))
        p.evaluate("""() => {
          const db={};
          Object.defineProperty(window,'localStorage',{configurable:true,value:{
            getItem:k=>db[k]??null,setItem:(k,v)=>{db[k]=String(v)},
            removeItem:k=>{delete db[k]},key:i=>Object.keys(db)[i]??null,
            get length(){return Object.keys(db).length}
          }});
          window.alert=()=>{};window.confirm=()=>true;
          HTMLMediaElement.prototype.load=()=>{};
          HTMLMediaElement.prototype.pause=()=>{};
          HTMLMediaElement.prototype.play=()=>Promise.resolve();
        }""")
        p.set_content((ASSETS / "index.html").read_text("utf8"), wait_until="load", timeout=90000)
        assert p.evaluate("P.version") == 7
        # Every source JS/CSS injection is in the exact MainActivity source
        # order, not just a partial fixture that avoids bf_home_nav.js.
        injected = []
        for name in modules:
            item = ASSETS / name
            if not item.is_file():
                assert name in OPTIONAL_GENERATED, ("Missing nonoptional asset", name)
                continue
            if name.endswith(".css"):
                p.add_style_tag(path=str(item))
            else:
                p.add_script_tag(path=str(item))
            injected.append(name)
        assert "bf_home_nav.js" in injected and "bf14300_original_quest_energy.js" in injected
        assert len(injected) >= 140, len(injected)
        assert p.evaluate("BF_homeNav.go('quest')") is True
        assert p.locator("#questlist button.questcard").count() == 106
        assert p.evaluate("typeof BFGlobalQuestText") == "object"
        assert p.evaluate("BFOriginalGlobalQuestEnergyV14300.source.recordCount") == 106
        # The real named-quest module overwrites the strong title. This is
        # exactly the full-injection defect that the previous test missed.
        p.wait_for_function("""() => {
          const card=document.querySelector('#questlist button.questcard');
          return card && !(card.querySelector('strong')?.textContent||'').includes('Mission 1');
        }""")
        assert "Mission 1" not in p.locator("#questlist button.questcard strong").first.inner_text()
        p.wait_for_function("""() =>
          document.querySelectorAll('#questlist button.questcard .bf143-original-cost').length===106
        """)
        assert p.locator("#bf143-energy-range").count() == 1
        assert p.locator("#bf143-energy-clear").count() == 1
        actual = p.evaluate("""() => [...document.querySelectorAll('#questlist button.questcard')]
          .map((button,i)=>({
            id:Number(button.dataset.bf143MissionId),
            quest:QUESTS[i].missionId,
            label:button.querySelector('.bf143-original-cost')?.textContent||''
          }))""")
        assert len(actual) == 106 and all(a["id"] == a["quest"] for a in actual), actual
        for item, record in zip(actual, rows):
            assert item["id"] == record[0], (item, record)
            assert "Energy " + str(record[4]) in item["label"], item
            assert "EXP " + str(record[5]) in item["label"], item

        baseline = snapshot(p)
        assert baseline["save"] is None
        for width in (320, 370, 390, 540):
            p.set_viewport_size({"width": width, "height": 844})
            bounds = p.evaluate("""() => {
              const outer=document.querySelector('#bf143-energy-filter').getBoundingClientRect();
              const range=document.querySelector('#bf143-energy-range').getBoundingClientRect();
              const clear=document.querySelector('#bf143-energy-clear').getBoundingClientRect();
              return {width:innerWidth,left:outer.left,right:outer.right,
                rangeHeight:range.height,clearHeight:clear.height,
                scroll:document.documentElement.scrollWidth};
            }""")
            assert bounds["left"] >= -1 and bounds["right"] <= width+1, (width,bounds)
            assert bounds["rangeHeight"] >= 44 and bounds["clearHeight"] >= 44, (width,bounds)
            assert bounds["scroll"] <= width, (width,bounds)
            for band, ids in expected.items():
                p.locator("#bf143-energy-range").select_option(band)
                found = p.evaluate("""() => [...document.querySelectorAll('#questlist button.questcard')]
                  .filter(button=>!button.hidden)
                  .map(button=>Number(button.dataset.bf143MissionId))""")
                assert found == ids, (width,band,found,ids)
                assert p.locator("#bf143-energy-count").inner_text() == \
                    f"{len(ids)} of 106 source-matched quests shown", (width,band)
                assert p.evaluate("""() => [...document.querySelectorAll(
                  '#questlist button.questcard')].filter(button=>button.hidden)
                  .every(button=>getComputedStyle(button).display==='none')"""), (width,band)
            # Mission 2022 labels survive CORE quest-list recreation even
            # while a narrower Energy filter is active.
            p.locator("#bf143-energy-range").select_option("7+")
            p.evaluate("renderQuestList()")
            p.wait_for_function("""() => document.querySelectorAll(
              '#questlist button.questcard .bf143-original-cost').length===106""")
            assert p.evaluate("""() => [...document.querySelectorAll('#questlist button.questcard')]
              .filter(button=>!button.hidden).length""") == 63
            p.locator("#bf143-energy-clear").click()
            assert p.locator("#bf143-energy-range").input_value() == "all"
            assert p.evaluate("document.activeElement.id") == "bf143-energy-range"
            assert p.evaluate("""() => [...document.querySelectorAll('#questlist button.questcard')]
              .filter(button=>!button.hidden).length""") == 106
        # Reordered card identity or live source drift must fail closed, not
        # silently label or hide the wrong mission.
        first = p.locator("#questlist button.questcard").first
        original_id = first.get_attribute("data-bf143-mission-id")
        first.evaluate("(el)=>el.dataset.bf143MissionId='99999'")
        assert p.evaluate("BFOriginalGlobalQuestEnergyV14300.refresh()") == 0
        assert p.locator("#bf143-energy-range").is_disabled()
        assert "unavailable" in p.locator("#bf143-energy-count").inner_text()
        assert p.evaluate("""() => [...document.querySelectorAll('#questlist button.questcard')]
          .every(button=>!button.hidden && !button.querySelector('.bf143-original-cost'))""")
        first.evaluate("(el,id)=>el.dataset.bf143MissionId=id", original_id)
        assert p.evaluate("BFOriginalGlobalQuestEnergyV14300.refresh()") == 106
        assert p.locator("#bf143-energy-range").is_enabled()
        assert p.locator("#questlist button.questcard .bf143-original-cost").count() == 106
        assert snapshot(p) == baseline, (snapshot(p),baseline)
        assert not errors, errors
    finally:
        browser.close()
print("PASS v415 real full MainActivity injection: translated 2022 labels + 106 working Energy filters + no v7 writes")
