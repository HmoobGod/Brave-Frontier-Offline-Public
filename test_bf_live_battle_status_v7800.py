"""v78 live battle statuses: source ailment indicators, Nullifier, Regen, privacy and save isolation."""
from pathlib import Path
import ast,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf7800_live_battle_status.js').read_text('utf8')
assert js.count('BF_GLOBAL_LIVE_BATTLE_STATUS_V7800')==1
assert len(js.encode('utf8'))<65536
assert 'min-height:44px' in js
assert 'Number.isFinite(unit.hp)' in js and 'Number.isFinite(unit.maxHp)' in js
assert 'DEMO HP ' in js
assert 'Number.isSafeInteger(S.round)' in js
assert 'validDeadline(immuneState.expiresAfterRound)' in js
assert 'validDeadline(regenState.untilRound)' in js
assert all(t not in js for t in ('localStorage','saveProgress(', 'BFAndroid'))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf7700_original_party_regen.js")')<java.index('readPackagedText("bf7800_live_battle_status.js")')
tree=ast.parse((R/'test_bf_status_reinfliction_v6300.py').read_text('utf8'))
names=next(ast.literal_eval(f.iter) for f in ast.walk(tree)
 if isinstance(f,ast.For) and isinstance(f.target,ast.Name) and f.target.id=='name'
 and isinstance(f.iter,ast.Tuple))
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,
 executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
 args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844});errors=[]
 p.on('pageerror',lambda x:errors.append(str(x)))
 p.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
 removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
 get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 p.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 p.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in names:p.add_script_tag(path=str(A/name))
 for name in ('bf6400_status_remedy_command.js','bf6500_sickness_recovery.js',
              'bf7500_original_saint_light.js','bf7600_original_status_nullifier.js',
              'bf7700_original_party_regen.js'):
  p.add_script_tag(path=str(A/name))
 # v458: transparent browser-only wrappers expose malformed provider
 # fixtures to the exact module instance captured on script load.
 p.evaluate("""()=>{
   const control={};window.__v458StatusFaults=control;
   const ailments=window.BFGlobalOriginalAilmentStateV5700;
   const immune=window.BFGlobalStatusNegationV7600;
   const regen=window.BFGlobalOriginalPartyRegenV7700;
   const guarded=(real,key)=>({...real,snapshot:()=>{
     if(control[key]==='THROW')throw Error('v458 provider unavailable');
     return Object.prototype.hasOwnProperty.call(control,key)?
       control[key]:real.snapshot();
   }});
   window.BFGlobalStatusNegationV7600=guarded(immune,'immune');
   window.BFGlobalOriginalPartyRegenV7700=guarded(regen,'regen');
   window.BFGlobalOriginalAilmentStateV5700={...ailments,codesFor:slot=>{
     if(control.codes==='THROW')throw Error('v458 codes unavailable');
     return Object.prototype.hasOwnProperty.call(control,'codes')?
       control.codes:ailments.codesFor(slot);
   }};
 }""")
 p.add_script_tag(path=str(A/'bf7800_live_battle_status.js'))
 p.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert p.evaluate('P.version')==7
 assert p.evaluate('BFGlobalLiveBattleStatusV7800.snapshot().visible') is False
 assert p.locator('#bf7800-status').is_hidden()
 assert p.evaluate("document.getElementById('bf7800-status').parentElement.tagName")!='CANVAS'
 before=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
 progress:JSON.stringify(P),hp:S.party.map(u=>u.hp)})""")
 registry='BFGlobalOriginalAilmentStateV5700'
 for code in (1,2,3,4,5,6):
  assert p.evaluate(f'{registry}.inflict(0,{code})') is True
 state=p.evaluate('BFGlobalLiveBattleStatusV7800.refresh()')
 assert state['visible'] and len(state['units'])==1
 # Only a real finite, in-range live ally HP pair may appear in the read-only UI.
 health=p.evaluate('''() => {
   const unit=S.party[0], hp=unit.hp, maxHp=unit.maxHp;
   const oldSave=localStorage.getItem('bf_global_offline_demo_v7');
   let nan, maxZero, overheal;
   try {
     unit.hp=NaN;nan=BFGlobalLiveBattleStatusV7800.refresh().visible;
     unit.hp=hp;unit.maxHp=0;
     maxZero=BFGlobalLiveBattleStatusV7800.refresh().visible;
     unit.maxHp=maxHp;unit.hp=maxHp+1;
     overheal=BFGlobalLiveBattleStatusV7800.refresh().visible;
   } finally {
     unit.hp=hp;unit.maxHp=maxHp;
     BFGlobalLiveBattleStatusV7800.refresh();
   }
   return {nan,maxZero,overheal,unchangedSave:
     localStorage.getItem('bf_global_offline_demo_v7')===oldSave};
 }''')
 assert health=={'nan':False,'maxZero':False,'overheal':False,'unchangedSave':True},health
 ally=state['units'][0]
 assert ally['codes']==[1,2,3,4,5,6]
 assert ally['actionBlocked'] and ally['bbBlocked']
 p.locator('#bf7800-status summary').click()
 for width in (320,390,540):
  p.set_viewport_size({'width':width,'height':844})
  box=p.locator('#bf7800-status summary').bounding_box()
  assert box and box['height']>=44,(width,box)
 content=p.locator('#bf7800-status').inner_text()
 demo_hp=p.evaluate('Math.round(S.party[0].hp)+"/"+Math.round(S.party[0].maxHp)')
 assert 'DEMO HP '+demo_hp in content,content
 for word in ('Poison','Weakness','Sickness','Injury','Curse','Paralysis'):
  assert word in content
 assert p.evaluate(f'{registry}.cure(0,20230).removed')==[6]
 assert p.evaluate(f'{registry}.cure(0,20220).removed')==[5]
 ally=p.evaluate('BFGlobalLiveBattleStatusV7800.snapshot().units[0]')
 assert ally['codes']==[1,2,3,4]
 assert not ally['actionBlocked'] and not ally['bbBlocked']
 assert p.evaluate(f'{registry}.cure(0,50200).removed')==[1,2,3,4]
 assert p.evaluate('BFGlobalLiveBattleStatusV7800.refresh().visible') is False
 assert p.evaluate('BFGlobalOriginalPartyRegenV7700.useRegeneration(2)') is True
 assert p.evaluate('BFGlobalStatusNegationV7600.useNullifier(3)') is True
 state=p.evaluate('BFGlobalLiveBattleStatusV7800.refresh()')
 assert state['visible'] and len(state['units'])>=4
 assert all(u['immune'] and u['regeneration'] for u in state['units'])
 assert all(u['immunityTurns']==3 and u['regenerationTurns']==3 for u in state['units'])
 # Invalid round values or malformed/throwing optional source providers must
 # hide unknown status lifetimes rather than render NaN or break the timer.
 before_faults=p.evaluate("""()=>({
   p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7'),
   s:JSON.stringify(S),round:S.round
 })""")
 bad_rounds=p.evaluate("""()=>{
   const saved=S.round,out={};
   try{
     for(const [key,value] of [
       ['negative',-1],['fraction',1.5],['string','2'],
       ['nan',NaN],['infinity',Infinity],['unsafe',Number.MAX_SAFE_INTEGER+1]
     ]){
       S.round=value;
       const state=BFGlobalLiveBattleStatusV7800.refresh();
       out[key]={visible:state.visible,hidden:document.getElementById('bf7800-status').hidden};
     }
   }finally{S.round=saved;BFGlobalLiveBattleStatusV7800.refresh();}
   return out;
 }""")
 assert all(not row['visible'] and row['hidden'] for row in bad_rounds.values()),bad_rounds
 fixtures=p.evaluate("""()=>{
   const faults=window.__v458StatusFaults,out={};
   const bad=[
     ['immuneNull','immune',null],['immuneEmpty','immune',{}],
     ['immuneThrown','immune','THROW'],
     ['immuneDeadline','immune',{protectedSlots:[0],expiresAfterRound:NaN}],
     ['regenNull','regen',null],['regenEmpty','regen',{}],
     ['regenThrown','regen','THROW'],
     ['regenDeadline','regen',{active:true,targetSlots:[0],untilRound:Infinity}],
     ['regenActiveString','regen',{active:'false',targetSlots:[],untilRound:null}],
     ['codesInvalid','codes',[99]],['codesType','codes','Poison'],
     ['codesThrown','codes','THROW']
   ];
   for(const [label,key,value] of bad){
     try{
       faults[key]=value;
       const s=BFGlobalLiveBattleStatusV7800.refresh();
       out[label]={visible:s.visible,hidden:document.getElementById('bf7800-status').hidden};
     }finally{delete faults[key];BFGlobalLiveBattleStatusV7800.refresh();}
   }
   return out;
 }""")
 assert all(not row['visible'] and row['hidden'] for row in fixtures.values()),fixtures
 assert p.evaluate('BFGlobalLiveBattleStatusV7800.refresh().visible') is True
 assert p.evaluate("""()=>({
   p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7'),
   s:JSON.stringify(S),round:S.round
 })""")==before_faults
 assert p.evaluate('BFGlobalOriginalAilmentStateV5700.inflict(0,1)') is False
 p.evaluate('S.round++')
 state=p.evaluate('BFGlobalLiveBattleStatusV7800.refresh()')
 assert all(u['immunityTurns']==2 and u['regenerationTurns']==2 for u in state['units'])
 p.evaluate('S.round+=3')
 assert p.evaluate('BFGlobalLiveBattleStatusV7800.refresh().visible') is False
 assert p.locator('#bf7800-status').is_hidden()
 after=p.evaluate("""()=>({save:localStorage.getItem('bf_global_offline_demo_v7'),
 progress:JSON.stringify(P),hp:S.party.map(u=>u.hp)})""")
 assert before==after,(before,after)
 p.locator('#mode').select_option('training')
 assert p.evaluate('BFGlobalLiveBattleStatusV7800.snapshot().visible') is False
 p.locator('#mode').select_option('archive')
 p.locator('#reset').click()
 assert p.evaluate('BFGlobalLiveBattleStatusV7800.snapshot().visible') is False
 p.add_script_tag(path=str(A/'bf7800_live_battle_status.js'))
 assert p.locator('#bf7800-status').count()==1
 assert not errors,errors
 b.close()
print('PASS v78 live status readout displays all six ailment effects, immunity and regen countdown, KO/mode/reset/save safe')
