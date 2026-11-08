"""v105: optional advanced Smart Auto only, original defaults unchanged."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
js=(A/'bf10500_qol_advanced_smart_auto.js').read_text('utf8')
assert js.count('BF_GLOBAL_QOL_ADVANCED_SMART_AUTO_V10500')==1
assert len(js.encode())<65536
assert not any(t in js for t in ('saveProgress(', 'awardDemoRewards(', 'P.squad=', 'S.party=', 'S.enemies='))
assert 'window.BF041SmartAuto=freeze({...smart,kindFor})' in js
assert 'window.BF042AutoCoordination=freeze({...coordinated,chooseTarget})' in js
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""()=>{
   const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
     getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
     removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
     get length(){return Object.keys(db).length}}});
 }""")
 p.set_content("""<html><body><label id="bf041-smart-auto-label">
 <input id="bf041-smart-auto" type="checkbox" checked>Smart Support</label></body></html>""")
 p.evaluate("""()=>{
   window.P={version:7,roster:[10011,20011,30011],squad:[10011,20011,30011],questClears:{}};
   localStorage.setItem('bf_global_offline_demo_v7',JSON.stringify(P));
   window.__party105=[
     {unitId:20011,id:0,active:true,hp:50,maxHp:100,bb:100},
     {unitId:10011,id:1,active:true,hp:100,maxHp:100,bb:100},
     {unitId:30011,id:2,active:true,hp:100,maxHp:100,bb:100}
   ];
   window.liveParty=()=>__party105;
   window.bfOriginalBB=id=>id===20011?{target:'support'}:
     id===30011?{target:'support'}:{target:'single_enemy'};
   window.originalSupport=id=>id===20011?{kind:'heal_all'}:
     id===30011?{kind:'atk_buff_all',pct:30}:null;
   window.BF041SmartAuto={
     enabled:()=>document.getElementById('bf041-smart-auto').checked,
     kindFor:p=>p.bb>=100?'burst':'attack'
   };
   window.BF042AutoCoordination={
     enabled:()=>BF041SmartAuto.enabled(),
     chooseTarget:foes=>foes.slice().sort((a,b)=>a.hp/a.maxHp-b.hp/b.maxHp)[0],
     plan:party=>new Map(party.map(u=>[u,BF041SmartAuto.kindFor(u)]))
   };
 }""")
 saved=p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")
 p.add_script_tag(path=str(A/'bf10500_qol_advanced_smart_auto.js'))
 api='BFGlobalQoLAdvancedAutoV10500'
 assert p.evaluate(api+'.get().on') is False
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[0])')=='burst'
 foes=[{'hp':70,'maxHp':1000,'slot':0},{'hp':20,'maxHp':100,'slot':1}]
 assert p.evaluate("""foes=>BF042AutoCoordination.chooseTarget(foes).slot""",foes)==0
 settings={'on':True,'heal':35,'target':'absolute','burst':'conserve'}
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
 assert p.evaluate(api+'.active()') is True
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[0])')=='attack'
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[1])')=='attack'
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[2])')=='burst'
 assert p.evaluate("""foes=>BF042AutoCoordination.chooseTarget(foes).slot""",foes)==1
 # The base Smart Auto targets only living enemies with valid positive max HP.
 # Advanced absolute targeting must preserve that legality gate, not choose
 # a smaller apparent HP on an impossible maxHp/unknown enemy.
 for bad in [{'hp':1,'maxHp':0,'slot':0},
             {'hp':1,'maxHp':-10,'slot':0},
             {'hp':1,'slot':0}]:
  rows=[bad,{'hp':60,'maxHp':100,'slot':1}]
  assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",rows)==1
 assert p.evaluate("""()=>BF042AutoCoordination.chooseTarget([
   {hp:1,maxHp:0,slot:0},{hp:2,slot:1}])""") is None
 good=[{'hp':80,'maxHp':1000,'slot':0},{'hp':20,'maxHp':100,'slot':1}]
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",good)==1
 # Optional player strategies add visible demo enemy ATK/DEF priorities without
 # touching the original default, battle commands, save or enemy-owned AI.
 assert p.locator('#bf10500-target option').count()==5
 candidates=[
   {'hp':30,'maxHp':100,'slot':0,'atk':12,'def':99},
   {'hp':90,'maxHp':100,'slot':1,'atk':88,'def':51},
   {'hp':70,'maxHp':100,'slot':2,'atk':44,'def':7},
   {'hp':1,'maxHp':0,'slot':3,'atk':9999,'def':-100},
   {'hp':1,'maxHp':100,'slot':-1,'atk':9999,'def':-100},
   {'hp':1,'maxHp':100,'slot':4}
 ]
 settings['target']='highest-atk'
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",candidates)==1
 assert p.locator('#bf10500-target').input_value()=='highest-atk'
 # A corrupt living foe must not be silently skipped: its native slot
 # could collide with the chosen target. Reject the entire player Auto choice.
 for bad in [
   {'hp':5,'maxHp':0,'slot':3,'atk':999,'def':1},
   {'hp':5,'maxHp':100,'slot':-1,'atk':999,'def':1},
   {'hp':5,'maxHp':100,'slot':1,'atk':999,'def':1},
   {'hp':5,'maxHp':100,'slot':3,'atk':float('inf'),'def':1},
 ]:
  rows=[{'hp':70,'maxHp':100,'slot':1,'atk':50,'def':30},bad]
  if bad['atk']==float('inf'):
   # Invalid ranking stat alone excludes that candidate, not the valid foe.
   assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",rows)==1
  else:
   assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)""",rows) is None
 settings['target']='lowest-def'
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",candidates)==2
 # Elemental player Auto priority uses the real source-backed six-element
 # matchup API; its threat choice is team-wide and never guesses unknown types.
 p.evaluate("""()=>{window.S={mode:'archive',over:false,round:0,enemies:[]};
   window.UNIT_BY_ID=new Map([
     [10011,{element:'Fire'}],[20011,{element:'Water'}],
     [30011,{element:'Thunder'}]
   ]);
   __party105[0].unitId=10011;__party105[2].unitId=20011;
 }""")
 p.add_script_tag(path=str(A/'bf6900_elemental_combat.js'))
 assert p.evaluate('BFGlobalElementalCombatV6900.source.advantage')==1.5
 settings['target']='elemental'
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
 assert p.locator('#bf10500-target').input_value()=='elemental'
 typed_foes=[
   {'hp':80,'maxHp':100,'slot':0,'element':'Earth'},
   {'hp':5,'maxHp':100,'slot':1,'element':'Fire'},
   {'hp':1,'maxHp':100,'slot':2,'element':'Water'}]
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",typed_foes)==0
 # Ties favor lower remaining HP%, then native slot.
 same=[{'hp':50,'maxHp':500,'slot':5,'element':'Earth'},
       {'hp':10,'maxHp':100,'slot':2,'element':'Earth'}]
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",same)==2
 # Unknown foe types carry no invented weaknesses: use current baseline.
 unknown=[{'hp':10,'maxHp':100,'slot':0,'element':'Unknown'},
          {'hp':40,'maxHp':100,'slot':1}]
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",unknown)==0
 # Ambiguous live slots or invalid maximum HP are never auto-targeted.
 bad_elements=[{'hp':80,'maxHp':100,'slot':0,'element':'Earth'},
               {'hp':5,'maxHp':100,'slot':0,'element':'Fire'}]
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)""",bad_elements) is None
 bad_elements[1]['slot']=1
 bad_elements[1]['maxHp']=0
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)""",bad_elements) is None
 p.evaluate("""()=>{__party105[0].unitId=20011;__party105[2].unitId=30011;}""")
 settings['target']='lowest-def'
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
 # Player Auto Guard is optional; test source-safe live battler identity,
 # archive Auto ownership, exact health threshold, and saved v7 isolation.
 settings['guard']=35
 # Keep BB conservation disabled here so the non-Guard fallback is Burst.
 settings['burst']='normal'
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
 assert p.locator('#bf10500-guard option').count()==4
 assert p.evaluate(api+'.get().guard')==35
 assert p.evaluate("""()=>JSON.parse(localStorage.getItem(
   'bf_global_offline_qol_advanced_auto_v105')).guard""")==35
 p.evaluate("""()=>{S.party=__party105;S.auto=true;S.mode='archive';S.over=false;
    __party105[1].hp=35;__party105[1].maxHp=100;}""")
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[1])')=='guard'
 assert p.evaluate('BF041SmartAuto.kindFor({...__party105[1]})')=='burst'
 p.evaluate('S.auto=false')
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[1])')=='burst'
 p.evaluate("""()=>{S.auto=true;S.mode='training'}""")
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[1])')=='burst'
 p.evaluate("""()=>{S.mode='archive';__party105[1].hp=36}""")
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[1])')=='burst'
 p.evaluate('__party105[1].hp=35;__party105[1].maxHp=0')
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[1])')=='burst'
 p.evaluate('__party105[1].maxHp=100')
 settings['guard']=999
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is False
 assert p.evaluate(api+'.get().guard')==35
 settings['guard']=0
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[1])')=='burst'
 p.evaluate("""()=>{S.auto=false;__party105[1].hp=100}""")
 # Source-backed quest final-wave offensive BB conservation. Support buffs
 # remain available in earlier waves, and unknown quest data never invents
 # a boss wave or changes existing kindFor decisions.
 settings['burst']='final-wave'
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
 assert p.locator('#bf10500-burst option').count()==3
 p.evaluate("""()=>{window.QUESTS=[{missionId:1,battles:3}];QUEST=QUESTS[0];
   S.party=__party105;S.wave=0;S.mode='archive';S.over=false;S.auto=true;}""")
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[1])')=='attack'
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[2])')=='burst'
 p.evaluate('S.wave=1')
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[1])')=='attack'
 p.evaluate('S.wave=2')
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[1])')=='burst'
 p.evaluate('S.wave=3')
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[1])')=='burst'
 p.evaluate("""()=>{S.wave=0;QUEST={missionId:99,battles:3}}""")
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[1])')=='burst'
 p.evaluate("""()=>{QUEST=QUESTS[0];S.mode='training'}""")
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[1])')=='burst'
 p.evaluate("""()=>{S.mode='archive';S.auto=false}""")
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[1])')=='burst'
 p.evaluate('S.auto=true')
 assert p.evaluate('BF041SmartAuto.kindFor({...__party105[1]})')=='burst'
 p.evaluate('S.auto=false')
 settings['burst']='normal'
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
 # Missing target statistics and impossible enemy records fail closed.
 invalid=[{'hp':1,'maxHp':0,'slot':0,'atk':500,'def':-40},
          {'hp':8,'maxHp':10,'slot':-1,'atk':500,'def':-40},
          {'hp':3,'maxHp':10,'slot':2}]
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)""",invalid) is None
 settings['target']='highest-atk'
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)""",invalid) is None
 settings['target']='invalid-priority'
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is False
 assert p.evaluate('BFGlobalQoLAdvancedAutoV10500.get().target')=='highest-atk'
 settings['target']='percent'
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",good)==0
 settings['heal']=75
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[0])')=='burst'
 p.locator('#bf041-smart-auto').uncheck()
 assert p.evaluate(api+'.active()') is False
 assert p.evaluate('BF041SmartAuto.kindFor(__party105[1])')=='burst'
 assert p.evaluate("localStorage.getItem('bf_global_offline_demo_v7')")==saved
 assert p.evaluate("JSON.parse(localStorage.getItem('bf_global_offline_qol_advanced_auto_v105')).on") is None
 p.add_script_tag(path=str(A/'bf10500_qol_advanced_smart_auto.js'))
 assert p.locator('#bf10500-auto-settings').count()==1
 assert not errors,errors
 b.close()
print('PASS v105 Smart Auto defaults, low-HP Guard, final-wave offensive BB, heal, elemental targeting and v7 isolation')

# Exercise optional SBB planning through actual Auto turns.
if __name__ == "__main__":
 import subprocess,sys
 subprocess.run([sys.executable,str(R/"test_bf_auto_sbb_demo.py")],check=True)
