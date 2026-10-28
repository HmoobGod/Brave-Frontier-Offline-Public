"""v163: browser-prove first-clear metadata loss across an older APK save.

Two actual repository HTML parsers run independently in Chromium:
* prepared v161+ bundled HTML (canonical v7 save with original Gem metadata)
* checked-in, unpatched pre-v160 parser (representative older schema)
No signed Android APK or owner's localStorage is modified.
"""
from pathlib import Path
import json
import shutil
import subprocess
from playwright.sync_api import sync_playwright

R = Path(__file__).resolve().parent
KEY = "bf_global_offline_demo_v7"
current = (R / "app/src/main/assets/index.html").read_text(encoding="utf8")
legacy = subprocess.run(
    ["git", "show", "HEAD:app/src/main/assets/index.html"],
    cwd=R, check=True, capture_output=True, text=True
).stdout
assert "BF_GLOBAL_GEM_V160_ORIGINAL_CLEAR_LEDGER" in current
assert "BF_GLOBAL_GEM_V161_NEW_FIRST_CLEAR_PENDING" in current
assert "BF_GLOBAL_GEM_V160_ORIGINAL_CLEAR_LEDGER" not in legacy
assert "BF_GLOBAL_GEM_V161_NEW_FIRST_CLEAR_PENDING" not in legacy
assert KEY in current and KEY in legacy
assert "function parseProgress(" in current and "function parseProgress(" in legacy

with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=True,
        executable_path=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable"),
        args=["--no-sandbox", "--disable-dev-shm-usage"]
    )
    errors = []

    def new_page(document):
        page = browser.new_page(viewport={"width":390,"height":844})
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.evaluate("""()=>{
            const db={}; window.__v163storage=db; window.__v163writes=[];
            Object.defineProperty(window,'localStorage',{configurable:true,value:{
                getItem:k=>db[k]??null,
                setItem:(k,v)=>{window.__v163writes.push(k);db[k]=String(v)},
                removeItem:k=>{window.__v163writes.push(k);delete db[k]},
                key:i=>Object.keys(db)[i]??null,
                get length(){return Object.keys(db).length}
            }});
            window.alert=()=>{}; window.confirm=()=>true;
            HTMLMediaElement.prototype.load=()=>{};
            HTMLMediaElement.prototype.pause=()=>{};
            HTMLMediaElement.prototype.play=()=>Promise.resolve();
        }""")
        page.set_content(document, wait_until="load", timeout=90000)
        assert page.evaluate("P.version") == 7
        return page

    modern = new_page(current)
    assert modern.evaluate("QUESTS.length") == 106
    assert modern.evaluate("P._bfGemV161Pending") == []
    modern.evaluate("QUEST=QUESTS.find(q=>q.missionId===12);awardDemoRewards()")
    assert modern.evaluate("P.questClears[12]") == 1
    assert modern.evaluate("P._bfGemV161Pending") == [12]
    before = modern.evaluate(f"localStorage.getItem('{KEY}')")
    saved = json.loads(before)
    assert saved["_bfGemV161Pending"] == [12]
    assert saved["_bfGemV160"]["legacyFinales"] == [12]
    assert saved["_bfGemV160"]["balance"] == 0
    assert saved["_bfGemV160"]["paidFinales"] == []

    # A representative older parser preserves the quest clear, but silently
    # drops the future metadata when its next save is written.
    old = new_page(legacy)
    old.evaluate("raw=>{P=parseProgress(JSON.parse(raw))}", before)
    assert old.evaluate("P.questClears[12]") == 1
    assert old.evaluate("Object.prototype.hasOwnProperty.call(P,'_bfGemV161Pending')") is False
    assert old.evaluate("Object.prototype.hasOwnProperty.call(P,'_bfGemV160')") is False
    assert old.evaluate("saveProgress()") is True
    downgraded = old.evaluate(f"localStorage.getItem('{KEY}')")
    assert downgraded is not None
    downgraded_data = json.loads(downgraded)
    assert downgraded_data["questClears"]["12"] == 1
    assert "_bfGemV161Pending" not in downgraded_data
    assert "_bfGemV160" not in downgraded_data
    assert set(old.evaluate("__v163writes")) == {KEY}

    # Re-upgrading cannot reconstruct a previous pending FIRST clear just
    # from questClears. It may safely reconstruct legacy clear history.
    modern.evaluate("raw=>{P=parseProgress(JSON.parse(raw))}", downgraded)
    assert modern.evaluate("P.questClears[12]") == 1
    assert modern.evaluate("P._bfGemV160.legacyFinales") == [12]
    assert modern.evaluate("P._bfGemV161Pending") == []
    modern.evaluate("QUEST=QUESTS.find(q=>q.missionId===12);awardDemoRewards()")
    assert modern.evaluate("P.questClears[12]") == 2
    assert modern.evaluate("P._bfGemV161Pending") == []
    assert modern.evaluate("P._bfGemV160.balance") == 0

    # The separate user-exported JSON from before downgrade is sufficient
    # to restore the correct pending metadata without a Gem payout.
    modern.evaluate("raw=>{P=parseProgress(JSON.parse(raw))}", before)
    assert modern.evaluate("P.questClears[12]") == 1
    assert modern.evaluate("P._bfGemV161Pending") == [12]
    assert modern.evaluate("saveProgress()") is True
    assert json.loads(modern.evaluate(f"localStorage.getItem('{KEY}')"))["_bfGemV161Pending"] == [12]
    assert set(modern.evaluate("__v163writes")) == {KEY}
    assert not errors, errors
    browser.close()

print("PASS v163: actual old/new HTML parser downgrade-roundtrip; export restores pending, no payouts")
