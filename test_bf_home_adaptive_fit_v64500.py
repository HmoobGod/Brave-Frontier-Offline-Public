"""v645 R4: measured adaptive Home fit, full app, real module order and original PNGs.

Checks 6 viewports x 3 text scales (18 cases). The text scale is SYNTHETIC: the
test multiplies every element's computed font-size (and px line-height) by
1.0 / 1.15 / 1.3 and then dispatches a resize so the fit re-measures. That is an
approximation of Android WebView textZoom, NOT textZoom itself (MainActivity
does not call setTextZoom; on device the system font scale applies before the
page loads, so the initial fit handles it). A PASS is not owner-device
acceptance and not 2022 pixel parity.
"""
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
CSS = (ASSETS / "bf_home_nav.css").read_text("utf-8")
NAV = (ASSETS / "bf_home_nav.js").read_text("utf-8")
FIT_JS = (ASSETS / "bf_home_battle_readiness_v420.js").read_text("utf-8")
ACTIVITY = (ROOT / "app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf-8")
MANIFEST = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf-8")

assert "android.permission.INTERNET" not in MANIFEST
assert "setTextZoom" not in ACTIVITY  # system text scaling is never overridden
assert FIT_JS.count("/* v645 measured Home fit") == 1
fit_src = FIT_JS.split("/* v645 measured Home fit", 1)[1]
for forbidden in ("localStorage", "saveProgress(", "saveGame(", "P.", "S.", "fetch(", "textZoom",
                  "font-size", "fontSize", ".hidden=", "display='none'", 'display="none"', "BF_homeNav.go("):
    assert forbidden not in fit_src, forbidden
assert CSS.count("/* v645 measured fit levels") == 1
fit_css = CSS.split("/* v645 measured fit levels", 1)[1]
for forbidden in ("display:none", "visibility:hidden", "font-size", "font:", "-webkit-line-clamp", "text-overflow"):
    assert forbidden not in fit_css, forbidden
for path, limit in ((ASSETS / "bf_home_nav.css", 128 * 1024), (ASSETS / "bf_home_nav.js", 128 * 1024),
                    (ASSETS / "bf_home_battle_readiness_v420.js", 64 * 1024)):
    assert path.stat().st_size < limit, (path.name, path.stat().st_size)
print("PASS v645 source: measured fit is presentation-only, no text-zoom override, budgets kept")
if "--source-only" in sys.argv:
    raise SystemExit(0)

from playwright.sync_api import sync_playwright

chrome = shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "Chromium is required"
HTML = (ASSETS / "index.html").read_text("utf-8").replace(
    "<head>", '<head><base href="http://bf-assets.test/">', 1)
from bf_home_test_module_order import ART, home_modules, assert_exact_home_art, exercise_exact_form_and_missing_art
MODULES = home_modules(ACTIVITY, ASSETS)
TYPES = {".png": "image/png", ".jpg": "image/jpeg"}


def serve(route):
    rel = route.request.url.split("bf-assets.test/", 1)[-1].split("?", 1)[0]
    file = ASSETS / rel
    if file.suffix in TYPES and file.is_file() and file.resolve().is_relative_to(ASSETS.resolve()):
        route.fulfill(status=200, body=file.read_bytes(), content_type=TYPES[file.suffix])
    else:
        route.fulfill(status=404, body=b"")


def open_app(browser, width, height, *, before_load=None):
    page = browser.new_page(viewport={"width": width, "height": height})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.route("http://bf-assets.test/**", serve)
    if before_load is not None:
        before_load(page)
    page.evaluate("""() => {const db={};let w=0;window.__v645Writes=()=>w;
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:k=>db[k]??null,setItem:(k,v)=>{w++;db[k]=String(v)},removeItem:k=>{w++;delete db[k]},
        key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});
      window.alert=()=>{};window.confirm=()=>true;
      HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
      HTMLMediaElement.prototype.play=()=>Promise.resolve();}""")
    page.set_content(HTML, wait_until="load", timeout=120000)
    for module in MODULES:
        if module.endswith(".css"):
            page.add_style_tag(path=str(ASSETS / module))
        else:
            page.add_script_tag(path=str(ASSETS / module))
    if ART in MODULES and before_load is None:
        assert_exact_home_art(page, starter_fixture=True)
    return page, errors


SYNTHETIC_TEXT_SCALE = """(k)=>{if(k===1)return;const seen=window.__v645Scaled||(window.__v645Scaled=new WeakSet());
  for(const e of document.querySelectorAll('body *')){if(seen.has(e))continue;seen.add(e);
  const c=getComputedStyle(e),fs=parseFloat(c.fontSize);if(fs)e.style.setProperty('font-size',(fs*k)+'px','important');
  if(c.lineHeight.endsWith('px'))e.style.setProperty('line-height',(parseFloat(c.lineHeight)*k)+'px','important');}}"""
SNAPSHOT = "()=>({p:JSON.stringify(P),s:JSON.stringify(S),w:window.__v645Writes()})"
HITS = """(el)=>{const r=el.getBoundingClientRect();let ok=0;for(let i=0;i<5;i++)for(let j=0;j<5;j++){
  const e=document.elementFromPoint(r.left+3+(r.width-6)*i/4,r.top+3+(r.height-6)*j/4);if(e&&(e===el||el.contains(e)))ok++;}return ok}"""
MEASURE = """()=>{const h=document.getElementById('bf-home'),nav=document.querySelector('.bf-navbar').getBoundingClientRect();
  const q=h.querySelector('.bf-home-play button.bf-scene-featured[data-bf-goto="quest"]'),qr=q.getBoundingClientRect();
  const cards=[...h.querySelectorAll('#bf-scene-party > .bf-scene-member')].map((c,i)=>{const s=c.querySelector('strong'),l=c.querySelector('small'),
    r=c.getBoundingClientRect(),sr=s.getBoundingClientRect(),lr=l.getBoundingClientRect(),a=c.querySelector(':scope > img,:scope > .bf-portrait-fallback');
    return {i,id:Number(c.dataset.bfHomeUnitId),squad:P.squad[i],shown:s.textContent,full:effectiveUnit(P.squad[i])?.name,
      aria:c.getAttribute('aria-label')||'',leader:!!c.querySelector('.bf-scene-leader'),art:a?a.getBoundingClientRect().width:0,
      nameOk:s.scrollWidth<=s.clientWidth+1&&s.scrollHeight<=s.clientHeight+1&&sr.bottom<=r.bottom+0.5&&sr.right<=r.right+0.5,
      levelOk:lr.bottom<=r.bottom+0.5&&lr.height>0,visibleName:sr.height>0&&getComputedStyle(s).visibility!=='hidden'}});
  const play=h.querySelector('.bf-home-play'),squad=h.querySelector('.bf-scene-squad');
  const focusOrder=[...h.querySelectorAll('button')].filter(b=>b.offsetParent).slice(0,9)
    .map(b=>b.dataset.bfHomeUnitId?'unit':(b.getAttribute('data-bf-goto')||b.id||'other'));
  return {level:Number(h.dataset.bfFit),wrap:!!h.querySelector('.bf-scene-toolrow[data-bf-wrap]'),
    clearance:nav.top-qr.bottom-scrollY,questTop:qr.top+scrollY,headBottom:document.querySelector('.bf-shell-head').getBoundingClientRect().bottom,
    questFirst:play.nextElementSibling===squad,squadFirst:squad.nextElementSibling===play,cards,focusOrder,
    scrollW:document.documentElement.scrollWidth,innerW:innerWidth,stage:cards[0].art}}"""

# Exercise focus against actual Home DOM, not a modeled tab sequence.
FOCUS_PROBE = """()=>{const h=document.getElementById('bf-home'),q=h.querySelector('.bf-home-play button.bf-scene-featured[data-bf-goto="quest"]'),p=q.closest('.bf-home-play');
  const active=document.activeElement;const observer=new MutationObserver(()=>{});observer.observe(h,{childList:true});
  const result=BFHomeFitV645.fit(),moves=observer.takeRecords().filter(r=>[...r.addedNodes,...r.removedNodes].includes(p)).length;observer.disconnect();
  return {level:result.level,moves,kept:document.activeElement===active,scroll:scrollY}}"""
QUEST = '#bf-home .bf-home-play button.bf-scene-featured[data-bf-goto="quest"]'

VIEWS = [(320, 740), (393, 852), (320, 660), (393, 752), (413, 852), (540, 852)]
SCALES = [1.0, 1.15, 1.3]
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=chrome, args=["--no-sandbox", "--disable-dev-shm-usage"])
    for width, height in VIEWS:
        for scale in SCALES:
            tag = f"{width}x{height}@{scale}(synthetic)"
            page, errors = open_app(browser, width, height)
            page.wait_for_function("()=>[...document.querySelectorAll('#bf-home img')].every(i=>i.complete&&i.naturalWidth>0)", timeout=20000)
            assert page.evaluate("BF_homeNav.current") == "home"
            before = page.evaluate(SNAPSHOT)
            if ART in MODULES and (width, height, scale) == (320, 740, 1.0):
                exercise_exact_form_and_missing_art(
                    page, SNAPSHOT,
                    lambda configure: open_app(browser, width, height, before_load=configure))
            page.evaluate(SYNTHETIC_TEXT_SCALE, scale)
            page.evaluate("dispatchEvent(new Event('resize'))")
            page.evaluate("window.scrollTo(0,0)")
            m = page.evaluate(MEASURE)
            # Quest is fully on the first screen, >=8px above the footer, 25/25 taps.
            assert m["clearance"] >= 8 and m["questTop"] >= m["headBottom"] - 0.5, (tag, m["level"], m["clearance"])
            assert page.locator('#bf-home .bf-home-play button[data-bf-goto="quest"]').evaluate(HITS) == 25, tag
            assert m["scrollW"] <= m["innerW"], (tag, m["scrollW"])
            # Large art is kept whenever it fits at normal text size.
            if scale == 1.0:
                assert m["level"] == 0, (tag, m["level"])
                if (width, height) == (320, 740):
                    assert m["stage"] == 80, (tag, m["stage"])
                if (width, height) in ((393, 852), (413, 852), (540, 852)):
                    assert m["stage"] == 104, (tag, m["stage"])
            # Six owned units, complete names, leader slot 1, nothing hidden.
            cards = m["cards"]
            assert len(cards) == 6 and len({c["id"] for c in cards}) == 6, (tag, cards)
            for c in cards:
                assert c["id"] == c["squad"] and c["shown"] == c["full"] and c["visibleName"], (tag, c)
                assert c["nameOk"] and c["levelOk"] and c["art"] >= 44, (tag, c)
                assert c["aria"].startswith("Inspect " + c["full"] + ", "), (tag, c)
                assert c["leader"] == (c["i"] == 0) and (("Leader, " in c["aria"]) == (c["i"] == 0)), (tag, c)
            # DOM order equals visual and keyboard order at every level.
            if m["level"] >= 4:
                assert m["questFirst"] and m["focusOrder"][0] == "quest", (tag, m["focusOrder"])
            else:
                assert m["squadFirst"] and m["focusOrder"][:7] == ["units"] + ["unit"] * 6, (tag, m["focusOrder"])
            # Focus a real Quest control, re-fit and prove no needless move at levels 0–3.
            page.locator(QUEST).evaluate("e=>e.focus({preventScroll:true})")
            assert page.locator(QUEST).evaluate("e=>document.activeElement===e"), tag
            focus = page.evaluate(FOCUS_PROBE)
            assert focus["kept"] and focus["level"] == m["level"] and focus["scroll"] == 0, (tag, focus)
            if m["level"] < 4:
                assert focus["moves"] == 0, (tag, "redundant Play relocation", focus)
            # Every card is fully tappable once scrolled into view.
            for i in range(6):
                card = page.locator("#bf-scene-party > .bf-scene-member").nth(i)
                card.evaluate("e=>e.scrollIntoView({block:'center',behavior:'instant'})")
                assert card.evaluate(HITS) == 25, (tag, i)
            page.evaluate("window.scrollTo(0,0)")
            # Leaving and returning Home re-fits to the same level; no state writes.
            # Returning re-renders the party cards, and re-rendered nodes do not
            # carry the SYNTHETIC inline font scale (real textZoom applies to all
            # text always), so the synthetic scale is re-applied before re-fitting.
            page.click('.bf-navbar button[data-bf-goto="menu"]')
            page.click('.bf-navbar button[data-bf-goto="home"]')
            assert page.evaluate("BF_homeNav.current") == "home", tag
            if ART in MODULES:
                assert_exact_home_art(page, starter_fixture=True)
            page.evaluate(SYNTHETIC_TEXT_SCALE, scale)
            page.evaluate("dispatchEvent(new Event('resize'))")
            assert page.evaluate("Number(document.getElementById('bf-home').dataset.bfFit)") == m["level"], tag
            after = page.evaluate(SNAPSHOT)
            assert after == before, (tag, "state changed")
            assert not errors, (tag, errors)
            print(f"PASS v645 {tag}: fit level {m['level']}{' wrap' if m['wrap'] else ''}, art {m['stage']:.0f}px, "
                  f"Quest clearance {m['clearance']:.1f}px, 25/25 taps, six complete names, leader slot 1, no writes")
            page.close()
    # Same-level re-fit while reading below Quest: reproduce both the level-4
    # relocation and the level-2 trial-layout drift independently. The focused
    # Quest must be outside the viewport; otherwise plain focus() would pass.
    for height, expected_level in ((660, 4), (740, 2)):
        page, errors = open_app(browser, 320, height)
        page.wait_for_function("()=>[...document.querySelectorAll('#bf-home img')].every(i=>i.complete&&i.naturalWidth>0)", timeout=20000)
        before = page.evaluate(SNAPSHOT)
        page.evaluate(SYNTHETIC_TEXT_SCALE, 1.3)
        page.evaluate("dispatchEvent(new Event('resize'));window.scrollTo(0,0)")
        assert page.evaluate("BFHomeFitV645.level") == expected_level
        page.locator(QUEST).evaluate("e=>e.focus({preventScroll:true})")
        for fraction in (1, 0.8):
            start = page.evaluate("""fraction=>{window.scrollTo({top:(document.documentElement.scrollHeight-innerHeight)*fraction,behavior:'instant'});return scrollY}""", fraction)
            assert start > 0, (height, fraction, "invalid scrolled fixture")
            assert page.locator(QUEST).evaluate("e=>document.activeElement===e"), (height, fraction, "Quest must remain focused")
            if expected_level == 4:
                assert page.locator(QUEST).evaluate("e=>e.getBoundingClientRect().bottom<0"), (height, fraction, "Quest must be offscreen for preventScroll negative control")
            probe = page.evaluate(FOCUS_PROBE)
            # Verify the final reading position after the browser has painted,
            # not only inside the synchronous fit call.
            settled = page.evaluate("()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r(scrollY))))")
            assert probe["kept"] and page.locator(QUEST).evaluate("e=>document.activeElement===e"), (height, fraction, "scrolled Quest focus lost", probe)
            assert probe["level"] == expected_level, (height, fraction, probe)
            assert abs(probe["scroll"]-start)<=1 and abs(settled-start)<=1, (height, fraction, "reading position drift", start, probe, settled)
            print(f"PASS v645 R4 scrolled focus {height}px level {expected_level} fraction {fraction}: {start} -> {probe['scroll']} -> {settled}")
        assert page.evaluate(SNAPSHOT)==before and not errors, (height, errors)
        page.close()
    # Actual resize across the Quest-first boundary, preserving focus in both directions.
    page, errors = open_app(browser, 320, 740)
    page.wait_for_function("()=>[...document.querySelectorAll('#bf-home img')].every(i=>i.complete&&i.naturalWidth>0)", timeout=20000)
    before = page.evaluate(SNAPSHOT)
    page.evaluate(SYNTHETIC_TEXT_SCALE, 1.3)
    page.evaluate("dispatchEvent(new Event('resize'));window.scrollTo(0,0)")
    assert page.evaluate("BFHomeFitV645.level") < 4
    page.locator(QUEST).evaluate("e=>e.focus({preventScroll:true})")
    for height, quest_first in ((660, True), (740, False), (660, True), (740, False)):
        page.set_viewport_size({"width": 320, "height": height})
        page.wait_for_function("want=> (BFHomeFitV645.level===4)===want", arg=quest_first)
        assert page.locator(QUEST).evaluate("e=>document.activeElement===e"), (height, "Quest focus lost")
        assert page.evaluate("scrollY") == 0, (height, "unexpected scroll")
        m = page.evaluate(MEASURE)
        assert m["clearance"] >= 8 and m["questFirst"] == quest_first, (height, m)
    # An unrelated focused control must not be stolen by a fit (including level 4).
    nav = page.locator('.bf-navbar button[data-bf-goto="home"]')
    nav.evaluate("e=>e.focus({preventScroll:true})")
    page.set_viewport_size({"width":320,"height":660})
    page.wait_for_function("()=>BFHomeFitV645.level===4")
    assert nav.evaluate("e=>document.activeElement===e"), "external focus stolen"
    assert page.evaluate(SNAPSHOT) == before and not errors, errors
    print("PASS v645 R4 focus: all same-level fits, 4 real resize transitions, external focus, no unwanted scroll or state writes")
    page.close()
    browser.close()
print("PASS v645: measured adaptive Home fit, 18/18 synthetic-scale cases (not Android textZoom; not device acceptance)")
