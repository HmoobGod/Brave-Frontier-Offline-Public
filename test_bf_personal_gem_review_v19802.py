"""v198.02 Claude N1/N2: isolated purchase receipts and second-transaction safety.

These tests run against the real patched HTML in GitHub Actions Chromium.
They never mutate the owner's installed app or personal save.
"""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
html=(ASSETS/'index.html').read_text('utf8')
assert html.count('BF198_PERSONAL_GEM_SUMMON_V19800')==1
assert html.count('localStorage.setItem(SAVE_KEY,JSON.stringify(P))')==1
assert "receipts:Object.freeze(P._bfGemV170Custom.receipts.map(r=>Object.freeze({...r})))" in html
assert 'bf_global_offline_demo_v7' in html

with sync_playwright() as pw:
 browser=pw.chromium.launch(
  headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""()=>{const db={};window.__fix19802DB=db;window.__fix19802Quota=false;
   Object.defineProperty(window,'localStorage',{configurable:true,value:{
    getItem:k=>db[k]??null,
    setItem:(k,v)=>{if(__fix19802Quota)throw Error('v19802 quota');db[k]=String(v)},
    removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
    get length(){return Object.keys(db).length}
   }});
   window.alert=()=>{};window.confirm=()=>true;
   HTMLMediaElement.prototype.load=()=>{};
   HTMLMediaElement.prototype.pause=()=>{};
   HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 page.set_content(html,wait_until='load',timeout=90000)
 page.add_script_tag(path=str(ASSETS/'bf17000_personal_gem_rewards_ui.js'))
 assert page.evaluate('P.version')==7
 assert page.evaluate('QUESTS.length')==106
 assert page.evaluate('P._bfGemV170Custom.schema')==1
 assert page.evaluate("""()=>{
   const before=BFGlobalCustomGemsV17000.snapshot();
   return Object.isFrozen(before)&&!('receipts' in before)&&!('spent' in before)
 }""")
 assert page.evaluate("BFGlobalCustomGemsV17000.setMode('custom')") is True
 assert page.evaluate("BFGlobalCustomGemsV17000.claimWelcome()") is True
 page.evaluate('Math.random=()=>0')
 first=page.evaluate('RECRUIT_IDS.find(id=>!P.roster.includes(id))')
 assert first is not None
 assert page.evaluate('bf198PersonalSummon()') is True
 assert page.evaluate('P._bfGemV170Custom.schema')==2
 assert page.evaluate('P._bfGemV170Custom.balance')==900
 assert page.evaluate('P._bfGemV170Custom.spent')==100

 # Snapshot is deeply detached and frozen for the entire new receipt tree.
 assert page.evaluate("""()=>{
   const s=BFGlobalCustomGemsV17000.snapshot();
   const live=P._bfGemV170Custom;
   if(!Object.isFrozen(s)||!Object.isFrozen(s.receipts)||s.spent!==100)return false;
   if(s.receipts===live.receipts||s.receipts[0]===live.receipts[0])return false;
   if(!Object.isFrozen(s.receipts[0]))return false;
   try{s.receipts.push({unitId:1,cost:1})}catch(_){}
   try{s.receipts[0].unitId=1}catch(_){}
   return live.receipts.length===1&&live.receipts[0].unitId===s.receipts[0].unitId;
 }""")
 assert page.evaluate('saveProgress()') is True
 assert page.evaluate('BFGlobalCustomGemsV17000.snapshot().receipts.length')==1

 # A second purchase, already in schema 2, must restore the precise old P
 # and persisted bytes on a storage exception (Claude's N1-adjacent gate).
 baseline=page.evaluate("""()=>({
   state:JSON.stringify(P),
   raw:localStorage.getItem('bf_global_offline_demo_v7'),
   next:RECRUIT_IDS.find(id=>!P.roster.includes(id))
 })""")
 assert baseline['next'] is not None
 assert page.evaluate('window.__fix19802Quota=true;bf198PersonalSummon()') is False
 assert page.evaluate('JSON.stringify(P)')==baseline['state']
 assert page.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==baseline['raw']
 page.evaluate('window.__fix19802Quota=false')
 assert page.evaluate('bf198PersonalSummon()') is True
 assert page.evaluate('P._bfGemV170Custom.spent')==200
 assert page.evaluate('P._bfGemV170Custom.balance')==800
 assert page.evaluate('P._bfGemV170Custom.receipts.length')==2

 # Quest earn logic continues after schema conversion: first clear +25,
 # the same mission replay +1; no second welcome claim.
 page.evaluate('QUEST=QUESTS.find(q=>q.missionId===10);awardDemoRewards()')
 assert page.evaluate('P._bfGemV170Custom.balance')==825
 page.evaluate('awardDemoRewards()')
 assert page.evaluate('P._bfGemV170Custom.balance')==826
 assert page.evaluate('P._bfGemV170Custom.spent')==200
 assert page.evaluate('BFGlobalCustomGemsV17000.claimWelcome()') is False
 assert page.evaluate("JSON.stringify(parseProgress(JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'))))===JSON.stringify(P)")

 # Cap existing summon history at 100 even when a Gem receipt is added.
 page.evaluate('P.summonHistory=Array(100).fill(RECRUIT_IDS[0])')
 assert page.evaluate('saveProgress()') is True
 assert page.evaluate('bf198PersonalSummon()') is True
 assert page.evaluate('P.summonHistory.length')==100
 assert page.evaluate('P._bfGemV170Custom.receipts.length')==3
 assert page.evaluate('P.summonHistory.at(-1)')==page.evaluate('P._bfGemV170Custom.receipts.at(-1).unitId')

 # Purchased receipt IDs must never be removed or changed in RECRUIT_IDS:
 # this invariant protects all existing and future schema-2 saved players.
 assert page.evaluate("""()=>{
   const wallet=P._bfGemV170Custom;
   return wallet.receipts.every(r=>
     RECRUIT_IDS.includes(r.unitId) && P.roster.includes(r.unitId) &&
     r.cost===100) && wallet.spent===wallet.receipts.length*100;
 }""")
 assert page.evaluate("""()=>{
   const bad=JSON.parse(JSON.stringify(P));
   bad._bfGemV170Custom.receipts[0].unitId=-1;
   try{parseProgress(bad);return false}catch(_){return true}
 }""")
 assert page.evaluate("""()=>{
   const bad=JSON.parse(JSON.stringify(P));
   bad.roster=bad.roster.filter(id=>id!==bad._bfGemV170Custom.receipts[0].unitId);
   try{parseProgress(bad);return false}catch(_){return true}
 }""")
 assert page.evaluate("""()=>{
   const starter=P.roster.find(id=>!RECRUIT_IDS.includes(id));
   if(starter===undefined)return true;
   const bad=JSON.parse(JSON.stringify(P));
   bad._bfGemV170Custom.receipts[0].unitId=starter;
   try{parseProgress(bad);return false}catch(_){return true}
 }""")

 # At zero eligible recruits, no purchase is possible regardless of funds.
 # Never serialize this synthetic all-owned test state as a production save.
 assert page.evaluate("""()=>{
   const real=P;
   const synthetic=JSON.parse(JSON.stringify(real));
   synthetic.roster=[...new Set([...synthetic.roster,...RECRUIT_IDS])];
   P=synthetic;renderSummonPanel();
   const blocked=document.getElementById('bf19800-personal-summon').disabled &&
                 bf198PersonalSummon()===false;
   P=real;renderSummonPanel();
   return blocked;
 }""")
 # Valid insufficient-funds case: a pre-cleared quest yields 99 replay
 # Gems with welcome unclaimed. This tests the real 99-Gem guard, rather
 # than a fabricated wallet that the validator would reject immediately.
 assert page.evaluate("""()=>{
   const old=defaultProgress();
   old.questClears={'10':1};
   P=parseProgress(old);
   return P._bfGemV170Custom.schema===1 &&
     P._bfGemV170Custom.balance===0 &&
     P._bfGemV170Custom.legacyClears.includes(10);
 }""")
 assert page.evaluate("BFGlobalCustomGemsV17000.setMode('custom')") is True
 page.evaluate("QUEST=QUESTS.find(q=>q.missionId===10);for(let i=0;i<99;i++)awardDemoRewards()")
 assert page.evaluate('P._bfGemV170Custom.balance')==99
 assert page.evaluate('P._bfGemV170Custom.replaysPaid')==99
 assert page.evaluate('JSON.stringify(parseProgress(P))===JSON.stringify(P)')
 assert page.locator('#bf19800-personal-summon').is_disabled()
 before99=page.evaluate('JSON.stringify(P)')
 assert page.evaluate('bf198PersonalSummon()') is False
 assert page.evaluate('JSON.stringify(P)')==before99
 assert not errors,errors
 browser.close()
print('PASS v198.02: frozen detached receipts, schema1 keys, 2nd quota rollback, post-purchase rewards, 100-history cap and recruit-ID stability')
