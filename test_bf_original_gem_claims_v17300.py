"""v173 production Chromium test: original one-Gem claims, save safety."""
import json,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent
html=(R/'app/src/main/assets/index.html').read_text('utf8')
assert html.count('BF_GLOBAL_GEMS_ORIGINAL_CLAIM_V17300')==1
assert html.count('localStorage.setItem(SAVE_KEY,JSON.stringify(P))')==1
assert 'bf173ValidateOriginalClaims(out._bfGemV160,out._bfGemV161Pending,out._bfGemV170Custom)' in html
assert 'bf173ValidateOriginalClaims(P._bfGemV160,P._bfGemV161Pending,P._bfGemV170Custom)' in html
g=json.loads((R/'source_data/bf_global_2022_dungeon_finale_eligibility_v156.json').read_text('utf8'))
assert g['currentPlayableFinales']==22 and g['amdahlUnplayableFinales']==7
assert "applicationId 'org.bravefrontier.offline'" in (R/'app/build.gradle').read_text('utf8')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{
  const db={};window.__originalGemDB=db;window.__originalGemWrites=[];
  window.__originalGemQuota=false;
  Object.defineProperty(window,'localStorage',{configurable:true,value:{
   getItem:k=>db[k]??null,
   setItem:(k,v)=>{if(window.__originalGemQuota)throw Error('quota');
    window.__originalGemWrites.push(k);db[k]=String(v)},
   removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
   get length(){return Object.keys(db).length}
  }});
  window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 p.set_content(html,wait_until='load',timeout=90000)
 assert p.locator('#bf17300-original-gems').count()==1
 assert p.evaluate('P.version')==7
 assert p.evaluate('QUESTS.length')==106
 assert p.evaluate('P._bfGemV160.balance')==0
 assert p.evaluate('BFGlobalOriginalGemClaimsV17300.claim()') is False
 assert p.evaluate('BFGlobalOriginalGemClaimsV17300.snapshot().eligible')==[]
 # First genuine original-mode source finale, no auto-credit.
 p.evaluate('QUEST=QUESTS.find(q=>q.missionId===12);awardDemoRewards()')
 assert p.evaluate('P._bfGemV161Pending')==[12]
 assert p.evaluate('P._bfGemV160.balance')==0
 assert p.evaluate('BFGlobalOriginalGemClaimsV17300.snapshot().eligible')==[12]
 assert p.evaluate('BFGlobalOriginalGemClaimsV17300.claim()')==1
 assert p.evaluate('P._bfGemV160.balance')==1
 assert p.evaluate('P._bfGemV160.paidFinales')==[12]
 assert p.evaluate('BFGlobalOriginalGemClaimsV17300.claim()') is False
 assert p.evaluate('JSON.stringify(parseProgress(P))===JSON.stringify(P)')
 assert p.evaluate("JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'))._bfGemV160.balance")==1
 # Custom first clear gets its custom payout but never an extra original claim.
 assert p.evaluate('BFGlobalCustomGemsV17000.setMode("custom")') is True
 p.evaluate('QUEST=QUESTS.find(q=>q.missionId===23);awardDemoRewards()')
 assert p.evaluate('P._bfGemV170Custom.firstPaid')==[23]
 assert p.evaluate('P._bfGemV170Custom.balance')==100
 assert p.evaluate('P._bfGemV161Pending')==[12,23]
 assert p.evaluate('BFGlobalOriginalGemClaimsV17300.claim()') is False
 assert p.evaluate('BFGlobalCustomGemsV17000.setMode("original")') is True
 assert p.evaluate('BFGlobalOriginalGemClaimsV17300.snapshot().eligible')==[]
 # One more first clear in original mode, then claim exactly one new Gem.
 p.evaluate('QUEST=QUESTS.find(q=>q.missionId===33);awardDemoRewards()')
 assert p.evaluate('BFGlobalOriginalGemClaimsV17300.snapshot().eligible')==[33]
 assert p.evaluate('BFGlobalOriginalGemClaimsV17300.claim()')==1
 assert p.evaluate('P._bfGemV160.paidFinales')==[12,33]
 assert p.evaluate('P._bfGemV160.balance')==2
 assert p.evaluate('JSON.stringify(parseProgress(P))===JSON.stringify(P)')
 # Legacy v124 imported clear is NOT an eligible new claim.
 p.evaluate("""()=>{
  const old=JSON.parse(JSON.stringify(P));
  old.questClears={'12':2,'23':1,'33':1,'43':1};
  delete old._bfGemV160;delete old._bfGemV161Pending;
  delete old._bfGemV170Custom;
  P=parseProgress(old);
 }""")
 assert p.evaluate('P._bfGemV160.legacyFinales')==[12,23,33,43]
 assert p.evaluate('P._bfGemV160.balance')==0
 assert p.evaluate('P._bfGemV161Pending')==[]
 p.evaluate('QUEST=QUESTS.find(q=>q.missionId===43);awardDemoRewards()')
 assert p.evaluate('BFGlobalOriginalGemClaimsV17300.claim()') is False
 # Forged, unbacked or custom-first-clear original payout must be quarantined.
 p.evaluate("""()=>{
  const old=JSON.parse(JSON.stringify(P));
  old.questClears[23]=1;old._bfGemV161Pending=[23];
  old._bfGemV170Custom.firstPaid=[23];
  old._bfGemV170Custom.legacyClears=[12,33,43];
  old._bfGemV170Custom.balance=100;
  window.__candidate173=old;
 }""")
 for bad in ('unbacked','custom','duplicate','wrong-balance','amdahl'):
  assert p.evaluate("""kind=>{
   const d=JSON.parse(JSON.stringify(window.__candidate173));
   d._bfGemV160.paidFinales=kind==='duplicate'?[23,23]:[kind==='amdahl'?404:23];
   d._bfGemV160.balance=kind==='duplicate'?2:kind==='wrong-balance'?0:1;
   if(kind==='unbacked')d._bfGemV161Pending=[];
   if(kind==='custom'){} // 23 already custom firstPaid.
   try{parseProgress(d);return false}catch(e){return true}
  }""",bad),bad
 # Atomic write rollback and successful retry after recovering saved state.
 p.evaluate('QUEST=QUESTS.find(q=>q.missionId===53);awardDemoRewards()')
 assert p.evaluate('BFGlobalOriginalGemClaimsV17300.snapshot().eligible')==[53]
 saved=p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 p.evaluate('window.__originalGemQuota=true')
 assert p.evaluate('BFGlobalOriginalGemClaimsV17300.claim()') is False
 assert p.evaluate('P._bfGemV160.balance')==0
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==saved
 p.evaluate("""raw=>{window.__originalGemQuota=false;P=parseProgress(JSON.parse(raw));
  saveEnabled=true;}""",saved)
 assert p.evaluate('BFGlobalOriginalGemClaimsV17300.claim()')==1
 assert p.evaluate('P._bfGemV160.balance')==1
 assert p.evaluate('JSON.stringify(parseProgress(P))===JSON.stringify(P)')
 assert set(p.evaluate('__originalGemWrites'))=={'bf_global_offline_demo_v7'}
 assert not errors,errors
 b.close()
print('PASS v173: one-original-Gem verified first-clear claims, custom exclusion, v124 migration, strict save and rollback')
