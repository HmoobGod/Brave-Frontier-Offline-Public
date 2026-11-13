#!/usr/bin/env python3
"""v424: manual DEMO target preview, source-legal display only."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
A=R/"app/src/main/assets"
js=(A/"bf2100_battle_command_tray.js").read_text("utf8")
assert "TARGET UNVERIFIED" in js and "new Set(living.map(e=>e.slot))" in js
assert "min-height:44px;touch-action:manipulation" in js
assert "orders.textContent=queuedTurnPreview()" in js
assert "localStorage" not in js and "saveProgress(" not in js
with sync_playwright() as pw:
    browser=pw.chromium.launch(
        headless=True, executable_path=shutil.which("chromium") or
        shutil.which("google-chrome") or shutil.which("google-chrome-stable"),
        args=["--no-sandbox","--disable-dev-shm-usage"])
    try:
        page=browser.new_page(viewport={"width":390,"height":844})
        errors=[]
        page.on("pageerror",lambda e:errors.append(str(e)))
        page.evaluate("""()=>{
          const db={};let writes=0;
          Object.defineProperty(window,"localStorage",{configurable:true,value:{
            getItem:k=>db[k]??null,
            setItem:(k,v)=>{writes++;db[k]=String(v)},
            removeItem:k=>{writes++;delete db[k]},
            key:i=>Object.keys(db)[i]??null,
            get length(){return Object.keys(db).length}
          }});
          window.__v424Writes=()=>writes;
          window.alert=()=>{};window.confirm=()=>true;
          HTMLMediaElement.prototype.load=()=>{};
          HTMLMediaElement.prototype.pause=()=>{};
          HTMLMediaElement.prototype.play=()=>Promise.resolve();
        }""")
        page.set_content((A/"index.html").read_text("utf8"),
                         wait_until="load",timeout=90000)
        page.add_style_tag(path=str(A/"bf_home_nav.css"))
        for file in ("bf_home_nav.js","bf080_morgan_map.js",
                     "bf090_st_lamia_map.js","bf100_grand_gaia_campaign.js",
                     "bf101_story_continue.js","bf110_quest_journal.js",
                     "bf2000_story_battle_hud.js","bf2100_battle_command_tray.js"):
            page.add_script_tag(path=str(A/file))
        page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
        # Regression: panel must be inserted into the real DOM, not just built.
        assert page.locator('#bf2100-tray').count()==1
        assert page.locator('#bf2100-tray').is_visible()
        api="BFGlobalBattleCommandsV2100"
        assert page.evaluate("P.version")==7
        assert page.evaluate(api+'.queueAll("attack")') is True
        orders=page.locator("#bf2100-orders")
        assert orders.inner_text().count(": Attack →")==6,orders.inner_text()
        target=page.evaluate("""()=>{
          const p=S.party.find(u=>u.active&&u.hp>0&&u.action?.kind==='attack');
          const e=S.enemies.find(e=>e.hp>0&&e.slot===p.action.target);
          return {slot:p.id,enemy:e.slot,name:e.name};
        }""")
        assert (f"Slot {target['slot']+1}: Attack → {target['name']} "
                f"(enemy slot {target['enemy']+1})") in orders.inner_text()
        before=page.evaluate("""()=>({
          p:JSON.stringify(P),s:JSON.stringify(S),
          save:localStorage.getItem('bf_global_offline_demo_v7'),
          writes:__v424Writes()
        })""")
        for width in (320,370,390,540):
            page.set_viewport_size({"width":width,"height":844})
            page.evaluate(api+".refresh()")
            assert orders.inner_text().count(": Attack →")==6
            buttons=page.locator("#bf2100-targets button")
            assert buttons.count()>0
            for i in range(buttons.count()):
                assert buttons.nth(i).evaluate("e=>e.getBoundingClientRect().height")>=44
        after=page.evaluate("""()=>({
          p:JSON.stringify(P),s:JSON.stringify(S),
          save:localStorage.getItem('bf_global_offline_demo_v7'),
          writes:__v424Writes()
        })""")
        assert before==after,(before,after)
        page.evaluate("S.party[0].action.target=99999")
        page.evaluate(api+".refresh()")
        assert "Slot 1: Attack → TARGET UNVERIFIED" in orders.inner_text()
        page.evaluate("""()=>{
          S.party[0].action.target=S.enemies[0].slot;
          window.__v424EnemyCount=S.enemies.length;
          S.enemies.push({...S.enemies[0]});
        }""")
        page.evaluate(api+".refresh()")
        assert "TARGET UNVERIFIED" in orders.inner_text()
        page.evaluate("S.enemies.length=window.__v424EnemyCount;delete window.__v424EnemyCount")
        page.evaluate(api+".refresh()")
        assert "Slot 1: Attack → TARGET UNVERIFIED" not in orders.inner_text()
        page.evaluate("""()=>{
          window.__v424Name=S.enemies[0].name;
          S.enemies[0].name='<img id="v424-injected" src=x>';
        }""")
        page.evaluate(api+".refresh()")
        assert page.locator("#v424-injected").count()==0
        page.evaluate("S.enemies[0].name=window.__v424Name;delete window.__v424Name")
        page.evaluate(api+".refresh()")
        assert page.evaluate("S.busy") is False
        assert page.evaluate("S.auto") is False
        assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')") is None
        assert page.evaluate("__v424Writes()")==before["writes"]
        assert not errors,errors
    finally:
        browser.close()
print("PASS v424 player target display, stale/duplicate rejection, 44px, no Execute/save")
