"""v242: visible original-asset Home prioritization, browser + source regressions.

No reward, game-state, save, unit, or network semantics are changed by v242.
"""
from pathlib import Path
import re
import sys

R=Path(__file__).resolve().parent
A=R/"app/src/main/assets"
J=(A/"bf_home_nav.js").read_text("utf8")
C=(A/"bf_home_nav.css").read_text("utf8")
W=(R/".github/workflows/build-debug-apk.yml").read_text("utf8")
PRE=(R/".github/workflows/android-back-ui-source-preflight.yml").read_text("utf8")
M=(R/"app/src/main/AndroidManifest.xml").read_text("utf8")

start=J.index("/* Build #9: original Global home location hub")
end=J.index("/* Build #11 - recovered BF1 Global artwork")
home=J[start:end]
available="bf-scene-available-label"
archived="bf-scene-archive-label"
assert home.count(available)==1 and home.count(archived)==1
assert home.count('class="bf-scene-place bf-scene-active bf-scene-featured"')==2
assert home.count('class="bf-scene-place bf-scene-locked"')==4
assert home.index("AVAILABLE OFFLINE") < home.index('data-bf-goto="quest"') < home.index('data-bf-goto="summon"') < home.index("RECOVERED GLOBAL LOCATIONS") < home.index("Vortex Gate not implemented")
for path in ("home_win_quest.png","home_win_akras_smn_hall.png",
             "home_win_gate.png","home_win_arena.png",
             "home_win_raid_open.png","home_win_randall.png"):
    assert path in home
assert "window.BFGlobalHome = {refreshParty};" in home
assert 'data-bf-goto="menu"' in home
assert "window.BF_homeNav = {go,get current()" in J
assert "/* v242: visual-first Home hierarchy" in C
assert C.count("/* v246: readable nameplates for original Global art-only") == 1
# v617: two original art assets, contrasting hierarchy on phones only.
gate="/* v617 original-art centered Quest gateway"
assert C.count(gate)==1
focus=C.split(gate,1)[1]
for token in ('@media(max-width:412px)', 'data-bf-goto="quest"',
              'data-bf-goto="summon"', 'grid-column:1/-1',
              'justify-self:center', 'width:min(100%,288px)',
              'width:min(100%,228px)', 'min-height:44px',
              'object-fit:contain', 'overflow-wrap:anywhere'):
    assert token in focus,token
for forbidden in ("localStorage", "saveProgress(", "awardDemoRewards(",
                  "P.", "S.", "fetch(", "XMLHttpRequest(",
                  "display:none", "visibility:hidden", "pointer-events:none"):
    assert forbidden not in focus,forbidden
sty=C.split("/* v242: visual-first Home hierarchy",1)[1].split(
    "/* v246: readable nameplates for original Global art-only",1
)[0]
for selector in (".bf-scene-places button.bf-scene-featured",
                 ".bf-scene-places .bf-scene-locked",
                 ".bf-scene-available-label",
                 ".bf-scene-archive-label",
                 "max-width:359px"):
    assert selector in sty
for forbidden in ("localStorage","saveProgress(","awardDemoRewards(",
                  "P.","S.","#battle", "animation-duration"):
    assert forbidden not in sty
for forbidden in ("localStorage.setItem(","saveProgress(","P.squad =",
                  "P.questClears =","awardDemoRewards("):
    assert forbidden not in home, forbidden
assert "android.permission.INTERNET" not in M
assert W.count("test_bf_home_ui_priority_v24200.py")==1
assert PRE.count("test_bf_home_ui_priority_v24200.py")==2
assert len(J.encode("utf8"))<128*1024 and len(C.encode("utf8"))<128*1024
print("PASS v242 source: active Home destinations first, original art intact, no game/save changes")
if "--source-only" in sys.argv:
    raise SystemExit(0)

# The original Global sprites are staged by the normal asset-preparation
# step before full browser/Android tests, not present at source-only checkout.
for name in ("home_win_quest.png","home_win_akras_smn_hall.png",
             "home_win_gate.png","home_win_arena.png",
             "home_win_raid_open.png","home_win_randall.png"):
    assert (A/"content/home"/name).is_file(), name

import shutil
from playwright.sync_api import sync_playwright
chrome=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable")
assert chrome, "Chromium required by full visual UI regression"
marker="\n})();"
assert J.count(marker)>=2
pilot=marker.join(J.split(marker)[:2])+marker
html='''<!doctype html><html><head><meta charset="utf-8"></head><body>
<main class="wrap">
<section class="progresspanel">Save menu</section>
<section class="questpanel">Quest route</section>
<section class="squadsetup">Units route</section>
<section class="summonpanel">Summon route</section>
</main></body></html>'''
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=chrome,
                               args=["--no-sandbox","--disable-dev-shm-usage"])
    for width in (320,360,393,412,540):
        page=browser.new_page(viewport={"width":width,"height":750},device_scale_factor=2)
        errors=[]
        page.on("pageerror",lambda error:errors.append(str(error)))
        page.set_content(html)
        # Record direct storage mutations without changing storage semantics.
        page.evaluate("""() => {window.__v242Writes=[];
          for(const name of ['setItem','removeItem','clear']){
            const orig=Storage.prototype[name];
            Storage.prototype[name]=function(...args){
              window.__v242Writes.push({name,key:args.length?String(args[0]):null});
              return orig.apply(this,args);
            };
          }
        }""")
        page.add_style_tag(content=C)
        page.add_script_tag(content=pilot)
        page.wait_for_timeout(35)
        assert page.evaluate('window.__v242Writes.length')==0,(width,'passive write')
        assert page.locator(".bf-scene-featured").count()==2
        assert page.locator(".bf-scene-locked").count()==4
        assert page.locator(".bf-scene-places > :first-child").get_attribute("class")==available
        positions=page.locator(".bf-scene-places").evaluate(
            "(root)=>Array.from(root.children).map(el=>el.className)")
        # Strictly accept the two authenticated presentations of the SAME
        # live Story node. All child classes and four locked cards are pinned.
        active="bf-scene-place bf-scene-active bf-scene-featured"
        locked="bf-scene-place bf-scene-locked"
        v636_order=[available,active,active,archived]+[locked]*4
        v639_order=[available,active,active,"bf-scene-story",archived]+[locked]*4
        # Source-selected strict ordering: v639 MUST not pass by silently
        # falling back to the historic v636 Story-before-Explore DOM order.
        quest_first_story='// v638 local: keep the exact live Story node' in J
        expected_order=v639_order if quest_first_story else v636_order
        assert positions==expected_order,(width,'source-pinned exact Story order',positions)
        fidelity=page.locator("#bf-home").evaluate("""home=>{
          const places=home.querySelector('.bf-scene-places'),
            story=home.querySelector('.bf-scene-story'),
            adventure=home.querySelector('.bf-scene-explore'),
            quest=places.querySelector(':scope > [data-bf-goto="quest"]'),
            summon=places.querySelector(':scope > [data-bf-goto="summon"]'),
            archive=places.querySelector(':scope > .bf-scene-archive-label'),
            locked=[...places.querySelectorAll(':scope > .bf-scene-locked')];
          return {
            storyCount:home.querySelectorAll('.bf-scene-story').length,
            storyButtonCount:home.querySelectorAll('#bf-home-story-open').length,
            archiveCount:home.querySelectorAll('.bf-scene-archive-label').length,
            archiveIdentity:archive?.getAttribute('role')==='heading'&&
              archive?.getAttribute('aria-level')==='3'&&
              archive?.querySelector('strong')?.textContent==='RECOVERED GLOBAL LOCATIONS',
            originalOrder:story?.parentElement===home&&
              story.nextElementSibling===adventure&&
              home.querySelector('.bf-scene-squad')?.nextElementSibling===story,
            relocatedOrder:story?.parentElement===places&&
              summon?.nextElementSibling===story&&story.nextElementSibling===archive,
            liveRoutes:quest?.getAttribute('data-bf-goto')==='quest'&&
              summon?.getAttribute('data-bf-goto')==='summon'&&
              places.querySelectorAll(':scope > .bf-scene-featured').length===2,
            originalArt:quest?.querySelector('img')?.getAttribute('src')==='content/home/home_win_quest.png'&&
              summon?.querySelector('img')?.getAttribute('src')==='content/home/home_win_akras_smn_hall.png',
            lockedCount:locked.length,
            lockedIdentity:locked.every(e=>e.getAttribute('aria-disabled')==='true'&&
              e.getAttribute('role')==='group'&&!e.hasAttribute('data-bf-goto')),
            lockedArt:locked.map(e=>e.querySelector('img')?.getAttribute('src')),
            archiveBeforeLocked:archive?.nextElementSibling===locked[0]&&
              locked.every((e,i)=>i===0||locked[i-1].nextElementSibling===e)
          };
        }""")
        assert fidelity['storyCount']==1 and fidelity['storyButtonCount']==1,(width,fidelity)
        assert fidelity['archiveCount']==1 and fidelity['archiveIdentity'],(width,fidelity)
        assert fidelity['lockedCount']==4 and fidelity['lockedIdentity'],(width,fidelity)
        assert fidelity['lockedArt']==['content/home/home_win_gate.png',
            'content/home/home_win_arena.png','content/home/home_win_raid_open.png',
            'content/home/home_win_randall.png'],(width,fidelity)
        assert fidelity['liveRoutes'] and fidelity['originalArt'] and fidelity['archiveBeforeLocked'],(width,fidelity)
        assert (fidelity['relocatedOrder'] and not fidelity['originalOrder']) if quest_first_story else (
            fidelity['originalOrder'] and not fidelity['relocatedOrder']), (width,fidelity)
        bounds=page.locator(".bf-scene-places").evaluate(
            "(el)=>({scroll:el.scrollWidth,client:el.clientWidth})")
        assert bounds["scroll"] <= bounds["client"]+2,(width,bounds)
        assert page.locator(".bf-scene-featured").first.evaluate(
            "(el)=>getComputedStyle(el).minHeight") != "0px"
        for target in ('quest','summon'):
            b=page.locator(f'.bf-scene-featured[data-bf-goto="{target}"]')
            b.scroll_into_view_if_needed()
            hit=b.evaluate("""el=>{
              const r=el.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2;
              const t=document.elementFromPoint(x,y);
              const visible=[];
              for(const px of [.1,.3,.5,.7,.9])for(const py of [.1,.3,.5,.7,.9]){
                const a=r.left+px*r.width,b=r.top+py*r.height;
                if(a<0||b<0||a>=innerWidth||b>=innerHeight)continue;
                const h=document.elementFromPoint(a,b);
                if(h&&(h===el||el.contains(h)))visible.push([px,py]);
              }
              return {width:r.width,height:r.height,atCenter:!!t&&(el===t||el.contains(t)),visibleHits:visible.length};
            }""")
            assert hit['width']>=44 and hit['height']>=44 and hit['visibleHits']>=1,(width,target,hit)
        # Existing active destinations and source order remain exactly the
        # same, but an owner phone now shows the original Quest gateway
        # centered and larger than the subordinate Summoning Hall tile.
        geometry=page.locator(".bf-scene-places").evaluate("""root=>{
          const q=root.querySelector('[data-bf-goto="quest"]'),
            s=root.querySelector('[data-bf-goto="summon"]'),
            a=root.getBoundingClientRect(),x=q.getBoundingClientRect(),
            y=s.getBoundingClientRect();
          return {qc:x.left+x.width/2,ac:a.left+a.width/2,
            qwidth:x.width,swidth:y.width,qheight:x.height,sheight:y.height,
            questBeforeSummon:x.bottom<=y.top+1,
            questGrid:getComputedStyle(q).gridColumnStart,
            summonGrid:getComputedStyle(s).gridColumnStart,
            questImage:q.querySelector('img').getAttribute('src'),
            summonImage:s.querySelector('img').getAttribute('src'),
            questAccessible:q.getAttribute('aria-label'),
            summonAccessible:s.getAttribute('aria-label')};
        }""")
        assert geometry['questAccessible']=='Quest: play demo battles',geometry
        assert geometry['summonAccessible']=='Summoning Hall: demo recruitment',geometry
        assert geometry['questImage']=='content/home/home_win_quest.png',geometry
        assert geometry['summonImage']=='content/home/home_win_akras_smn_hall.png',geometry
        if width<=412:
            assert geometry['qwidth']>geometry['swidth'],(width,geometry)
            assert abs(geometry['qc']-geometry['ac'])<=2,(width,geometry)
            assert geometry['qheight']>=160 and geometry['sheight']>=90,(width,geometry)
            assert geometry['questBeforeSummon'],(width,geometry)
            assert geometry['questGrid']=='1' and geometry['summonGrid']=='1',(width,geometry)
        page.locator('.bf-scene-featured[data-bf-goto="summon"]').click()
        assert page.evaluate("BF_homeNav.current")=="summon"
        page.locator('.bf-navbar [data-bf-goto="home"]').click()
        page.locator('.bf-scene-featured[data-bf-goto="quest"]').click()
        assert page.evaluate("BF_homeNav.current")=="quest"
        page.locator('.bf-navbar [data-bf-goto="home"]').click()
        page.locator('.bf-scene-toolrow [data-bf-goto="menu"]').click()
        assert page.evaluate("BF_homeNav.current")=="menu"
        assert not errors,(width,errors)
        assert page.evaluate('window.__v242Writes.length')==0,(width,'unexpected storage write',page.evaluate('window.__v242Writes'))
        page.close()
    browser.close()
print("PASS v242 browser: 320/360/393/412/540px usable Quest, Summon and Saves UI")
