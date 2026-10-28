"""v161: verify real quest reward's source-verified first-clear evidence, zero Gems."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import ast,hashlib,json,os,re,shutil
R=Path(__file__).resolve().parent
html=Path(os.environ.get('BF161_HTML',str(R/'app/src/main/assets/index.html')))
s=html.read_text('utf8')
g=json.loads((R/'source_data/bf_global_2022_dungeon_finale_eligibility_v156.json').read_text('utf8'))
h=json.loads((R/'source_data/bf_global_2015_explicit_first_clear_gem_crosscheck_v157.json').read_text('utf8'))
assert g['originalRewardFinales']==h['corroboratedMissionCount']==29
assert g['currentPlayableFinales']==h['currentlyPlayable']==22
assert g['amdahlUnplayableFinales']==h['amdahlSourceOnly']==7
assert hashlib.sha256(json.dumps(g['rows'],separators=(',',':')).encode()).hexdigest()=='0086bcd4f08b1fc6a748c800f5444221afbb1c1a6fc749e9c7e593111498b3c8'
assert s.count('BF_GLOBAL_GEM_V161_NEW_FIRST_CLEAR_PENDING')==1
assert s.count('bf161RecordNewFirstClear(')==2
assert s.count('bf161ValidateOriginalPending(')==3
assert s.count('localStorage.setItem(SAVE_KEY,JSON.stringify(P))')==1
assert "const SAVE_KEY='bf_global_offline_demo_v7'" in s
assert 'P._bfGemV160.balance+=' not in s
assert 'P._bfGemV160.balance++' not in s
m=re.search(r'const BF160_ORIGINAL_GEM_FINAL_IDS=Object.freeze\((\[.*?\])\);',s,re.S)
assert m and re.fullmatch(r'[\[\],0-9\s]+',m.group(1))
assert ast.literal_eval(m.group(1))==[x[0] for x in g['rows'] if x[4]==1]
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
    executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
    args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{
  const db={};window.__db161=db;window.__writes161=[];window.__quota161=false;
  Object.defineProperty(window,'localStorage',{configurable:true,value:{
    getItem:k=>db[k]??null,
    setItem:(k,v)=>{if(window.__quota161)throw Error('quota');
       window.__writes161.push(k);db[k]=String(v)},
    removeItem:k=>{window.__writes161.push(k);delete db[k]},
    key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}
  }});
  window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};
  HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""")
 p.set_content(s,wait_until='load',timeout=90000)
 assert p.evaluate('P.version')==7
 assert p.evaluate('QUESTS.length')==106
 assert p.evaluate('P._bfGemV161Pending')==[]
 assert p.evaluate('P._bfGemV160.balance')==0
 p.evaluate('QUEST=QUESTS.find(q=>q.missionId===12);awardDemoRewards()')
 assert p.evaluate('P._bfGemV161Pending')==[12]
 assert p.evaluate('P._bfGemV160.legacyFinales')==[12]
 assert p.evaluate('P._bfGemV160.balance')==0
 p.evaluate('awardDemoRewards()')
 assert p.evaluate('P._bfGemV161Pending')==[12]
 assert p.evaluate('P.questClears[12]')==2
 p.evaluate('QUEST=QUESTS.find(q=>q.missionId===23);awardDemoRewards()')
 assert p.evaluate('P._bfGemV161Pending')==[12,23]
 assert p.evaluate('parseProgress(P)._bfGemV161Pending')==[12,23]
 # Import a pre-v161 v7 save: earlier finale 33 cannot become a new award.
 p.evaluate("""()=>{
   window.old161=JSON.parse(JSON.stringify(P));
   old161.questClears[33]=1;
   delete old161._bfGemV160;
   delete old161._bfGemV161Pending;
   P=parseProgress(old161);
 }""")
 assert p.evaluate('P._bfGemV161Pending')==[]
 assert p.evaluate('P._bfGemV160.legacyFinales')==[12,23,33]
 p.evaluate('QUEST=QUESTS.find(q=>q.missionId===33);awardDemoRewards()')
 assert p.evaluate('P._bfGemV161Pending')==[]
 p.evaluate('QUEST=QUESTS.find(q=>q.missionId===43);awardDemoRewards()')
 assert p.evaluate('P._bfGemV161Pending')==[43]
 assert p.evaluate('P._bfGemV160.legacyFinales')==[12,23,33,43]
 assert p.evaluate('bf161RecordNewFirstClear(0)') is False
 assert p.evaluate('bf161RecordNewFirstClear(1)') is False
 p.evaluate('QUEST={...QUEST,missionId:404}')
 assert p.evaluate('bf161RecordNewFirstClear(0)') is False
 for bad in ('[404]','[43,43]','[43,12]','null','[365]'):
  assert p.evaluate("""bad=>{
    const v=JSON.parse(JSON.stringify(P));
    v._bfGemV161Pending=(0,eval)(bad);
    try{parseProgress(v);return false;}catch(_){return true}
  }""",bad),bad
 # Quota failure must preserve the last persisted canonical v7 save.
 old=p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 p.evaluate('window.__quota161=true')
 assert p.evaluate('saveProgress()') is False
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==old
 p.evaluate('window.__quota161=false')
 assert p.evaluate('saveProgress()') is True
 assert p.evaluate('JSON.stringify(parseProgress(P))===JSON.stringify(P)')
 assert set(p.evaluate('__writes161'))=={'bf_global_offline_demo_v7'}
 assert p.evaluate('P._bfGemV160.balance')==0
 assert p.evaluate('P._bfGemV160.paidFinales')==[]
 assert not errors,errors
 b.close()
print('PASS v161: 22 original finale first-clear markers in live quest flow, no Gemini payout and v7 persistence safe')
