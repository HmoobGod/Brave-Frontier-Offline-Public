"""v640: CUSTOM six-owned-unit Home, real app module order and original PNGs.

Owner-approved CUSTOM layout for this offline build (NOT historical 2022
geometry): six owned units in one 3x2 squad with complete names, the leader
badge on the first owned slot, Quest and Summon fully inside the first screen
at 320x740 and 393x852, and auxiliary Home panels (locked location previews,
next-adventure preview, build info, source notes, summoner details) moved to
the Menu screen as the same live nodes.

A PASS means measured DOM geometry in the full app, decoded original images,
routing and save isolation with a synthetic in-memory profile. It is NOT pixel
parity with any original client and NOT owner-device acceptance.
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

assert "android.permission.INTERNET" not in MANIFEST
assert 'package="org.bravefrontier.offline"' in MANIFEST or "org.bravefrontier.offline" in ACTIVITY
assert BUILD.count("python3 test_bf_home_six_slot_custom_v64000.py") == 1
assert CSS.count("/* v640 CUSTOM six-owned-unit Home") == 1
assert JS.count("/* v640 CUSTOM six-owned-unit Home") == 1
v640_js = JS.split("/* v640 CUSTOM six-owned-unit Home", 1)[1]
for forbidden in ("localStorage", "saveProgress(", "awardDemoRewards(", "P.", "S.", "fetch(",
                  "XMLHttpRequest", "QUEST", "setTab(", "go('quest')"):
    assert forbidden not in v640_js, forbidden
v640_css = CSS.split("/* v640 CUSTOM six-owned-unit Home", 1)[1]
for forbidden in ("font-size:9px", "font:800 9px", "font:700 9px", "letter-spacing:-",
                  "pointer-events:none", "visibility:hidden"):
    assert forbidden not in v640_css, forbidden
assert "grid-template-columns:repeat(3,minmax(0,1fr))" in v640_css
assert len(CSS.encode("utf-8")) <= 128 * 1024 and len(JS.encode("utf-8")) <= 128 * 1024
print("PASS v640 source: custom six-slot Home layer, no state/route writes, CI registered, offline")

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
for art in ("home_win_quest.png", "home_win_akras_smn_hall.png", "home_win_gate.png"):
    assert (ASSETS / "content/home" / art).is_file(), "run prepare_original_home_assets.py first"


def serve(route):
    rel = route.request.url.split("bf-assets.test/", 1)[-1].split("?", 1)[0]
    file = ASSETS / rel
    if (file.suffix in TYPES and file.is_file()
            and file.resolve().is_relative_to(ASSETS.resolve())):
        route.fulfill(status=200, body=file.read_bytes(), content_type=TYPES[file.suffix])
    else:
        route.fulfill(status=404, body=b"")


SNAPSHOT = """() => ({player:JSON.stringify(P),session:JSON.stringify(S),
  writes:window.__v640Writes(),keys:Array.from({length:localStorage.length},
  (_,i)=>localStorage.key(i)).sort()})"""


def open_app(browser, width, height):
    page = browser.new_page(viewport={"width": width, "height": height})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.route("http://bf-assets.test/**", serve)
    page.evaluate("""() => {const db={};let w=0;window.__v640Writes=()=>w;
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


LAYOUT = """() => {
  const home=document.getElementById('bf-home'),party=home.querySelector('#bf-scene-party');
  const head=document.querySelector('.bf-shell-head').getBoundingClientRect();
  const nav=document.querySelector('.bf-navbar').getBoundingClientRect();
  const hits=el=>{const r=el.getBoundingClientRect();let ok=0;
    for(let i=0;i<5;i++)for(let j=0;j<5;j++){const e=document.elementFromPoint(
      r.left+3+(r.width-6)*i/4,r.top+3+(r.height-6)*j/4);if(e&&(e===el||el.contains(e)))ok++;}return ok;};
  const cards=[...party.children].map((c,i)=>{const r=c.getBoundingClientRect(),s=c.querySelector('strong'),
    l=c.querySelector('small'),img=c.querySelector('img');
    const unit=P.squad[i]!==undefined?effectiveUnit(P.squad[i]):null;
    return {i,tag:c.tagName,id:Number(c.dataset.bfHomeUnitId),squad:P.squad[i],full:unit&&unit.name,
      shown:s?s.textContent:null,aria:c.getAttribute('aria-label')||'',leader:!!c.querySelector('.bf-scene-leader'),
      left:r.left,top:r.top,right:r.right,bottom:r.bottom,w:r.width,h:r.height,
      nameFs:s?parseFloat(getComputedStyle(s).fontSize):0,levelFs:l?parseFloat(getComputedStyle(l).fontSize):0,
      nameFits:s?s.scrollWidth<=s.clientWidth+1&&s.getBoundingClientRect().bottom<=r.bottom+0.5:false,
      level:l?l.textContent:null,art:img?img.naturalWidth>0&&img.getBoundingClientRect().width>=48:false,
      hit:hits(c)}});
  const q=home.querySelector('.bf-home-play button.bf-scene-featured[data-bf-goto="quest"]');
  const s=home.querySelector('.bf-home-play button.bf-scene-featured[data-bf-goto="summon"]');
  const box=e=>{const r=e.getBoundingClientRect();return {top:r.top,bottom:r.bottom,left:r.left,right:r.right,w:r.width,h:r.height}};
  const order=[...home.querySelectorAll('button,[tabindex="0"]')].filter(e=>e.offsetParent!==null).slice(0,9)
    .map(e=>e.dataset.bfHomeUnitId?'unit':e.getAttribute('data-bf-goto')||e.id||e.className);
  const aux=['bf420-home-readiness','bf054-home-details','bf-home-build-info','bf-home-squad-reference',
    'bf-location-launch'].filter(id=>document.getElementById(id)?.closest('#bf-home'));
  return {cls:home.className,headBottom:head.bottom,navTop:nav.top,cards,quest:box(q),summon:box(s),
    questHit:hits(q),summonHit:hits(s),questArt:q.querySelector('img').naturalWidth,
    summonArt:s.querySelector('img').naturalWidth,questStatus:q.querySelector('.bf-scene-status').textContent,
    scrollW:document.documentElement.scrollWidth,innerW:innerWidth,order,aux,
    homeLocked:home.querySelectorAll('.bf-scene-locked').length,
    noteInHome:!!home.querySelector('.bf-scene-note'),launchInHome:!!home.querySelector('.bf-location-launch'),
    extras:(()=>{const x=document.getElementById('bf-menu-home-extras');return x?{inMenu:!!x.closest('.progresspanel'),
      locked:x.querySelectorAll('.bf-scene-locked').length,
      ids:['bf420-home-readiness','bf054-home-details','bf-home-build-info','bf-home-squad-reference','bf-location-launch']
        .filter(id=>x.contains(document.getElementById(id))),note:!!x.querySelector('.bf-scene-note')}:null})(),
    api:window.BFHomeSixSlotV640&&{custom:window.BFHomeSixSlotV640.custom,historical:window.BFHomeSixSlotV640.historicalGeometry,slots:window.BFHomeSixSlotV640.slots}}
}"""

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=chrome,
                                 args=["--no-sandbox", "--disable-dev-shm-usage"])
    for width, height in ((320, 740), (393, 852), (413, 852), (540, 852)):
        page, errors = open_app(browser, width, height)
        page.wait_for_function("""() => [...document.querySelectorAll(
          '#bf-home img')].every(i => i.complete && i.naturalWidth > 0)""", timeout=20000)
        page.evaluate("window.scrollTo(0,0)")
        before = page.evaluate(SNAPSHOT)
        g = page.evaluate(LAYOUT)
        tag = f"{width}x{height}"
        assert "bf-home-v640" in g["cls"] and "bf-home-v635" not in g["cls"] and "bf-home-v636" not in g["cls"], g["cls"]
        assert g["api"] == {"custom": True, "historical": False, "slots": 6}, g["api"]
        cards = g["cards"]
        assert len(cards) == 6, cards
        for c in cards:
            assert c["tag"] == "BUTTON" and c["id"] == c["squad"], (tag, c)
            assert c["shown"] == c["full"], (tag, c)  # complete, truthful owned name
            assert c["aria"].startswith("Inspect " + c["full"] + ", "), (tag, c)
            assert ("Leader, " in c["aria"]) == (c["i"] == 0), (tag, c)
            assert c["aria"].endswith("squad slot %d of 6" % (c["i"] + 1)), (tag, c)
            assert c["leader"] == (c["i"] == 0), (tag, c)
            assert c["nameFs"] >= 11 and c["levelFs"] >= 11 and c["nameFits"], (tag, c)
            assert c["art"] and c["hit"] == 25 and c["w"] >= 88 and c["h"] >= 110, (tag, c)
            assert c["left"] >= 0 and c["right"] <= width + 0.5, (tag, c)
            assert c["top"] >= g["headBottom"] - 0.5 and c["bottom"] <= g["navTop"], (tag, c)
        # 3x2: three equal columns, two rows, row-major slot order.
        lefts = sorted({round(c["left"]) for c in cards})
        tops = sorted({round(c["top"]) for c in cards})
        assert len(lefts) == 3 and len(tops) == 2, (tag, lefts, tops)
        for i, c in enumerate(cards):
            assert round(c["left"]) == lefts[i % 3] and round(c["top"]) == tops[i // 3], (tag, i, c)
        widths = [c["w"] for c in cards]
        assert max(widths) - min(widths) < 1, (tag, widths)
        # Primary Quest entirely inside the first viewport, directly after the
        # squad; Summon follows (v617 gateway) and is fully tappable when shown.
        q, sm = g["quest"], g["summon"]
        assert q["top"] >= g["headBottom"] - 0.5 and q["bottom"] <= g["navTop"], (tag, q)
        assert q["w"] >= 150 and q["h"] >= 150, (tag, q)
        assert q["top"] > max(c["bottom"] for c in cards), (tag, q)
        assert sm["w"] >= 150 and sm["h"] >= 90, (tag, sm)
        assert sm["top"] >= q["bottom"] - 1 or (width > 412 and abs(sm["top"] - q["top"]) < 1), (tag, q, sm)
        assert g["questHit"] == 25, (tag, g["questHit"])
        page.locator('#bf-home button.bf-scene-featured[data-bf-goto="summon"]').evaluate(
            "e=>e.scrollIntoView({block:'center',behavior:'instant'})")
        assert page.evaluate(LAYOUT)["summonHit"] == 25, tag
        page.evaluate("window.scrollTo(0,0)")
        assert g["questArt"] == 450 and g["summonArt"] == 450 and g["questStatus"] == "PLAY QUEST"
        assert g["scrollW"] <= g["innerW"], (tag, g["scrollW"])
        # Keyboard order: Edit Squad, six owned cards, then Quest, Summon.
        assert g["order"][:9] == ["units"] + ["unit"] * 6 + ["quest", "summon"], (tag, g["order"])
        # Auxiliary panels are off Home and live in Menu.
        assert g["aux"] == [] and g["homeLocked"] == 0 and not g["noteInHome"] and not g["launchInHome"], (tag, g)
        x = g["extras"]
        assert x and x["inMenu"] and x["locked"] == 4 and x["note"], (tag, x)
        assert x["ids"] == ["bf420-home-readiness", "bf054-home-details", "bf-home-build-info",
                            "bf-home-squad-reference", "bf-location-launch"], (tag, x["ids"])
        after = page.evaluate(SNAPSHOT)
        assert after == before, (tag, "Home layout wrote state")
        # Navigation: Quest, Units (via unit card), Summon, Menu, each back Home.
        page.click('#bf-home .bf-home-play button.bf-scene-featured[data-bf-goto="quest"]')
        assert page.evaluate("BF_homeNav.current") == "quest"
        page.click('.bf-navbar button[data-bf-goto="home"]')
        assert page.evaluate("BF_homeNav.current") == "home"
        page.click('#bf-scene-party > button.bf-scene-member:nth-child(6)')
        assert page.evaluate("BF_homeNav.current") == "units"
        assert page.evaluate("document.getElementById('bf-box-detail')?.textContent.includes(effectiveUnit(P.squad[5]).name)")
        page.click('.bf-navbar button[data-bf-goto="home"]')
        page.click('#bf-home .bf-home-play button.bf-scene-featured[data-bf-goto="summon"]')
        assert page.evaluate("BF_homeNav.current") == "summon"
        page.click('.bf-navbar button[data-bf-goto="menu"]')
        assert page.evaluate("BF_homeNav.current") == "menu"
        assert page.evaluate("document.getElementById('bf-menu-home-extras').getBoundingClientRect().height>0")
        page.click('#bf-home-build-info')
        assert page.evaluate("document.getElementById('bf-about-build').open===true")
        page.click('.bf-navbar button[data-bf-goto="home"]')
        assert page.evaluate("BF_homeNav.current") == "home"
        final = page.evaluate(SNAPSHOT)
        assert final["player"] == before["player"] and final["writes"] == before["writes"], (tag, "navigation wrote state")
        assert not errors, errors
        print(f"PASS v640 {tag}: six owned cards 3x2 (full names, leader slot 1, 25/25 taps), "
              f"Quest {g['quest']['top']:.0f}-{g['quest']['bottom']:.0f}px above footer {g['navTop']:.0f}, "
              "extras in Menu, Quest/Units/Summon/Menu routes, no state writes")
        page.close()
    browser.close()
print("PASS v640: custom six-owned-unit Home (custom layout; not 2022 pixel parity, not device acceptance)")
