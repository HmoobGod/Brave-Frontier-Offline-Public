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
   // Simulate the actual native player Auto ownership for kindFor overrides.
   window.S={mode:'archive',auto:true,over:false,party:__party105,wave:0};
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
 # Player-owned source BB/support queries must not interrupt native Auto
 # when the optional record provider or team-health helper throws.
 provider_failures=p.evaluate("""()=>{
   const originalBB=window.bfOriginalBB,originalSupport=window.originalSupport,
     originalParty=window.liveParty,beforeTarget=S.target,
     beforeActions=__party105.map(x=>JSON.stringify(x.action)),
     beforePlayer=JSON.stringify(P),
     beforeSave=localStorage.getItem('bf_global_offline_demo_v7');
   let badBB, badSupport, badParty, recovered;
   try{
     window.bfOriginalBB=()=>{throw Error('BB table unavailable')};
     badBB=BF041SmartAuto.kindFor(__party105[1]);
     window.bfOriginalBB=originalBB;
     window.originalSupport=()=>{throw Error('support table unavailable')};
     badSupport=BF041SmartAuto.kindFor(__party105[0]);
     window.originalSupport=originalSupport;
     window.liveParty=()=>{throw Error('team health unavailable')};
     badParty=BF041SmartAuto.kindFor(__party105[0]);
   }finally{
     window.bfOriginalBB=originalBB;
     window.originalSupport=originalSupport;
     window.liveParty=originalParty;
   }
   recovered=BF041SmartAuto.kindFor(__party105[0]);
   return {badBB,badSupport,badParty,recovered,
     targetSame:S.target===beforeTarget,
     ordersSame:__party105.every((x,i)=>JSON.stringify(x.action)===beforeActions[i]),
     playerSame:JSON.stringify(P)===beforePlayer,
     saveSame:localStorage.getItem('bf_global_offline_demo_v7')===beforeSave};
 }""")
 assert provider_failures=={'badBB':'burst','badSupport':'burst',
   'badParty':'burst','recovered':'attack','targetSame':True,
   'ordersSame':True,'playerSame':True,'saveSame':True},provider_failures
 # Optional targeting must not override the baseline in manual play,
 # training, or a completed fight. Selected-target mode already has its
 # separate fail-closed null policy and is covered below.
 turn_scopes=p.evaluate("""rows=>{const old={auto:S.auto,mode:S.mode,over:S.over};
   try{
     S.auto=false;S.mode='archive';S.over=false;
     const manual=BF042AutoCoordination.chooseTarget(rows)?.slot;
     S.auto=true;S.mode='training';
     const training=BF042AutoCoordination.chooseTarget(rows)?.slot;
     S.mode='archive';S.over=true;
     const finished=BF042AutoCoordination.chooseTarget(rows)?.slot;
     S.over=false;
     const playerAuto=BF042AutoCoordination.chooseTarget(rows)?.slot;
     return {manual,training,finished,playerAuto};
   }finally{S.auto=old.auto;S.mode=old.mode;S.over=old.over;}
 }""",foes)
 assert turn_scopes=={'manual':0,'training':0,'finished':0,'playerAuto':1},turn_scopes
 # The base Smart Auto targets only living enemies with valid positive max HP.
 # Advanced absolute targeting must preserve that legality gate, not choose
 # a smaller apparent HP on an impossible maxHp/unknown enemy.
 for bad in [{'hp':1,'maxHp':0,'slot':0},
             {'hp':1,'maxHp':-10,'slot':0},
             {'hp':1,'slot':0}]:
  rows=[bad,{'hp':60,'maxHp':100,'slot':1}]
  assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)""",rows) is None
 assert p.evaluate("""()=>BF042AutoCoordination.chooseTarget([
   {hp:1,maxHp:0,slot:0},{hp:2,slot:1}])""") is None
 good=[{'hp':80,'maxHp':1000,'slot':0},{'hp':20,'maxHp':100,'slot':1}]
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",good)==1
 # Optional player strategies add visible demo enemy ATK/DEF priorities without
 # touching the original default, battle commands, save or enemy-owned AI.
 assert p.locator('#bf10500-target option').count()==8
 candidates=[
   {'hp':30,'maxHp':100,'slot':0,'atk':12,'def':99},
   {'hp':90,'maxHp':100,'slot':1,'atk':88,'def':51},
   {'hp':70,'maxHp':100,'slot':2,'atk':44,'def':7},
    {'hp':1,'maxHp':100,'slot':4,'atk':15,'def':82}
 ]
 settings['target']='highest-atk'
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",candidates)==1
 assert p.locator('#bf10500-target').input_value()=='highest-atk'
 # For stat-based optional target modes, the whole living foe roster
 # must contain valid native ATK/DEF; skipping a missing stat is unsafe.
 # A single unknown foe cannot be silently omitted from target ranking.
 for target_mode in ('highest-atk','lowest-def'):
  settings['target']=target_mode
  assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
  for invalid in ('missing','string-infinity','nan','null'):
   result=p.evaluate("""({rows,mode,variant})=>{
     const copy=rows.map(x=>({...x})),key=mode==='highest-atk'?'atk':'def';
     if(variant==='missing')delete copy[3][key];
     else if(variant==='string-infinity')copy[3][key]='Infinity';
     else if(variant==='nan')copy[3][key]=NaN;
     else copy[3][key]=null;
     return BF042AutoCoordination.chooseTarget(copy);
   }""",{'rows':candidates,'mode':target_mode,'variant':invalid})
   assert result is None,(target_mode,invalid)
  assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",
    candidates)==(1 if target_mode=='highest-atk' else 2)
 settings['target']='highest-atk'
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
 # A corrupt living foe must not be silently skipped: its native slot
 # could collide with the chosen target. Reject the entire player Auto choice.
 for bad in [
   {'hp':5,'maxHp':0,'slot':3,'atk':999,'def':1},
   {'hp':5,'maxHp':100,'slot':-1,'atk':999,'def':1},
   {'hp':5,'maxHp':100,'slot':1,'atk':999,'def':1},
  ]:
  rows=[{'hp':70,'maxHp':100,'slot':1,'atk':50,'def':30},bad]
  assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)""",rows) is None
 settings['target']='lowest-def'
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",candidates)==2
 # New opt-in boss-focused choices have distinct absolute and relative HP
 # semantics. Both use native slots; ties prefer the lower original slot.
 hp_choices=[
   {'hp':500,'maxHp':1000,'slot':5,'atk':60,'def':80},
   {'hp':80,'maxHp':100,'slot':2,'atk':20,'def':40},
   {'hp':150,'maxHp':200,'slot':7,'atk':100,'def':20}
 ]
 settings['target']='highest-hp'
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",hp_choices)==5
 assert p.locator('#bf10500-target').input_value()=='highest-hp'
 assert p.evaluate("""()=>JSON.parse(localStorage.getItem(
   'bf_global_offline_qol_advanced_auto_v105')).target""")=='highest-hp'
 # Open the native settings disclosure before exercising the *visible*
 # player select control. Playwright must not click a collapsed <details>.
 p.locator('#bf10500-auto-settings summary').click()
 assert p.locator('#bf10500-auto-settings').get_attribute('open') is not None
 p.locator('#bf10500-target').select_option('highest-hp-percent')
 assert p.evaluate(api+'.get().target')=='highest-hp-percent'
 settings['target']='highest-hp-percent'
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",hp_choices)==2
 tied=[{'hp':80,'maxHp':100,'slot':5},
       {'hp':40,'maxHp':50,'slot':2}]
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",tied)==2
 for high_priority in ('highest-hp','highest-hp-percent'):
  settings['target']=high_priority
  assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
  # Corrupt living foe data must block targeting rather than discarding a
  # badly typed, duplicate, or otherwise ambiguous native enemy slot.
  for malformed in ('numeric-infinity','string-infinity','zero-max','duplicate-slot'):
   outcome=p.evaluate("""({rows,variant})=>{
     const bad=variant==='numeric-infinity'?{hp:Infinity,maxHp:100,slot:9}:
       variant==='string-infinity'?{hp:'Infinity',maxHp:100,slot:9}:
       variant==='zero-max'?{hp:4,maxHp:0,slot:9}:
       {hp:4,maxHp:10,slot:2};
     return BF042AutoCoordination.chooseTarget([bad,...rows]);
   }""",{'rows':hp_choices,'variant':malformed})
   assert outcome is None,(high_priority,malformed)
  assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",hp_choices)==(5 if high_priority=='highest-hp' else 2)
 # Player-selected Auto priority should follow the original native selected
 # enemy slot only while source-owned Auto combat is live. Stale or corrupt
 # targets fail closed rather than sending a command to a different foe.
 settings['target']='selected'
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
 p.locator('#bf10500-target').select_option('selected')
 assert p.evaluate(api+'.get().target')=='selected'
 assert p.evaluate("""()=>JSON.parse(localStorage.getItem(
   'bf_global_offline_qol_advanced_auto_v105')).target""")=='selected'
 selected_foes=[
   {'slot':0,'hp':90,'maxHp':100},
   {'slot':1,'hp':10,'maxHp':100},
   {'slot':2,'hp':80,'maxHp':100}
 ]
 p.evaluate("""()=>{window.S={mode:'archive',over:false,auto:true,target:2,round:1};}""")
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",selected_foes)==2
 p.evaluate('S.target=0')
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",selected_foes)==0
 p.evaluate('S.target=9')
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)""",selected_foes) is None
 p.evaluate('S.target=-1')
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)""",selected_foes) is None
 p.evaluate("""()=>{S.target=2;S.auto=false}""")
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)""",selected_foes) is None
 p.evaluate("""()=>{S.auto=true;S.mode='training'}""")
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)""",selected_foes) is None
 p.evaluate("""()=>{S.mode='archive';S.over=true}""")
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)""",selected_foes) is None
 p.evaluate('S.over=false')
 for bad in ('numeric-infinity','string-infinity','bad-max','duplicate-slot'):
  rejected=p.evaluate("""({rows,variant})=>{
    const invalid=variant==='numeric-infinity'?{slot:5,hp:Infinity,maxHp:100}:
      variant==='string-infinity'?{slot:5,hp:'Infinity',maxHp:100}:
      variant==='bad-max'?{slot:5,hp:10,maxHp:0}:
      {slot:2,hp:10,maxHp:100};
    return BF042AutoCoordination.chooseTarget([...rows,invalid]);
  }""",{'rows':selected_foes,'variant':bad})
  assert rejected is None,bad
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",selected_foes)==2
 # If the chosen enemy is KO'd, never silently retarget another living foe.
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)""",
   [{'slot':0,'hp':90,'maxHp':100},
    {'slot':1,'hp':10,'maxHp':100},
    {'slot':2,'hp':0,'maxHp':100}]) is None
 # Native scheduler strictness: any opt-in advanced choice that returns
 # no legal target must not be replaced by the legacy absolute-HP fallback.
 assert p.evaluate(api+'.requiresValidatedTarget()') is True
 settings['target']='percent'
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
 assert p.evaluate(api+'.requiresValidatedTarget()') is False
 settings['target']='absolute'
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
 assert p.evaluate(api+'.requiresSelectedTarget()') is False
 assert p.evaluate(api+'.requiresValidatedTarget()') is True
 settings['target']='lowest-def'
 assert p.evaluate("""opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)""",settings) is True
 # Elemental player Auto priority uses the real source-backed six-element
 # matchup API; its threat choice is team-wide and never guesses unknown types.
 p.evaluate("""()=>{window.S={mode:'archive',auto:true,over:false,round:0,enemies:[]};
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
 # Source-backed elemental fallback should not blindly select a heavily
 # resisted low-HP foe when NO squad member can exploit a weakness.
 # Player squad: Fire, Fire, Water. Water resists both Fire attacks;
 # Thunder resists the Water attack but is neutral against both Fire attacks.
 no_weakness=[
   {'hp':1,'maxHp':100,'slot':0,'element':'Water'},
   {'hp':95,'maxHp':100,'slot':1,'element':'Thunder'}
 ]
 before_source_fallback=p.evaluate("""()=>({
   player:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7'),
   target:S.target,actions:__party105.map(x=>JSON.stringify(x.action))
 })""")
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",no_weakness)==1
 # If any enemy element is unknown, no resistance-based ranking is
 # authorized: preserve the existing lowest HP% target exactly.
 unknown_opponent=[
   {'hp':1,'maxHp':100,'slot':0,'element':'Water'},
   {'hp':95,'maxHp':100,'slot':1,'element':'Unknown'}
 ]
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",unknown_opponent)==0
 # Missing ally source identity makes team-wide resistance counts uncertain.
 p.evaluate('__party105[2].unitId=999999')
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",no_weakness)==0
 # An unknown ally must NOT erase a separately verified advantage:
 # two known Fire allies still favor Earth despite a lower-HP Water foe.
 unknown_ally_but_advantage=[
   {'hp':1,'maxHp':100,'slot':0,'element':'Water'},
   {'hp':80,'maxHp':100,'slot':1,'element':'Earth'}
 ]
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",
                   unknown_ally_but_advantage)==1
 p.evaluate('__party105[2].unitId=20011')
 # Equal resistance counts and equal HP percentages must preserve the
 # native baseline tie-break of lower ABSOLUTE HP before native slot.
 for element_name in ('Water','Earth'):
  equal_ratio=[
    {'hp':50,'maxHp':100,'slot':0,'element':element_name},
    {'hp':5,'maxHp':10,'slot':7,'element':element_name}
  ]
  assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",
                    equal_ratio)==7,element_name
 # Equal advantage counts prefer fewer resisted allied elements, rather
 # than mistaking the smallest DEMO HP percentage for the best matchup.
 p.evaluate('__party105[1].unitId=30011')
 tied_advantage=[
   {'hp':1,'maxHp':100,'slot':0,'element':'Earth'},
   {'hp':80,'maxHp':100,'slot':1,'element':'Fire'}
 ]
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",tied_advantage)==1
 p.evaluate('__party105[1].unitId=10011')
 # A provider returning a non-source multiplier cannot authorize an
 # Auto target, and its failure must not change live player actions.
 invalid_matchup=p.evaluate("""rows=>{
   const old=BFGlobalElementalCombatV6900;
   try{
     BFGlobalElementalCombatV6900={normalize:old.normalize,multiplier:()=>2};
     return BF042AutoCoordination.chooseTarget(rows);
   }finally{BFGlobalElementalCombatV6900=old}
 }""",no_weakness)
 assert invalid_matchup is None
 after_source_fallback=p.evaluate("""()=>({
   player:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7'),
   target:S.target,actions:__party105.map(x=>JSON.stringify(x.action))
 })""")
 assert before_source_fallback==after_source_fallback
 # Bad optional source helpers must not crash the player's live Auto turn,
 # silently guess a legacy HP% target, or change orders/canonical v7 bytes.
 source_failures=p.evaluate("""rows=>{
   const original=window.BFGlobalElementalCombatV6900,
     before=localStorage.getItem('bf_global_offline_demo_v7'),
     player=JSON.stringify(P),selected=S.target,
     orders=__party105.map(u=>JSON.stringify(u.action));
   const providers=[
     {normalize:()=>{throw Error('ally type unavailable')},
       multiplier:original.multiplier},
     {normalize:value=>{if(value==='Earth')throw Error('foe type unavailable');
       return original.normalize(value);},multiplier:original.multiplier},
     {normalize:original.normalize,
       multiplier:()=>{throw Error('weakness unavailable')}},
     Object.defineProperty({multiplier:original.multiplier},'normalize',
       {get(){throw Error('source property unavailable')}})
   ];
   const rejected=[];
   try{
     for(const provider of providers){
       window.BFGlobalElementalCombatV6900=provider;
       rejected.push(BF042AutoCoordination.chooseTarget(rows)===null);
     }
   }finally{window.BFGlobalElementalCombatV6900=original}
   return {rejected,normalRecovered:BF042AutoCoordination.chooseTarget(rows)?.slot===0,
     targetSame:S.target===selected,
     ordersSame:__party105.every((u,i)=>JSON.stringify(u.action)===orders[i]),
     playerSame:JSON.stringify(P)===player,
     saveSame:localStorage.getItem('bf_global_offline_demo_v7')===before,
     strictTarget:BFGlobalQoLAdvancedAutoV10500.requiresValidatedTarget()};
 }""",typed_foes)
 assert source_failures=={'rejected':[True]*4,'normalRecovered':True,
   'targetSame':True,'ordersSame':True,'playerSame':True,'saveSame':True,
   'strictTarget':True},source_failures
 # Ties favor lower remaining HP%, then native slot.
 same=[{'hp':50,'maxHp':500,'slot':5,'element':'Earth'},
       {'hp':10,'maxHp':100,'slot':2,'element':'Earth'}]
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",same)==2
 # Unknown foe types carry no invented weaknesses: use current baseline.
 unknown=[{'hp':10,'maxHp':100,'slot':0,'element':'Unknown'},
          {'hp':40,'maxHp':100,'slot':1}]
 assert p.evaluate("""rows=>BF042AutoCoordination.chooseTarget(rows)?.slot""",unknown)==0
 # Malformed positive HP cannot be silently dropped from elemental target roster.
 # Numeric Infinity and coercible string Infinity both invalidate selection.
 for malformed in ('number','string'):
  if malformed=='number':
   choice=p.evaluate("""()=>BF042AutoCoordination.chooseTarget([
     {hp:Infinity,maxHp:100,slot:2,element:'Fire'},
     {hp:80,maxHp:100,slot:0,element:'Earth'}])""")
  else:
   choice=p.evaluate("""()=>BF042AutoCoordination.chooseTarget([
     {hp:'Infinity',maxHp:100,slot:2,element:'Unknown'},
     {hp:80,maxHp:100,slot:0,element:'Unknown'}])""")
  assert choice is None,malformed
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
 # Broken optional paralysis/Curse providers may not crash player Auto,
 # guess Guard under unknown paralysis, or authorize a BB under unknown Curse.
 status_failures=p.evaluate("""()=>{
   const paralysis=window.BFGlobalParalysisActionLockV6000,
     curse=window.BFGlobalCurseBBLockV5900,
     actor=__party105[1], hp=actor.hp,
     nativeTarget=S.target,
     orders=__party105.map(u=>JSON.stringify(u.action)),
     beforePlayer=JSON.stringify(P),
     beforeSave=localStorage.getItem('bf_global_offline_demo_v7');
   let paralyzedThrows,paralyzedGetterThrows,paralyzedTrue,paralyzedFalse,
     cursedThrows,cursedGetterThrows,cursedTrue,cursedFalse,cloneBaseline,recovered;
   try{
     window.BFGlobalParalysisActionLockV6000={
       paralyzed:()=>{throw Error('paralysis service missing')},
     };
     paralyzedThrows=BF041SmartAuto.kindFor(actor);
     window.BFGlobalParalysisActionLockV6000=Object.defineProperty({},'paralyzed',
       {get(){throw Error('paralysis getter unavailable')}});
     paralyzedGetterThrows=BF041SmartAuto.kindFor(actor);
     // A cloned actor must never consult optional player status providers.
     window.BFGlobalCurseBBLockV5900={
       cursed:()=>{throw Error('curse service missing')},
     };
     cloneBaseline=BF041SmartAuto.kindFor({...actor});
     window.BFGlobalParalysisActionLockV6000={paralyzed:()=>true};
     window.BFGlobalCurseBBLockV5900={cursed:()=>false};
     paralyzedTrue=BF041SmartAuto.kindFor(actor);
     window.BFGlobalParalysisActionLockV6000={paralyzed:()=>false};
     paralyzedFalse=BF041SmartAuto.kindFor(actor);
     actor.hp=100; // leave Guard threshold, reach Curse branch
     window.BFGlobalCurseBBLockV5900={
       cursed:()=>{throw Error('curse service missing')},
     };
     cursedThrows=BF041SmartAuto.kindFor(actor);
     window.BFGlobalCurseBBLockV5900=Object.defineProperty({},'cursed',
       {get(){throw Error('curse getter unavailable')}});
     cursedGetterThrows=BF041SmartAuto.kindFor(actor);
     window.BFGlobalCurseBBLockV5900={cursed:()=>true};
     cursedTrue=BF041SmartAuto.kindFor(actor);
     window.BFGlobalCurseBBLockV5900={cursed:()=>false};
     cursedFalse=BF041SmartAuto.kindFor(actor);
   }finally{
     actor.hp=hp;
     window.BFGlobalParalysisActionLockV6000=paralysis;
     window.BFGlobalCurseBBLockV5900=curse;
   }
   recovered=BF041SmartAuto.kindFor(actor);
   return {paralyzedThrows,paralyzedGetterThrows,paralyzedTrue,paralyzedFalse,
     cursedThrows,cursedGetterThrows,cursedTrue,cursedFalse,cloneBaseline,recovered,
     targetSame:S.target===nativeTarget,
     ordersSame:__party105.every((u,i)=>JSON.stringify(u.action)===orders[i]),
     playerSame:JSON.stringify(P)===beforePlayer,
     saveSame:localStorage.getItem('bf_global_offline_demo_v7')===beforeSave};
 }""")
 assert status_failures=={'paralyzedThrows':'burst','paralyzedGetterThrows':'burst','paralyzedTrue':'burst',
   'paralyzedFalse':'guard','cursedThrows':'attack','cursedGetterThrows':'attack','cursedTrue':'attack',
   'cursedFalse':'burst','cloneBaseline':'burst','recovered':'guard',
   'targetSame':True,'ordersSame':True,'playerSame':True,'saveSame':True},status_failures
 # Opt-in source-backed PLAYER healing can take priority over optional
 # low-HP Guard. No unverified healer, status or cloned actor may gain a BB.
 assert p.locator('#bf10500-heal-before-guard').count()==1
 assert p.evaluate(api+'.get().healBeforeGuard') is False
 settings['healBeforeGuard']=True
 assert p.evaluate("opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)",settings) is True
 assert p.evaluate(api+'.get().healBeforeGuard') is True
 assert p.locator('#bf10500-heal-before-guard').is_checked()
 assert p.evaluate("""()=>JSON.parse(localStorage.getItem(
   'bf_global_offline_qol_advanced_auto_v105')).healBeforeGuard""") is True
 # Caller must be the ORIGINAL player-owned caster with a known heal-all BB.
 healing_priority=p.evaluate("""()=>{
   const healer=__party105[0],teammate=__party105[1],
     originalHp=healer.hp,originalTeammateHp=teammate.hp,
     originalBB=healer.bb, originalMode=S.mode, originalAuto=S.auto,
     paralysis=window.BFGlobalParalysisActionLockV6000,
     curse=window.BFGlobalCurseBBLockV5900,
     sourceBB=window.bfOriginalBB,
     support=window.originalSupport,
     beforePlayer=JSON.stringify(P),
     beforeSave=localStorage.getItem('bf_global_offline_demo_v7'),
     beforeTarget=S.target,
     beforeActions=__party105.map(p=>JSON.stringify(p.action));
   let noStatus,approved,blockedCurse,blockedParalysis,unknownSkill,
     unknownSupport,insufficientGauge,clone,duplicate,providerThrows;
   try{
     healer.hp=20;teammate.hp=15;healer.bb=100;
     S.mode='archive';S.auto=true;
     window.BFGlobalParalysisActionLockV6000=undefined;
     window.BFGlobalCurseBBLockV5900=undefined;
     noStatus=BF041SmartAuto.kindFor(healer);
     window.BFGlobalParalysisActionLockV6000={paralyzed:()=>false};
     window.BFGlobalCurseBBLockV5900={cursed:()=>false};
     approved=BF041SmartAuto.kindFor(healer);
     window.BFGlobalCurseBBLockV5900={cursed:()=>true};
     blockedCurse=BF041SmartAuto.kindFor(healer);
     window.BFGlobalCurseBBLockV5900={cursed:()=>false};
     // Paralysis blocks the native performUnit execution, so preserve its
     // PREEXISTING baseline selected action; do not authorize an extra heal.
     window.BFGlobalParalysisActionLockV6000={paralyzed:()=>true};
     blockedParalysis=BF041SmartAuto.kindFor(healer);
     window.BFGlobalParalysisActionLockV6000={paralyzed:()=>false};
     window.bfOriginalBB=()=>null;
     unknownSkill=BF041SmartAuto.kindFor(healer);
     window.bfOriginalBB=sourceBB;
     window.originalSupport=()=>null;
     unknownSupport=BF041SmartAuto.kindFor(healer);
     window.originalSupport=support;
     healer.bb=99;
     insufficientGauge=BF041SmartAuto.kindFor(healer);
     healer.bb=100;
     clone=BF041SmartAuto.kindFor({...healer});
     const beforeLength=S.party.length, fourth=S.party[3];
     try{S.party[3]=healer;duplicate=BF041SmartAuto.kindFor(healer)}
     finally{S.party[3]=fourth;S.party.length=beforeLength;}
     window.originalSupport=()=>{throw Error('source unavailable')};
     providerThrows=BF041SmartAuto.kindFor(healer);
   }finally{
     healer.hp=originalHp;teammate.hp=originalTeammateHp;
     healer.bb=originalBB;S.mode=originalMode;S.auto=originalAuto;
     window.BFGlobalParalysisActionLockV6000=paralysis;
     window.BFGlobalCurseBBLockV5900=curse;
     window.bfOriginalBB=sourceBB;
     window.originalSupport=support;
   }
   return {noStatus,approved,blockedCurse,blockedParalysis,unknownSkill,
     unknownSupport,insufficientGauge,clone,duplicate,providerThrows,
     playerSame:JSON.stringify(P)===beforePlayer,
     saveSame:localStorage.getItem('bf_global_offline_demo_v7')===beforeSave,
     targetSame:S.target===beforeTarget,
     ordersSame:__party105.every((p,i)=>JSON.stringify(p.action)===beforeActions[i])};
 }""")
 assert healing_priority=={
   'noStatus':'guard','approved':'burst','blockedCurse':'guard',
   'blockedParalysis':'burst','unknownSkill':'guard',
   'unknownSupport':'guard','insufficientGauge':'guard',
   'clone':'burst','duplicate':'burst','providerThrows':'guard',
   'playerSame':True,'saveSame':True,'targetSame':True,
   'ordersSame':True},healing_priority
 settings['healBeforeGuard']='yes'
 assert p.evaluate("opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)",settings) is False
 assert p.evaluate(api+'.get().healBeforeGuard') is True
 settings['healBeforeGuard']=False
 assert p.evaluate("opts=>BFGlobalQoLAdvancedAutoV10500.set(opts)",settings) is True
 assert p.evaluate(api+'.get().healBeforeGuard') is False
 # Duplicate references are not unique player actors even if the native
 # id slot still points to the same object. Do not grant optional Guard.
 duplicate=p.evaluate("""()=>{const originalLength=S.party.length,
   originalSlot=S.party[3],actor=__party105[1];
   const saved=localStorage.getItem('bf_global_offline_demo_v7');
   try{S.party[3]=actor;
     return {action:BF041SmartAuto.kindFor(actor),
       saveSame:localStorage.getItem('bf_global_offline_demo_v7')===saved};
   }finally{S.party[3]=originalSlot;S.party.length=originalLength;}
 }""")
 assert duplicate=={'action':'burst','saveSame':True},duplicate
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
 # When the pinned source-wave API exists, do not conserve offensive BB
 # if a runtime quest record disagrees with its source count or fails closed.
 # This only affects the opt-in player Auto heuristic, not enemy or NPC AI.
 source_waves=p.evaluate("""()=>{
   const old=window.BFGrandGaiaCampaignV100,oldTotal=S.totalWaves,
     actor=__party105[1];
   const before=localStorage.getItem('bf_global_offline_demo_v7');
   const beforePlayer=JSON.stringify(P),results={};
   try{
     window.BFGrandGaiaCampaignV100={waveReadiness:id=>({missionId:id,verifiedWaveCount:3})};
     S.totalWaves=3;
     results.match=BF041SmartAuto.kindFor(actor);
     // No offensive BB should be conserved for a recorded third wave when
     // the running DEMO battle has a different or unknowable live wave count.
     // Exact positive safe integer parity is required in source-backed mode.
     results.badLiveWave=[undefined,null,NaN,Infinity,'3',3.5,0,-1,2,4]
       .every(value=>{S.totalWaves=value;
         return BF041SmartAuto.kindFor(actor)==='burst';});
     S.totalWaves=3;
     window.BFGrandGaiaCampaignV100={waveReadiness:id=>({missionId:id,verifiedWaveCount:4})};
     results.mismatch=BF041SmartAuto.kindFor(actor);
     window.BFGrandGaiaCampaignV100={waveReadiness:()=>null};
     results.corrupt=BF041SmartAuto.kindFor(actor);
     window.BFGrandGaiaCampaignV100={waveReadiness:()=>{throw Error('corrupt source')}};
     results.exception=BF041SmartAuto.kindFor(actor);
     window.BFGrandGaiaCampaignV100={};
     results.missingApi=BF041SmartAuto.kindFor(actor);
     // Older isolated embeds without authenticated source campaign keep
     // their preexisting heuristic; only production source-backed pages
     // require the additional live wave count validation.
     window.BFGrandGaiaCampaignV100=null;
     S.totalWaves=undefined;
     results.legacy=BF041SmartAuto.kindFor(actor);
     return {...results,saveSame:localStorage.getItem('bf_global_offline_demo_v7')===before,
       playerSame:JSON.stringify(P)===beforePlayer};
   }finally{window.BFGrandGaiaCampaignV100=old;S.totalWaves=oldTotal;}
 }""")
 assert source_waves=={'match':'attack','badLiveWave':True,
   'mismatch':'burst','corrupt':'burst','exception':'burst',
   'missingApi':'burst','legacy':'attack','saveSame':True,
   'playerSame':True},source_waves
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
 # Strict malformed-roster rejection is for an active player Auto choice;
 # manual/training scopes intentionally use the unchanged baseline target.
 p.evaluate("S.auto=true")
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
 # Advanced behavior must not leak onto enemy/partner actors, cloned player
 # units, manual turns or a shuffled player slot that shares an ID.
 # The baseline still runs, but only a real player-owned Auto actor gets
 # optional heal/Curse/Guard overrides.
 player_ownership=p.evaluate("""()=>{const oldCurse=window.BFGlobalCurseBBLockV5900;
   const oldMode=S.mode,oldAuto=S.auto,oldParty=S.party;
   const healer=__party105[0],attacker=__party105[1],hp=healer.hp;
   const teammate=__party105[2],teammateHp=teammate.hp;
   try{
     S.party=__party105;S.mode='archive';S.auto=true;S.over=false;
     healer.hp=healer.maxHp;attacker.hp=attacker.maxHp;
     teammate.hp=teammate.maxHp;
     const ownedHealer=BF041SmartAuto.kindFor(healer)==='attack';
     const clonedHealer=BF041SmartAuto.kindFor({...healer})==='burst';
     window.BFGlobalCurseBBLockV5900={cursed:id=>id===1};
     const ownedCursed=BF041SmartAuto.kindFor(attacker)==='attack';
     const clonedCursed=BF041SmartAuto.kindFor({...attacker})==='burst';
     S.auto=false;
     const manualCursed=BF041SmartAuto.kindFor(attacker)==='burst';
     S.auto=true;S.mode='training';
     const trainingCursed=BF041SmartAuto.kindFor(attacker)==='burst';
     S.mode='archive';
     S.party=[__party105[1],__party105[0],__party105[2]];
     const shuffledCursed=BF041SmartAuto.kindFor(attacker)==='burst';
     return {ownedHealer,clonedHealer,ownedCursed,clonedCursed,
       manualCursed,trainingCursed,shuffledCursed};
   }finally{
     S.mode=oldMode;S.auto=oldAuto;S.party=oldParty;
     healer.hp=hp;teammate.hp=teammateHp;
     window.BFGlobalCurseBBLockV5900=oldCurse;
   }
 }""")
 assert player_ownership=={
   'ownedHealer':True,'clonedHealer':True,
   'ownedCursed':True,'clonedCursed':True,
   'manualCursed':True,'trainingCursed':True,'shuffledCursed':True
 },player_ownership
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
