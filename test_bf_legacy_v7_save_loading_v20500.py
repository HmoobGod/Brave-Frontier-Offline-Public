"""v205: synthetic, privacy-safe pre-Gem/Imp v7 save load and corruption safety.

The owner's real v7 save was checked separately and is not embedded or uploaded.
No runtime code, combat, quest mechanics or save schema changes.
"""
from pathlib import Path
import hashlib
import json
import shutil
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
HTML=ROOT/'app/src/main/assets/index.html'
SOURCE=ROOT/'source_data/bf_global_original_2022_live_quest_economy_v142.json'
html=HTML.read_text('utf8')
original=json.loads(SOURCE.read_text('utf8'))
assert original['total']==106 and original['year']==2022
assert hashlib.sha256(json.dumps(original['records'],separators=(',',':')).encode()).hexdigest()==original['canonicalTupleSha256']=='a1b36659dfc80bc6e1e0e244ba52b3c6d423b239cf684439a5488bf679764a66'
assert "const SAVE_KEY='bf_global_offline_demo_v7'" in html

legacy_fields=('format','version','trainingShards','trainingSpent','evolutions',
               'materials','exp','zel','karma','clears','level','squad','roster',
               'summonTokens','summonHistory','unitExp','questClears','lastMission')

with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 starter=browser.new_page(viewport={'width':390,'height':844})
 starter.set_content(html,wait_until='load',timeout=120000)
 base=starter.evaluate('() => JSON.parse(JSON.stringify(P))')
 assert base['version']==7
 legacy={k:base[k] for k in legacy_fields}
 legacy.update(exp=50,level=5,zel=1234,karma=27,clears=1,
               questClears={'1':1},lastMission=1)
 legacy['unitExp'][str(legacy['squad'][0])]=50
 assert not any(k.startswith('_bf') for k in legacy)
 starter.close()

 def check_save(source,should_recover):
  raw=json.dumps(source,separators=(',',':'))
  p=browser.new_page(viewport={'width':390,'height':844})
  errors=[];p.on('pageerror',lambda error:errors.append(str(error)))
  p.evaluate("""raw=>{
    const memory={'bf_global_offline_demo_v7':raw};
    Object.defineProperty(window,'localStorage',{configurable:true,value:{
     getItem:k=>Object.prototype.hasOwnProperty.call(memory,k)?memory[k]:null,
     setItem:(k,v)=>memory[k]=String(v),removeItem:k=>delete memory[k],
     key:i=>Object.keys(memory)[i]??null,get length(){return Object.keys(memory).length}}});
    window.alert=()=>{};window.confirm=()=>true;
    HTMLMediaElement.prototype.load=()=>{};
    HTMLMediaElement.prototype.pause=()=>{};
    HTMLMediaElement.prototype.play=()=>Promise.resolve();
  }""",raw)
  p.set_content(html,wait_until='load',timeout=120000)
  state=p.evaluate("""()=>({
    version:P.version,format:P.format,source:saveRecoveredFrom,
    pending:saveRecoveryPending,issues:saveRecoveryIssues.length,
    original:localStorage.getItem('bf_global_offline_demo_v7'),
    quarantineKeys:[...Array(localStorage.length)].map((_,i)=>localStorage.key(i)).filter(k=>k.startsWith('bf_global_offline_quarantine_')),
    player:JSON.parse(JSON.stringify(P)),quests:QUESTS.map(q=>[
      q.missionId,q.dungeonId,q.requires,q.battles,q.energy,q.exp,q.zel,q.karma]),
    wallet:P._bfGemV170Custom?.balance,
    gemBalance:P._bfGemV160?.balance,
    saveResult:saveRecoveryPending?saveProgress():null
  })""")
  assert state['original']==raw, 'raw v7 save overwritten on load'
  assert state['version']==7 and state['format']=='bf-global-offline-demo'
  assert state['quests']==original['records']
  assert state['pending']==should_recover
  if should_recover:
   assert state['issues']==1 and state['source'] is None
   assert len(state['quarantineKeys'])==1
   assert state['saveResult'] is False
  else:
   assert state['issues']==0 and state['source']=='bf_global_offline_demo_v7'
   assert not state['quarantineKeys']
   for k in ('roster','squad','unitExp','materials','questClears',
             'exp','zel','karma','clears','lastMission'):
    assert state['player'][k]==source[k],k
   assert state['wallet']==0 and state['gemBalance']==0
  assert not errors,errors[:3]
  p.close()

 check_save(legacy,False)
 broken=json.loads(json.dumps(legacy))
 broken['questClears']['999999']=1
 check_save(broken,True)
 browser.close()
print('PASS v205: synthetic legacy v7 preserves progress, no free Gems; malformed saves quarantined')
