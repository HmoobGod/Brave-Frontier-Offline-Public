import sys,pathlib,shutil
from playwright.sync_api import sync_playwright
A=pathlib.Path(sys.argv[1]); errors=[]; n=0
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':390,'height':844});p.on('pageerror',lambda e:errors.append(e.stack or str(e)));p.route('**/*',lambda r:r.abort())
 p.evaluate('''()=>{const db={};window.__db=db;Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>db[k]??null,setItem:(k,v)=>{db[k]=String(v)},removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});window.alert=()=>{};window.confirm=()=>true;HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};HTMLMediaElement.prototype.play=()=>Promise.resolve();}''')
 p.set_content((A/'index.html').read_text(),wait_until='load',timeout=45000)
 p.add_style_tag(content=(A/'bf_home_nav.css').read_text())
 order=pathlib.Path(__file__).with_name('native-order.txt').read_text().splitlines()
 for f in order:
  before=len(errors);p.add_script_tag(content=(A/f).read_text())
  if len(errors)>before:print('MODULE ERROR',f,errors[before:],flush=True)
 print('INJECTED',len(order),'errors',len(errors),flush=True)
 def check(v,name):
  global n
  assert v,name
  n+=1;print('PASS',name,flush=True)
 check(not errors,'native-order modules no uncaught errors')
 p.evaluate('''()=>{const id=RECRUIT_IDS[0],c=1000000001;P.roster.push(id,c);P.unitExp[id]=10000;P.unitExp[c]=15000;P._bfUnitInstancesV1={nextId:c+1,baseById:{[c]:id}};P.squad=[c,id,...P.squad.slice(0,4)];P.zel=100000;const r=copyNextRecipes(c)[0];for(const [k,v] of Object.entries(r.materials))P.materials[k]=v;if(!saveProgress())throw Error('fixture save');reset();renderProgress();BF_homeNav.go('units');BFInnerScreens.setTab('box')}''')
 p.locator('#bf-copy-stack-toggle').check(timeout=3000)
 if not p.locator('.bf-copy-stack').evaluate('(e)=>e.open'):p.locator('.bf-copy-stack summary').click(timeout=3000)
 p.locator('[data-bf-unit-id="1000000001"]').click(timeout=3000);p.locator('#bf10200-lock').click(timeout=3000)
 check(p.evaluate('copyOrgRead().locked.includes(1000000001)'),'copy lock via actual UI')
 p.locator('#bf10200-show-locks').click(timeout=3000)
 check(p.locator('[data-bf-unit-id="1000000001"]').is_visible() and not p.locator('[data-bf-unit-id="10021"]').is_visible(),'locked-only filter separates copies')
 p.locator('#bf10200-show-locks').click(timeout=3000)
 p.evaluate("BFInnerScreens.setTab('squad')")
 p.locator('#bf10000-squad-presets summary').click(timeout=3000);p.locator('#bf10000-name').fill('Copy leader');p.locator('#bf10000-save').click(timeout=3000)
 check(p.evaluate('copyOrgRead().presets[0].squad[0]===1000000001'),'saved copy leader preset')
 p.locator('#squadpicker .squadpick').filter(has_text='Copy #1000000001').locator('input').uncheck(timeout=3000)
 check(p.evaluate('!P.squad.includes(1000000001)'),'manual removal exact copy')
 p.locator('#bf10000-apply').click(timeout=3000)
 check(p.evaluate('P.squad[0]===1000000001&&S.party[0].baseId===1000000001'),'preset restores copy leader and party')
 p.evaluate("BFInnerScreens.setTab('evolve')")
 p.locator('.evocard').filter(has_text='Copy #1000000001').locator('.evoaction').click(timeout=4000)
 check(p.evaluate('P.evolutions[1000000001]===stackOwnedUnit(1000000001).id&&!P.evolutions[RECRUIT_IDS[0]]&&P.unitExp[1000000001]===0&&P.unitExp[RECRUIT_IDS[0]]===10000'),'actual evolution targets copy only')
 p.evaluate("P.unitExp[1000000001]=15000;saveProgress();reset();renderProgress();BF_homeNav.go('quest')")
 print('battle init',p.evaluate('({mode:S.mode,mission:QUEST.missionId,waves:S.totalWaves,party:S.party.map(x=>({baseId:x.baseId,unitId:x.unitId,hp:x.hp,atk:x.atk})),ready:sourceWaveCountReady()})'),flush=True)
 initial=p.evaluate('({exp:P.exp,copy:P.unitExp[1000000001],base:P.unitExp[RECRUIT_IDS[0]],quest:P.questClears[QUEST.missionId]||0,reward:QUEST.exp,token:P.summonTokens})')
 check(p.evaluate('S.party[0].baseId===1000000001&&S.party[1].baseId===RECRUIT_IDS[0]&&S.party[0].unitId!==S.party[1].unitId'),'battle uses separate owned IDs and forms')
 p.evaluate("E.speed.value='5';E.speed.dispatchEvent(new Event('change'));E.auto.click()")
 try:p.wait_for_function('S.over===true',timeout=45000)
 except Exception:print('battle timeout',p.evaluate('({phase:E.phase.textContent,round:S.round,wave:S.wave,auto:S.auto,busy:S.busy,log:E.log.innerText.slice(-2000)})'),errors[-5:],flush=True);raise
 print('battle end',p.evaluate('({phase:S.phase,round:S.round,wave:S.wave,log:E.log.innerText.slice(-2000)})'),flush=True)
 check(p.evaluate('S.phase==="Victory"'),'native Auto reaches victory')
 check(p.evaluate('(i)=>P.exp===i.exp+i.reward&&P.unitExp[1000000001]===i.copy+i.reward&&P.unitExp[RECRUIT_IDS[0]]===i.base+i.reward&&P.questClears[QUEST.missionId]===i.quest+1&&P.summonTokens===i.token+1',initial),'clear awards independent EXP and one token')
 check(p.evaluate('localStorage.getItem(SAVE_KEY)===JSON.stringify(P)&&JSON.stringify(parseProgress(JSON.parse(localStorage.getItem(SAVE_KEY))))===JSON.stringify(P)'),'victory exact canonical save and reload parse')
 check(not errors,'no uncaught browser errors')
 print('TOTAL',n,flush=True);b.close()
