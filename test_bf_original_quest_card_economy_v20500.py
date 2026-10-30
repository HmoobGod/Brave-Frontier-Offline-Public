"""v205: authentic 106-quest economy display + synthetic legacy-v7 save smoke.

Pure test fixture; never loads or publishes the owner's private save.
"""
from pathlib import Path
from copy import deepcopy
import hashlib, importlib.util, json, shutil
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
APP=R/'app/src/main/assets/index.html'
F=R/'source_data/bf_global_original_2022_live_quest_economy_v142.json'
PATCH=R/'patch_bf_original_quest_card_economy_v20500.py'
spec=importlib.util.spec_from_file_location('v205patch',PATCH)
patch=importlib.util.module_from_spec(spec);spec.loader.exec_module(patch)
html=APP.read_text('utf8')
assert patch.patch(html)==html, 'not idempotent'
assert html.count(patch.AFTER_CARD)==html.count(patch.AFTER_INFO)==1
assert patch.BEFORE_CARD not in html and patch.BEFORE_INFO not in html
assert "const SAVE_KEY='bf_global_offline_demo_v7'" in html
assert 'P.exp+=QUEST.exp;P.zel+=QUEST.zel;P.karma+=QUEST.karma;' in html
for missing in (patch.AFTER_CARD,patch.AFTER_INFO):
 try:patch.patch(html.replace(missing,'',1))
 except ValueError:pass
 else:raise AssertionError('drift did not fail closed')
original=json.loads(F.read_text('utf8'))
columns=['missionId','missionDungeonId','requiredMissionId','missionBattleCount',
         'missionEnergyUse','exp','zel','karma']
assert original['columns']==columns and original['total']==106
raw=json.dumps(original['records'],separators=(',',':')).encode()
assert hashlib.sha256(raw).hexdigest()==original['canonicalTupleSha256']==(
 'a1b36659dfc80bc6e1e0e244ba52b3c6d423b239cf684439a5488bf679764a66')

with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=(shutil.which('chromium') or
  shutil.which('google-chrome') or shutil.which('google-chrome-stable')),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 bootstrap=browser.new_page(viewport={'width':390,'height':844})
 bootstrap.set_content(html,wait_until='load',timeout=120000)
 state=bootstrap.evaluate('() => JSON.parse(JSON.stringify(P))')
 legacy_keys=('format','version','trainingShards','trainingSpent','evolutions',
  'materials','exp','zel','karma','clears','level','squad','roster',
  'summonTokens','summonHistory','unitExp','questClears','lastMission')
 legacy={k:deepcopy(state[k]) for k in legacy_keys}
 legacy.update(exp=50,level=5,zel=1234,karma=27,clears=1,
   questClears={'1':1},lastMission=1)
 legacy['unitExp'][str(legacy['squad'][0])]=50
 seeded=json.dumps(legacy,separators=(',',':'))
 bootstrap.close()
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""raw=>{
  const storage={'bf_global_offline_demo_v7':raw};
  Object.defineProperty(window,'localStorage',{configurable:true,value:{
   getItem:k=>Object.prototype.hasOwnProperty.call(storage,k)?storage[k]:null,
   setItem:(k,v)=>storage[k]=String(v),removeItem:k=>delete storage[k],
   key:i=>Object.keys(storage)[i]??null,
   get length(){return Object.keys(storage).length}}});
  window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};
  HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve();
 }""",seeded)
 page.set_content(html,wait_until='load',timeout=120000)
 after=page.evaluate("""()=>({
  player:JSON.parse(JSON.stringify(P)),pending:saveRecoveryPending,
  issues:saveRecoveryIssues.length,recoveredFrom:saveRecoveredFrom,
  stored:localStorage.getItem('bf_global_offline_demo_v7'),
  cards:[...document.querySelectorAll('#questlist button.questcard')].map((b,i)=>({
   missionId:QUESTS[i].missionId, summary:b.querySelector('small').textContent,
   locked:b.disabled})),
  quests:QUESTS.map(q=>[q.missionId,q.dungeonId,q.requires,q.battles,
   q.energy,q.exp,q.zel,q.karma]),
  detail:document.getElementById('questinfo').textContent
 })""")
 assert after['recoveredFrom']=='bf_global_offline_demo_v7'
 assert after['pending'] is False and after['issues']==0
 assert after['stored']==seeded, 'view changed stored v7 save'
 assert after['player']['version']==7
 for k in ('roster','squad','unitExp','materials','questClears','exp',
           'zel','karma','clears','lastMission'):
  assert after['player'][k]==legacy[k],k
 assert after['quests']==original['records']
 assert len(after['cards'])==106
 for q,card in zip(after['quests'],after['cards']):
  mid,dun,req,battles,energy,exp,zel,karma=q
  expect=f'{battles} battles · {exp} EXP · {zel} Zel · {karma} Karma · {energy} source Energy'
  if card['locked']:expect+=f' · Clear Mission {req} to unlock'
  assert card['missionId']==mid and card['summary']==expect,(mid,card,expect)
 assert any(c['locked'] for c in after['cards'])
 assert any(not c['locked'] for c in after['cards'])
 assert 'source Energy (not charged in demo)' in after['detail']
 assert not errors,errors[:3]
 browser.close()
print('PASS v205: 106 exact original quest card values; legacy v7 saved state unchanged')
