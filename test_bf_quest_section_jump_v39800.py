"""v398: Quest route section jump bar; Chromium only, never an owner's Android save.
The bar is a reconstructed offline convenience (not claimed 2022 parity). It may
only scroll: no mission selection, no battle start, no save/player/battle writes.
"""
from pathlib import Path
import re
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
A = ROOT / "app/src/main/assets"
SCRIPT = A / "bf39800_quest_section_jump.js"
JAVA = ROOT / "app/src/main/java/org/bravefrontier/offline/MainActivity.java"

js = SCRIPT.read_text(encoding="utf-8")
native = JAVA.read_text(encoding="utf-8")
chain = re.findall(r'readPackagedText\("([^"]+\.js)"\)', native)
assert chain.count("bf39800_quest_section_jump.js") == 1
assert chain[-1] == "bf39800_quest_section_jump.js", "Must load after every Quest panel"
assert "bf_global_offline_demo_v7" not in js
for forbidden in ("localStorage", "sessionStorage", "saveProgress(", "awardDemoRewards(",
                  "P.squad", "P.questClears", "P.lastMission", "QUEST=", ".click()",
                  "startBattle", "S.busy", "reset("):
    assert forbidden not in js, forbidden
assert "BF_homeNav" in js and "bf-route-change" in js
assert len(js.encode("utf-8")) < 16384
chrome = (shutil.which("google-chrome") or shutil.which("google-chrome-stable")
          or shutil.which("chromium"))
assert chrome, "Chromium required for Quest section jump regression"

EXPECTED = ["story", "map", "areas", "mission", "live", "list", "battle", "squad"]

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=chrome,
                                 args=["--no-sandbox", "--disable-dev-shm-usage"])
    page = browser.new_page(viewport={"width": 390, "height": 844})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.evaluate("""() => {
      const data = {};
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem(k){return data[k]??null},
        setItem(k,v){data[k]=String(v)},
        removeItem(k){delete data[k]},
        key(i){return Object.keys(data)[i]??null},
        get length(){return Object.keys(data).length}
      }});
      window.alert=()=>{};window.confirm=()=>true;
    }""")
    page.set_content((A / "index.html").read_text(encoding="utf-8"),
                     wait_until="load", timeout=60000)
    page.add_style_tag(path=str(A / "bf_home_nav.css"))
    page.add_script_tag(path=str(A / "bf_home_nav.js"))
    # Stand-ins for optional Quest panels from other modules, so this test
    # exercises every jump target without depending on their packaging.
    page.evaluate("""() => {
      const panel = document.querySelector('section.questpanel');
      const add = (html) => panel.insertAdjacentHTML('afterbegin', html);
      add('<section id="bf2000-run" style="height:900px">live</section>');
      add('<section id="bf-quest-details" style="height:600px">details</section>');
      add('<section class="bf-quest-areas" style="height:1500px">areas</section>');
      add('<section class="bf-mistral-map" style="height:1200px">map</section>');
      add('<section id="bf101-story-continue" style="height:400px">story</section>');
    }""")
    state = page.evaluate("""() => ({
      save:localStorage.getItem('bf_global_offline_demo_v7'),
      player:JSON.stringify(P),
      quest:JSON.stringify(QUEST),
      battle:typeof S==='undefined'?null:JSON.stringify(S)
    })""")
    page.add_script_tag(path=str(SCRIPT))
    page.add_script_tag(path=str(SCRIPT))
    bar = page.locator("#bf39800-quest-jump")
    assert bar.count() == 1, "Idempotent load"
    assert page.evaluate("BF_homeNav.current") == "home"
    assert not bar.is_visible(), "Hidden off the Quest route"
    assert page.evaluate("BFQuestSectionJumpV39800.jump('list')") is False

    page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
    assert page.evaluate("BF_homeNav.current") == "quest"
    assert bar.is_visible()
    assert page.evaluate("BFQuestSectionJumpV39800.offered") == EXPECTED
    # Mounted outside .questpanel (which clips overflow) so it can stick.
    assert page.evaluate("""() => {
      const b = document.getElementById('bf39800-quest-jump');
      return !b.closest('.questpanel') && b.nextElementSibling.matches('section.questpanel');
    }""")

    for width in (320, 390, 540):
        page.set_viewport_size({"width": width, "height": 844})
        page.evaluate("scrollTo(0,0)")
        page.evaluate("BFQuestSectionJumpV39800.refresh()")
        doc = page.evaluate("""() => ({sw:document.documentElement.scrollWidth,
                                       w:document.documentElement.clientWidth})""")
        b = bar.evaluate("e => {const r=e.getBoundingClientRect();return {l:r.left,r:r.right}}")
        assert 0 <= b["l"] and b["r"] <= width + 1, (width, b)
        heights = page.locator("#bf39800-quest-jump button").evaluate_all(
            "bs => bs.map(b => b.getBoundingClientRect().height)")
        assert min(heights) >= 44, (width, heights)
        for key in EXPECTED:
            button = page.locator(f'#bf39800-quest-jump [data-bf-jump="{key}"]')
            button.scroll_into_view_if_needed()
            button.click()
            page.wait_for_timeout(60)
            r = page.evaluate("""key => {
              const head = document.querySelector('.bf-shell-head').getBoundingClientRect();
              const b = document.getElementById('bf39800-quest-jump');
              const br = b.getBoundingClientRect();
              const cur = b.querySelector('[aria-current="location"]');
              return {head:head.bottom, top:br.top, bottom:br.bottom, pos:b.style.position,
                      cur:cur && cur.dataset.bfJump, y:scrollY}
            }""", key)
            assert r["cur"] == key, (width, key, r)
            if key in ("battle", "squad"):
                # Never floats over live combat controls.
                assert r["pos"] == "relative" and r["bottom"] <= r["head"] + 1, (width, key, r)
            else:
                assert r["pos"] == "sticky" and abs(r["top"] - r["head"]) <= 1, (width, key, r)
        assert doc["sw"] <= doc["w"] + 1, (width, doc)

    # Hidden targets are not offered; leaving Quest hides the bar again.
    page.evaluate("document.getElementById('bf2000-run').hidden = true")
    page.evaluate("BFQuestSectionJumpV39800.refresh()")
    assert "live" not in page.evaluate("BFQuestSectionJumpV39800.offered")
    assert page.evaluate("BFQuestSectionJumpV39800.jump('live')") is False
    page.locator('.bf-navbar button[data-bf-goto="home"]').click()
    assert page.evaluate("BF_homeNav.current") == "home"
    assert not bar.is_visible()

    after = page.evaluate("""() => ({
      save:localStorage.getItem('bf_global_offline_demo_v7'),
      player:JSON.stringify(P),
      quest:JSON.stringify(QUEST),
      battle:typeof S==='undefined'?null:JSON.stringify(S)
    })""")
    assert after == state, (state, after)
    assert not errors, errors
    browser.close()
print("PASS v398 Quest section jump: 8 targets, sticky outside clipped panel, un-sticks over combat, 320/390/540px, no save/player/quest/battle mutations")
