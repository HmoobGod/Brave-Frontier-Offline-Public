"""v636: artwork-first Home composition, real app module order and original PNGs.

Evidence-checked: archived layout_home2.csv places the Home menu/action
buttons (y~510-612) directly beneath the 640x356 party frame (y161-517);
the original home_new_btn_* PNG bytes are served unchanged from the
hash-pinned home pack. Reconstruction (not verified client behavior): cell
sizing, labels under icons, compact status bar, visually hidden section
headings. A PASS means measured DOM geometry, decoded original images,
routing and save isolation. It is NOT pixel parity with any original client
screenshot and NOT owner-device acceptance. Synthetic in-memory profile only.
"""
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
CSS = (ASSETS / "bf_home_nav.css").read_text("utf-8")
JS = (ASSETS / "bf_home_nav.js").read_text("utf-8")
MANIFEST = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf-8")
ACTIVITY = (ROOT / "app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf-8")
BUILD = (ROOT / ".github/workflows/build-debug-apk.yml").read_text("utf-8")
PRE = (ROOT / ".github/workflows/android-back-ui-source-preflight.yml").read_text("utf-8")

assert "android.permission.INTERNET" not in MANIFEST
assert BUILD.count("python3 test_bf_home_artwork_first_v63600.py") == 1
assert PRE.count("test_bf_home_artwork_first_v63600.py") == 2
assert CSS.count("/* v636 artwork-first Home composition") == 1
v636_css = CSS.split("/* v636 artwork-first Home composition", 1)[1].split(
    "/* v617 original-art centered Quest gateway", 1)[0]
assert CSS.index("/* v635 original Global Home squad frame") < CSS.index(
    "/* v636 artwork-first Home composition") < CSS.index("/* v617 original-art centered Quest gateway")
assert "grid-template-columns:repeat(5,minmax(0,1fr))" in v636_css
for forbidden in ("display:none", "visibility:hidden", "pointer-events:none", "letter-spacing:-1",
                  "font-size:9px", "font:800 9px"):
    assert forbidden not in v636_css, forbidden
v636_js = JS.split("// v636: archived layout_home2", 1)[1].split("const homeArtFallbacks", 1)[0]
for forbidden in ("localStorage", "saveProgress(", "awardDemoRewards(", "P.", "S.", "fetch(",
                  "XMLHttpRequest", ".remove()", "innerHTML"):
    assert forbidden not in v636_js, forbidden
HOME = JS.split("/* Build #9: original Global home location hub", 1)[1].split(
    "/* Build #11 - recovered BF1 Global artwork", 1)[0]
for title in ("GRAND GAIA", "CURRENT SQUAD", "ADVENTURE", "HOME SHORTCUTS"):
    assert title in HOME  # headings stay in source and accessibility tree
assert len(CSS.encode("utf-8")) < 128 * 1024 and len(JS.encode("utf-8")) < 128 * 1024
print("PASS v636 source: icon row CSS between v635 and v617 gates, no hiding/tracking hacks, no state writes")

if "--source-only" in sys.argv:
    raise SystemExit(0)

from playwright.sync_api import sync_playwright

chrome = shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "Chromium is required"
HTML = (ASSETS / "index.html").read_text("utf-8").replace(
    "<head>", '<head><base href="http://bf-assets.test/">', 1)
MODULES = [m for m in dict.fromkeys(re.findall(r"bf[0-9a-z_]*\.(?:js|css)", ACTIVITY))
           if (ASSETS / m).is_file()]
assert MODULES[:2] == ["bf_home_nav.js", "bf_home_nav.css"], MODULES[:2]
TYPES = {".png": "image/png", ".jpg": "image/jpeg"}
ICONS = ["home_new_btn_mission1.png", "home_new_btn_shortcut1.png", "home_new_btn_menu1.png",
         "home_new_btn_box1.png", "home_new_btn_exchange1.png"]
for icon in ICONS:
    assert (ASSETS / "content/home" / icon).is_file(), "run prepare_original_home_assets.py first"


def serve(route):
    rel = route.request.url.split("bf-assets.test/", 1)[-1].split("?", 1)[0]
    file = ASSETS / rel
    if (file.suffix in TYPES and file.is_file()
            and file.resolve().is_relative_to(ASSETS.resolve())):
        route.fulfill(status=200, body=file.read_bytes(), content_type=TYPES[file.suffix])
    else:
        route.fulfill(status=404, body=b"")


SNAPSHOT = """() => ({player:JSON.stringify(P),session:JSON.stringify(S),
  writes:window.__v636Writes(),keys:Array.from({length:localStorage.length},
  (_,i)=>localStorage.key(i)).sort()})"""


def open_app(browser, width, height):
    page = browser.new_page(viewport={"width": width, "height": height})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.route("http://bf-assets.test/**", serve)
    page.evaluate("""() => {const db={};let w=0;window.__v636Writes=()=>w;
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:k=>db[k]??null,setItem:(k,v)=>{w++;db[k]=String(v)},
        removeItem:k=>{w++;delete db[k]},key:i=>Object.keys(db)[i]??null,
        get length(){return Object.keys(db).length}}});
      window.alert=()=>{};window.confirm=()=>true;
      HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
      HTMLMediaElement.prototype.play=()=>Promise.resolve();}""")
    page.set_content(HTML, wait_until="load", timeout=120000)
    for module in MODULES:
        if module.endswith(".css"):
            page.add_style_tag(path=str(ASSETS / module))
        else:
            page.add_script_tag(path=str(ASSETS / module))
    return page, errors


GEOMETRY = """() => {
  const home=document.getElementById('bf-home'),squad=home.querySelector('.bf-scene-squad');
  const party=squad.querySelector('#bf-scene-party'),row=squad.querySelector(':scope > .bf-scene-toolrow');
  const edit=squad.querySelector(':scope > .bf-scene-heading button[data-bf-goto="units"]');
  const story=home.querySelector('.bf-scene-story'),quest=home.querySelector('.bf-scene-featured[data-bf-goto="quest"]');
  const head=document.querySelector('.bf-shell-head').getBoundingClientRect();
  const footer=document.querySelector('.bf-navbar').getBoundingClientRect();
  const cells=[...row.children].map(c=>{const r=c.getBoundingClientRect(),i=c.querySelector('img'),s=c.querySelector('span');
    const ir=i.getBoundingClientRect(),cx=r.left+r.width/2,cy=r.top+r.height/2,hit=document.elementFromPoint(cx,cy);
    return {tag:c.tagName,w:r.width,h:r.height,src:i.getAttribute('src'),nat:i.naturalWidth,
      imgH:ir.height,label:s.textContent,fs:parseFloat(getComputedStyle(s).fontSize),
      ls:getComputedStyle(s).letterSpacing,fit:s.scrollWidth<=s.clientWidth+1&&s.scrollHeight<=s.clientHeight+1,
      inside:r.left>=-0.5&&r.right<=innerWidth+0.5,hit:!!hit&&(hit===c||c.contains(hit)),
      disabled:c.getAttribute('aria-disabled'),focusable:c.matches('button')}});
  const hidden=['.bf-scene-explore>.bf-scene-heading','.bf-scene-tools>.bf-scene-heading',
    '.bf-scene-places>.bf-scene-available-label'].map(sel=>{const e=home.querySelector(sel),r=e.getBoundingClientRect();
    return {sel,area:r.width*r.height,text:e.textContent.trim().length>0,heading:!!e.querySelector('[role="heading"]')||e.getAttribute('role')==='heading'}});
  const pr=party.getBoundingClientRect(),rr=row.getBoundingClientRect(),er=edit.getBoundingClientRect();
  return {headBottom:head.bottom,partyTop:pr.top,frameBottom:pr.top+parseFloat(getComputedStyle(party,'::after').height),
    sixthBottom:party.children[5].getBoundingClientRect().bottom,editBottom:er.bottom,rowTop:rr.top,rowBottom:rr.bottom,
    sixthHeight:party.children[5].getBoundingClientRect().height,
    sixthAndEditSeparate:(()=>{
      const s=party.children[5].getBoundingClientRect(),b=edit.getBoundingClientRect(),
        e=document.elementFromPoint(b.left+b.width/2,b.top+b.height/2);
      return s.right+1<=b.left&&b.width>=44&&b.height>=44&&
        !!e&&(e===edit||edit.contains(e));
    })(),
    questVisiblePx:Math.max(0,Math.min(quest.getBoundingClientRect().bottom,footer.top)-Math.max(quest.getBoundingClientRect().top,head.bottom)),
    questFullyVisible:quest.getBoundingClientRect().bottom<=footer.top,
    summonBottom:home.querySelector('.bf-scene-featured[data-bf-goto="summon"]').getBoundingClientRect().bottom,
    archiveTop:home.querySelector('.bf-scene-archive-label').getBoundingClientRect().top,
    storyNested:story.parentElement===home.querySelector('.bf-scene-places')&&
      story.previousElementSibling===home.querySelector('.bf-scene-featured[data-bf-goto="summon"]')&&
      story.nextElementSibling===home.querySelector('.bf-scene-archive-label'),
    storyTop:story.getBoundingClientRect().top,questTop:quest.getBoundingClientRect().top,
    rowInSquad:row.parentElement===squad,rowLabel:row.getAttribute('aria-label'),
    order:[...squad.children].map(c=>c.id||c.className).join('|'),cells,hidden,
    ids:[...party.children].map(c=>Number(c.dataset.bfHomeUnitId)||null),squad:Array.from(P.squad),
    leaders:[...party.children].map(c=>!!c.querySelector('.bf-scene-leader')),
    scroll:document.documentElement.scrollWidth,viewport:innerWidth};
}"""

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=chrome,
                                 args=["--no-sandbox", "--disable-dev-shm-usage"])
    try:
        for width, height in ((320, 740), (393, 852), (413, 852), (450, 852), (540, 852)):
            page, errors = open_app(browser, width, height)
            assert page.evaluate("BF_homeNav.current") == "home" and page.evaluate("P.version") == 7
            page.wait_for_function("""() => [...document.querySelectorAll(
              '#bf-home .bf-scene-squad > .bf-scene-toolrow img')].every(i=>i.complete&&i.naturalWidth>0)""",
              timeout=15000)
            before = page.evaluate(SNAPSHOT)
            page.evaluate('window.scrollTo(0,0)')
            g = page.evaluate(GEOMETRY)
            # v638: header -> frame -> sixth -> Edit -> icon row -> Quest/Summon -> story -> archived previews.
            assert g["rowInSquad"] and g["rowLabel"] == "Home menu", (width, g)
            assert 0 <= g["partyTop"] - g["headBottom"] <= 24, (width, g)
            assert g["sixthBottom"] <= g["editBottom"] <= g["rowTop"] + 1, (width, g)
            assert g["rowTop"] - g["editBottom"] <= 16, (width, "icon row not beneath squad", g)
            assert g["rowBottom"] <= g["questTop"] + 1 and g["summonBottom"] <= g["storyTop"] + 1, (width, g)
            assert g["storyTop"] <= g["archiveTop"] + 1 and g["storyNested"], (width, g)
            assert g["sixthHeight"] <= 70, (width, "compact sixth unit", g)
            ref = page.evaluate("""() => {const d=document.getElementById('bf-home-squad-reference');
              return {inTools:!!d.closest('.bf-scene-tools'),open:d.open,hidden:d.hidden,
                notes:BFHomeSquadFrameV635.referenceIds.filter(id=>document.getElementById(id)).every(
                  id=>d.contains(document.getElementById(id)))}}""")
            assert ref["inTools"] and not ref["open"] and not ref["hidden"] and ref["notes"], (width, ref)
            assert g["scroll"] <= g["viewport"] + 1, (width, g)
            visibility={320:185,393:185,413:155,450:155,540:155}
            assert g["questVisiblePx"]>=visibility[width],(width,"unscrolled Quest visibility",g)
            assert g["questFullyVisible"],(width,"Quest fully above fixed footer",g)
            if width==540:
                assert g["sixthAndEditSeparate"],(width,"compact sixth and separate Edit Squad hit areas",g)
            # Five original-art cells, readable labels, touch-sized, unobstructed.
            cells = g["cells"]
            assert [c["src"].rsplit("/", 1)[-1] for c in cells] == ICONS, (width, cells)
            assert all(c["nat"] > 0 and c["imgH"] >= 40 for c in cells), (width, cells)
            widths = [c["w"] for c in cells]
            assert max(widths) - min(widths) <= 1 and min(widths) >= 44, (width, widths)
            assert all(c["h"] >= 64 and c["inside"] and c["fit"] for c in cells), (width, cells)
            assert all(c["fs"] >= 10 for c in cells), (width, cells)
            assert all(c["ls"] in ("normal", "0px") or float(c["ls"].rstrip("px")) >= -0.5 for c in cells), (width, cells)
            assert all(c["hit"] for c in cells), (width, cells)
            assert [c["focusable"] for c in cells] == [True, True, True, True, False], (width, cells)
            assert cells[4]["disabled"] == "true" and "LATER" in cells[4]["label"], (width, cells)
            # Prototype headings are visually hidden but remain in the accessibility tree.
            assert all(h["area"] <= 1 and h["text"] and h["heading"] for h in g["hidden"]), (width, g["hidden"])
            # Six real owned units; leader strictly on the first actual slot.
            assert g["ids"] == g["squad"] and len(g["squad"]) == 6, (width, g)
            assert g["leaders"] == [True, False, False, False, False, False], (width, g)

            if width in (320, 393):
                # Keyboard order follows the visual order: portraits, Edit Squad, icon row.
                page.locator("#bf-scene-party > button").first.focus()
                seen = []
                for _ in range(11):
                    seen.append(page.evaluate("""() => {const a=document.activeElement;
                      return a.dataset.bfHomeUnitId?'unit':(a.closest('.bf-scene-toolrow')?
                        'icon:'+a.querySelector('span').textContent:(a.matches('.bf-scene-heading button')?'edit':a.tagName))}"""))
                    page.keyboard.press("Tab")
                assert seen == ["unit"] * 6 + ["edit", "icon:QUESTS", "icon:UNITS", "icon:SAVES", "icon:UNIT BOX"], (width, seen)
                # Real pointer taps on each icon reach their existing routes.
                for index, route, tab in ((0, "quest", None), (1, "units", None), (2, "menu", None), (3, "units", "box")):
                    page.evaluate("window.scrollTo(0,0)")
                    box = page.locator("#bf-home .bf-scene-squad > .bf-scene-toolrow > *").nth(index).bounding_box()
                    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                    assert page.evaluate("BF_homeNav.current") == route, (width, index, route)
                    if tab:
                        assert page.evaluate("window.BFInnerScreens.unitTab") == tab, (width, "box tab")
                    page.locator('.bf-navbar button[data-bf-goto="home"]').click()
                    assert page.evaluate("BF_homeNav.current") == "home"
                # Locked Exchange stays inert.
                page.evaluate("window.scrollTo(0,0)")
                box = page.locator("#bf-home .bf-scene-tool-locked").bounding_box()
                page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                assert page.evaluate("BF_homeNav.current") == "home"
                # Quest and Summon gateways: whole rectangle above the fixed footer, 5x5 hits.
                for route in ("quest", "summon"):
                    sel = '#bf-home .bf-scene-featured[data-bf-goto="' + route + '"]'
                    page.locator(sel).evaluate("el=>el.scrollIntoView({block:'center',behavior:'instant'})")
                    clear = page.evaluate("""(sel) => {const b=document.querySelector(sel),s=b.getBoundingClientRect(),
                      nav=document.querySelector('.bf-navbar').getBoundingClientRect();let misses=0;
                      for(let i=0;i<5;i++)for(let j=0;j<5;j++){const e=document.elementFromPoint(
                        s.left+3+(s.width-6)*i/4,s.top+3+(s.height-6)*j/4);if(!e||!b.contains(e))misses++;}
                      return {bottom:s.bottom,top:s.top,navTop:nav.top,misses}}""", sel)
                    assert clear["bottom"] <= clear["navTop"] + 0.5 and clear["top"] >= 0 and not clear["misses"], (width, route, clear)
                    page.locator(sel).click()
                    assert page.evaluate("BF_homeNav.current") == route, (width, route)
                    page.locator('.bf-navbar button[data-bf-goto="home"]').click()
            after = page.evaluate(SNAPSHOT)
            assert after["player"] == before["player"] and after["writes"] == before["writes"], (width, "no additional writes since snapshot")
            assert after["keys"] == before["keys"], (width, after)
            assert not errors, (width, errors)
            print(f"PASS v636 {width}x{height}: icon row {g['rowTop']:.0f}-{g['rowBottom']:.0f}px beneath frame "
                  f"(frame ends {g['frameBottom']:.0f}), 5 original icons {min(widths):.0f}px wide, "
                  "labels fit >=10px, six owned units, leader slot 1, no additional writes")
            page.close()
    finally:
        browser.close()
print("PASS v636: artwork-first Home composition (geometry/behavior only; not pixel parity, not device acceptance)")
