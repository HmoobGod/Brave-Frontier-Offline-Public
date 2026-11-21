"""v621: real packaged Home has readable *owned* 5+1 squad lineup on phones.

This checks the actual generated index.html, original Home/Status modules,
and disposable in-memory state, not only synthetic CSS text. It never loads
an owner's APK, screenshots or saved progress, and asserts no state writes.
"""
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
TEST = "test_bf_home_lineup_readability_v62100.py"
CSS = (ASSETS / "bf_home_nav.css").read_text("utf-8")
JS = (ASSETS / "bf_home_nav.js").read_text("utf-8")
HEADER = (ASSETS / "bf054_header_status.js").read_text("utf-8")
BUILD = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf-8")
PREFLIGHT = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf-8")
MANIFEST = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf-8")

MARK = "/* v621 owner Home P0: actual owned five-up unit portrait labels, phone readable."
assert CSS.count(MARK) == 1
assert "repeat(5,minmax(0,1fr))" in CSS, "keep five-plus-one owner-phone layout"
assert "max-height:24px" in CSS and "overflow-wrap:anywhere" in CSS
assert "bf-scene-leader" in CSS and "bf-scene-member" in CSS
assert "bf-scene-party" in JS and "bf-scene-leader" in JS
assert "roster.includes(baseId)" in JS and "!seen.has(baseId)" in JS
assert "homeTitle.after(sceneSquad)" in HEADER, "squad precedes Adventure"
assert BUILD.count("python3 " + TEST) == 1
assert PREFLIGHT.count(TEST) == 2, "path trigger plus source-only run"
# Story placement is selected by the pinned source, never inferred from the DOM.
V638_STORY_MOVE = "summonV638.insertAdjacentElement('afterend', storyV638);"
assert JS.count(V638_STORY_MOVE) in (0, 1)
STORY_MODE = "v638" if JS.count(V638_STORY_MOVE) == 1 else "legacy"
assert "android.permission.INTERNET" not in MANIFEST
assert len(CSS.encode("utf-8")) < 128 * 1024
assert len(JS.encode("utf-8")) < 128 * 1024
print("PASS v621 source: 5+1 owned Home art, readable styles, app CI registration, offline identity")
if "--source-only" in sys.argv:
    raise SystemExit(0)

from playwright.sync_api import sync_playwright

chrome = (shutil.which("chromium") or shutil.which("google-chrome")
          or shutil.which("google-chrome-stable"))
assert chrome, "Chromium required for live Home portrait readability"

html = (ASSETS / "index.html").read_text("utf-8")
assert "<head>" in html
html = html.replace("<head>", '<head><base href="http://bf-assets.test/">', 1)

def serve_local_art(route):
    relative = route.request.url.split("bf-assets.test/", 1)[-1].split("?", 1)[0]
    target = (ASSETS / relative).resolve()
    if target.is_relative_to(ASSETS.resolve()) and target.is_file() and target.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
        types = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
        route.fulfill(status=200, body=target.read_bytes(), content_type=types[target.suffix.lower()])
    else:
        route.fulfill(status=404, body=b"")

def snap(page):
    return page.evaluate("""()=>({
      p:JSON.stringify(P),s:JSON.stringify(S),quest:QUEST.missionId,
      writes:window.__v621Writes(),
      storage:Array.from({length:localStorage.length},(_,i)=>{
        const k=localStorage.key(i);return [k,localStorage.getItem(k)];
      }).sort((a,b)=>a[0].localeCompare(b[0]))
    })""")

with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=True, executable_path=chrome,
        args=["--no-sandbox", "--disable-dev-shm-usage"])
    try:
        for width in (320, 360, 393, 412, 540):
            page = browser.new_page(viewport={"width": width, "height": 844})
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.route("http://bf-assets.test/**", serve_local_art)
            try:
                page.evaluate("""() => {
                  const db={};let writes=0;
                  Object.defineProperty(window,"localStorage",{configurable:true,value:{
                    getItem:k=>db[k]??null,
                    setItem:(k,v)=>{writes++;db[k]=String(v)},
                    removeItem:k=>{writes++;delete db[k]},
                    key:i=>Object.keys(db)[i]??null,
                    get length(){return Object.keys(db).length}
                  }});
                  window.__v621Writes=()=>writes;
                  window.alert=()=>{};window.confirm=()=>true;
                  HTMLMediaElement.prototype.load=()=>{};
                  HTMLMediaElement.prototype.pause=()=>{};
                  HTMLMediaElement.prototype.play=()=>Promise.resolve();
                }""")
                page.set_content(html, wait_until="load", timeout=90000)
                page.add_style_tag(path=str(ASSETS / "bf_home_nav.css"))
                page.add_script_tag(path=str(ASSETS / "bf_home_nav.js"))
                page.add_script_tag(path=str(ASSETS / "bf054_header_status.js"))
                assert page.evaluate("P.version") == 7
                assert page.evaluate("BF_homeNav.current") == "home"
                assert page.evaluate("document.body.classList.contains('bf-menu-mode')")
                before = snap(page)
                lineup = page.locator("#bf-scene-party > .bf-scene-member")
                assert lineup.count() == 6, (width, lineup.count())
                assert page.locator("#bf-scene-party .bf-scene-leader").count() == 1
                assert page.locator("#bf-scene-party button.bf-scene-member").count() == 6
                order = page.evaluate("""(mode)=>{
                  const home=document.getElementById('bf-home'),fail=[];
                  const stories=document.querySelectorAll('.bf-scene-story');
                  const actions=document.querySelectorAll('#bf-home-story-open');
                  const story=stories[0],squad=home.querySelector(':scope > .bf-scene-squad');
                  const explore=home.querySelector(':scope > .bf-scene-explore');
                  const places=explore?.querySelector(':scope > .bf-scene-places');
                  if(stories.length!==1)fail.push('story nodes '+stories.length);
                  if(actions.length!==1||!story?.contains(actions[0]))fail.push('story actions '+actions.length);
                  if(!squad||!explore||!places)return {ok:false,mode,fail:fail.concat('missing squad/explore/places')};
                  const gates=[...places.querySelectorAll(':scope > button')];
                  const goto=gates.map(b=>b.dataset.bfGoto).join(',');
                  if(goto!=='quest,summon'||!gates.every(b=>b.classList.contains('bf-scene-featured')))fail.push('gateways '+goto);
                  const labels=places.querySelectorAll(':scope > .bf-scene-archive-label');
                  const label=labels[0],locked=[...places.querySelectorAll(':scope > .bf-scene-locked')];
                  if(labels.length!==1)fail.push('archive labels '+labels.length);
                  if(locked.length!==4)fail.push('locked '+locked.length);
                  if(label&&!locked.every(l=>(label.compareDocumentPosition(l)&Node.DOCUMENT_POSITION_FOLLOWING)!==0))fail.push('locked before label');
                  if(places.querySelectorAll('.bf-scene-locked').length!==locked.length)fail.push('nested locked');
                  if(story){
                    const prev=story.previousElementSibling,next=story.nextElementSibling;
                    if(mode==='legacy'){
                      if(story.parentElement!==home||prev!==squad||next!==explore)fail.push('legacy order');
                    }else if(mode==='v638'){
                      if(story.parentElement!==places||prev!==gates[1]||next!==label||home.querySelector(':scope > .bf-scene-story'))fail.push('v638 order');
                    }else fail.push('unknown mode');
                  }
                  return {ok:fail.length===0,mode,fail};
                }""", STORY_MODE)
                assert order["ok"] and order["mode"] == STORY_MODE, (width, order)
                proof = page.locator("#bf-scene-party").evaluate("""root=>{
                  const cards=[...root.children], boxes=cards.map(c=>c.getBoundingClientRect());
                  return {
                    boxCount:boxes.length,
                    cardWidth:boxes[0].width,
                    cardHeight:boxes[0].height,
                    firstRowSameTop:boxes.slice(0,5).every(b=>Math.abs(b.top-boxes[0].top)<=2),
                    sixthBelow:boxes[5].top>=boxes[0].bottom,
                    sixFull:cards[5].getAttribute("aria-label"),
                    nameFont:parseFloat(getComputedStyle(cards[0].querySelector("strong")).fontSize),
                    levelFont:parseFloat(getComputedStyle(cards[0].querySelector("small")).fontSize),
                    leaderFont:parseFloat(getComputedStyle(cards[0].querySelector(".bf-scene-leader")).fontSize),
                    nameMaxHeight:parseFloat(getComputedStyle(cards[0].querySelector("strong")).maxHeight),
                    nativePortraits:cards.slice(0,5).every(c=>c.querySelector("img, .bf-portrait-fallback")),
                    readableName:cards.slice(0,5).every(c=>
                      !!c.querySelector("strong")?.textContent.trim() &&
                      c.getAttribute("aria-label")?.startsWith("Inspect ")),
                    scroll:document.documentElement.scrollWidth,viewport:innerWidth
                  };
                }""")
                assert proof["nativePortraits"] and proof["readableName"], (width, proof)
                assert proof["scroll"] <= proof["viewport"] + 1, (width, proof)
                assert lineup.first.get_attribute("aria-label").find("Leader") >= 0
                if width <= 412:
                    assert proof["firstRowSameTop"] and proof["sixthBelow"], (width, proof)
                    assert proof["cardWidth"] >= 44 and proof["cardHeight"] >= 44, (width, proof)
                    assert proof["nameFont"] >= 10 and proof["levelFont"] >= 10, (width, proof)
                    assert proof["leaderFont"] >= 9, (width, proof)
                    assert proof["nameMaxHeight"] == 24, (width, proof)
                # Keyboard focus and returned route remain owned-unit actions.
                first = lineup.first
                first.focus()
                assert first.evaluate("(el)=>document.activeElement===el")
                assert snap(page) == before, (width, "refresh/focus mutated player/save")
                assert not errors, (width, errors)
                print("PASS v621 live Home", width, "px labels", proof["nameFont"],
                      proof["levelFont"], "leader", proof["leaderFont"])
            finally:
                page.close()
    finally:
        browser.close()
print("PASS v621: actual Home squad 5+1 art/readability/keyboard, five phone widths, unchanged v7; "
      f"Story order {STORY_MODE} (source-selected), 1 Story/action, Quest->Summon, 4 locked")
