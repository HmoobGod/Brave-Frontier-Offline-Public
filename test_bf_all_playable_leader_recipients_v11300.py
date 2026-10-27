"""v113: 2022 source-verified type2 leader bonuses apply to all matching playable recipients.

CI-prepared game core only. Does not activate Spark, mitigation or compound
LEADER effects belonging to the recipients. Does not mutate persisted saves.
"""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf11300_all_playable_leader_recipients.js').read_text('utf8')
catalog=json.loads((R/'source_data/bf_global_2022_playable_leader_catalog_v112.json').read_text('utf8'))
assert catalog['totalForms']==72 and catalog['skillTypesCount']['2']==30
assert sum(x['skillTypeRaw']!='2' for x in catalog['rows'])==42
assert js.count('BF_GLOBAL_SOURCE_ALL_PLAYABLE_LEADER_RECIPIENTS_V11300')==1
assert 'const original=window.playerUnit' in js
assert 'String(original).includes' in js
assert "recipient.skillTypeRaw==='2'" in js
assert 'recipient.unimplementedRaw!==true' in js
assert 'recipientLeaderSkillActivated:false' in js
assert 'originalLeaderTypes31Or5Activated:false' in js
assert not any(x in js for x in [
    'saveProgress(', 'localStorage','P.squad=','P.roster=', 'S.party=',
    'S.enemies=', 'awardDemoRewards(', 'Math.random', 'fetch(', 'XMLHttpRequest',
    'window.reset=', 'window.enemyPhase='])
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf11200_all_playable_leader_source.js")')<java.index('readPackagedText("bf11300_all_playable_leader_recipients.js")')
core=(A/'index.html').read_text('utf8')
for signature in ['function playerUnit(i){','const uid=P.squad[i],src=uid?effectiveUnit(uid):null;',
                  'function reset(){selectSavedQuest();','party:Array.from({length:6},(_,i)=>playerUnit(i))']:
 assert signature in core
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
   executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
   args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda err:errors.append(str(err)))
 p.evaluate("""()=>{const db={};
 Object.defineProperty(window,'localStorage',{configurable:true,value:{
  getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
  removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
  get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve();}""")
 p.set_content(core,wait_until='load',timeout=90000)
 assert p.evaluate('P.version')==7
 assert p.evaluate('typeof window.playerUnit')=='function'
 assert p.evaluate('typeof window.reset')=='function'
 # Prepared v39 should contain all 72 playable original forms.
 for uid in (10011,10015,10021,10041,20021,60041):
  assert p.evaluate(f'UNIT_BY_ID.has({uid})') is True,uid
 original=p.evaluate("""()=>({
   p:JSON.stringify(P),stored:localStorage.getItem('bf_global_offline_demo_v7')
 })""")
 p.add_script_tag(path=str(A/'bf11000_source_starter_leader_skills.js'))
 p.add_script_tag(path=str(A/'bf11100_original_starter_leader_combat.js'))
 p.add_script_tag(path=str(A/'bf11200_all_playable_leader_source.js'))
 p.add_script_tag(path=str(A/'bf11300_all_playable_leader_recipients.js'))
 assert p.evaluate('BFGlobalPlayableLeadersV11200.snapshot().count')==72
 assert p.evaluate('BFGlobalAllLeaderRecipientsV11300.source.activatesUnknownLeaderSkills') is False
 assert p.locator('#bf11300-leader-recipients').count()==1
 for uid,skill in ((10021,'31'),(10041,'5'),(20021,'31'),(60041,'5')):
  assert p.evaluate(f'BFGlobalPlayableLeadersV11200.lookup({uid}).skillTypeRaw')==skill
 before=p.evaluate('JSON.stringify(P)')
 p.evaluate("""()=>{
   for(const id of [10021,10041,20021,60041])if(!P.roster.includes(id))P.roster.push(id);
   P.squad=[10011,10021,10041,20021,60041,40011];
   document.getElementById('mode').value='archive';
   reset();
 }""")
 def base(uid):
  return p.evaluate("""id=>{const src=effectiveUnit(id),grow=demoLevel(P.unitExp[id]??0)-1;
      return {atk:src.stats.atk+grow*12,hp:src.stats.hp+grow*30}}""",uid)
 units=p.evaluate('S.party.map(u=>({base:u.baseId,id:u.unitId,atk:u.atk,hp:u.hp,max:u.maxHp}))')
 for i in range(6):
  row=units[i]; ref=base(row['base'])
  if i<=2:
   assert row['atk']==ref['atk']*125//100,(i,row,ref)
  else:assert row['atk']==ref['atk'],(i,row,ref)
  assert row['hp']==row['max']==ref['hp']
 assert p.evaluate('BFGlobalStarterLeaderCombatV11100.snapshot().appliedPartyUnits')==1
 snap=p.evaluate('BFGlobalAllLeaderRecipientsV11300.snapshot()')
 assert snap['expandedRecipientCount']==2
 assert {x['unitId'] for x in snap['actualRows']}=={10021,10041}
 assert snap['originalLeaderTypes31Or5Activated'] is False
 first=p.evaluate('S.party.map(u=>[u.atk,u.hp,u.maxHp])')
 p.evaluate('reset()')
 assert p.evaluate('S.party.map(u=>[u.atk,u.hp,u.maxHp])')==first
 assert p.evaluate('BFGlobalAllLeaderRecipientsV11300.snapshot().expandedRecipientCount')==2
 p.evaluate('BFGlobalAllLeaderRecipientsV11300.apply(S.party[1],1)')
 assert p.evaluate('S.party[1].atk')==first[1][0] # no double bonus
 assert p.evaluate('BFGlobalAllLeaderRecipientsV11300.eligibility(10011,20021)') is None
 assert p.evaluate('BFGlobalAllLeaderRecipientsV11300.eligibility(10011,10011)') is None
 assert p.evaluate('BFGlobalAllLeaderRecipientsV11300.eligibility(10011,10021).atkPercent')==25
 # Higher tier type2 leader must boost ALL confirmed Fire recipients.
 p.evaluate('P.evolutions[10011]=10015;reset()')
 for i in range(3):
  unit=p.evaluate(f'S.party[{i}]')
  src=base(unit['baseId'])
  assert unit['atk']==src['atk']*150//100,(i,unit,src)
  assert unit['hp']==unit['maxHp']==src['hp']*110//100,(i,unit,src)
 assert p.evaluate('BFGlobalAllLeaderRecipientsV11300.snapshot().expandedRecipientCount')==2
 # Switching leader to a raw type31 must NOT activate its undecoded effects.
 p.evaluate('P.squad=[10021,10011,10041,20021,60041,40011];reset()')
 for row in p.evaluate('S.party'):
  src=base(row['baseId'])
  assert row['atk']==src['atk'] and row['maxHp']==src['hp']
 assert p.evaluate('BFGlobalAllLeaderRecipientsV11300.snapshot().expandedRecipientCount')==0
 assert p.evaluate('BFGlobalStarterLeaderCombatV11100.snapshot().appliedPartyUnits')==0
 # Training battle always remains unmodified, even with starter leader.
 p.evaluate("""()=>{P.squad=[10011,10021,10041,20021,60041,40011];
   document.getElementById('mode').value='training';reset();}""")
 for row in p.evaluate('S.party'):
  src=base(row['baseId'])
  assert row['atk']==src['atk'] and row['maxHp']==src['hp']
 assert p.evaluate('BFGlobalAllLeaderRecipientsV11300.snapshot().expandedRecipientCount')==0
 # Restore progress object to demonstrate no hidden writes to the original v7.
 p.evaluate("""state=>{const obj=JSON.parse(state);for(const k of Object.keys(P))delete P[k];
    Object.assign(P,obj);
    document.getElementById('mode').value='archive';reset();}""",before)
 assert p.evaluate('JSON.stringify(P)')==before
 assert p.evaluate('localStorage.getItem("bf_global_offline_demo_v7")')==original['stored']
 p.locator('#bf11300-leader-recipients').evaluate('(el)=>el.open=true')
 p.evaluate('BFGlobalAllLeaderRecipientsV11300.refresh()')
 assert p.locator('#bf11300-rows li').count()==0
 p.add_script_tag(path=str(A/'bf11300_all_playable_leader_recipients.js'))
 assert p.locator('#bf11300-leader-recipients').count()==1
 assert not errors,errors
 b.close()
print('PASS v113 original type2 leader buffs on 72 sourced elements, both raw recipient types, HP, restart, save, training')
