"""v124: Verify live level-one demo units exactly match 2022 Global base stats.
This is a guard for future authentic growth work, NOT EXP migration or native mid-level math.
"""
import json
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

R = Path(__file__).resolve().parent
A = R / "app/src/main/assets"
manifest = json.loads((R / "source_data/bf_global_2022_playable_lord_stat_endpoints_v116.json").read_text("utf8"))
assert manifest["schema"] == "bf-global-2022-playable-lord-stat-endpoints-v116"
assert manifest["unitCount"] == 72
assert manifest["source"]["archiveSha256"] == "69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
reference = {row["unitId"]: row for row in manifest["rows"]}
assert len(reference) == 72
assert all(row["expPatternId"] in (10, 15, 20) for row in reference.values())

# Earlier verified generation stages add evolved forms to the APK-bound HTML.
# Fail rather than checking only the old pre-preparation subset of playable forms.
html = (A / "index.html").read_text("utf8")
def array_from_inline_html(name):
    marker = "window." + name + "="
    assert html.count(marker) == 1, name
    start = html.index(marker) + len(marker)
    end = html.index("];", start) + 1
    return json.loads(html[start:end])

starters = array_from_inline_html("BF_STARTER_UNITS")
evolved = array_from_inline_html("BF_EVOLVED_UNITS")
assert len(starters) == 18 and len(evolved) == 54, (len(starters), len(evolved))
units = starters + evolved
ids = [row["id"] for row in units]
assert len(ids) == len(set(ids)) == 72
assert set(ids) == set(reference)
assert all(u["id"] // 10 * 10 + 1 in {s["id"] for s in starters} for u in units)

for unit in units:
    original = reference[unit["id"]]
    assert original["maxLevel"] >= 1
    assert all(type(unit["stats"][k]) is int for k in ("hp", "atk", "def", "rec"))
    assert {k: unit["stats"][k] for k in ("hp", "atk", "def", "rec")} == original["base"], unit["id"]

# Exercise the actual battle-unit constructor, not just two matching data dumps.
# All mutations here are temporary in a disposable Chromium test page.
expected = [{"id": uid, "baseId": uid // 10 * 10 + 1, "stats": reference[uid]["base"]}
            for uid in sorted(reference)]
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        headless=True,
        executable_path=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable"),
        args=["--no-sandbox", "--disable-dev-shm-usage"])
    page = browser.new_page(viewport={"width": 390, "height": 844})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    # about:blank denies localStorage without a controlled stub; match existing UI regressions.
    page.evaluate("""() => {
      const db={};
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:k=>db[k]??null,setItem:(k,v)=>{db[k]=String(v)},
        removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
        get length(){return Object.keys(db).length}
      }});
      window.alert=()=>{};window.confirm=()=>true;
      HTMLMediaElement.prototype.load=()=>{};
      HTMLMediaElement.prototype.pause=()=>{};
      HTMLMediaElement.prototype.play=()=>Promise.resolve();
    }""")
    page.set_content(html, wait_until="load", timeout=90000)
    result = page.evaluate("""rows => {
      if (P.version !== 7 || typeof playerUnit !== 'function' ||
          typeof effectiveUnit !== 'function' || typeof demoLevel !== 'function')
        return {error: 'Missing original demo runtime or v7 save'};
      const saved = JSON.stringify(P), key='bf_global_offline_demo_v7';
      const savedStorage=localStorage.getItem(key);
      const old={squad:[...P.squad],roster:[...P.roster],
        evolutions:{...P.evolutions},unitExp:{...P.unitExp}};
      const mismatches=[];
      try {
        for (const row of rows) {
          P.squad[0]=row.baseId;
          P.unitExp[row.baseId]=0;
          if (row.id===row.baseId) delete P.evolutions[row.baseId];
          else P.evolutions[row.baseId]=row.id;
          const actual=playerUnit(0), stats=row.stats;
          if (!actual.active || actual.unitId!==row.id || actual.level!==1 ||
              actual.hp!==stats.hp || actual.maxHp!==stats.hp ||
              actual.atk!==stats.atk || actual.def!==stats.def || actual.rec!==stats.rec)
            mismatches.push({unitId:row.id,actual,stats});
        }
      } finally {
        P.squad=old.squad;P.roster=old.roster;
        P.evolutions=old.evolutions;P.unitExp=old.unitExp;
      }
      return {count:rows.length,mismatches,
        progressUnchanged:JSON.stringify(P)===saved,
        storageUnchanged:localStorage.getItem(key)===savedStorage,
        expFormulaUnchanged:demoLevel(0)===1 && demoLevel(5)===2,
        schema:P.version};
    }""", expected)
    assert result.get("count") == 72, result
    assert result["mismatches"] == [], result["mismatches"][:3]
    assert result["progressUnchanged"] and result["storageUnchanged"], result
    assert result["expFormulaUnchanged"] and result["schema"] == 7, result
    assert not errors, errors
    browser.close()
print("PASS v124: 72 original Global level-one base stat blocks equal live battle constructor; demo EXP, v7 state and storage unchanged")
