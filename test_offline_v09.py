from pathlib import Path
from playwright.sync_api import sync_playwright
import json, re
h=Path('/mnt/data/Brave_Frontier_Offline_v0.9_Summons_Collection.html').read_text()
script=re.search(r"<script>'use strict';(.*?)</script>",h,re.S).group(1)
Path('/mnt/data/_bf09_main.js').write_text("'use strict';"+script)
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 pg=b.new_page(viewport={'width':390,'height':844});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
 pg.evaluate('''() => {
 window._testStorage={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem(k){return window._testStorage[k]??null},setItem(k,v){window._testStorage[k]=String(v)}}});
 const a=CanvasRenderingContext2D.prototype.save,b=CanvasRenderingContext2D.prototype.restore;
 window._stack={save:0,restore:0};CanvasRenderingContext2D.prototype.save=function(){window._stack.save++;return a.call(this)};CanvasRenderingContext2D.prototype.restore=function(){window._stack.restore++;return b.call(this)};
 }''')
 pg.set_content(h,wait_until='load',timeout=60000);pg.wait_for_timeout(1000)
 print('INIT ERRORS',errs)
 assert not errs,errs
 assert pg.evaluate('STARTERS.length')==12
 assert pg.locator('.squadpick').count()==12
 assert pg.locator('.questcard').count()==6
 assert pg.locator('#summonbutton').is_disabled()
 assert pg.evaluate('P.roster.length')==6
 assert pg.evaluate('starterImages.every(x=>x.complete && x.naturalWidth>0)')
 # v3 compatibility
 old=pg.evaluate('''() => parseProgress({format:'bf-global-offline-demo',version:3,exp:25,zel:500,karma:100,clears:2,level:3,squad:[10011,20011],unitExp:{10011:15,20011:10},questClears:{1:2},lastMission:1})''')
 assert old['version']==4 and len(old['roster'])==6 and old['squad']==[10011,20011] and old['questClears']=={'1':2}
 # one quest clear -> summon
 pg.evaluate('awardDemoRewards()')
 assert pg.evaluate('P.summonTokens')==1
 assert pg.locator('#summonbutton').is_enabled()
 pg.locator('#summonbutton').click()
 assert pg.evaluate('P.summonTokens')==0
 assert pg.evaluate('P.roster.length')==7
 first_id=pg.evaluate('P.roster[6]')
 assert first_id in [10021,20021,30021,40021,50021,60021]
 assert pg.evaluate('P.summonHistory.length')==1
 # Change squad: remove one starter, add acquired recruit
 pg.locator('.squadpick input').nth(5).uncheck()
 i=pg.evaluate('ALL_IDS.indexOf(P.roster[6])')
 pg.locator('.squadpick input').nth(i).check()
 assert pg.evaluate('P.squad.includes(P.roster[6])')
 assert pg.evaluate('S.party.some(p=>p.unitId===P.roster[6] && p.active)')
 assert not errs,errs
 # collect rest, demonstrate no duplicates
 pg.evaluate('''() => {P.summonTokens=8;saveProgress();renderProgress()}''')
 for i in range(5):pg.locator('#summonbutton').click()
 assert pg.evaluate('P.roster.length')==12
 assert pg.evaluate('new Set(P.roster).size')==12
 assert pg.locator('#summonbutton').is_disabled()
 assert pg.evaluate('P.summonTokens')==3
 # save roundtrip with 12 units
 pg.locator('#exportsave').click()
 data=json.loads(pg.locator('#savetc').input_value());assert data['version']==4 and len(data['roster'])==12
 assert pg.evaluate('parseProgress(JSON.parse(document.querySelector("#savetc").value)).roster.length')==12
 # later quest progression intact
 assert pg.locator('.questcard').count()==6
 pg.evaluate('''() => {QUEST=QUESTS[0];P.lastMission=1;saveProgress();loadQuestBackground();reset();for(const e of S.enemies)e.hp=1}''')
 pg.locator('#auto').check()
 for wave in [1,2]:
  pg.wait_for_function('(wanted)=>BF_debug.state().wave>=wanted',arg=wave,timeout=30000)
  pg.evaluate('for(const e of S.enemies)e.hp=1')
 pg.wait_for_function('BF_debug.state().over===true',timeout=30000)
 assert pg.evaluate('S.phase')=='Victory'
 assert not errs,errs
 stack=pg.evaluate('window._stack'); assert stack['save']==stack['restore'],stack
 print('ALL PASS',{'roster':pg.evaluate('P.roster.length'),'quest':pg.evaluate('QUEST.missionId'),'stack':stack,'errors':errs})
 # screenshot with recruit still visible
 pg.evaluate('window.scrollTo(0,0)');pg.screenshot(path='/mnt/data/BF_v0.9_Summoning_Collection_Preview.png',full_page=True)
 b.close()
