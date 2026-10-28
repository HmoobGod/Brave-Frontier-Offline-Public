"""v160: real bundled-v7-save first-clear Gem ledger migration, no rewards."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import ast,json,re,shutil
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets/index.html'
s=A.read_text('utf8')
g=json.loads((R/'source_data/bf_global_2022_dungeon_finale_eligibility_v156.json').read_text('utf8'))
h=json.loads((R/'source_data/bf_global_2015_explicit_first_clear_gem_crosscheck_v157.json').read_text('utf8'))
assert g['schema']=='bf-global-original-2022-final-dungeon-first-clear-gate-v156'
assert g['originalRewardFinales']==h['corroboratedMissionCount']==29
assert g['currentPlayableFinales']==h['currentlyPlayable']==22
assert g['amdahlUnplayableFinales']==h['amdahlSourceOnly']==7
assert g['canonicalRowsSha256']=='0086bcd4f08b1fc6a748c800f5444221afbb1c1a6fc749e9c7e593111498b3c8'
m=re.search(r'const BF160_ORIGINAL_GEM_FINAL_IDS=Object.freeze\((\[.*?\])\);',s,re.S)
assert m and re.fullmatch(r'[\[\],0-9\s]+',m.group(1))
ids=ast.literal_eval(m.group(1))
assert ids==[x[0] for x in g['rows'] if x[4]==1] and len(ids)==22
assert [x[0] for x in g['rows'] if x[4]==0]==[404,414,424,434,444,454,465]
assert s.count('BF_GLOBAL_GEM_V160_ORIGINAL_CLEAR_LEDGER')==1
assert s.count('bf160MigratedGemState(')==3
assert 'questClears:{},lastMission:1,_bfGemV160:{schema:1,balance:0,paidFinales:[],legacyFinales:[]}' in s
assert 'out._bfGemV160=bf160MigratedGemState(data._bfGemV160,out.questClears);' in s
assert 'P._bfGemV160=bf160MigratedGemState(P._bfGemV160,P.questClears);' in s
assert s.count("localStorage.setItem(SAVE_KEY,JSON.stringify(P))")==1
assert "const SAVE_KEY='bf_global_offline_demo_v7'" in s
assert "const BF160_ORIGINAL_GEM_FINAL_IDS" in s
# No JS implementing currency payouts or a separate Gem storage key.
assert 'P._bfGemV160.balance+=' not in s
assert 'P._bfGemV160.balance++' not in s
assert 'bf_global_offline_gem_wallet' not in s
assert "applicationId 'org.bravefrontier.offline'" in (R/'app/build.gradle').read_text('utf8')
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
     executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
     args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[]
 p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{
  const db={};window.__db160=db;window.__writes160=[];window.__quota160=false;
  Object.defineProperty(window,'localStorage',{configurable:true,value:{
   getItem:k=>db[k]??null,
   setItem:(k,v)=>{if(window.__quota160)throw Error('simulated quota');
      window.__writes160.push(k);db[k]=String(v);},
   removeItem:k=>{window.__writes160.push(k);delete db[k]},
   key:i=>Object.keys(db)[i]??null,
   get length(){return Object.keys(db).length}
  }});
  window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};
  HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 p.set_content(s,wait_until='load',timeout=90000)
 assert p.evaluate('P.version')==7
 assert p.evaluate('P._bfGemV160')=={'schema':1,'balance':0,'paidFinales':[],'legacyFinales':[]}
 assert p.evaluate('typeof parseProgress')=='function'
 assert p.evaluate('__writes160')==[]
 # Simulate a valid old v124 save (the new field is entirely absent).
 p.evaluate("""()=>{
   const old=JSON.parse(JSON.stringify(P));
   old.questClears={'12':1,'23':3,'365':1,'1':2};
   old.clears=7;old.exp=111;old.zel=107;old.karma=204;
   delete old._bfGemV160;
   window.__old160=old;
   window.__restored160=parseProgress(old);
 }""")
 assert p.evaluate('__restored160.version')==7
 assert p.evaluate('__restored160._bfGemV160')=={
   'schema':1,'balance':0,'paidFinales':[],'legacyFinales':[12,23,365]}
 assert p.evaluate('__restored160.questClears')=={'12':1,'23':3,'365':1,'1':2}
 assert p.evaluate('__restored160.zel')==107
 assert p.evaluate('__restored160.karma')==204
 assert p.evaluate('__restored160.squad')==p.evaluate('__old160.squad')
 assert p.evaluate('__restored160.roster')==p.evaluate('__old160.roster')
 assert p.evaluate('__restored160.materials')==p.evaluate('__old160.materials')
 assert p.evaluate('__restored160.unitExp')==p.evaluate('__old160.unitExp')
 assert p.evaluate('JSON.stringify(parseProgress(__restored160))===JSON.stringify(__restored160)')
 p.evaluate('P=__restored160;saveProgress()')
 assert p.evaluate('__writes160')==['bf_global_offline_demo_v7']
 assert p.evaluate("JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'))._bfGemV160.legacyFinales")==[12,23,365]
 # A new quest cleared on v160 is recorded in the exact same canonical save.
 p.evaluate("P.questClears[33]=1;P.clears++;saveProgress()")
 assert p.evaluate('P._bfGemV160.legacyFinales')==[12,23,33,365]
 assert p.evaluate("JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'))._bfGemV160.legacyFinales")==[12,23,33,365]
 assert p.evaluate('__writes160')==['bf_global_offline_demo_v7']*2
 assert p.evaluate('P._bfGemV160.balance')==0
 assert p.evaluate('P._bfGemV160.paidFinales')==[]
 assert p.evaluate('JSON.stringify(parseProgress(P))===JSON.stringify(P)')
 # Corrupted award/claim data must be refused rather than credit free gems.
 for value in (
   'null',
   '{schema:1,balance:1,paidFinales:[],legacyFinales:[]}',
   '{schema:1,balance:0,paidFinales:[12],legacyFinales:[]}',
   '{schema:1,balance:0,paidFinales:[],legacyFinales:[365,12]}',
   '{schema:1,balance:0,paidFinales:[],legacyFinales:[12,12]}',
   '{schema:1,balance:0,paidFinales:[],legacyFinales:[404]}',
   '{schema:0,balance:0,paidFinales:[],legacyFinales:[]}',
 ):
  rejected=p.evaluate("""v=>{const d=JSON.parse(JSON.stringify(P));
     d._bfGemV160=(0,eval)('('+v+')');
     try{parseProgress(d);return false;}catch(e){return true;}
  }""",value)
  assert rejected,value
 old_key=p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 p.evaluate('__quota160=true;P.questClears[43]=1')
 assert p.evaluate('saveProgress()') is False
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==old_key
 assert p.evaluate('P._bfGemV160.balance')==0
 p.evaluate('__quota160=false')
 assert p.evaluate('saveProgress()') is True
 assert p.evaluate("JSON.parse(localStorage.getItem('bf_global_offline_demo_v7'))._bfGemV160.legacyFinales")==[12,23,33,43,365]
 assert p.evaluate('__writes160')==['bf_global_offline_demo_v7']*3
 assert not errors,errors
 b.close()
print('PASS v160: source-exact 22 original finale IDs, legacy v7 save roundtrip, single-key ledgers, no currency or data loss')
