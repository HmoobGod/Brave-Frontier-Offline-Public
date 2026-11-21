"""v635: original-style Home squad frame, real app module order, 320x740 and 393x852.

Evidence-checked: archived layout_home2.csv five 128x350 portraits inside a
640x356 party frame; original character_frame.png (644x354) bytes unchanged.
Reconstruction (not verified client behavior): frame scaling, thumbnail
placement, CSS LEADER badge, sixth owned unit strip, diagnostics disclosure.
Scope of a PASS: decoded original PNG dimensions, measured DOM geometry,
routing and guard behavior. It is NOT pixel parity with any original client
screenshot and NOT owner-device acceptance. Storage checks mean "no
additional in-memory localStorage writes and unchanged P/S since the
snapshot". Synthetic in-memory browser profile only; never reads owner saves.
"""
from pathlib import Path
import hashlib
import re
import shutil
import struct
import sys
import zipfile

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
CSS = (ASSETS / "bf_home_nav.css").read_text("utf-8")
JS = (ASSETS / "bf_home_nav.js").read_text("utf-8")
MANIFEST = (ROOT / "app/src/main/AndroidManifest.xml").read_text("utf-8")
ACTIVITY = (ROOT / "app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf-8")
PREP = (ROOT / "prepare_original_home_assets.py").read_text("utf-8")

assert "android.permission.INTERNET" not in MANIFEST
assert CSS.count("/* v635 original Global Home squad frame") == 1
assert CSS.index("/* v635 original Global Home squad frame") < CSS.index(
    "/* v617 original-art centered Quest gateway")
assert 'url("content/home/character_frame.png")' in CSS
assert "aspect-ratio:640/356" in CSS and "aspect-ratio:128/350" in CSS
assert '"character_frame.png",' in PREP
assert "home.classList.add('bf-home-v635')" in JS
v635 = JS.split("// v635: original-style Home squad frame", 1)[1].split("const homeArtFallbacks", 1)[0]
for forbidden in ("localStorage", "saveProgress(", "awardDemoRewards(", "P.squad",
                  "P.roster", "S.", "fetch(", "XMLHttpRequest", ".remove()"):
    assert forbidden not in v635, forbidden
assert len(CSS.encode("utf-8")) < 128 * 1024
# Original bytes: pinned archive identity, pinned entry identity, and the
# staged copy must be byte-identical to that entry (no re-encode or crop).
HOME_PACK_SHA256 = "2f23e6f57b03e359c53097fdd1ee7e8619bf978e5514dd91bb6c55d1f4a6ae69"
FRAME_SHA256 = "fc0e49fe5d0cd63b0bf89d792f718e16478adfc1e5c5bf511692654955b06d03"
pack = ROOT / "source_assets/bf1/BF1_home_part001.zip"
assert hashlib.sha256(pack.read_bytes()).hexdigest() == HOME_PACK_SHA256
assert ('"home": (\n        "' + HOME_PACK_SHA256 + '"') in PREP, "prepare script pin changed"
with zipfile.ZipFile(pack) as archive:
    original = archive.read("content/home/character_frame.png")
assert hashlib.sha256(original).hexdigest() == FRAME_SHA256
assert original[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", original[16:24]) == (644, 354)
staged = ASSETS / "content/home/character_frame.png"
assert staged.is_file() or "--source-only" in sys.argv, "run prepare_original_home_assets.py first"
if staged.is_file():
    assert staged.read_bytes() == original, "staged character_frame.png bytes differ from pinned entry"
print("PASS v635 source: frame CSS precedes v617 gate; pack and frame SHA-256 pinned; staged bytes identical; no save/engine writes")

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


def serve(route):
    rel = route.request.url.split("bf-assets.test/", 1)[-1].split("?", 1)[0]
    file = ASSETS / rel
    if (file.suffix in TYPES and file.is_file()
            and file.resolve().is_relative_to(ASSETS.resolve())):
        route.fulfill(status=200, body=file.read_bytes(), content_type=TYPES[file.suffix],
                      headers={"Access-Control-Allow-Origin": "*"})
    else:
        route.fulfill(status=404, body=b"")


SNAPSHOT = """() => ({player:JSON.stringify(P),session:JSON.stringify(S),
  writes:window.__v635Writes(),keys:Array.from({length:localStorage.length},
  (_,i)=>localStorage.key(i)).sort()})"""

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, executable_path=chrome,
                                 args=["--no-sandbox", "--disable-dev-shm-usage"])
    try:
        for width, height in ((320, 740), (393, 852)):
            page = browser.new_page(viewport={"width": width, "height": height})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.route("http://bf-assets.test/**", serve)
            page.evaluate("""() => {const db={};let w=0;window.__v635Writes=()=>w;
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
            assert page.evaluate("BF_homeNav.current") == "home"
            assert page.evaluate("P.version") == 7
            before = page.evaluate(SNAPSHOT)
            page.wait_for_function("""() => [...document.images].filter(i=>
              /content\\/home\\/(home_win_quest|home_win_akras_smn_hall)\\.png$/.test(i.src))
              .every(i=>i.complete&&i.naturalWidth===450)""", timeout=15000)
            frame_loaded = page.evaluate("""() => new Promise(done=>{const i=new Image();
              i.onload=()=>done([i.naturalWidth,i.naturalHeight]);i.onerror=()=>done(null);
              i.src='content/home/character_frame.png';})""")
            assert frame_loaded == [644, 354], (width, frame_loaded)  # decode check only, not parity

            # R6: compare ALL five owned portrait slots to the pinned original
            # PNG's bottom-right alpha ornaments (source y=290, not 300).
            # Test both the readable compact text and the full aria-label
            # without weakening the existing v423 invalid-EXP/getter guards.
            if width == 320:
                page.evaluate("""() => {
                  window.__r6Exp=P.unitExp;
                  P.unitExp=Object.fromEntries(P.squad.slice(0,5).map(id=>[id,'0']));
                  BFGlobalHome.refreshParty();
                }""")
                try:
                    for w in (320,393,413,450,540):
                        page.set_viewport_size({"width":w,"height":852})
                        measured=page.evaluate("""async()=> {
                          const party=document.querySelector('#bf-scene-party');
                          const p=party.getBoundingClientRect();
                          const overlay=getComputedStyle(party,'::after');
                          const png=new Image();png.crossOrigin='anonymous';
                          png.src='content/home/character_frame.png';
                          await png.decode();
                          const canvas=document.createElement('canvas');
                          canvas.width=png.width;canvas.height=png.height;
                          const ctx=canvas.getContext('2d',{willReadFrequently:true});
                          ctx.drawImage(png,0,0);
                          const pixels=ctx.getImageData(0,0,png.width,png.height).data;
                          const cards=[...party.querySelectorAll(':scope > button.bf-scene-member')].slice(0,5);
                          const ornamentalBand=p.top+parseFloat(overlay.height)*290/354;
                          const samples=cards.map((card,index)=>{
                            const small=card.querySelector('small'),strong=card.querySelector('strong');
                            const portrait=card.querySelector('img, .bf-portrait-fallback');
                            const style=getComputedStyle(small);
                            const span=style.letterSpacing==='normal'?0:parseFloat(style.letterSpacing);
                            const glyphs=[];
                            for(let j=0;j<small.firstChild.length;j++){
                              const range=document.createRange();
                              range.setStart(small.firstChild,j);
                              range.setEnd(small.firstChild,j+1);
                              const rect=range.getBoundingClientRect();
                              glyphs.push({left:rect.left,right:rect.right,top:rect.top,bottom:rect.bottom});
                            }
                            let opaque=0;
                            for(let y=290;y<354;y++)for(let x=index*128+80;x<index*128+128;x++)
                              if(pixels[4*(y*png.width+x)+3]>=200)opaque++;
                            const cardRect=card.getBoundingClientRect();
                            const name=strong.getBoundingClientRect();
                            const art=portrait?.getBoundingClientRect();
                            return {text:small.textContent,aria:card.getAttribute('aria-label'),
                              labelFont:parseFloat(style.fontSize),letterSpacing:span,
                              client:small.clientWidth,scroll:small.scrollWidth,
                              glyphTops:glyphs.map(g=>g.top),
                              left:Math.min(...glyphs.map(g=>g.left)),
                              right:Math.max(...glyphs.map(g=>g.right)),
                              top:Math.min(...glyphs.map(g=>g.top)),
                              bottom:Math.max(...glyphs.map(g=>g.bottom)),
                              cardLeft:cardRect.left,cardRight:cardRect.right,
                              nameTop:name.top,nameBottom:name.bottom,
                              artBottom:art?.bottom??null,ornamentOpaque:opaque,
                              leader:card.querySelectorAll('.bf-scene-leader').length,
                              id:Number(card.dataset.bfHomeUnitId)};
                          });
                          const sixth=party.querySelector(':scope > button:nth-child(6)');
                          return {frame:[png.width,png.height],image:overlay.backgroundImage,
                            opaqueStart:ornamentalBand,
                            ids:P.squad.slice(0,5),sixthId:Number(sixth?.dataset.bfHomeUnitId),
                            sixthTop:sixth?.getBoundingClientRect().top,
                            frameBottom:p.top+parseFloat(overlay.height),
                            homeRoute:BF_homeNav.current,
                            routes:['home','quest','units','summon','menu'].every(r=>
                              !!document.querySelector('.bf-navbar button[data-bf-goto="'+r+'"]')),
                            samples};
                        }""")
                        assert measured["frame"]==[644,354] and "character_frame.png" in measured["image"],(w,measured)
                        assert measured["homeRoute"]=="home" and measured["routes"],(w,measured)
                        assert len(measured["samples"])==5,(w,measured)
                        assert [s["id"] for s in measured["samples"]]==measured["ids"],(w,measured)
                        assert [s["leader"] for s in measured["samples"]]==[1,0,0,0,0],(w,measured)
                        assert measured["sixthId"]==page.evaluate("P.squad[5]"),(w,measured)
                        assert measured["sixthTop"]>=measured["frameBottom"]-1,(w,measured)
                        for i,s in enumerate(measured["samples"]):
                            assert s["text"]=="Lv —" and "LEVEL UNAVAILABLE" in s["aria"],(w,i,s)
                            assert s["ornamentOpaque"]>0,(w,i,"PNG's original orb missing",s)
                            assert s["labelFont"]>=10 and s["letterSpacing"]>=-0.5,(w,i,s)
                            assert s["scroll"]<=s["client"],(w,i,s)
                            assert max(s["glyphTops"])-min(s["glyphTops"])<=0.5,(w,i,"wrapped compact label",s)
                            assert s["left"]>=s["cardLeft"]-0.5 and s["right"]<=s["cardRight"]+0.5,(w,i,s)
                            assert s["nameBottom"]+2<=s["top"],(w,i,"name/level overlap",s)
                            assert s["artBottom"] is not None and s["artBottom"]<=s["nameTop"]+0.5,(w,i,"portrait/name overlap",s)
                            assert s["bottom"]+2<=measured["opaqueStart"],(w,i,"ornament occludes glyphs",s)
                        with_frame=page.screenshot()
                        disable_frame=page.add_style_tag(content="#bf-home.bf-home-v635 #bf-scene-party::after{background-image:none!important}")
                        try:
                            without_frame=page.screenshot()
                        finally:
                            disable_frame.evaluate("el=>el.remove()")
                        assert with_frame!=without_frame,(w,"original PNG not composited")
                        print(f"PASS R6 five-slot genuine original PNG {w}px: "
                              f"5/5 readable Lv —, full aria, >=10px, tracking >=-0.5px, "
                              "orb starts source y=290, no label/name/portrait overlap")
                finally:
                    page.evaluate("""() => {
                      P.unitExp=window.__r6Exp;delete window.__r6Exp;
                      BFGlobalHome.refreshParty();
                    }""")
                    page.set_viewport_size({"width":width,"height":height})
                assert page.evaluate(SNAPSHOT)==before,"R6 P/S/v7 storage unchanged"


            g = page.evaluate("""() => {
              const home=document.getElementById('bf-home'),party=home.querySelector('#bf-scene-party');
              const header=document.querySelector('.bf-shell-head').getBoundingClientRect();
              const pr=party.getBoundingClientRect(),after=getComputedStyle(party,'::after');
              const cards=[...party.children],rects=cards.map(c=>c.getBoundingClientRect());
              const hit=c=>{const r=c.getBoundingClientRect();const e=document.elementFromPoint(
                r.left+r.width/2,r.top+r.height/2);return !!e&&(e===c||c.contains(e));};
              const title=home.querySelector('.bf-scene-title').getBoundingClientRect();
              return {partyTop:pr.top,partyLeft:pr.left,partyWidth:pr.width,headerBottom:header.bottom,
                frameImage:after.backgroundImage,frameEvents:after.pointerEvents,
                frameHeight:parseFloat(after.height),
                rects:rects.map(r=>({l:r.left,t:r.top,w:r.width,h:r.height,b:r.bottom})),
                ids:cards.map(c=>c.dataset.bfHomeUnitId?Number(c.dataset.bfHomeUnitId):null),
                squad:Array.from(P.squad),
                forms:Array.from(P.squad).map(id=>effectiveUnit(id).name),
                names:cards.map(c=>c.querySelector('strong')?.textContent),
                labels:cards.map(c=>c.getAttribute('aria-label')),
                leaders:cards.map(c=>!!c.querySelector('.bf-scene-leader')),
                leaderVisible:(()=>{const b=cards[0].querySelector('.bf-scene-leader');
                  const r=b?.getBoundingClientRect();return !!r&&r.width>0&&r.height>0&&
                  getComputedStyle(b).visibility==='visible';})(),
                hits:cards.map(hit),titleArea:title.width*title.height,
                scroll:document.documentElement.scrollWidth,viewport:innerWidth};
            }""")
            # Frame and five tall openings follow layout_home2.csv proportions.
            assert "character_frame.png" in g["frameImage"] and g["frameEvents"] == "none", (width, g)
            assert abs(g["frameHeight"] - g["partyWidth"] * 356 / 640) <= 1.5, (width, g)
            assert 0 <= g["partyTop"] - g["headerBottom"] <= 24, (width, g)
            assert g["titleArea"] <= 1, (width, "visible title banner returned")
            slot_w = g["partyWidth"] / 5
            for i, r in enumerate(g["rects"][:5]):
                assert abs(r["l"] - (g["partyLeft"] + i * slot_w)) <= 1, (width, i, r)
                assert abs(r["w"] - slot_w) <= 1 and abs(r["h"] - slot_w * 350 / 128) <= 1.5, (width, i, r)
                assert abs(r["t"] - g["partyTop"]) <= 1, (width, i, r)
            # Six real owned units; leader strictly first actual slot; sixth below frame.
            assert g["ids"] == g["squad"] and len(g["squad"]) == 6, (width, g)
            assert g["names"] == g["forms"], (width, g)
            assert g["leaders"] == [True, False, False, False, False, False] and g["leaderVisible"], (width, g)
            assert "Leader, squad slot 1 of 6" in g["labels"][0], (width, g)
            assert "squad slot 6 of 6" in g["labels"][5], (width, g)
            sixth = g["rects"][5]
            assert sixth["t"] >= g["partyTop"] + g["frameHeight"] - 1 and sixth["h"] >= 44, (width, sixth)
            assert all(g["hits"]), (width, g["hits"])
            assert g["scroll"] <= g["viewport"] + 1, (width, g)

            # Diagnostics relocated, intact, and collapsed by default.
            ref = page.evaluate("""() => {const d=document.getElementById('bf-home-squad-reference');
              const ids=BFHomeSquadFrameV635.referenceIds.filter(id=>document.getElementById(id));
              return {open:d.open,hidden:d.hidden,inside:ids.every(id=>
                d.contains(document.getElementById(id))),count:ids.length,
                roles:ids.map(id=>document.getElementById(id).getAttribute('role')),
                text:ids.map(id=>document.getElementById(id).textContent)}}""")
            assert ref["count"] >= 2 and ref["inside"] and not ref["open"] and not ref["hidden"], (width, ref)
            assert all(r == "status" for r in ref["roles"]) and all(ref["text"]), (width, ref)
            page.locator("#bf-home-squad-reference > summary").focus()
            page.keyboard.press("Enter")
            assert page.evaluate("document.getElementById('bf-home-squad-reference').open")
            assert page.locator("#bf12600-home-squad-cost").is_visible()
            page.keyboard.press("Enter")

            # Keyboard: slot buttons in visual order, then sixth, then Edit Squad.
            page.locator("#bf-scene-party > button").first.focus()
            seen = []
            for _ in range(6):
                seen.append(page.evaluate("document.activeElement.dataset.bfHomeUnitId||null"))
                page.keyboard.press("Tab")
            assert [int(x) for x in seen] == g["squad"], (width, seen)
            assert page.evaluate("document.activeElement.matches('.bf-scene-squad .bf-scene-heading button')")

            # Footer clearance: the WHOLE Quest and Summon gateway rectangles fit
            # between the header and the fixed footer after scrolling, and a
            # 5x5 grid of inset points across each rectangle hits that button.
            for route in ("quest", "summon"):
                sel = '#bf-home .bf-scene-featured[data-bf-goto="' + route + '"]'
                page.locator(sel).evaluate("el=>el.scrollIntoView({block:'center',behavior:'instant'})")
                clear = page.evaluate("""(sel) => {const b=document.querySelector(sel),
                  s=b.getBoundingClientRect(),nav=document.querySelector('.bf-navbar').getBoundingClientRect();
                  const head=document.querySelector('.bf-shell-head').getBoundingClientRect();
                  const headFixed=['fixed','sticky'].includes(getComputedStyle(document.querySelector('.bf-shell-head')).position);
                  let misses=[];for(let i=0;i<5;i++)for(let j=0;j<5;j++){
                    const x=s.left+3+(s.width-6)*i/4,y=s.top+3+(s.height-6)*j/4;
                    const e=document.elementFromPoint(x,y);if(!e||!b.contains(e))misses.push([Math.round(x),Math.round(y),e?.className||e?.tagName||null]);}
                  return {top:s.top,bottom:s.bottom,left:s.left,right:s.right,h:s.height,navTop:nav.top,
                    headBottom:headFixed?head.bottom:0,viewport:innerHeight,width:innerWidth,misses}}""", sel)
                assert clear["bottom"] <= clear["navTop"] + 0.5, (width, route, clear)
                assert clear["top"] >= clear["headBottom"] - 0.5 and clear["top"] >= 0, (width, route, clear)
                assert clear["left"] >= -0.5 and clear["right"] <= clear["width"] + 0.5, (width, route, clear)
                assert not clear["misses"], (width, route, clear)
                print(f"  {width}x{height} {route}: rect {clear['top']:.0f}-{clear['bottom']:.0f}px, "
                      f"footer top {clear['navTop']:.0f}px, 25/25 points hit")
            assert page.evaluate(SNAPSHOT) == before, (width, "no additional writes since snapshot")

            # Real pointer click through the frame overlay -> guarded Unit Box
            # handoff; then busy / Auto / stale-form refusals on the same path.
            def click_slot(index):
                page.evaluate("window.scrollTo(0,0)")
                box = page.locator("#bf-scene-party > button").nth(index).bounding_box()
                page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                page.wait_for_timeout(50)
                return page.evaluate("BF_homeNav.current")
            for index in (0, 5):
                expected = page.evaluate(f"""() => {{const id=P.squad[{index}];
                  return {{id,name:effectiveUnit(id).name}}}}""")
                assert click_slot(index) == "units", (width, index)
                shown = page.evaluate("""() => {const d=document.getElementById('bf-box-detail'),
                  h=d.querySelector('h3');return {text:h?.textContent||'',focused:document.activeElement===h,
                  visible:!!h&&h.getBoundingClientRect().height>0}}""")
                assert expected["name"] in shown["text"] and shown["focused"] and shown["visible"], (width, index, shown)
                page.locator('.bf-navbar button[data-bf-goto="home"]').click()
                assert page.evaluate("BF_homeNav.current") == "home"
            refusals = {
                "busy": ("S.busy=true", "S.busy=false"),
                "auto": ("S.auto=true", "S.auto=false"),
                "stale-form": ("window.__v635Eff=effectiveUnit;effectiveUnit=id=>{const u=window.__v635Eff(id);"
                               "return u&&id===P.squad[0]?Object.assign({},u,{id:u.id+1}):u;}",
                               "effectiveUnit=window.__v635Eff;delete window.__v635Eff"),
            }
            for label, (arm, disarm) in refusals.items():
                assert page.evaluate("S.busy===false&&S.auto===false"), (width, label, "precondition")
                page.evaluate(arm)
                try:
                    route = click_slot(0)
                finally:
                    page.evaluate(disarm)
                assert route == "home", (width, label, route)
            assert click_slot(0) == "units", (width, "guards restored")
            page.locator('.bf-navbar button[data-bf-goto="home"]').click()
            after_box = page.evaluate(SNAPSHOT)
            assert after_box["player"] == before["player"] and after_box["writes"] == before["writes"], (width, "no additional writes since snapshot")
            print(f"  {width}x{height} Unit Box: slot 1 and 6 click handoff OK; busy/auto/stale-form refused")

            # Manual navigation still works: Quest gateway, Summon, Units, Menu, Home.
            page.evaluate("window.scrollTo(0,0)")
            page.locator('#bf-home .bf-scene-featured[data-bf-goto="quest"]').click()
            assert page.evaluate("BF_homeNav.current") == "quest"
            for route in ("summon", "units", "menu", "home"):
                page.locator(f'.bf-navbar button[data-bf-goto="{route}"]').click()
                assert page.evaluate("BF_homeNav.current") == route, (width, route)
            assert page.locator("#bf-scene-party > button").count() == 6
            after = page.evaluate(SNAPSHOT)
            assert after["player"] == before["player"] and after["writes"] == before["writes"], (width, after)
            assert not errors, (width, errors)
            print(f"PASS v635 {width}x{height}: geometry five 128x350 openings in 640x356 frame "
                  f"(slot {slot_w:.1f}x{slot_w*350/128:.1f}px), leader slot 1, sixth below, "
                  "disclosure intact, navigation OK, no additional writes since snapshot "
                  "(geometry/behavior only; not screenshot parity)")
            page.close()
    finally:
        browser.close()
print("PASS v635: squad frame geometry, owned-unit identity, guarded Unit Box handoff, footer clearance, no additional writes (not pixel parity, not device acceptance)")
