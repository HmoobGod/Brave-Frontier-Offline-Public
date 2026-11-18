"""v618: real app Home Quest/Summon gateway geometry and readable active labels.

Render generated index.html and the live Home modules at five cold-start widths,
not the synthetic v242 fixture. Verify local original art, keyboard order and
no state/storage changes. Test-only draft: never touches an owner save or APK.
"""
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
CSS = (ASSETS / "bf_home_nav.css").read_text("utf-8")
JS = (ASSETS / "bf_home_nav.js").read_text("utf-8")
BUILD = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf-8")
PREFLIGHT = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf-8")
MANIFEST = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf-8")

TEST = "test_bf_home_gateway_live_v61800.py"
assert BUILD.count("python3 " + TEST) == 1, "full signed Android CI registration"
assert PREFLIGHT.count(TEST) == 2, "source preflight path and run registration"
assert "android.permission.INTERNET" not in MANIFEST
assert CSS.count("/* v617 original-art centered Quest gateway") == 1
assert "window.BF_homeNav = {go,get current()" in JS
assert "data-bf-goto=\"quest\"" in JS and "data-bf-goto=\"summon\"" in JS
assert len(CSS.encode("utf-8")) < 128 * 1024
assert "v634 Home-first mobile art" in CSS
assert "content/home/character_frame.png" in CSS
print("PASS v618 source: full APK and preflight registered, original-art Home CSS, offline identity")

if "--source-only" in sys.argv:
    raise SystemExit(0)

from playwright.sync_api import sync_playwright

chrome = (shutil.which("chromium") or shutil.which("google-chrome")
          or shutil.which("google-chrome-stable"))
assert chrome, "Chromium is required for real-app geometry checks"
HTML = (ASSETS / "index.html").read_text("utf-8")
assert "<head>" in HTML
HTML = HTML.replace("<head>", '<head><base href="http://bf-assets.test/">', 1)
MODULES = (
    "bf_home_nav.js", "bf054_header_status.js",
    "bf080_morgan_map.js", "bf090_st_lamia_map.js",
    "bf100_grand_gaia_campaign.js", "bf101_story_continue.js",
    "bf14300_original_quest_energy.js",
)
IMAGES = ("home_win_quest.png", "home_win_akras_smn_hall.png",
          "character_frame.png", "home_character_frame_bg.png")
for name in IMAGES:
    assert (ASSETS / "content/home" / name).is_file(), name


def serve_local_png(route):
    relative = route.request.url.split("bf-assets.test/", 1)[-1]
    file = ASSETS / relative
    if (file.suffix == ".png" and file.is_file()
            and file.resolve().is_relative_to(ASSETS.resolve())):
        route.fulfill(status=200, body=file.read_bytes(), content_type="image/png")
    else:
        route.fulfill(status=404, body=b"")


def snapshot(page):
    return page.evaluate("""() => ({
      player:JSON.stringify(P),session:JSON.stringify(S),
      mission:QUEST.missionId,
      save:localStorage.getItem('bf_global_offline_demo_v7'),
      keys:Array.from({length:localStorage.length},(_,i)=>{
        const k=localStorage.key(i);return [k,localStorage.getItem(k)]
      }).sort((a,b)=>a[0].localeCompare(b[0]))
    })""")


with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=True, executable_path=chrome,
        args=["--no-sandbox", "--disable-dev-shm-usage"])
    try:
        for width,height in ((320,740),(360,844),(393,852),(412,844),(540,844)):
            page = browser.new_page(viewport={"width": width, "height": height})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.route("http://bf-assets.test/**", serve_local_png)
            try:
                # Private in-memory browser fixture; never read or write owner data.
                page.evaluate("""() => {
                  const db={};
                  window.__bfTestStorageWrites={set:0,remove:0,clear:0};
                  Object.defineProperty(window,'localStorage',{configurable:true,value:{
                    getItem:k=>db[k]??null,
                    setItem:(k,v)=>{window.__bfTestStorageWrites.set++;db[k]=String(v)},
                    removeItem:k=>{window.__bfTestStorageWrites.remove++;delete db[k]},
                    clear:()=>{window.__bfTestStorageWrites.clear++;for(const k of Object.keys(db))delete db[k]},
                    key:i=>Object.keys(db)[i]??null,
                    get length(){return Object.keys(db).length}
                  }});
                  window.alert=()=>{};window.confirm=()=>true;
                  HTMLMediaElement.prototype.load=()=>{};
                  HTMLMediaElement.prototype.pause=()=>{};
                  HTMLMediaElement.prototype.play=()=>Promise.resolve();
                }""")
                page.set_content(HTML, wait_until="load", timeout=90000)
                page.add_style_tag(path=str(ASSETS / "bf_home_nav.css"))
                for module in MODULES:
                    page.add_script_tag(path=str(ASSETS / module))
                assert page.evaluate("P.version") == 7
                assert page.evaluate("BF_homeNav.current") == "home"
                before = snapshot(page)
                active = page.locator("#bf-home .bf-scene-places button.bf-scene-featured")
                assert active.count() == 2, (width, active.count())
                assert active.evaluate_all("(nodes)=>nodes.map(x=>x.dataset.bfGoto)") == [
                    "quest", "summon"], width
                assert page.locator("#bf-scene-archive").evaluate("(e)=>!e.open")
                # Advisory A1: data remains in an opt-in disclosure after
                # navigation, never occupying the first-screen squad area.
                details = page.locator("#bf-home-element-disclosure")
                assert details.count() == 1 and not details.evaluate("(e)=>e.open"), width
                assert page.locator(".bf-scene-tools > #bf-home-element-disclosure").count() == 1
                assert page.locator(".bf-scene-squad #bf-home-element-reference").count() == 0
                assert details.locator("#bf-home-element-reference").count() == 1
                assert not details.locator("#bf-home-element-reference").is_visible(), width
                locked = page.locator("#bf-home .bf-scene-archive-grid .bf-scene-locked")
                assert locked.count() == 4
                assert locked.evaluate_all(
                    "(nodes)=>nodes.every(n=>n.getAttribute('aria-disabled')==='true')")

                # Actual local 450x316 original PNGs must resolve in-page.
                page.wait_for_function("""() => ['quest','summon'].every(route=>{
                  const img=document.querySelector(
                    '#bf-home .bf-scene-featured[data-bf-goto="'+route+'"] img');
                  return img && img.complete && img.naturalWidth===450 &&
                    img.naturalHeight===316;
                })""", timeout=15000)
                frame_dimensions = page.evaluate("""async () => {
                  const frame=new Image();frame.src='content/home/character_frame.png';
                  await frame.decode();return [frame.naturalWidth,frame.naturalHeight];
                }""")
                assert frame_dimensions == [644,354], (width, frame_dimensions)
                if width <= 412:
                    art = page.locator("#bf-scene-party").evaluate("""party => ({
                      overlay:getComputedStyle(party,'::before').backgroundImage,
                      slots:[...party.children].slice(0,5).map(
                        node=>getComputedStyle(node).backgroundImage),
                      sixth:party.children.length === 6
                    })""")
                    assert "character_frame.png" in art["overlay"], (width, art)
                    assert art["sixth"] and all("home_character_frame_bg.png" in bg
                                                for bg in art["slots"]), (width, art)
                g = page.locator("#bf-home .bf-scene-places").evaluate("""root=>{
                  const q=root.querySelector('button[data-bf-goto="quest"]'),
                    s=root.querySelector('button[data-bf-goto="summon"]'),
                    qr=q.getBoundingClientRect(),sr=s.getBoundingClientRect(),
                    rr=root.getBoundingClientRect();
                  const style=node=>getComputedStyle(node);
                  const font=node=>parseFloat(style(node.querySelector(
                    '.bf-scene-status')).fontSize);
                  return {
                    questWidth:qr.width,questHeight:qr.height,
                    summonWidth:sr.width,summonHeight:sr.height,
                    questCenter:qr.left+qr.width/2,
                    containerCenter:rr.left+rr.width/2,
                    questBeforeSummon:qr.bottom<=sr.top+1,
                    questFont:font(q),summonFont:font(s),
                    questVisible:style(q).visibility==='visible' &&
                      style(q).display!=='none',
                    summonVisible:style(s).visibility==='visible' &&
                      style(s).display!=='none',
                    questLabel:q.getAttribute('aria-label'),
                    summonLabel:s.getAttribute('aria-label'),
                    questImage:q.querySelector('img').getAttribute('src'),
                    summonImage:s.querySelector('img').getAttribute('src'),
                    scroll:document.documentElement.scrollWidth,
                    viewport:innerWidth
                  };
                }""")
                assert g["questVisible"] and g["summonVisible"], (width, g)
                assert g["questLabel"] == "Quest: play demo battles", (width, g)
                assert g["summonLabel"] == "Summoning Hall: demo recruitment", (width, g)
                assert g["questImage"] == "content/home/home_win_quest.png", (width, g)
                assert g["summonImage"] == "content/home/home_win_akras_smn_hall.png", (width, g)
                # Catches the 7px active Quest-label mutant that survived v242/v243.
                assert g["questFont"] >= 10 and g["summonFont"] >= 10, (width, g)
                assert g["scroll"] <= g["viewport"] + 1, (width, g)
                if width <= 412:
                    assert g["questWidth"] >= 280 and g["questHeight"] >= 170, (width, g)
                    assert 215 <= g["summonWidth"] <= 235, (width, g)
                    assert g["summonHeight"] >= 90, (width, g)
                    assert g["questWidth"] >= g["summonWidth"] + 50, (width, g)
                    assert abs(g["questCenter"] - g["containerCenter"]) <= 2, (width, g)
                    assert g["questBeforeSummon"], (width, g)
                    if (width,height) in ((320,740),(393,852)):
                        def safe_gateway():
                            return page.evaluate("""() => {
                              const q=document.querySelector('#bf-home .bf-scene-featured[data-bf-goto="quest"]').getBoundingClientRect();
                              const nav=document.querySelector('.bf-navbar').getBoundingClientRect();
                              const head=document.querySelector('.bf-shell-head').getBoundingClientRect();
                              return {questTop:q.top,questBottom:q.bottom,footerTop:nav.top,headerBottom:head.bottom};
                            }""")
                        safe=safe_gateway()
                        assert safe["questTop"] >= safe["headerBottom"]-1, (width,height,safe)
                        assert safe["questBottom"] <= safe["footerTop"]-4, (width,height,safe)
                        # v634: inspect untouched layout before route resets or focus.
                        before_tap = snapshot(page)
                        writes_before = page.evaluate("({...window.__bfTestStorageWrites})")
                        initial = page.evaluate("""() => {
                          const sc=document.scrollingElement;
                          const s=document.querySelector('#bf-home button[data-bf-goto="summon"]');
                          const h=document.querySelector('.bf-shell-head').getBoundingClientRect();
                          const f=document.querySelector('.bf-navbar').getBoundingClientRect();
                          const r=s.getBoundingClientRect();
                          return {scrollY:scrollY,scrollTop:sc.scrollTop,
                            maxScroll:sc.scrollHeight-sc.clientHeight,
                            headerBottom:h.bottom,footerTop:f.top,
                            summonTop:r.top,summonBottom:r.bottom};
                        }""")
                        assert initial["maxScroll"] > 0, (width,height,initial)
                        page.evaluate("""() => document.querySelector(
                          '#bf-home button[data-bf-goto="summon"]').scrollIntoView({
                            block:'center',behavior:'instant'
                          })""")
                        visible = page.evaluate("""() => {
                          const sc=document.scrollingElement;
                          const s=document.querySelector('#bf-home button[data-bf-goto="summon"]');
                          const r=s.getBoundingClientRect();
                          const h=document.querySelector('.bf-shell-head').getBoundingClientRect();
                          const f=document.querySelector('.bf-navbar').getBoundingClientRect();
                          const x=r.left+r.width/2,y=r.top+r.height/2;
                          const target=document.elementFromPoint(x,y);
                          return {scrollY:scrollY,scrollTop:sc.scrollTop,
                            maxScroll:sc.scrollHeight-sc.clientHeight,
                            summonTop:r.top,summonBottom:r.bottom,
                            headerBottom:h.bottom,footerTop:f.top,
                            x:x,y:y,hit:!!target&&(target===s||s.contains(target))};
                        }""")
                        assert visible["scrollTop"] >= 0 and visible["scrollTop"] <= visible["maxScroll"] + 1, (width,height,visible)
                        assert visible["summonTop"] >= visible["headerBottom"] + 4, (width,height,visible)
                        assert visible["summonBottom"] <= visible["footerTop"] - 4, (width,height,visible)
                        assert visible["hit"], (width,height,visible)
                        page.mouse.click(visible["x"], visible["y"])
                        assert page.evaluate("BF_homeNav.current") == "summon", (width,height)
                        assert page.locator(".summonpanel").evaluate_all("""panels => panels.some(
                          node=>node.isConnected && node.getAttribute('aria-hidden')==='false' &&
                            !node.classList.contains('bf-hidden') &&
                            getComputedStyle(node).display!=='none')"""), (width,height)
                        assert snapshot(page) == before_tap, (width,height,"Summon tap mutated game state")
                        assert page.evaluate("({...window.__bfTestStorageWrites})") == writes_before, (width,height,"Summon tap attempted a storage write")
                        assert not errors, (width,height,errors)
                        assert page.evaluate("BF_homeNav.go('home')") is True, (width,height)
                        page.evaluate("BF_homeNav.go('units');BF_homeNav.go('home')")
                        after_return=safe_gateway()
                        assert after_return["questBottom"] <= after_return["footerTop"]-4, (width,height,after_return)
                else:
                    # The v617 mobile-only composition cannot break wider Home.
                    assert abs(g["questWidth"] - g["summonWidth"]) <= 2, (width, g)

                # Functional tab order remains Quest then Summon, no hidden route.
                quest = page.locator(
                    '#bf-home .bf-scene-featured[data-bf-goto="quest"]')
                summon = page.locator(
                    '#bf-home .bf-scene-featured[data-bf-goto="summon"]')
                quest.focus()
                assert quest.evaluate("el=>document.activeElement===el"), width
                page.keyboard.press("Tab")
                assert summon.evaluate("el=>document.activeElement===el"), width
                assert snapshot(page) == before, (width, "Home geometry/focus wrote state")
                assert not errors, (width, errors)
                print("PASS v618 real-app Home:", width, "px Quest", g["questWidth"],
                      "Summon", g["summonWidth"], "fonts",
                      g["questFont"], g["summonFont"])
            finally:
                page.close()
    finally:
        browser.close()

print("PASS v618: actual HTML/Home modules, local art, 5 cold starts, readable active labels, no v7 writes")
