"""v623: real packaged Home sixth owned squad label/portrait uses accessible geometry.

This checks the actual generated index.html, original Home/Status modules,
and disposable in-memory state, not only synthetic CSS text. It never loads
an owner's APK, screenshots or saved progress, and asserts no state writes.
"""
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
TEST = "test_bf_home_sixth_slot_readability_v62300.py"
CSS = (ASSETS / "bf_home_nav.css").read_text("utf-8")
JS = (ASSETS / "bf_home_nav.js").read_text("utf-8")
HEADER = (ASSETS / "bf054_header_status.js").read_text("utf-8")
BUILD = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf-8")
PREFLIGHT = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf-8")
MANIFEST = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf-8")

# v636 ships the original 320-412px compact-sixth marker. v639 carries
# that same behavior forward into its 320-540px owner viewport layout.
# The exact verified JS layout marker chooses the acceptable CSS marker;
# accepting either variant blindly would weaken this source fidelity gate.
MARK = "/* v623 owner Home P0: readable sixth owned-squad card on 320-412px screens."
NEW_MARK = "/* v623/v638 owner Home P0: readable compact sixth owned-squad card on"
QUEST_FIRST_STORY = "// v638 local: keep the exact live Story node" in JS
if QUEST_FIRST_STORY:
    assert CSS.count(MARK)==0 and CSS.count(NEW_MARK)==1, "v639 320-540 compact sixth marker"
    assert "@media(max-width:540px)" in CSS, "v639 must support 540px compact sixth"
    assert "#bf-home.bf-home-v636 #bf-scene-party>.bf-scene-member:nth-child(6)" in CSS
else:
    assert CSS.count(MARK)==1 and CSS.count(NEW_MARK)==0, "v636 original v623 marker"
assert "repeat(5,minmax(0,1fr))" in CSS, "keep five-plus-one owner-phone layout"
assert "max-height:24px" in CSS and "overflow-wrap:anywhere" in CSS
assert "bf-scene-leader" in CSS and "bf-scene-member" in CSS
assert "bf-scene-party" in JS and "bf-scene-leader" in JS
assert "roster.includes(baseId)" in JS and "!seen.has(baseId)" in JS
assert "homeTitle.after(sceneSquad)" in HEADER, "squad precedes Adventure"
assert BUILD.count("python3 " + TEST) == 1
assert PREFLIGHT.count(TEST) == 2, "path trigger plus source-only run"
assert "grid-template-columns:minmax(58px,max-content) 56px minmax(0,1fr)" in CSS
assert "button.bf-scene-member:nth-child(6) strong" in CSS
assert "button.bf-scene-member:nth-child(6) small" in CSS
assert BUILD.count("python3 test_bf_home_lineup_readability_v62100.py") == 1
assert PREFLIGHT.count("test_bf_home_lineup_readability_v62100.py") == 2
assert "android.permission.INTERNET" not in MANIFEST
assert len(CSS.encode("utf-8")) < 128 * 1024
assert len(JS.encode("utf-8")) < 128 * 1024
print("PASS v623 source: 5+1 owned Home art, readable styles, app CI registration, offline identity")
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
      writes:window.__v623Writes(),
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
                  window.__v623Writes=()=>writes;
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
                layout=page.evaluate("""()=>{
                  const home=document.getElementById('bf-home');
                  const squad=home.querySelector('.bf-scene-squad'),
                    story=home.querySelector('.bf-scene-story'),
                    explore=home.querySelector('.bf-scene-explore'),
                    places=explore?.querySelector(':scope > .bf-scene-places'),
                    summon=places?.querySelector(':scope > button.bf-scene-featured[data-bf-goto="summon"]'),
                    archive=places?.querySelector(':scope > .bf-scene-archive-label');
                  return {
                    squadBeforeStory:!!(squad&&story&&(squad.compareDocumentPosition(story)&Node.DOCUMENT_POSITION_FOLLOWING)),
                    originalStoryBeforeExplore:!!(story&&explore&&(story.compareDocumentPosition(explore)&Node.DOCUMENT_POSITION_FOLLOWING)),
                    newExploreBeforeStory:!!(explore&&story&&(explore.compareDocumentPosition(story)&Node.DOCUMENT_POSITION_FOLLOWING)),
                    storyCount:home.querySelectorAll('.bf-scene-story').length,
                    oldSibling:story?.parentElement===home&&story?.nextElementSibling===explore,
                    newNested:story?.parentElement===places&&story?.previousElementSibling===summon&&story?.nextElementSibling===archive,
                    archiveCount:home.querySelectorAll('.bf-scene-archive-label').length,
                    activeRoutes:places?.querySelectorAll(':scope > button.bf-scene-featured[data-bf-goto]').length,
                    locked:places?.querySelectorAll(':scope > .bf-scene-locked').length
                  };
                }""")
                assert layout['squadBeforeStory'] and layout['storyCount']==1, (width,layout)
                assert layout['archiveCount']==1 and layout['activeRoutes']==2 and layout['locked']==4,(width,layout)
                if QUEST_FIRST_STORY:
                    assert layout['newExploreBeforeStory'] and layout['newNested'] and not layout['oldSibling'],(width,layout)
                else:
                    assert layout['originalStoryBeforeExplore'] and layout['oldSibling'] and not layout['newNested'],(width,layout)
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
                # Option A uses a compact, source-derived single-line name, not
                # the obsolete v623 two-line 24px box. Prove actual visibility
                # and complete identity without weakening squad/focus/save checks.
                assert proof["nameMaxHeight"] == (16 if width >= 510 else 14), (width, proof)
                label_proof = lineup.evaluate_all("""cards=>cards.slice(0,5).map((card,index)=>{
                  const node=card.querySelector('strong');
                  const id=Number(card.dataset.bfHomeUnitId);
                  const original=effectiveUnit(id)?.name;
                  const visible=node?.textContent.trim()||'';
                  const sourceWord=typeof original==='string' ? original.trim().split(/\\s+/u).pop() : '';
                  const marker=visible.match(/ ·([1-5])$/u);
                  const core=marker ? visible.slice(0,-marker[0].length) : visible;
                  const stem=core.endsWith('…') ? core.slice(0,-1) : core;
                  const truthful=core===sourceWord || (
                    core.endsWith('…') && Array.from(stem).length>=3 &&
                    sourceWord.startsWith(stem));
                  const style=node && getComputedStyle(node);
                  const box=node?.getBoundingClientRect();
                  const range=document.createRange();
                  if(node)range.selectNodeContents(node);
                  const ink=range.getBoundingClientRect();
                  return {truthful:!!truthful,
                    completeAria:typeof original==='string' &&
                      card.getAttribute('aria-label')?.startsWith('Inspect '+original+','),
                    markerCorrect:!marker || Number(marker[1])===index+1,
                    oneLine:!!style && style.whiteSpace==='nowrap' &&
                      parseFloat(style.lineHeight)<=node.clientHeight+1,
                    visible:!!box && box.width>0 && box.height>0 &&
                      node.scrollWidth<=node.clientWidth+1 &&
                      node.scrollHeight<=node.clientHeight+1 &&
                      ink.left>=box.left-1 && ink.right<=box.right+1 &&
                      ink.top>=box.top-1 && ink.bottom<=box.bottom+1,
                    font:style?parseFloat(style.fontSize):0,
                    shown:visible, original};
                })""")
                assert len(label_proof) == 5 and all(
                    p["truthful"] and p["completeAria"] and p["markerCorrect"] and
                    p["oneLine"] and p["visible"] and p["font"] >= 10
                    for p in label_proof), (width, label_proof)
                sixth = lineup.nth(5)
                assert sixth.get_attribute("aria-label").startswith("Inspect "), width
                sixth_proof = sixth.evaluate("""el => {
                  const portrait = el.querySelector("img, .bf-portrait-fallback");
                  const name = el.querySelector("strong"), level = el.querySelector("small");
                  const slot = el.querySelector(".bf-scene-slot");
                  const eb = el.getBoundingClientRect(), pb = portrait?.getBoundingClientRect();
                  const nb = name?.getBoundingClientRect(), lb = level?.getBoundingClientRect();
                  return {
                    display:getComputedStyle(el).display,
                    width:eb.width,height:eb.height,
                    viewport:innerWidth,
                    left:eb.left,right:eb.right,
                    artRight:pb?.right??-1,artHeight:pb?.height??0,
                    nameLeft:nb?.left??-1,nameRight:nb?.right??-1,
                    nameFont:parseFloat(getComputedStyle(name).fontSize),
                    nameText:name?.textContent.trim()||"",
                    levelLeft:lb?.left??-1,
                    levelFont:parseFloat(getComputedStyle(level).fontSize),
                    levelText:level?.textContent.trim()||"",
                    slotFont:parseFloat(getComputedStyle(slot).fontSize),
                    slotText:slot?.textContent.trim()||"",
                    horizontalScroll:document.documentElement.scrollWidth
                  };
                }""")
                assert sixth_proof["nameText"] and sixth_proof["levelText"], (width, sixth_proof)
                assert "SLOT 6" in sixth_proof["slotText"], (width, sixth_proof)
                assert sixth_proof["horizontalScroll"] <= width + 1, (width, sixth_proof)
                if width <= 412 or (QUEST_FIRST_STORY and width == 540):
                    assert sixth_proof["display"] == "grid", (width, sixth_proof)
                    assert sixth_proof["height"] >= 62, (width, sixth_proof)
                    assert sixth_proof["artHeight"] >= 40, (width, sixth_proof)
                    assert sixth_proof["nameFont"] >= 11, (width, sixth_proof)
                    assert sixth_proof["levelFont"] >= 10, (width, sixth_proof)
                    assert sixth_proof["slotFont"] >= 10, (width, sixth_proof)
                    assert sixth_proof["nameLeft"] >= sixth_proof["artRight"] - 2, (width, sixth_proof)
                    assert sixth_proof["levelLeft"] >= sixth_proof["artRight"] - 2, (width, sixth_proof)
                    assert sixth_proof["left"] >= -1 and sixth_proof["right"] <= width + 1, (width, sixth_proof)
                sixth.focus()
                assert sixth.evaluate("(el)=>document.activeElement===el"), (width, "sixth focus")
                # Switch into keyboard modality and return to the sixth owned tile;
                # the real focus-visible ring must be visible to keyboard users.
                page.keyboard.press("Shift+Tab")
                page.keyboard.press("Tab")
                if width <= 412 or (QUEST_FIRST_STORY and width == 540):
                    focus = sixth.evaluate("""el => ({
                      active:document.activeElement===el,
                      visible:el.matches(":focus-visible"),
                      width:parseFloat(getComputedStyle(el).outlineWidth),
                      style:getComputedStyle(el).outlineStyle
                    })""")
                    assert focus["active"] and focus["visible"], (width, focus)
                    assert focus["width"] >= 3 and focus["style"] != "none", (width, focus)
                assert snap(page) == before, (width, "sixth focus mutated v7")

                # Regression against v268: the real original-art fallback on
                # sixth owned slot must keep NO ART on ONE line at 320-412px.
                # The earlier 40px grid column split it into NO / ART.
                if width <= 412 or (QUEST_FIRST_STORY and width == 540):
                    sixth.evaluate("""el => {
                      const image=el.querySelector("img");
                      if(image) image.dispatchEvent(new Event("error"));
                    }""")
                    fallback = sixth.locator(".bf-portrait-fallback")
                    assert fallback.count() == 1 and fallback.is_visible(), width
                    assert fallback.inner_text() == "NO ART", width
                    fallback_geometry = fallback.evaluate("""e => {
                      const t=e.firstChild, ys=[];
                      for(let i=0;i<t.length;i++){
                        const range=document.createRange();
                        range.setStart(t,i);range.setEnd(t,i+1);
                        ys.push(Math.round(range.getBoundingClientRect().y));
                      }
                      const f=e.getBoundingClientRect();
                      const parent=e.parentElement.getBoundingClientRect();
                      return {
                        lines:new Set(ys).size,
                        font:parseFloat(getComputedStyle(e).fontSize),
                        scroll:e.scrollWidth,client:e.clientWidth,
                        scrollHeight:e.scrollHeight,clientHeight:e.clientHeight,
                        left:f.left,right:f.right,
                        parentLeft:parent.left,parentRight:parent.right
                      };
                    }""")
                    assert fallback_geometry["lines"] == 1, (width, fallback_geometry)
                    assert fallback_geometry["font"] >= 11, (width, fallback_geometry)
                    assert fallback_geometry["scroll"] <= fallback_geometry["client"] + 1, (width, fallback_geometry)
                    assert fallback_geometry["scrollHeight"] <= fallback_geometry["clientHeight"] + 1, (width, fallback_geometry)
                    assert fallback_geometry["left"] >= fallback_geometry["parentLeft"] - 1, (width, fallback_geometry)
                    assert fallback_geometry["right"] <= fallback_geometry["parentRight"] + 1, (width, fallback_geometry)
                    assert snap(page) == before, (width, "portrait fallback mutated owner v7")

                # Keyboard focus and returned route remain owned-unit actions.
                first = lineup.first
                first.focus()
                assert first.evaluate("(el)=>document.activeElement===el")
                assert snap(page) == before, (width, "refresh/focus mutated player/save")
                assert not errors, (width, errors)
                print("PASS v623 live Home", width, "px labels", proof["nameFont"],
                      proof["levelFont"], "leader", proof["leaderFont"])
            finally:
                page.close()
    finally:
        browser.close()
print("PASS v623: actual Home squad 5+1 art/readability/keyboard, five phone widths, unchanged v7")
