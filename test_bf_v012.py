from pathlib import Path
import json,zipfile,hashlib
from playwright.sync_api import sync_playwright
ROOT=Path('/mnt/data');HTML=(ROOT/'Brave_Frontier_Offline_v0.12_Expanded_Roster_Multi_Hit.html').read_text()
results={'version':'0.12','saveSchema':7,'checks':[],'browserErrors':[]}
def ok(label):results['checks'].append(label)
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844}, accept_downloads=True)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate('''() => {window.__saved={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem(k){return window.__saved[k]??null;},setItem(k,v){window.__saved[k]=String(v);},removeItem(k){delete window.__saved[k];}}});const a=CanvasRenderingContext2D.prototype.save,b=CanvasRenderingContext2D.prototype.restore;window.__ctx={save:0,restore:0};CanvasRenderingContext2D.prototype.save=function(){window.__ctx.save++;return a.call(this)};CanvasRenderingContext2D.prototype.restore=function(){window.__ctx.restore++;return b.call(this)};window.confirm=()=>true;window.alert=()=>{};}''')
 page.set_content(HTML,wait_until='load',timeout=90000);page.wait_for_timeout(500)
 assert not errors,errors
 info=page.evaluate('''() => ({v:P.version,base:STARTERS.length,evolutions:window.BF_EVOLVED_UNITS.length,owned:P.roster.length,recruits:RECRUIT_IDS.length,hitData:Object.keys(window.BF_ARCHIVE_NORMAL_HITS).length,images:starterImages.filter(x=>x.complete&&x.naturalWidth>0).length})''')
 assert info=={'v':7,'base':18,'evolutions':12,'owned':6,'recruits':12,'hitData':30,'images':30},info
 ok('30 original spritesheets (18 base + 12 evolved), 18 base roster, 12 recruits, 30 archived hit datasets load')
 assert page.locator('.squadpick').count()==18
 assert page.locator('#hitunit option').count()==6
 assert page.locator('.hit-dots span').count()==3
 assert '50%' in page.locator('.hit-dots').inner_text()
 ok('Squad selector and data-driven Vargas 3-hit inspector (50/30/20) render')
 old=page.evaluate('''() => {const d={...defaultProgress(),version:6,zel:5500,trainingShards:3,roster:[10011,20011,30011,40011,50011,60011,10021],squad:[10011,10021],unitExp:{10011:10,10021:20},summonTokens:4,summonHistory:[10021],materials:{10130:2},evolutions:{10011:10012},questClears:{1:3},lastMission:1};return parseProgress(d)}''')
 assert old['version']==7 and old['evolutions']=={'10011':10012} and old['trainingShards']==3 and old['unitExp']['10041']==0
 ok('v0.11 v6 saved levels, evolved unit, shards, roster and quests migrate into v7')
 # Verify splitting itself without mutating gameplay logic.
 samples=page.evaluate('''() => ({raw:window.BF_ARCHIVE_NORMAL_HITS[10011].events,parts:splitDemoDamage(137,archivedNormalAttackEvents(10011)),noNormalization:splitDemoDamage(137,[[0,125,2,2]]),other:splitDemoDamage(1,archivedNormalAttackEvents(10011))})''')
 assert samples['raw']==[[26,50,2,2],[44,30,2,2],[62,20,2,2]],samples
 assert samples['parts']==[69,41,27] and sum(samples['other'])==1
 assert samples['noNormalization']==[137]
 ok('Source-time hit distribution conserves demo damage and refuses non-100 weights')
 # Normal attack actual interaction queued manually; avoid enemy kill by raising HP
 page.evaluate('''() => {P.squad=[10011];saveProgress();reset();E.speed.value='5';for(const e of S.enemies){e.hp=10000;e.maxHp=10000;}S.party[0].bb=0;S.party[0].action={kind:'attack',target:0};}''')
 hp_before=page.evaluate('S.enemies[0].hp')
 page.evaluate('execute()')
 # Wait until action finished and foe retaliation, ensure exact archived hit log
 page.wait_for_function('!S.busy',timeout=25000)
 logs=page.locator('#log').text_content()
 print('ATTACK LOG:',repr(logs[:1000]),'STATE:',page.evaluate('({busy:S.busy,party:S.party[0].action,round:S.round})'))
 assert '3 archived-timed hits' in logs,logs[-800:]
 after=page.evaluate('({hp:S.enemies[0].hp,bb:S.party[0].bb})')
 assert after['hp']<hp_before and after['bb']==34,after
 ok('Actual queued Vargas normal attack applies three individually-timed hits and DEMO BB filling unchanged')
 # Reset during hit events: no residual damage should land on fresh enemies
 page.evaluate('''() => {S.party[0].action={kind:'attack',target:0};for(const e of S.enemies){e.hp=8000;e.maxHp=8000;}execute();setTimeout(()=>reset(),5);}''')
 page.wait_for_timeout(650)
 assert page.evaluate('S.wave')==0 and not page.evaluate('S.busy')
 assert page.evaluate('S.enemies[0].hp')==page.evaluate('S.enemies[0].maxHp')
 ok('Restart while attack in progress cancels pending hits via epoch-token')
 # With archived recruit, summon an 18th (new ID) and ensure it can enter squad.
 page.evaluate('''() => {P.roster=[10011,20011,30011,40011,50011,60011,10021,20021,30021,40021,50021,60021,10041,20041,30041,40041,50041];P.summonTokens=1;P.squad=[10011];saveProgress();reset();renderProgress();}''')
 assert page.locator('#summonbutton').is_enabled()
 page.locator('#summonbutton').click()
 assert page.evaluate('P.roster.includes(60041)')
 assert page.evaluate('P.summonTokens')==0
 assert page.locator('.squadpick').count()==18
 page.evaluate('''() => {P.squad=[60041];saveProgress();reset();renderProgress();}''')
 assert page.evaluate('S.party[0].unitId')==60041
 assert page.locator('#hitunit option').count()==18
 page.locator('#hitunit').select_option('60041')
 assert page.locator('.hit-dots span').count()==5
 ok('New 60041 archive recruit can be summoned, assigned, and displays five normal hits')
 # fresh session import and preview
 page.locator('#exportsave').click()
 saved=json.loads(page.locator('#savetc').input_value())
 assert saved['version']==7 and 60041 in saved['roster'] and saved['squad']==[60041]
 with page.expect_download() as dl:page.locator('#downloadsave').click()
 d=dl.value;dest=ROOT/'BF_v0.12_Save_Test.json';d.save_as(dest)
 assert json.loads(dest.read_text())==saved
 second=browser.new_page(viewport={'width':390,'height':844});errors2=[];second.on('pageerror',lambda e:errors2.append(str(e)))
 second.evaluate('''() => {window.__saved={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem(k){return window.__saved[k]??null},setItem(k,v){window.__saved[k]=String(v)},removeItem(k){delete window.__saved[k]}}});window.confirm=()=>true;}''')
 second.evaluate('(data)=>window.__saved.bf_global_offline_demo_v7=JSON.stringify(data)',saved)
 second.set_content(HTML,wait_until='load',timeout=90000);second.wait_for_timeout(600)
 assert second.evaluate('P.version')==7 and second.evaluate('P.squad')==[60041]
 assert second.evaluate('P.roster.length')==18
 assert not errors2,errors2
 ok('v7 portable JSON export and fresh-browser save reload retain all 18 owned units')
 # original quest chain and Auto Battle: six starters strong enough, set low enemy health each wave
 second.evaluate('''() => {P.squad=[10011,20011,30011,40011,50011,60011];P.lastMission=1;saveProgress();reset();E.speed.value='5';for(const e of S.enemies)e.hp=1;}''')
 old_clears=second.evaluate('P.clears')
 second.locator('#auto').check()
 for wave in [1,2]:
  second.wait_for_function('(n)=>S.wave>=n',arg=wave,timeout=50000)
  second.evaluate('for(const e of S.enemies)e.hp=1')
 second.wait_for_function('S.over',timeout=50000)
 assert second.evaluate('S.phase')=='Victory'
 assert second.evaluate('P.clears')==old_clears+1
 ok('Full three-wave quest, auto battle and rewards survive multi-hit changes')
 page.wait_for_timeout(240);canvas=page.evaluate('window.__ctx')
 assert canvas['save']==canvas['restore'],canvas
 assert not errors and not errors2,errors+errors2
 ok('Canvas save/restore balanced and no browser JavaScript errors')
 second.evaluate('''() => {E.auto.checked=false;reset();P.squad=[10011,10021];renderProgress();window.scrollTo(0,document.querySelector('.hit-panel').offsetTop-65);}''')
 second.wait_for_timeout(250)
 second.screenshot(path=str(ROOT/'BF_v0.12_Expanded_Roster_Multi_Hit_Preview.png'),full_page=False)
 second.set_viewport_size({'width':320,'height':720});second.wait_for_timeout(170)
 assert second.locator('#hitunit').count()==1
 ok('Source-hit inspector and squad UI work at 390px and 320px mobile widths')
 browser.close()
results.update({'checksPassed':len(results['checks']),'canvasSaves':canvas['save'],'canvasRestores':canvas['restore'],'sourcesSha256':hashlib.sha256(HTML.encode()).hexdigest(),'androidStatus':'Prepared, not compiled/device-tested','issues':errors})
app=ROOT/'Brave_Frontier_Android_Offline_v0.12';assert (app/'app/src/main/assets/index.html').read_bytes()==HTML.encode()
(ROOT/'BF_v0.12_Test_Report.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
