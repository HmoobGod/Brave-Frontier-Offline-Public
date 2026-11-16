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
        # Hold the painted card while live providers/data change. Keyboard
        # activation must fail closed without refreshing away the stale card.
        for width in (320,390,540):
            page.set_viewport_size({'width':width,'height':844})
            for key in ('Enter','Space'):
                count=page.evaluate("""()=>{
                  BF_homeNav.go('home');BFGlobalHome.refreshParty();
                  const card=document.querySelector('#bf-scene-party button');
                  const old={busy:S.busy,auto:S.auto,roster:P.roster,squad:P.squad,
                    effective:effectiveUnit,repeat:window.BFGlobalQoLQuestRepeatV9800};
                  const fixtures=[];
                  for(const flag of ['busy','auto'])for(const value of [true,null,undefined,0,'','false'])
                    fixtures.push(()=>S[flag]=value);
                  fixtures.push(()=>P.roster=[...old.roster,old.roster[0]],
                    ()=>P.roster=[...old.roster,-1],()=>P.roster=Array(2),
                    ()=>P.squad=[...old.squad,old.squad[0]],
                    ()=>effectiveUnit=()=>({id:0,name:'Invalid'}),
                    ()=>effectiveUnit=()=>({id:1,name:' '}),
                    ()=>effectiveUnit=()=>{throw Error('profile unavailable')});
                  for(const value of [null,{}, {active:'false'}])
                    fixtures.push(()=>window.BFGlobalQoLQuestRepeatV9800={statusSnapshot:()=>value});
                  const reset=()=>{S.busy=old.busy;S.auto=old.auto;P.roster=old.roster;
                    P.squad=old.squad;effectiveUnit=old.effective;
                    window.BFGlobalQoLQuestRepeatV9800=old.repeat;};
                  const snap=()=>JSON.stringify({P,S,mission:QUEST.missionId,
                    storage:Object.fromEntries(Array.from({length:localStorage.length},(_,i)=>{
                      const k=localStorage.key(i);return [k,localStorage.getItem(k)];})),writes:__v423Writes()});
                  window.__stalePortrait={card,fixtures,reset,snap,original:snap()};
                  return fixtures.length;
                }""")
                assert count==22,count
                for case in range(count):
                    page.evaluate('(i)=>{const f=__stalePortrait;f.reset();f.fixtures[i]();f.before=f.snap();f.card.focus();}',case)
                    page.keyboard.press(key)
                    assert page.evaluate("BF_homeNav.current==='home'&&__stalePortrait.snap()===__stalePortrait.before"),(width,key,case)
                assert page.evaluate('()=>{const f=__stalePortrait;f.reset();return f.snap()===f.original;}')
                # The same retained card still works after all fixtures restore.
                page.evaluate('__stalePortrait.card.focus()')
                page.keyboard.press(key)
                assert page.evaluate("BF_homeNav.current==='units'")
                page.evaluate("BF_homeNav.go('home');delete window.__stalePortrait")
        print('PASS stale portrait strict idle/ownership/profile guards: 132 keyboard probes, full storage invariance')
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
        corrupt=page.evaluate("""()=>{const original={squad:P.squad,roster:P.roster,version:P.version},before=JSON.stringify({P,S}),out=[];
          try{for(const [key,value] of [['squad',null],['squad',{}],['squad',Array(7).fill(P.squad[0])],['roster',null],['roster',[P.roster[0],P.roster[0]]],['roster',Array(2)],['version',6]]){Object.assign(P,original);P[key]=value;BFGlobalHome.refreshParty();out.push(document.querySelectorAll('#bf-scene-party button').length===0&&!document.querySelector('#bf-scene-party-review').hidden&&document.querySelector('#bf-scene-party-review').textContent.includes('unavailable'));}}
          finally{Object.assign(P,original);BFGlobalHome.refreshParty();}return {out,same:before===JSON.stringify({P,S})};}""")
        assert corrupt=={'out':[True]*7,'same':True},corrupt
        level_proof=page.evaluate("""()=>{const exp=P.unitExp,id=P.squad[0],before=JSON.stringify({P,S}),out=[];let getterCalls=0;
          try{for(const value of [null,{},[0],{[id]:'0'},{[id]:-1},{[id]:NaN}]){P.unitExp=value;BFGlobalHome.refreshParty();out.push(document.querySelector('#bf-scene-party button small').textContent==='LEVEL UNAVAILABLE');}
          P.unitExp={};Object.defineProperty(P.unitExp,String(id),{get:()=>{getterCalls++;return 0;}});BFGlobalHome.refreshParty();out.push(document.querySelector('#bf-scene-party button small').textContent==='LEVEL UNAVAILABLE');
          }finally{P.unitExp=exp;BFGlobalHome.refreshParty();}return {out,getterCalls,same:before===JSON.stringify({P,S})};}""")
        assert level_proof=={'out':[True]*7,'getterCalls':0,'same':True},level_proof
        # Combined role/ownership/level behaviors must agree on the same painted cards.
        for width in (320,390,540):
            page.set_viewport_size({'width':width,'height':844})
            combined=page.evaluate("""()=>{
              const old={squad:P.squad,roster:P.roster,version:P.version,exp:P.unitExp,
                unit:window.effectiveUnit},reports=[];let reads=0;
              const firstId=old.squad[0];
              const reset=()=>{P.squad=old.squad;P.roster=old.roster;P.version=old.version;
                P.unitExp=old.exp;window.effectiveUnit=old.unit};
              const snap=()=>JSON.stringify({P,S,mission:QUEST.missionId,writes:__v423Writes(),
                storage:Object.fromEntries(Array.from({length:localStorage.length},(_,i)=>{
                  const k=localStorage.key(i);return [k,localStorage.getItem(k)]}))});
              const original=snap(),party=document.getElementById('bf-scene-party');
              const buttons=()=>[...party.querySelectorAll('button')];
              const leaders=()=>party.querySelectorAll('.bf-scene-leader').length;
              const run=(name,change,verify)=>{
                try{reset();change();const before=snap();BFGlobalHome.refreshParty();
                  reports.push({name,ok:verify(),unchanged:snap()===before});
                }finally{reset();BFGlobalHome.refreshParty();}
              };
              const unavailable=()=>buttons().length===0&&leaders()===0&&
                !document.getElementById('bf-scene-party-review').hidden&&
                document.getElementById('bf-scene-party-review').textContent.includes('unavailable');
              run('unreadable roster',()=>P.roster=null,unavailable);
              run('wrong version',()=>P.version=6,unavailable);
              const unknownLevel=()=>{
                const first=buttons()[0],level=first?.querySelector('small');
                if(!level)return false;const a=first.getBoundingClientRect(),b=level.getBoundingClientRect();
                return buttons().length===6&&leaders()===1&&
                  first.querySelectorAll('.bf-scene-leader').length===1&&
                  first.getAttribute('aria-label').includes('squad slot 1 of 6')&&
                  level.textContent==='LEVEL UNAVAILABLE'&&
                  level.scrollWidth<=level.clientWidth&&
                  b.left>=a.left+first.clientLeft-.5&&b.right<=a.right-first.clientLeft+.5;
              };
              run('invalid EXP remains owned, readable leader',()=>P.unitExp={[firstId]:'0'},unknownLevel);
              run('EXP accessor never invoked',()=>{P.unitExp={};
                Object.defineProperty(P.unitExp,String(firstId),{get(){reads++;return 0}})},
                ()=>unknownLevel()&&reads===0);
              const noFallback=()=>buttons().length===5&&leaders()===0&&
                Number(buttons()[0]?.dataset.bfHomeUnitId)===old.squad[1]&&
                buttons()[0]?.getAttribute('aria-label').includes('squad slot 2 of 6');
              run('bad first profile ID',()=>window.effectiveUnit=id=>
                id===firstId?{...old.unit(id),id:0}:old.unit(id),noFallback);
              run('bad first profile name',()=>window.effectiveUnit=id=>
                id===firstId?{...old.unit(id),name:''}:old.unit(id),noFallback);
              run('first profile throws',()=>window.effectiveUnit=id=>{
                if(id===firstId)throw Error('profile unavailable');return old.unit(id)},noFallback);
              run('portrait failure preserves owned role',()=>{},()=>{
                const first=buttons()[0],home=document.getElementById('bf-home');
                const before=home.querySelectorAll('.bf-home-art-fallback').length;
                const photo=bfOfflineUnitPortraitV266('content/home/missing-fixture.png','Fixture');
                first.prepend(photo);photo.dispatchEvent(new Event('error'));
                return buttons().length===6&&leaders()===1&&!photo.isConnected&&
                  !!first.querySelector('.bf-portrait-fallback')&&
                  first.querySelectorAll('.bf-scene-leader').length===1&&
                  home.querySelectorAll('.bf-home-art-fallback').length===before;
              });
              return {reports,reads,restored:snap()===original};
            }""")
            assert len(combined['reports'])==8 and all(
                row['ok'] and row['unchanged'] for row in combined['reports']), (width,combined)
            assert combined['reads']==0 and combined['restored'],(width,combined)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
        print('PASS combined Home roles/ownership/EXP matrix, no false leader, unreadable level or state writes')
        focused=page.evaluate("""()=>{BF_homeNav.go('home');BFGlobalHome.refreshParty();const first=document.querySelector('#bf-scene-party button'),id=first.dataset.bfHomeUnitId;first.focus();const before=JSON.stringify({P,S});BFGlobalHome.refreshParty();return {same:before===JSON.stringify({P,S}),focused:document.activeElement.dataset.bfHomeUnitId===id};}""")
        assert focused=={'same':True,'focused':True},focused
        removed=page.evaluate("""()=>{const old=P.squad,before=JSON.stringify({P,S});const button=document.querySelector('#bf-scene-party button');button.focus();try{P.squad=[999999,...old.slice(1)];BFGlobalHome.refreshParty();return document.activeElement.id==='bf-scene-party-review';}finally{P.squad=old;BFGlobalHome.refreshParty();}}""")
        assert removed
        for width in (320,390,540):
            page.set_viewport_size({'width':width,'height':844})
            focus_matrix=page.evaluate("""async()=>{
              BF_homeNav.go('home');BFGlobalHome.refreshParty();
              const old={squad:P.squad,roster:P.roster};
              const snap=()=>JSON.stringify({P,S,mission:QUEST.missionId,
                storage:Object.fromEntries(Array.from({length:localStorage.length},(_,i)=>{
                  const k=localStorage.key(i);return [k,localStorage.getItem(k)];})),writes:__v423Writes()});
              const initial=snap(),rows=[];
              const buttons=()=>[...document.querySelectorAll('#bf-scene-party button')];
              const title=document.querySelector('#bf-home .bf-scene-title');
              const review=document.getElementById('bf-scene-party-review');
              const run=(name,mutate,expect)=>{
                P.squad=old.squad;P.roster=old.roster;BFGlobalHome.refreshParty();
                buttons()[0].focus();mutate();const before=snap();
                BFGlobalHome.refreshParty();rows.push({name,ok:expect(),unchanged:snap()===before});
              };
              try{
                for(const slot of [0,2,5]){
                  const button=buttons()[slot],id=button.dataset.bfHomeUnitId;
                  button.focus();const before=snap(),scroll=scrollY;BFGlobalHome.refreshParty();
                  rows.push({name:'same slot '+slot,ok:document.activeElement===buttons()[slot]&&
                    document.activeElement.dataset.bfHomeUnitId===id&&scrollY===scroll,unchanged:snap()===before});
                }
                run('lost ownership',()=>P.roster=old.roster.filter(id=>id!==old.squad[0]),
                  ()=>document.activeElement===review&&!review.hidden);
                run('empty first slot',()=>P.squad=[null,...old.squad.slice(1)],
                  ()=>document.activeElement===title);
                run('different unit at same slot',()=>P.squad=[old.squad[1],old.squad[0],...old.squad.slice(2)],
                  ()=>document.activeElement===title);
                run('unreadable roster',()=>P.roster=null,()=>document.activeElement===review&&!review.hidden);
                P.roster=old.roster;BFGlobalHome.refreshParty();
                rows.push({name:'review recovers',ok:review.hidden&&document.activeElement===title,
                  unchanged:snap()===initial});
                const nav=document.querySelector('.bf-navbar button[data-bf-goto="home"]');
                nav.focus();const before=snap();BFGlobalHome.refreshParty();
                rows.push({name:'external focus',ok:document.activeElement===nav,unchanged:snap()===before});
                BF_homeNav.go('units');const label=document.getElementById('bf-route-title');
                label.tabIndex=-1;label.focus();BFGlobalHome.refreshParty();
                rows.push({name:'other route',ok:document.activeElement===label,unchanged:snap()===before});
                BF_homeNav.go('home');BFGlobalHome.refreshParty();buttons()[2].focus();
                const id=buttons()[2].dataset.bfHomeUnitId;
                const marker=document.createComment('focus refresh');
                document.getElementById('squadpicker').append(marker);
                await Promise.resolve();marker.remove();await Promise.resolve();
                rows.push({name:'picker observer',ok:document.activeElement===buttons()[2]&&
                  document.activeElement.dataset.bfHomeUnitId===id,unchanged:snap()===before});
                return {rows,restored:snap()===initial};
              }finally{P.squad=old.squad;P.roster=old.roster;BF_homeNav.go('home');BFGlobalHome.refreshParty();}
            }""")
            assert len(focus_matrix['rows'])==11 and focus_matrix['restored'],(width,focus_matrix)
            assert all(r['ok'] and r['unchanged'] for r in focus_matrix['rows']),(width,focus_matrix)
            for key in ('Enter','Space'):
                unit_id=page.evaluate("()=>{const button=document.querySelectorAll('#bf-scene-party button')[2];button.focus();BFGlobalHome.refreshParty();return Number(document.activeElement.dataset.bfHomeUnitId);}")
                page.keyboard.press(key)
                assert page.evaluate("BF_homeNav.current==='units'")
                assert f'Base roster ID {unit_id} ·' in page.locator('#bf-box-detail').inner_text()
                page.evaluate("BF_homeNav.go('home');BFGlobalHome.refreshParty()")
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
        print('PASS Home refresh focus: 33 matrix probes, 6 keyboard inspections, no identity substitution or state writes')
        assert not errors, errors
    finally:
        browser.close()
print("PASS v423 Home owned squad validation, mobile REVIEW status, no save/Auto changes")
