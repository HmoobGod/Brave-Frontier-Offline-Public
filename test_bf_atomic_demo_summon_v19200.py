"""v192 Chromium: demo summons commit one canonical v7 transaction or roll back.

No original 2022 summon rates, and NO Gem purchasing is added.
"""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
A=R/"app/src/main/assets"
html=(A/"index.html").read_text("utf8")
assert html.count("BF192_ATOMIC_DEMO_SUMMON")==1
assert "if(S?.busy||saveRecoveryPending||P?.version!==7)return;" in html
assert "if(P.summonHistory.length>100)P.summonHistory=P.summonHistory.slice(-100);" in html
assert "if(!saveProgress()){\n   P=before;" in html
assert "bf_global_offline_demo_v7" in html
assert html.count('localStorage.setItem(SAVE_KEY,JSON.stringify(P))')==1
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
   executable_path=shutil.which("chromium") or shutil.which("google-chrome") or shutil.which("google-chrome-stable"),
   args=["--no-sandbox","--disable-dev-shm-usage"])
 p=b.new_page(viewport={"width":390,"height":844})
 errors=[]
 p.on("pageerror",lambda e:errors.append(str(e)))
 p.evaluate("""()=>{
   const db={};window.__v192DB=db;window.__v192Writes=[];
   window.__v192Quota=false;
   Object.defineProperty(window,"localStorage",{configurable:true,value:{
     getItem:k=>db[k]??null,
     setItem:(k,v)=>{
       if(__v192Quota)throw Error('intentional simulated full storage');
       db[k]=String(v);__v192Writes.push(k);
     },
     removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
     get length(){return Object.keys(db).length}
   }});
   window.alert=()=>{};window.confirm=()=>true;
   HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
   HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 p.set_content(html,wait_until="load",timeout=90000)
 assert p.evaluate("P.version")==7
 assert p.evaluate("QUESTS.length")==106
 assert p.evaluate("RECRUIT_IDS.length")>0
 assert p.locator("#summonbutton").count()==1
 assert p.evaluate("P.summonTokens")==0
 assert p.locator("#summonbutton").is_disabled()
 # Persist a source-valid starting point for the transaction.
 p.evaluate("P.summonTokens=1;renderSummonPanel();")
 assert p.evaluate("saveProgress()") is True
 assert not p.locator("#summonbutton").is_disabled()
 p.evaluate("Math.random=()=>0")
 baseline=p.evaluate("""()=>({
   state:JSON.stringify(P),saved:localStorage.getItem('bf_global_offline_demo_v7'),
   writes:__v192Writes.length,
   recruit:RECRUIT_IDS.find(id=>!P.roster.includes(id))
 })""")
 # Full storage: the failed summon must not consume token/recruit/history.
 p.evaluate("__v192Quota=true;document.getElementById('summonbutton').click()")
 fail=p.evaluate("""()=>({
   state:JSON.stringify(P),saved:localStorage.getItem('bf_global_offline_demo_v7'),
   writes:__v192Writes.length,result:document.getElementById('summonresult').textContent
 })""")
 assert fail["state"]==baseline["state"],"Failed save changed in-memory roster/wallet"
 assert fail["saved"]==baseline["saved"],"Failed save overwrote prior valid save"
 assert fail["writes"]==baseline["writes"],"Failed save recorded a write"
 assert "No token was spent" in fail["result"]
 assert p.evaluate("P.summonTokens")==1
 assert p.evaluate("P.roster.includes("+str(baseline["recruit"])+")") is False
 # Retry after storage is restored; exactly one token and ONE unique unit.
 p.evaluate("__v192Quota=false;renderSummonPanel();document.getElementById('summonbutton').click()")
 assert p.evaluate("P.summonTokens")==0
 assert p.evaluate("P.roster.includes("+str(baseline["recruit"])+")") is True
 assert p.evaluate("P.summonHistory.at(-1)")==baseline["recruit"]
 assert p.evaluate("""()=>{
   const stored=JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'));
   return stored.summonTokens===0&&
     stored.roster.length===P.roster.length&&
     JSON.stringify(stored.roster)===JSON.stringify(P.roster)&&
     JSON.stringify(stored.summonHistory)===JSON.stringify(P.summonHistory)&&
     JSON.stringify(parseProgress(stored))===JSON.stringify(P);
 }""")
 assert "Recruited" in p.locator("#summonresult").inner_text()
 assert p.locator("#summonbutton").is_disabled()
 before=p.evaluate("JSON.stringify(P)")
 p.evaluate("document.getElementById('summonbutton').click()")
 assert p.evaluate("JSON.stringify(P)")==before,"Zero-token summon changed state"
 # At the 100-recruit-history ceiling, retain the last 100 valid IDs.
 p.evaluate("P.summonHistory=Array(100).fill(RECRUIT_IDS[0]);P.summonTokens=1;renderSummonPanel()")
 assert p.evaluate("saveProgress()") is True
 p.evaluate("document.getElementById('summonbutton').click()")
 assert p.evaluate("P.summonHistory.length")==100
 assert p.evaluate("P.summonHistory.at(-1)") in p.evaluate("RECRUIT_IDS")
 assert p.evaluate("""()=>JSON.stringify(parseProgress(JSON.parse(
   localStorage.getItem('bf_global_offline_demo_v7'))))===JSON.stringify(P)""")
 # Save-recovery protection disables the button and even programmatic click
 # cannot spend tokens or mutate this source-valid save.
 p.evaluate("P.summonTokens=1;saveRecoveryPending=true;renderSummonPanel()")
 assert p.locator("#summonbutton").is_disabled()
 before=p.evaluate("JSON.stringify(P)")
 p.evaluate("document.getElementById('summonbutton').click()")
 assert p.evaluate("JSON.stringify(P)")==before
 p.evaluate("saveRecoveryPending=false;renderSummonPanel()")
 assert p.evaluate("P._bfGemV170Custom.schema")==1
 assert p.evaluate("P._bfGemV160.schema")==1
 assert not errors,errors
 b.close()
print("PASS v192: quota rollback, valid save commit, zero-token and recovery guards, 100-history cap; no Gem spending")
