#!/usr/bin/env python3
"""v416: real Chromium original-level-cap preview, live Units route, save-safe."""
from pathlib import Path
import json
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
catalog = json.loads((ROOT / "source_data/bf_global_2022_playable_level_caps_v115.json").read_text("utf8"))
first = catalog["firstStarterCapByElement"]
caps = {}
for element in range(1, 7):
    for i in range(5):
        caps[element * 10000 + 11 + i] = first[str(element)][i]
        caps[element * 10000 + 21 + i] = catalog["secondStarterCap"][i]
    for i in range(2):
        caps[element * 10000 + 41 + i] = catalog["alternateCap"][i]
assert len(caps) == catalog["supportedForms"] == 72
js = (ASSETS / "bf11500_original_unit_level_caps.js").read_text("utf8")
assert "bf11300-squad-cap-preview" in js
assert "localStorage." not in js and "saveProgress(" not in js

with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=True,
        executable_path=shutil.which("chromium") or shutil.which("google-chrome") or
                        shutil.which("google-chrome-stable"),
        args=["--no-sandbox", "--disable-dev-shm-usage"])
    page = browser.new_page(viewport={"width": 390, "height": 844})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    # about:blank is an opaque origin; establish disposable browser storage
    # before loading the real index, and detect all transient writes.
    page.evaluate("""() => {
        const items = {};
        let writes = 0;
        Object.defineProperty(window, 'localStorage', {configurable:true,value:{
          getItem(k){return items[k] ?? null;},
          setItem(k,v){writes++;items[k]=String(v)},
          removeItem(k){writes++;delete items[k]},
          clear(){writes++;for(const k of Object.keys(items))delete items[k]},
          key(i){return Object.keys(items)[i] ?? null},
          get length(){return Object.keys(items).length}
        }});
        window.__v416SaveWrites = () => writes;
        window.alert = () => {};
        window.confirm = () => true;
    }""")
    page.set_content((ASSETS / "index.html").read_text("utf8"),
                     wait_until="load", timeout=90000)
    assert page.evaluate("P.version") == 7
    for name in ("bf11000_source_starter_leader_skills.js",
                 "bf11100_original_starter_leader_combat.js",
                 "bf11200_all_playable_leader_source.js",
                 "bf11500_original_unit_level_caps.js"):
        page.add_script_tag(path=str(ASSETS / name))
    page.add_style_tag(path=str(ASSETS / "bf_home_nav.css"))
    page.add_script_tag(path=str(ASSETS / "bf_home_nav.js"))
    api = "BFGlobalOriginalUnitLevelCapsV11500"
    assert page.evaluate("typeof " + api + ".refresh") == "function"
    panel = page.locator("#bf11300-original-level-caps")
    assert panel.count() == 1
    before = page.evaluate("""() => ({
        player: JSON.stringify(P), battle: JSON.stringify(S),
        quest: JSON.stringify(window.QUEST ?? null),
        auto: JSON.stringify(S.auto),
        save: localStorage.getItem('bf_global_offline_demo_v7'),
        length: localStorage.length, writes: __v416SaveWrites()
    })""")
    page.locator('.bf-navbar button[data-bf-goto="units"]').click()
    assert page.evaluate("BF_homeNav.current") == "units"
    page.evaluate("document.getElementById('mode').value='archive'")
    panel.locator("summary").click()
    page.evaluate(api + ".refresh()")
    assert panel.is_visible()

    # Derive only IDs and DEMO levels from the live game. Caps are independently
    # calculated from the pinned original source manifest, never from module.lookup.
    units = page.evaluate("""() => P.squad.slice(0,6).map((baseId,slot) => {
      if(!Number.isSafeInteger(baseId) || !P.roster.includes(baseId))return null;
      const u=effectiveUnit(baseId);
      if(!u || !Number.isSafeInteger(u.id))return null;
      return {slot,id:u.id,level:demoLevel(P.unitExp?.[baseId])};
    }).filter(Boolean)""")
    expected = [
        "Slot %s · Unit #%s · DEMO level %s / original cap %s · %s" %
        (row["slot"] + 1, row["id"], row["level"], caps[row["id"]],
         "at/above source cap" if row["level"] >= caps[row["id"]] else "below source cap")
        for row in units if row["id"] in caps and row["level"] >= 1
    ]
    assert expected, "default owner-independent demo squad should be populated"
    for width in (320, 370, 390, 540):
        page.set_viewport_size({"width": width, "height": 844})
        page.evaluate(api + ".refresh()")
        rows = page.locator("#bf11300-squad-cap-preview li").all_text_contents()
        assert rows == expected, (width, rows, expected)
        geometry = panel.evaluate("""el=>{
          const r=el.getBoundingClientRect();
          return {left:r.left,right:r.right,width:r.width,
                  viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth};
        }""")
        assert geometry["left"] >= -0.5, (width, geometry)
        assert geometry["right"] <= width + 0.5, (width, geometry)
        assert geometry["scrollWidth"] <= width, (width, geometry)

    # Independently exercise both text branches, using only temporary demo EXP.
    probe = page.evaluate("""() => {
      const baseId = P.squad[0], u = effectiveUnit(baseId);
      return {baseId, unitId:u.id, had:Object.prototype.hasOwnProperty.call(P.unitExp,baseId),
              old:P.unitExp[baseId]};
    }""")
    cap = caps[probe["unitId"]]
    assert 1 < cap < 99, (probe, cap)
    exact = page.evaluate("""({baseId,cap}) => {
      let low = 0, high = 10000000;
      if(demoLevel(high) < cap)throw Error('cap not reachable by demoLevel');
      while(low < high){
        const mid = Math.floor((low + high) / 2);
        if(demoLevel(mid) >= cap)high = mid;
        else low = mid + 1;
      }
      if(demoLevel(low) !== cap)throw Error('no exact cap demo level');
      P.unitExp[baseId] = low;
      return demoLevel(P.unitExp[baseId]);
    }""", {"baseId": probe["baseId"], "cap": cap})
    assert exact == cap
    page.evaluate(api + ".refresh()")
    rows = page.locator("#bf11300-squad-cap-preview li").all_text_contents()
    assert ("Slot 1 · Unit #%s · DEMO level %s / original cap %s · at/above source cap" %
            (probe["unitId"], cap, cap)) in rows, rows
    page.evaluate("(baseId) => {P.unitExp[baseId]=999999;}", probe["baseId"])
    above = page.evaluate("(baseId)=>demoLevel(P.unitExp[baseId])", probe["baseId"])
    assert above > cap, (above, cap)
    page.evaluate(api + ".refresh()")
    rows = page.locator("#bf11300-squad-cap-preview li").all_text_contents()
    assert ("Slot 1 · Unit #%s · DEMO level %s / original cap %s · at/above source cap" %
            (probe["unitId"], above, cap)) in rows, rows
    page.evaluate("""({baseId,had,old}) => {
        if(had) P.unitExp[baseId] = old;
        else delete P.unitExp[baseId];
    }""", probe)
    page.evaluate(api + ".refresh()")

    # A valid but unowned form MUST be rejected specifically by P.roster guard.
    unowned = page.evaluate("""() => {
      for(const baseId of [10012,20012,30012,40012,50012,60012,
                          10013,20013,30013,40013,50013,60013]){
        if(P.roster.includes(baseId))continue;
        const u = effectiveUnit(baseId);
        if(u && Number.isSafeInteger(u.id) &&
           BFGlobalOriginalUnitLevelCapsV11500.lookup(u.id))return baseId;
      }
      return null;
    }""")
    assert unowned is not None, "no valid unowned form available for ownership negative"
    page.evaluate("(id) => {window.__v416Unowned=id;}", unowned)

    # No unit may appear merely because its ID is in a squad slot.
    page.evaluate("""() => {
      window.__v416OriginalSquad=P.squad.slice();
      P.squad=[10011,window.__v416Unowned,99999,-1,null,60011,40011,50011];
    }""")
    page.evaluate(api + ".refresh()")
    changed = page.locator("#bf11300-squad-cap-preview").inner_text()
    assert "99999" not in changed and "Slot 7" not in changed and "Slot 8" not in changed
    assert "Slot 2 ·" not in changed, "unowned valid form was rendered: " + changed
    assert page.locator("#bf11300-squad-cap-preview li").count() <= 6
    page.evaluate("P.squad=[]")
    page.evaluate(api + ".refresh()")
    assert page.locator("#bf11300-squad-cap-preview li").all_text_contents() == [
        "No eligible owned squad forms to preview."
    ]
    page.evaluate("P.squad=window.__v416OriginalSquad;delete window.__v416OriginalSquad;delete window.__v416Unowned")
    page.evaluate(api + ".refresh()")
    page.locator('.bf-navbar button[data-bf-goto="home"]').click()
    assert page.evaluate("BF_homeNav.current") == "home"
    assert not panel.is_visible()
    page.locator('.bf-navbar button[data-bf-goto="units"]').click()
    assert panel.is_visible()
    after = page.evaluate("""() => ({
        player: JSON.stringify(P), battle: JSON.stringify(S),
        quest: JSON.stringify(window.QUEST ?? null),
        auto: JSON.stringify(S.auto),
        save: localStorage.getItem('bf_global_offline_demo_v7'),
        length: localStorage.length, writes: __v416SaveWrites()
    })""")
    assert before == after, (before, after)
    assert not errors, errors
    browser.close()
print("PASS v416 real Units-route original-cap preview: 320/370/390/540, ownership, slot limit, no save writes")
