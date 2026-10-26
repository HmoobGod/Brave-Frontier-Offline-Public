from pathlib import Path
from playwright.sync_api import sync_playwright
import json
h=(Path(__file__).parent/'app/src/main/assets/index.html').read_text()
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);pg=b.new_page(viewport={'width':390,'height':844})
 errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
 pg.evaluate('''() => {
 window._testStorage={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem(k){return window._testStorage[k]??null},setItem(k,v){window._testStorage[k]=String(v)}}});
 const a=CanvasRenderingContext2D.prototype.save,b=CanvasRenderingContext2D.prototype.restore;
 window._stack={save:0,restore:0};CanvasRenderingContext2D.prototype.save=function(){window._stack.save++;return a.call(this)};CanvasRenderingContext2D.prototype.restore=function(){window._stack.restore++;return b.call(this)};
 }''')
 pg.set_content(h,wait_until='load',timeout=60000)
 pg.wait_for_timeout(600)
 print('initial_errors',errs)
 assert not errs
 assert pg.evaluate('BF_debug.state().missionId')==1
 assert pg.locator('.questcard').count()==6
 assert pg.locator('.squadpick').count()==6
 assert pg.evaluate('monsterAtlas.naturalWidth===1000 && monsterAtlas.naturalHeight===2304')
 assert pg.evaluate('starterImages.every(x=>x.naturalWidth>0)')
 assert pg.evaluate('originalBg.naturalWidth>0')
 assert not pg.locator('.questcard').nth(1).is_enabled()
 pg.evaluate('awardDemoRewards()')
 assert pg.evaluate('P.questClears[1]')==1
 assert pg.evaluate('P.exp')==5
 assert pg.locator('.questcard').nth(1).is_enabled()
 pg.locator('.questcard').nth(1).click()
 assert pg.evaluate('BF_debug.state().missionId')==2
 for mission,nextmission in [(2,10),(10,11),(11,12),(12,20)]:
  assert pg.evaluate('QUEST.missionId')==mission
  pg.evaluate('awardDemoRewards()')
  pg.evaluate('''id=>{const q=QUEST_BY_ID.get(id);QUEST=q;P.lastMission=id;saveProgress();loadQuestBackground();reset()}''',nextmission)
 assert pg.evaluate('S.totalWaves')==5
 assert pg.evaluate('QUEST.background')=='dungeon_battle_10200.jpg'
 pg.wait_for_timeout(450)
 assert pg.evaluate('originalBg.naturalWidth>0')
 pg.locator('#exportsave').click()
 export=json.loads(pg.locator('#savetc').input_value())
 assert export['version']==3 and export['lastMission']==20
 migrated=pg.evaluate('''() => parseProgress({format:'bf-global-offline-demo',version:2,exp:15,zel:111,karma:10,clears:2,level:3,squad:[10011,20011],unitExp:{10011:10,20011:5}})''')
 assert migrated['version']==3 and migrated['questClears']=={'1':2} and migrated['squad']==[10011,20011]
 pg.locator('#mode').select_option('training');assert pg.evaluate('S.totalWaves')==2
 pg.locator('#mode').select_option('archive');assert pg.evaluate('S.totalWaves')==5
 pg.evaluate('''() => {QUEST=QUESTS[0];P.lastMission=1;saveProgress();loadQuestBackground();reset();for(const e of S.enemies)e.hp=1}''')
 pg.locator('#auto').check()
 pg.wait_for_function('BF_debug.state().wave>=1',timeout=30000)
 pg.evaluate('for(const e of S.enemies)e.hp=1')
 pg.wait_for_function('BF_debug.state().wave>=2',timeout=30000)
 pg.evaluate('for(const e of S.enemies)e.hp=1')
 pg.wait_for_function('BF_debug.state().over===true',timeout=30000)
 assert pg.evaluate('S.phase')=='Victory'
 assert pg.evaluate('P.questClears[1]')==2
 pg.wait_for_timeout(150)
 counts=pg.evaluate('window._stack')
 assert counts['save']==counts['restore'],counts
 assert not errs,errs
 pg.evaluate('window.scrollTo(0,0)')
 pg.screenshot(path='/mnt/data/BF_v0.8_Quest_Path_Preview.png',full_page=True)
 print('PASS: quest unlock chain, 2 backgrounds, 8 monster art IDs, 6 original party units, migrations, mode switching, Auto through 3 waves; no JS errors or canvas state leaks')
 print(json.dumps({'canvas':counts,'clears':pg.evaluate('P.questClears'),'total_catalog':pg.evaluate('QUESTS.length'),'atlas':pg.evaluate('[monsterAtlas.naturalWidth,monsterAtlas.naturalHeight]'),'errors':errs},indent=2))
 b.close()
