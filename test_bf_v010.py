from pathlib import Path
from playwright.sync_api import sync_playwright
import json,re,zipfile
H=Path('/mnt/data/Brave_Frontier_Offline_v0.10_Evolution_Lab.html').read_text()
REPORT={}; errors=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 pg=b.new_page(viewport={'width':390,'height':844},accept_downloads=True)
 pg.on('pageerror',lambda e:errors.append(str(e)))
 pg.evaluate('''() => { window._testStorage={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem(k){return window._testStorage[k]??null},setItem(k,v){window._testStorage[k]=String(v)},removeItem(k){delete window._testStorage[k]}}});const a=CanvasRenderingContext2D.prototype.save,b=CanvasRenderingContext2D.prototype.restore;window._stack={save:0,restore:0};CanvasRenderingContext2D.prototype.save=function(){window._stack.save++;return a.call(this)};CanvasRenderingContext2D.prototype.restore=function(){window._stack.restore++;return b.call(this)};window.confirm=()=>true;}''')
 pg.set_content(H,wait_until='load',timeout=90000);pg.wait_for_timeout(1500)
 assert not errors,errors
 REPORT['catalog']=pg.evaluate('({owned:P.roster.length,base:STARTERS.length,evolved:window.BF_EVOLVED_UNITS.length,loaded:starterImages.filter(x=>x.complete && x.naturalWidth>0).length})')
 assert REPORT['catalog']=={'owned':6,'base':12,'evolved':12,'loaded':24}, REPORT['catalog']
 assert pg.locator('.evocard').count()==6
 assert pg.locator('.questcard').count()==6
 assert pg.evaluate('P.version')==5
 REPORT['v4_migration']=pg.evaluate('''() => {const o=parseProgress({format:'bf-global-offline-demo',version:4,exp:12,zel:2510,karma:100,clears:1,level:2,squad:[10011,20011],roster:[10011,20011,30011,40011,50011,60011],summonTokens:2,summonHistory:[],unitExp:{10011:5},questClears:{1:1},lastMission:1});return {version:o.version,zel:o.zel,evolutions:o.evolutions,materials:o.materials,squad:o.squad};}''')
 assert REPORT['v4_migration']['version']==5
 assert pg.evaluate('''() => { try{ parseProgress({format:'bf-global-offline-demo',version:5,exp:0,zel:0,karma:0,clears:0,level:1,squad:[10011],roster:[10011,20011,30011,40011,50011,60011],summonTokens:0,summonHistory:[],unitExp:{},questClears:{},lastMission:1,evolutions:{10011:40012},materials:{}}); return false;}catch(e){return true;} }''')
 # Archived quest 1 grants catalyst 10130 in demo. At 3 clears it grants 10131.
 pg.evaluate('''() => {QUEST=QUESTS[0];P.lastMission=1;P.squad=[10011];saveProgress();reset();renderProgress();}''')
 pg.evaluate('awardDemoRewards()')
 assert pg.evaluate('P.materials[10130]')==1
 pg.evaluate('awardDemoRewards();awardDemoRewards()')
 assert pg.evaluate('P.materials[10130]')==2 and pg.evaluate('P.materials[10131]')==1
 REPORT['catalyst_loop']={'clear1':10130,'clear3':10131}
 # evolve Vargas: 2500 archived and demo Zel, 1 catalyst and Lv>=2
 pg.evaluate('''() => {P.zel=2500;P.unitExp[10011]=5;saveProgress();renderProgress();}''')
 button=pg.locator('.evocard').first.locator('button')
 assert button.is_enabled(),pg.locator('.evocard').first.inner_text()
 button.click();pg.wait_for_timeout(300)
 assert pg.evaluate('P.evolutions[10011]')==10012
 assert pg.evaluate('P.zel')==0
 assert pg.evaluate('P.materials[10130]')==1
 assert pg.evaluate('P.unitExp[10011]')==0
 assert pg.evaluate('S.party[0].unitId')==10012
 assert pg.evaluate('S.party[0].maxHp')==pg.evaluate('UNIT_BY_ID.get(10012).stats.hp')
 assert pg.evaluate('P.squad[0]')==10011
 REPORT['evolution']={'from':10011,'to':10012,'squadRetained':True,'levelReset':True,'zelSpent':2500}
 assert pg.locator('.evocard').first.locator('button').is_disabled()
 # Save export + validation + reload with evolved form and catalyst progress.
 pg.locator('#exportsave').click()
 save=json.loads(pg.locator('#savetc').input_value())
 assert save['version']==5 and save['evolutions']=={'10011':10012}
 assert pg.evaluate('parseProgress(JSON.parse(document.querySelector("#savetc").value)).evolutions[10011]')==10012
 REPORT['export']={'version':5,'evolutions':save['evolutions'],'questClears':save['questClears']}
 pg.evaluate('''() => {P.roster.push(10021);P.squad.push(10021);P.unitExp[10021]=5;P.materials[10130]=10;P.materials[10131]=2;P.zel=2500;saveProgress();reset();renderProgress();}''')
 recruit=pg.locator('.evocard').filter(has=pg.locator('strong',has_text='Unit 10021')).locator('button')
 assert recruit.count()==1 and recruit.is_enabled(),recruit.count()
 recruit.click()
 assert pg.evaluate('P.evolutions[10021]')==10022
 assert pg.evaluate('S.party.some(p=>p.active&&p.unitId===10022)')
 REPORT['recruit_evolution']=True
 # Validate assets of both actors and battle-state hygiene
 pg.evaluate('''() => {P.squad=[10011,20011];saveProgress();reset();for(const e of S.enemies)e.hp=1;}''')
 pg.locator('#auto').check()
 for wave in (1,2):
  pg.wait_for_function('(wanted)=>S.wave>=wanted',arg=wave,timeout=40000)
  pg.evaluate('for(const e of S.enemies)e.hp=1')
 pg.wait_for_function('S.over===true',timeout=45000)
 assert pg.evaluate('S.phase')=='Victory'
 REPORT['battle']='3-wave demo Auto Battle victory'
 pg.wait_for_timeout(500)
 stack=pg.evaluate('window._stack');assert stack['save']==stack['restore'],stack
 REPORT['canvasStack']=stack
 assert not errors,errors
 pg.evaluate('window.scrollTo(0,document.querySelector(".evo-panel").offsetTop-60)')
 pg.screenshot(path='/mnt/data/BF_v0.10_Evolution_Lab_Preview.png',full_page=False)
 # Launch fresh independent page with v5 save seeded BEFORE game initializes
 pg2=b.new_page(viewport={'width':390,'height':844})
 errors2=[];pg2.on('pageerror',lambda e:errors2.append(str(e)))
 pg2.evaluate('''() => {window._testStorage={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem(k){return window._testStorage[k]??null},setItem(k,v){window._testStorage[k]=String(v)}}});}''')
 pg2.evaluate('(saved)=>window._testStorage.bf_global_offline_demo_v5=JSON.stringify(saved)',save)
 pg2.set_content(H,wait_until='load',timeout=90000)
 pg2.wait_for_timeout(500)
 assert pg2.evaluate('P.evolutions[10011]')==10012
 assert pg2.evaluate('S.party[0].unitId')==10012
 assert not errors2,errors2
 REPORT['fresh_session_reload']=True
 REPORT['errors']=errors+errors2
 b.close()
Path('/mnt/data/BF_v0.10_Test_Report.json').write_text(json.dumps(REPORT,indent=2))
print(json.dumps(REPORT,indent=2))
