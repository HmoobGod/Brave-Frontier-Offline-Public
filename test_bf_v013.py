from pathlib import Path
from playwright.sync_api import sync_playwright
import hashlib,json,zipfile,os
R=Path('/mnt/data')
html=(R/'Brave_Frontier_Offline_v0.13_BB_Hit_Lab.html').read_text()
report={'version':'0.13','checks':[],'browserErrors':[]}
def passed(s):report['checks'].append(s);print('PASS',s,flush=True)
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844},accept_downloads=True)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate('''() => {
 window.__saved={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem(k){return window.__saved[k]??null},setItem(k,v){window.__saved[k]=String(v)},removeItem(k){delete window.__saved[k]}}});
 window.confirm=()=>true;window.alert=()=>{};
 let a=CanvasRenderingContext2D.prototype.save,b=CanvasRenderingContext2D.prototype.restore;
 window.__ctx={save:0,restore:0};
 CanvasRenderingContext2D.prototype.save=function(){window.__ctx.save++;return a.call(this)};
 CanvasRenderingContext2D.prototype.restore=function(){window.__ctx.restore++;return b.call(this)};
 }''')
 page.set_content(html,wait_until='load',timeout=60000)
 page.wait_for_timeout(650)
 assert not errors,errors
 status=page.evaluate('''() => ({schema:P.version,owned:P.roster.length,base:STARTERS.length,evolved:window.BF_EVOLVED_UNITS.length,bbSource:Object.keys(window.BF_ARCHIVE_BB_HITS).length,offensive:Object.values(window.BF_ARCHIVE_BB_HITS).filter(x=>x.offensiveCandidate).length})''')
 assert status=={'schema':7,'owned':6,'base':18,'evolved':12,'bbSource':30,'offensive':24},status
 passed('30 original BB profiles load, with 24 candidates for first-group damage scheduling and save schema v7 unchanged')
 assert page.locator('#hitmode option').count()==2
 page.locator('#hitmode').select_option('bb')
 assert page.locator('.hit-dots span').count()==5
 assert '20%' in page.locator('.hit-dots').inner_text()
 assert 'BB source ID 10011' in page.locator('#hitevents').inner_text()
 passed('Inspector shows Vargas original first BB group: five hits of 20%')
 src=page.evaluate('''() => ({events:archivedBraveBurstEvents(10011),supp:window.BF_ARCHIVE_BB_HITS['10021'].groups.length,buff:archivedBraveBurstEvents(20041),split:splitDemoDamage(107,archivedBraveBurstEvents(10011)),normal:archivedNormalAttackEvents(10011).length})''')
 assert src['events']==[[26,20,2,2],[47,20,2,2],[68,20,2,2],[89,20,2,2],[110,20,2,2]],src
 assert src['supp']==2 and src['buff'] is None and sum(src['split'])==107 and src['normal']==3,src
 passed('Original hit times and weights preserved, @ groups not merged; non-offensive skills gated to demo fallback')
 # Normal source attacks remain unchanged, choose one Vargas and high enemy HP to see all hit events.
 page.evaluate('''() => {P.squad=[10011];saveProgress();reset();E.speed.value='5';for(const e of S.enemies){e.hp=e.maxHp=20000;}S.party[0].bb=100;S.party[0].action={kind:'burst',target:0};}''')
 hp=page.evaluate('S.enemies[0].hp')
 page.evaluate('execute()')
 page.wait_for_function('!S.busy',timeout=28000)
 logs=page.locator('#log').text_content()
 print('DEBUG',repr(logs[-900:]), 'errors',errors,'state',page.evaluate('({phase:S.phase,busy:S.busy,round:S.round,party:S.party[0].bb})'),flush=True)
 assert '5 archived-timed BB hits' in logs,logs
 assert page.evaluate('S.party[0].bb')==0
 assert page.evaluate('S.enemies[0].hp')<hp
 passed('Actual queued Vargas BB applies five source-timed demo damage events, empties gauge and completes round')
 # For non-offensive source preserve same simulated BB fallback (single hit, NOT claiming effect type).
 page.evaluate('''() => {P.roster=[10011,20011,30011,40011,50011,60011,20041];P.squad=[20041];saveProgress();reset();E.speed.value='5';for(const e of S.enemies){e.hp=e.maxHp=20000;}S.party[0].bb=100;S.party[0].action={kind:'burst',target:0};}''')
 page.evaluate('execute()');page.wait_for_function('!S.busy',timeout=22000)
 logs=page.locator('#log').text_content()
 assert 'simulated BB hit' in logs,logs
 passed('Non-offensive candidate remains a labeled simulated BB fallback instead of decoding unknown support effects')
 # cancellation: restarting mid long BB should halt pending hits
 page.evaluate('''() => {P.squad=[10011];saveProgress();reset();E.speed.value='2';for(const e of S.enemies){e.hp=e.maxHp=10000;}S.party[0].bb=100;S.party[0].action={kind:'burst',target:0};execute();setTimeout(()=>reset(),30);}''')
 page.wait_for_timeout(780)
 assert page.evaluate('S.enemies[0].hp')==page.evaluate('S.enemies[0].maxHp')
 assert not page.evaluate('S.busy')
 passed('Reset during pending BB event cancels future hits via epoch token')
 # Import v6 saved progress still parses into current format
 migrated=page.evaluate('''() => parseProgress({...defaultProgress(),version:6,zel:7777,trainingShards:3,roster:[10011,20011,30011,40011,50011,60011],squad:[10011,20011],questClears:{1:2},unitExp:{10011:35}})''')
 assert migrated['version']==7 and migrated['zel']==7777 and migrated['unitExp']['10011']==35
 passed('v6 save format still imports to v7 without changes')
 # Export, then fresh page reload with same saved data
 page.locator('#exportsave').click();text=page.locator('#savetc').input_value();saved=json.loads(text)
 with page.expect_download() as d:page.locator('#downloadsave').click()
 file=R/'BF_v0.13_Exported_Test_Save.json';d.value.save_as(file)
 assert json.loads(file.read_text())==saved
 fresh=browser.new_page(viewport={'width':390,'height':844});e2=[];fresh.on('pageerror',lambda e:e2.append(str(e)))
 fresh.evaluate('''() => {window.__saved={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem(k){return window.__saved[k]??null},setItem(k,v){window.__saved[k]=String(v)},removeItem(k){delete window.__saved[k]}}});window.confirm=()=>true;}''')
 fresh.evaluate('(d)=>window.__saved.bf_global_offline_demo_v7=JSON.stringify(d)',saved)
 fresh.set_content(html,wait_until='load',timeout=60000)
 assert fresh.evaluate('P.squad')==saved['squad'] and fresh.evaluate('P.version')==7
 passed('Save export/reimport into independent browser session preserves v7 progress')
 # Full auto battle with six starters, minimize enemy HP to reach clear within timing timeout
 fresh.evaluate('''() => {P.squad=[10011,20011,30011,40011,50011,60011];P.lastMission=1;saveProgress();reset();E.speed.value='5';for(const e of S.enemies){e.hp=1;}}''')
 prior=fresh.evaluate('P.clears');fresh.locator('#auto').check()
 for wave in (1,2):
  fresh.wait_for_function('(n)=>S.wave>=n',arg=wave,timeout=45000)
  fresh.evaluate('for(const e of S.enemies){e.hp=1;}')
 fresh.wait_for_function('S.over',timeout=50000)
 assert fresh.evaluate('S.phase')=='Victory' and fresh.evaluate('P.clears')==prior+1
 passed('Three-wave auto quest clears, and archived BB update does not disrupt rewards')
 # Canvas state leaks, javascript errors, and image loading
 page.wait_for_timeout(280)
 canvas=page.evaluate('window.__ctx');assert canvas['save']==canvas['restore'],canvas
 assert not errors and not e2,errors+e2
 imgs=page.evaluate('starterImages.filter(i=>i.complete&&i.naturalWidth>0).length');assert imgs==30,imgs
 passed('Canvas saves/restores balanced, 30 sprite atlases loaded, no JS errors')
 # Capture useful screenshot of BB schedule selected, scroll to inspection panel
 page.locator('#hitmode').select_option('bb')
 page.locator('#hitunit').select_option('10011')
 page.evaluate("document.querySelector('.hit-panel').scrollIntoView({block:'start'})")
 page.wait_for_timeout(450)
 page.screenshot(path=str(R/'BF_v0.13_BB_Hit_Lab_Preview.png'))
 page.set_viewport_size({'width':320,'height':720})
 page.wait_for_timeout(250)
 assert page.locator('#hitmode').is_visible()
 passed('BB inspector remains accessible at 390px and 320px mobile widths')
 browser.close()
report.update({'checksPassed':len(report['checks']),'browserErrors':errors,'canvasSaves':canvas['save'],'canvasRestores':canvas['restore'],'sha256':hashlib.sha256(html.encode()).hexdigest(),'androidStatus':'project generated; APK not compiled or device-tested'})
(R/'BF_v0.13_Test_Report.json').write_text(json.dumps(report,indent=2))
assert (R/'Brave_Frontier_Android_Offline_v0.13/app/src/main/assets/index.html').read_text()==html
print(json.dumps(report,indent=2),flush=True)
