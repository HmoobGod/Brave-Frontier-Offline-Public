#!/usr/bin/env python3
"""v423: Home shows only owned, nonduplicate live squad entries (read-only)."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "app/src/main/assets"
JS = (ASSETS / "bf_home_nav.js").read_text("utf8")
CSS = (ASSETS / "bf_home_nav.css").read_text("utf8")
assert "bf-scene-party-review" in JS and CSS
assert "roster.includes(baseId)" in JS and "!seen.has(baseId)" in JS
assert "saveProgress(" not in JS
with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=True,
        executable_path=shutil.which("chromium") or shutil.which("google-chrome")
                        or shutil.which("google-chrome-stable"),
        args=["--no-sandbox", "--disable-dev-shm-usage"])
    try:
        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.evaluate("""() => {
            const db={};let writes=0;
            Object.defineProperty(window, "localStorage", {configurable:true,value:{
              getItem:k=>db[k]??null,
              setItem:(k,v)=>{writes++;db[k]=String(v)},
              removeItem:k=>{writes++;delete db[k]},
              key:i=>Object.keys(db)[i]??null,
              get length(){return Object.keys(db).length}
            }});
            window.__v423Writes=()=>writes;
            window.alert=()=>{};window.confirm=()=>true;
            HTMLMediaElement.prototype.load=()=>{};
            HTMLMediaElement.prototype.pause=()=>{};
            HTMLMediaElement.prototype.play=()=>Promise.resolve();
        }""")
        page.set_content((ASSETS / "index.html").read_text("utf8"),
                         wait_until="load", timeout=90000)
        page.add_style_tag(path=str(ASSETS / "bf_home_nav.css"))
        page.add_script_tag(path=str(ASSETS / "bf_home_nav.js"))
        assert page.evaluate("P.version") == 7
        assert page.evaluate("BF_homeNav.current") == "home"
        assert page.locator("#bf-scene-party .bf-scene-member").count() == 6
        warning = page.locator("#bf-scene-party-review")
        assert warning.count() == 1 and warning.is_hidden()
        # Real Home portrait controls open the CURRENT owned profile through
        # the existing Unit Box, including keyboard activation and narrow phones.
        # Home identifies actual ordered squad slots, not a promoted fallback leader.
        slot_snapshot = """()=>JSON.stringify({P,S,quest:QUEST.missionId,
          storage:Object.fromEntries(Array.from({length:localStorage.length},(_,i)=>{
            const k=localStorage.key(i);return [k,localStorage.getItem(k)]})),
          writes:__v423Writes()})"""
        slot_before=page.evaluate(slot_snapshot)
        for width in (320,390,540):
            page.set_viewport_size({'width':width,'height':844})
            page.evaluate('BFGlobalHome.refreshParty()')
            cards=page.locator('#bf-scene-party .bf-scene-member')
            assert page.locator('#bf-scene-party .bf-scene-leader').count()==1
            for index in range(6):
                role=cards.nth(index).locator('.bf-scene-slot')
                assert role.is_visible() and f'SLOT {index+1}' in role.inner_text()
                assert f'squad slot {index+1} of 6' in cards.nth(index).get_attribute('aria-label')
                assert ('Leader' in cards.nth(index).get_attribute('aria-label'))==(index==0)
                assert cards.nth(index).locator('.bf-scene-leader').count()==int(index==0)
                assert role.evaluate('(el)=>el.scrollWidth<=el.clientWidth'),(width,index)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert page.evaluate(slot_snapshot)==slot_before
        for first in (None, -1):
            page.evaluate("""first=>{window.__slotSquad=P.squad;P.squad=[first,...P.squad.slice(1)];}""",first)
            try:
                fixture_before=page.evaluate(slot_snapshot)
                page.evaluate('BFGlobalHome.refreshParty()')
                assert page.locator('#bf-scene-party .bf-scene-leader').count()==0
                assert 'Leader' not in page.locator('#bf-scene-party').inner_text()
                assert 'squad slot 2 of 6' in page.locator('#bf-scene-party button').first.get_attribute('aria-label')
                assert page.evaluate(slot_snapshot)==fixture_before
            finally:
                page.evaluate('P.squad=window.__slotSquad;delete window.__slotSquad;BFGlobalHome.refreshParty()')
        print('PASS ordered Home slot/leader labels at three widths, no fallback leader or player/storage writes')
        before_inspect = page.evaluate("""()=>({
          p:JSON.stringify(P),s:JSON.stringify(S),quest:QUEST.missionId,
          save:localStorage.getItem('bf_global_offline_demo_v7'),writes:__v423Writes()
        })""")
        for width in (320,390,540):
            page.set_viewport_size({"width":width,"height":844})
            for slot in (0,5):
                portrait = page.locator('#bf-scene-party button.bf-scene-member').nth(slot)
                unit_id = portrait.get_attribute('data-bf-home-unit-id')
                bounds = portrait.bounding_box()
                assert bounds['width'] >= 44 and bounds['height'] >= 44,(width,bounds)
                assert portrait.get_attribute('aria-label').startswith('Inspect ')
                if slot == 0:
                    portrait.click()
                else:
                    portrait.focus()
                    portrait.press('Enter' if width == 390 else 'Space')
                assert page.evaluate('BF_homeNav.current') == 'units'
                assert page.evaluate('BFInnerScreens.unitTab') == 'box'
                detail = page.locator('#bf-box-detail')
                assert detail.is_visible()
                assert f'Base roster ID {unit_id} ·' in detail.inner_text()
                assert detail.locator('h3').evaluate('(e)=>document.activeElement===e')
                assert page.locator(f'#bf-box-results [data-bf-unit-id="{unit_id}"]').get_attribute('aria-pressed') == 'true'
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
                page.locator('.bf-navbar button[data-bf-goto="home"]').click()
        after_inspect = page.evaluate("""()=>({
          p:JSON.stringify(P),s:JSON.stringify(S),quest:QUEST.missionId,
          save:localStorage.getItem('bf_global_offline_demo_v7'),writes:__v423Writes()
        })""")
        assert before_inspect == after_inspect
        # A painted portrait cannot bypass ownership or in-progress controls
        # if the live state changes before a click. All fixtures are restored.
        blocked = page.evaluate("""()=>{
          const card=document.querySelector('#bf-scene-party button');
          const original={squad:P.squad,roster:P.roster,busy:S.busy,auto:S.auto,
            repeat:window.BFGlobalQoLQuestRepeatV9800};
          const reports=[];
          const click=()=>{card.click();reports.push(BF_homeNav.current)};
          try{
            S.busy=true;click();S.busy=original.busy;
            S.auto=true;click();S.auto=original.auto;
            for(const provider of [()=>({active:true}),()=>null,
                ()=>{throw Error('unavailable') }]){
              window.BFGlobalQoLQuestRepeatV9800={statusSnapshot:provider};click();
            }
            window.BFGlobalQoLQuestRepeatV9800=original.repeat;
            P.roster=[];click();P.roster=original.roster;
            P.squad=[];click();P.squad=original.squad;
          }finally{
            P.squad=original.squad;P.roster=original.roster;
            S.busy=original.busy;S.auto=original.auto;
            window.BFGlobalQoLQuestRepeatV9800=original.repeat;
          }
          return reports;
        }""")
        assert len(blocked) == 7 and all(route == 'home' for route in blocked),blocked
        assert page.evaluate("""()=>({
          p:JSON.stringify(P),s:JSON.stringify(S),quest:QUEST.missionId,
          save:localStorage.getItem('bf_global_offline_demo_v7'),writes:__v423Writes()
        })""") == before_inspect
        ids = page.evaluate("""() => {
           const owned = P.roster.find(id=>Number.isSafeInteger(id)&&id>0&&effectiveUnit(id));
           const unowned = [10012,20012,30012,40012,50012,60012,
                            10013,20013,30013,40013,50013,60013]
                .find(id=>!P.roster.includes(id)&&effectiveUnit(id));
           return {owned,unowned};
        }""")
        assert ids["owned"] is not None and ids["unowned"] is not None, ids
        page.evaluate("""({owned,unowned})=>{
           window.__v423Original=P.squad.slice();
           P.squad=[owned,unowned,owned,null,-1,{}];
        }""", ids)
        state = page.evaluate("""()=>({
           p:JSON.stringify(P),s:JSON.stringify(S),
           save:localStorage.getItem('bf_global_offline_demo_v7'),
           writes:__v423Writes()
        })""")
        for width in (320,370,390,540):
            page.set_viewport_size({"width":width,"height":844})
            page.evaluate("BFGlobalHome.refreshParty()")
            cards = page.locator("#bf-scene-party .bf-scene-member")
            assert cards.count() == 6
            assert page.locator('#bf-scene-party button.bf-scene-member').count() == 1
            assert "REVIEW" not in cards.nth(0).inner_text()
            for i in (1,2,4,5):
                assert cards.nth(i).inner_text() == "REVIEW", (width,i)
                assert "Unverified" in cards.nth(i).get_attribute("aria-label")
            assert "Empty squad slot" in cards.nth(3).get_attribute("aria-label")
            assert warning.is_visible()
            assert "4 squad entries need review" in warning.inner_text()
            bounds = warning.evaluate("""el=>{
              const r=el.getBoundingClientRect();
              return {left:r.left,right:r.right};
            }""")
            assert bounds["left"] >= -1 and bounds["right"] <= width+1, (width,bounds)
        after = page.evaluate("""()=>({
           p:JSON.stringify(P),s:JSON.stringify(S),
           save:localStorage.getItem('bf_global_offline_demo_v7'),
           writes:__v423Writes()
        })""")
        assert state == after, (state,after)
        page.evaluate("P.squad=window.__v423Original;delete window.__v423Original")
        page.evaluate("BFGlobalHome.refreshParty()")
        assert warning.is_hidden()
        assert page.locator("#bf-scene-party .bf-scene-member").count() == 6
        assert not errors, errors
    finally:
        browser.close()
print("PASS v423 Home owned squad validation, mobile REVIEW status, no save/Auto changes")
