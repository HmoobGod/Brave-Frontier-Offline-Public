"""v200: historical v198 demo purchase IDs must stay valid in future v7 saves.

The pinned recruit pool was extracted from the checked-in merged-v198 HTML
blob, not from a 2022 native summon source or a user's actual save.
Test current prepared HTML, with canonical v124 synthetic save as the base.
"""
import json
import hashlib
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
KEY='bf_global_offline_demo_v7'
baseline_raw=(ROOT/'source_data/bf_v198_recruit_id_compat_baseline_v200.json').read_bytes()
baseline=json.loads(baseline_raw)
original_raw=(ROOT/'source_data/bf165_real_signed_v124_first_clear_save.json').read_text('utf8').rstrip('\n')
original=json.loads(original_raw)
html=(ASSETS/'index.html').read_text('utf8')
assert html.count('BF198_PERSONAL_GEM_SUMMON_V19800')==1
assert html.count('localStorage.setItem(SAVE_KEY,JSON.stringify(P))')==1
assert baseline['schema']=='bf-global-v200-merged-v198-summon-pool-compatibility-baseline'
assert baseline['provenance']['baselineMainCommit']=='e40924d7b54960ff0ca4d685835c84b5e33ac18a'
assert baseline['provenance']['unpreparedIndexGitBlob']=='4ef5f1a1a4c3c0817828f29c0646a51a98843c77'
assert baseline['provenance']['baselineVersion']=='v198'
starter=baseline['startingUnitIds']
recruits=baseline['historicallyPurchasableDemoIds']
receipts=baseline['syntheticSchema2ReceiptIds']
assert starter==[10011,20011,30011,40011,50011,60011]
assert recruits==[10021,20021,30021,40021,50021,60021,10041,20041,30041,40041,50041,60041]
assert receipts==[10021,20021] and set(receipts)<=set(recruits)
assert len(recruits)==len(set(recruits)) and not set(starter)&set(recruits)
assert baseline['syntheticPersonalEarnedGems']==1000
assert baseline['syntheticPersonalSpentGems']==200
assert baseline['changesToGame'] is False
assert hashlib.sha256(original_raw.encode('utf8')).hexdigest()=='503165ae5b5f476a92f8a0e9f4d2197b8e2aa41a3a3462d23e1e202bec953170'
assert original['version']==7 and original['questClears']=={'12':1}

with sync_playwright() as pw:
 browser=pw.chromium.launch(
    headless=True,
    executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
    args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[]
 page.on('pageerror',lambda error:errors.append(str(error)))
 page.evaluate("""()=>{
    const storage={};
    window.__v200Storage=storage;
    window.__v200Writes=[];
    Object.defineProperty(window,'localStorage',{configurable:true,value:{
      getItem:k=>storage[k]??null,
      setItem:(k,v)=>{storage[k]=String(v);window.__v200Writes.push(k)},
      removeItem:k=>delete storage[k],
      key:i=>Object.keys(storage)[i]??null,
      get length(){return Object.keys(storage).length}
    }});
    window.alert=()=>{};
    window.confirm=()=>true;
    HTMLMediaElement.prototype.load=()=>{};
    HTMLMediaElement.prototype.pause=()=>{};
    HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 page.set_content(html,wait_until='load',timeout=90000)
 assert page.evaluate('P.version')==7
 assert page.evaluate('QUESTS.length')==106
 # A change that removes, renumbers, or reclassifies any existing purchasable
 # v198 ID must fail this test, even if new IDs are freely appended.
 checks=page.evaluate("""base=>{
    const present=arr=>arr.every(id=>Number.isSafeInteger(id));
    return {
      starters:present(base.startingUnitIds)&&base.startingUnitIds.every(
         id=>STARTER_IDS.includes(id)&&ALL_IDS.includes(id)&&UNIT_BY_ID.has(id)),
      recruits:present(base.historicallyPurchasableDemoIds)&&
         base.historicallyPurchasableDemoIds.every(
         id=>RECRUIT_IDS.includes(id)&&ALL_IDS.includes(id)&&UNIT_BY_ID.has(id)),
      disjoint:base.historicallyPurchasableDemoIds.every(id=>!STARTER_IDS.includes(id)),
      allUnique:new Set(RECRUIT_IDS).size===RECRUIT_IDS.length,
      oldPoolCount:base.historicallyPurchasableDemoIds.length,
      currentPoolCount:RECRUIT_IDS.length
    };
 }""",baseline)
 assert checks['starters'] is True and checks['recruits'] is True
 assert checks['disjoint'] is True and checks['allUnique'] is True
 assert checks['oldPoolCount']==12 and checks['currentPoolCount']>=12

 # Construct a SYNTHETIC schema-2 owner-upgrade save using v124-signed test
 # fixture plus frozen historical v198 receipt IDs. This is a forward parser
 # compatibility test, NOT a historical owner save or live player transaction.
 constructed=page.evaluate("""data=>{
    const old=parseProgress(data.old);
    if(old.version!==7||old._bfGemV170Custom.schema!==1||
       old._bfGemV170Custom.balance!==0)return null;
    const historical=JSON.parse(JSON.stringify(old));
    const w=historical._bfGemV170Custom;
    if(w.legacyClears.length!==1||w.legacyClears[0]!==12)return null;
    historical.roster.push(...data.ids);
    historical.summonHistory.push(...data.ids);
    historical._bfGemV170Custom={
      ...w, schema:2, mode:'custom', welcomeClaimed:true,
      balance:data.earned-data.spent,
      spent:data.spent,
      receipts:data.ids.map(unitId=>({unitId,cost:100}))
    };
    const accepted=parseProgress(historical);
    return {
      payload:JSON.stringify(historical),
      parsed:JSON.stringify(accepted),
      ids:accepted._bfGemV170Custom.receipts.map(r=>r.unitId),
      schema:accepted._bfGemV170Custom.schema,
      balance:accepted._bfGemV170Custom.balance,
      spent:accepted._bfGemV170Custom.spent,
      squad:[...accepted.squad],
      roster:[...accepted.roster],
      originalGemLedgerUnchanged:
        JSON.stringify(accepted._bfGemV160)===JSON.stringify(old._bfGemV160)
    };
 }""",{'old':original,'ids':receipts,'earned':1000,'spent':200})
 assert constructed is not None
 assert constructed['ids']==receipts
 assert constructed['schema']==2
 assert constructed['balance']==800 and constructed['spent']==200
 assert constructed['squad']==original['squad']
 assert constructed['roster']==original['roster']+receipts
 assert constructed['originalGemLedgerUnchanged'] is True
 # Persist an actual parse-accepted synthetic schema-2 save through the same
 # production saveProgress code, then parse the stored canonical v7 bytes.
 page.evaluate("raw=>{P=parseProgress(JSON.parse(raw));}",constructed['payload'])
 assert page.evaluate("saveProgress()") is True
 stored=page.evaluate(f"localStorage.getItem('{KEY}')")
 assert stored is not None
 stored_obj=json.loads(stored)
 assert set(page.evaluate("window.__v200Writes"))=={KEY}
 assert stored_obj['_bfGemV170Custom']['receipts']==[
     {'unitId':id,'cost':100} for id in receipts]
 assert stored_obj['_bfGemV170Custom']['spent']==200
 assert page.evaluate("""()=>JSON.stringify(
   parseProgress(JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'))))===
   JSON.stringify(P)""") is True
 # A previously purchased schema-2 owner fixture may still earn the
 # authentic source-gated 2022 finale's *personal offline* +100 reward.
 # This closes Claude's optional W6 without changing native Gem claims.
 page.evaluate('QUEST=QUESTS.find(q=>q.missionId===23);awardDemoRewards()')
 assert page.evaluate('P._bfGemV170Custom.balance')==900
 assert page.evaluate('P._bfGemV170Custom.spent')==200
 assert page.evaluate('P._bfGemV170Custom.firstPaid.includes(23)') is True
 assert page.evaluate('P._bfGemV170Custom.receipts.map(r=>r.unitId)')==receipts
 assert page.evaluate('JSON.stringify(parseProgress(P))===JSON.stringify(P)') is True
 page.evaluate('awardDemoRewards()')
 assert page.evaluate('P._bfGemV170Custom.balance')==901
 assert page.evaluate('P._bfGemV170Custom.replaysPaid')==1
 assert page.evaluate('JSON.stringify(parseProgress(P))===JSON.stringify(P)') is True
 assert page.evaluate("JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'))._bfGemV170Custom.balance")==901
 assert not errors,errors
 browser.close()

print('PASS v200: merged-v198 12-recruit historical IDs remain eligible; synthetic 2-receipt canonical v7 save accepts and roundtrips')
