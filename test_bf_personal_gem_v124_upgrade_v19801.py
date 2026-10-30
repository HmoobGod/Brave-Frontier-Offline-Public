"""v198.01: signed-v124 fixture -> personal Gem purchase -> export/reload gate.

Browser test uses the synthetic save produced by the actual signed v124 APK
and the current v7 parser. Never reads or changes the owner's real Android save.
"""
from pathlib import Path
import hashlib
import json
import shutil
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
KEY='bf_global_offline_demo_v7'
raw=(ROOT/'source_data/bf165_real_signed_v124_first_clear_save.json').read_text('utf8').rstrip('\n')
assert hashlib.sha256(raw.encode()).hexdigest()=='503165ae5b5f476a92f8a0e9f4d2197b8e2aa41a3a3462d23e1e202bec953170'
fixture=json.loads(raw)
assert fixture['version']==7 and fixture['questClears']=={'12':1}
assert len(fixture['roster'])==6 and len(fixture['squad'])==6
assert '_bfGemV170Custom' not in fixture
html=(ASSETS/'index.html').read_text('utf8')
assert html.count('BF198_PERSONAL_GEM_SUMMON_V19800')==1
assert html.count('localStorage.setItem(SAVE_KEY,JSON.stringify(P))')==1

with sync_playwright() as pw:
 browser=pw.chromium.launch(
  headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 p=browser.new_page(viewport={'width':390,'height':844})
 errors=[]
 p.on('pageerror',lambda error:errors.append(str(error)))
 p.evaluate("""()=>{const db={};window.__v19801writes=[];
   Object.defineProperty(window,'localStorage',{configurable:true,value:{
     getItem:k=>db[k]??null,
     setItem:(k,v)=>{db[k]=String(v);__v19801writes.push(k)},
     removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
     get length(){return Object.keys(db).length}
   }});
   window.alert=()=>{};window.confirm=()=>true;
   HTMLMediaElement.prototype.load=()=>{};
   HTMLMediaElement.prototype.pause=()=>{};
   HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 p.set_content(html,wait_until='load',timeout=90000)
 p.add_script_tag(path=str(ASSETS/'bf17000_personal_gem_rewards_ui.js'))
 assert p.evaluate('P.version')==7
 p.evaluate('raw=>{P=parseProgress(JSON.parse(raw));renderProgress()}',raw)
 assert p.evaluate('P.roster')==fixture['roster']
 assert p.evaluate('P.squad')==fixture['squad']
 assert p.evaluate('P.questClears')==fixture['questClears']
 assert p.evaluate('P._bfGemV160.legacyFinales')==[12]
 assert p.evaluate('P._bfGemV161Pending')==[]
 assert p.evaluate('P._bfGemV160.balance')==0
 assert p.evaluate('P._bfGemV170Custom.schema')==1
 assert p.evaluate('P._bfGemV170Custom.balance')==0
 assert p.evaluate('P._bfGemV170Custom.legacyClears')==[12]
 before=p.evaluate("""()=>({
   roster:[...P.roster],squad:[...P.squad],
   clears:{...P.questClears},original:JSON.stringify(P._bfGemV160),
   pending:JSON.stringify(P._bfGemV161Pending),
   tokens:P.summonTokens
 })""")
 assert p.evaluate("BFGlobalCustomGemsV17000.setMode('custom')") is True
 assert p.evaluate('BFGlobalCustomGemsV17000.claimWelcome()') is True
 assert p.evaluate('P._bfGemV170Custom.balance')==1000
 p.evaluate('Math.random=()=>0')
 next_id=p.evaluate('RECRUIT_IDS.find(id=>!P.roster.includes(id))')
 assert next_id is not None
 assert p.evaluate('bf198PersonalSummon()') is True
 assert p.evaluate('P._bfGemV170Custom.schema')==2
 assert p.evaluate('P._bfGemV170Custom.balance')==900
 assert p.evaluate('P._bfGemV170Custom.spent')==100
 assert p.evaluate('P._bfGemV170Custom.receipts')==[{'unitId':next_id,'cost':100}]
 assert p.evaluate('P.roster')==before['roster']+[next_id]
 assert p.evaluate('P.squad')==before['squad']
 assert p.evaluate('P.questClears')==before['clears']
 assert p.evaluate('P.summonTokens')==before['tokens']
 assert p.evaluate('JSON.stringify(P._bfGemV160)')==before['original']
 assert p.evaluate('JSON.stringify(P._bfGemV161Pending)')==before['pending']
 persisted=p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 assert persisted is not None
 assert json.loads(persisted)['_bfGemV170Custom']['spent']==100
 assert p.evaluate('raw=>JSON.stringify(parseProgress(JSON.parse(raw)))===JSON.stringify(P)',persisted)

 # Export CURRENT canonical save, not a possibly stale rotating snapshot.
 p.evaluate("""()=>{window.__v19801export=null;
   window.BFAndroid={exportSaveFile:(raw,name)=>{window.__v19801export={raw,name}}};
 }""")
 p.add_script_tag(path=str(ASSETS/'bf9700_qol_rotating_backups.js'))
 assert p.locator('#bf9700-export-current').count()==1
 p.locator('#bf9700-backups summary').click()
 p.locator('#bf9700-export-current').click()
 exported=p.evaluate('window.__v19801export')
 assert exported is not None and exported['raw']==persisted
 assert exported['name'].startswith('BraveFrontier-v7-current-')
 assert exported['name'].endswith('.json')

 # Simulate restoring the exact export with the modern parser: no free second
 # welcome claim, no vanished purchase, and no duplicated original claim.
 p.evaluate('raw=>{P=parseProgress(JSON.parse(raw));renderProgress()}',exported['raw'])
 assert p.evaluate('P._bfGemV170Custom.balance')==900
 assert p.evaluate('P._bfGemV170Custom.spent')==100
 assert p.evaluate('P._bfGemV170Custom.receipts.length')==1
 assert p.evaluate('P.roster.includes('+str(next_id)+')') is True
 assert p.evaluate('BFGlobalCustomGemsV17000.claimWelcome()') is False
 assert p.evaluate('BFGlobalOriginalGemClaimsV17300.claim()') is False

 # Malformed new receipts may never be accepted as a valid imported save.
 for which in ('duplicate','cost','missingUnit','debit'):
  assert p.evaluate("""which=>{
   const bad=JSON.parse(JSON.stringify(P));
   const w=bad._bfGemV170Custom;
   if(which==='duplicate')w.receipts.push({...w.receipts[0]});
   if(which==='cost')w.receipts[0].cost=1;
   if(which==='missingUnit')bad.roster=bad.roster.filter(x=>x!==w.receipts[0].unitId);
   if(which==='debit')w.spent=0;
   try{parseProgress(bad);return false}catch(_){return true}
  }""",which),which
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==persisted
 assert not errors,errors
 browser.close()
print('PASS v198.01: actual signed-v124 fixture survives custom Gem purchase, exact v7 export/reload and malformed receipt rejection')
