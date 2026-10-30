"""v198 browser regression for opt-in PERSONAL OFFLINE Gem summons.

Never confuse with 2022 original gacha rates/price/currency. Owner's existing
v7 save must survive schema-1 -> schema-2 receipts without data loss.
"""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
A=R/"app/src/main/assets"
html=(A/"index.html").read_text("utf8")
assert html.count("BF198_PERSONAL_GEM_SUMMON_V19800")==1
assert html.count("localStorage.setItem(SAVE_KEY,JSON.stringify(P))")==1
assert "bf_global_offline_demo_v7" in html
assert "BF_GLOBAL_GEMS_ORIGINAL_CLAIM_V17300" in html
assert "BF192_ATOMIC_DEMO_SUMMON" in html

with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
   executable_path=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable"),
   args=["--no-sandbox","--disable-dev-shm-usage"])
 p=b.new_page(viewport={"width":390,"height":844})
 errors=[]
 p.on("pageerror",lambda e:errors.append(str(e)))
 p.evaluate("""()=>{
   const db={};window.__v198DB=db;window.__v198Writes=[];
   window.__v198Quota=false;
   Object.defineProperty(window,"localStorage",{configurable:true,value:{
     getItem:k=>db[k]??null,
     setItem:(k,v)=>{
       if(window.__v198Quota)throw Error('v198 simulated quota exceeded');
       db[k]=String(v);window.__v198Writes.push(k);
     },
     removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
     get length(){return Object.keys(db).length}
   }});
   window.alert=()=>{};window.confirm=()=>true;
   HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
   HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 p.set_content(html,wait_until="load",timeout=90000)
 p.add_script_tag(path=str(A/"bf17000_personal_gem_rewards_ui.js"))
 assert p.evaluate("P.version")==7
 assert p.evaluate("BF198_PERSONAL_SUMMON_COST")==100
 assert p.evaluate("P._bfGemV170Custom.schema")==1
 assert p.locator("#bf19800-personal-summon").count()==1
 assert p.locator("#bf19800-personal-summon").is_disabled()
 original=p.evaluate("JSON.stringify(P._bfGemV160)")
 token=p.evaluate("P.summonTokens")
 initial=p.evaluate("P.roster.length")
 assert p.evaluate("BFGlobalCustomGemsV17000.claimWelcome()") is False
 assert p.evaluate("BFGlobalCustomGemsV17000.setMode('custom')") is True
 assert p.locator("#bf19800-personal-summon").is_disabled()
 assert p.evaluate("BFGlobalCustomGemsV17000.claimWelcome()") is True
 assert p.evaluate("P._bfGemV170Custom.balance")==1000
 assert not p.locator("#bf19800-personal-summon").is_disabled()
 assert p.evaluate("saveProgress()") is True
 p.evaluate("Math.random=()=>0")
 baseline=p.evaluate("""()=>({
   data:JSON.stringify(P),
   save:localStorage.getItem('bf_global_offline_demo_v7'),
   writes:__v198Writes.length,
   id:RECRUIT_IDS.find(id=>!P.roster.includes(id))
 })""")
 # All wallet, roster and history mutations must be rolled back on failure.
 p.evaluate("__v198Quota=true;document.getElementById('bf19800-personal-summon').click()")
 failed=p.evaluate("""()=>({
   data:JSON.stringify(P),
   save:localStorage.getItem('bf_global_offline_demo_v7'),
   writes:__v198Writes.length,
   result:document.getElementById('summonresult').textContent
 })""")
 assert failed["data"]==baseline["data"]
 assert failed["save"]==baseline["save"]
 assert failed["writes"]==baseline["writes"]
 assert "No Gems spent" in failed["result"]
 p.evaluate("__v198Quota=false;document.getElementById('bf19800-personal-summon').click()")
 assert p.evaluate("P._bfGemV170Custom.schema")==2
 assert p.evaluate("P._bfGemV170Custom.balance")==900
 assert p.evaluate("P._bfGemV170Custom.spent")==100
 assert p.evaluate("P._bfGemV170Custom.receipts")==[{"unitId":baseline["id"],"cost":100}]
 assert p.evaluate("P.roster.length")==initial+1
 assert p.evaluate("P.summonHistory.at(-1)")==baseline["id"]
 assert p.evaluate("P.summonTokens")==token
 assert p.evaluate("JSON.stringify(P._bfGemV160)")==original
 assert p.evaluate("""()=>{
   const saved=JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'));
   return JSON.stringify(parseProgress(saved))===JSON.stringify(P) &&
     saved._bfGemV170Custom.balance===900 && saved.roster.includes(saved._bfGemV170Custom.receipts[0].unitId)
 }""")
 # The next summon never duplicates the already purchased recruit.
 p.evaluate("document.getElementById('bf19800-personal-summon').click()")
 assert p.evaluate("P._bfGemV170Custom.balance")==800
 assert p.evaluate("P._bfGemV170Custom.spent")==200
 assert p.evaluate("new Set(P._bfGemV170Custom.receipts.map(r=>r.unitId)).size")==2
 assert p.evaluate("P.roster.length")==initial+2
 assert p.evaluate("P.summonTokens")==token
 # Original mode cannot buy and cannot make an RNG call through v198.
 assert p.evaluate("BFGlobalCustomGemsV17000.setMode('original')") is True
 assert p.locator("#bf19800-personal-summon").is_disabled()
 original_state=p.evaluate("JSON.stringify(P)")
 p.evaluate("document.getElementById('bf19800-personal-summon').click()")
 assert p.evaluate("JSON.stringify(P)")==original_state
 assert p.evaluate("bf198PersonalSummon()") is False
 assert p.evaluate("BFGlobalCustomGemsV17000.setMode('custom')") is True
 # A later legitimate daily claim works after migration and maintains ledger.
 assert p.evaluate("BFGlobalCustomGemsV17000.claimDaily()") is True
 assert p.evaluate("P._bfGemV170Custom.balance")==900
 assert p.evaluate("P._bfGemV170Custom.spent")==200
 # Strict ledger validation refuses free money, duplicate units, wrong
 # prices, forged ownership, and a schema-1 wallet with unexpected keys.
 for tamper in ("spent","balance","duplicate","cost","foreign","schema1extra"):
  assert p.evaluate("""which=>{
   const bad=JSON.parse(JSON.stringify(P));
   const w=bad._bfGemV170Custom;
   if(which==='spent')w.spent+=100;
   if(which==='balance')w.balance+=100;
   if(which==='duplicate')w.receipts.push({...w.receipts[0]});
   if(which==='cost')w.receipts[0].cost=1;
   if(which==='foreign')w.receipts[0].unitId=99999999;
   if(which==='schema1extra')w.schema=1;
   try{parseProgress(bad);return false}catch(_){return true}
  }""",tamper),tamper
 # Ensure older v7 snapshots without the optional Gem wallet still parse as
 # valid zero-balance schema 1; no forced conversion until a real purchase.
 assert p.evaluate("""()=>{
   const old=JSON.parse(JSON.stringify(P));
   delete old._bfGemV170Custom;
   const next=parseProgress(old);
   return next._bfGemV170Custom.schema===1 &&
     next._bfGemV170Custom.balance===0 &&
     next.version===7;
 }""")
 assert set(p.evaluate("window.__v198Writes"))=={"bf_global_offline_demo_v7"}
 assert not errors,errors
 b.close()
print("PASS v198 personal-only 100-Gem summons, receipt integrity, schema1 backward compatibility, atomic quota rollback and original ledger separation")
