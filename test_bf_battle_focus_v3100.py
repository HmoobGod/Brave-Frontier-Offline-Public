"""v31.00 deterministic demo foe priority and queued squad attacks through existing controls."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf3100_battle_focus.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_PLAYABLE_FOCUS_ACTIONS_V3100 */')==1
assert len(src.encode('utf8'))<65536 and 'localStorage' not in src and 'saveProgress(' not in src
assert java.index('readPackagedText("bf3000_battle_results.js")')<java.index('readPackagedText("bf3100_battle_focus.js")')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
 getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
 removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,get length(){return Object.keys(db).length}}});
 window.alert=()=>{};window.confirm=()=>true;
 HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
 HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 page.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 page.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
 'bf100_grand_gaia_campaign.js','bf101_story_continue.js',
 'bf110_quest_journal.js','bf2000_story_battle_hud.js',
 'bf2100_battle_command_tray.js','bf2200_original_event_reader.js',
 'bf2300_morgan_event_dialogue.js','bf2400_st_lamia_event_dialogue.js',
 'bf2500_story_event_prompt.js','bf2600_original_event_portraits.js',
 'bf2700_original_event_stage.js','bf2800_dialogue_speaker_cues.js',
 'bf2900_original_event_expressions.js','bf3000_battle_results.js',
 'bf3100_battle_focus.js'):
  page.add_script_tag(path=str(A/name))
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.locator('#bf3100-focus').is_visible()
 assert page.evaluate('BFGlobalBattleFocusV3100.snapshot().canQueue') is True
 assert page.evaluate('BFGlobalBattleFocusV3100.focus("invalid")') is False
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("low","fake")') is False
 # Original source-gated mission selection, no fabricated foe wave table.
 page.evaluate('()=>{P.questClears[1]=1;renderQuestList();BFQuestAreas.choose(QUESTS.find(q=>q.missionId===2))}')
 before=page.evaluate("""()=>({p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert page.evaluate('S.enemies.length')==3
 page.evaluate("""()=>{const es=S.enemies;
 es[0].hp=390;es[0].maxHp=5000;es[0].atk=800;es[0].def=50;
 es[1].hp=75;es[1].maxHp=100;es[1].atk=100;es[1].def=180;
 es[2].hp=760;es[2].maxHp=2000;es[2].atk=300;es[2].def=5;update()}""")
 assert page.evaluate('BFGlobalBattleFocusV3100.lookup("lowest-hp").slot')==1
 assert page.evaluate('BFGlobalBattleFocusV3100.lookup("lowest-hp-percent").slot')==0
 assert page.evaluate('BFGlobalBattleFocusV3100.lookup("highest-hp").slot')==2
 assert page.evaluate('BFGlobalBattleFocusV3100.lookup("highest-hp-percent").slot')==1
 assert page.evaluate('BFGlobalBattleFocusV3100.lookup("highest-atk").slot')==0
 assert page.evaluate('BFGlobalBattleFocusV3100.lookup("lowest-def").slot')==2
 assert page.evaluate('BFGlobalBattleFocusV3100.lookup("wounded-threat").slot')==0
 assert page.evaluate('BFGlobalBattleFocusV3100.lookup("wounded-armor").slot')==2
 assert page.evaluate('BFGlobalBattleFocusV3100.focus("highest-atk")') is True
 assert page.evaluate('S.target')==0
 assert page.locator('#bf3100-options button').count()==11
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("lowest-hp-percent")') is True
 assert page.evaluate('S.party.filter(p=>p.active&&p.hp>0).every(p=>p.action?.target===0)')
 assert page.evaluate('BFGlobalBattleFocusV3100.snapshot().strategy')=='lowest-hp-percent'
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("lowest-hp")') is True
 assert page.evaluate('S.party.filter(p=>p.active&&p.hp>0).every(p=>p.action?.kind==="attack"&&p.action.target===1)')
 # Real manual queued commands use the same native actor and target buttons
 # as the existing focus presets, without executing or changing the save.
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("wounded-threat")') is True
 assert page.evaluate('S.party.filter(p=>p.active&&p.hp>0).every(p=>p.action?.kind==="attack"&&p.action.target===0)')
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("wounded-armor")') is True
 assert page.evaluate('S.party.filter(p=>p.active&&p.hp>0).every(p=>p.action?.kind==="attack"&&p.action.target===2)')
 assert page.evaluate('S.busy') is False
 # Native Focus changes S.target before calling the shared queue planner.
 # With shuffled or cloned player actors, its caller must reject the request
 # BEFORE mutating the old selected target or the existing squad actions.
 guarded_focus=page.evaluate("""()=>{const party=S.party,selected=S.target;
   const oldOrders=party.map(p=>JSON.stringify(p.action));
   const stored=localStorage.getItem('bf_global_offline_demo_v7');
   const initialStrategy=BFGlobalBattleFocusV3100.snapshot().strategy;
   const testCase=()=>({
     attack:BFGlobalBattleFocusV3100.queueFocus('highest-atk')===false,
     burst:BFGlobalBattleFocusV3100.queueFocus('highest-atk','burst')===false
   });
   try{
     S.party=[party[1],party[0],...party.slice(2)];
     const shuffled=testCase();
     S.party=[party[0],{...party[1],id:party[0].id},...party.slice(2)];
     const cloned=testCase();
     return {shuffled,cloned,selectedSame:S.target===selected,
       strategySame:BFGlobalBattleFocusV3100.snapshot().strategy===initialStrategy,
       ordersSame:oldOrders.every((a,i)=>a===JSON.stringify(party[i].action)),
       savedSame:localStorage.getItem('bf_global_offline_demo_v7')===stored,
       noTurn:!S.busy};
   }finally{S.party=party;}
 }""")
 assert guarded_focus=={'shuffled':{'attack':True,'burst':True},
   'cloned':{'attack':True,'burst':True},'selectedSame':True,
   'strategySame':True,'ordersSame':True,'savedSame':True,'noTurn':True},guarded_focus
 page.evaluate('S.party[0].bb=100;update()')
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("lowest-def","burst")') is True
 assert page.evaluate('S.party[0].action.kind')=='burst'
 assert page.evaluate('S.party.filter(p=>p.active&&p.hp>0).every(p=>p.action?.target===2)')
 # New high-HP player controls queue the real native Attack actions and
 # never execute the round unless the owner presses the Execute button.
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("highest-hp")') is True
 assert page.evaluate('BFGlobalBattleFocusV3100.snapshot().strategy')=='highest-hp'
 assert page.evaluate('S.party.filter(p=>p.active&&p.hp>0).every(p=>p.action?.kind==="attack"&&p.action.target===2)')
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("highest-hp-percent")') is True
 assert page.evaluate('BFGlobalBattleFocusV3100.snapshot().strategy')=='highest-hp-percent'
 assert page.evaluate('S.party.filter(p=>p.active&&p.hp>0).every(p=>p.action?.kind==="attack"&&p.action.target===1)')
 assert page.evaluate('S.busy') is False
 # Source-known elemental manual focus is a separate tactic from the
 # per-ally Element Advantage action. The Android app loads v69 later,
 # so this dynamic API must remain inactive until that source loads.
 assert page.evaluate('BFGlobalBattleFocusV3100.lookup("elemental")') is None
 assert page.locator('#bf3100-options button[data-strategy="elemental"]').is_disabled()
 page.add_script_tag(path=str(A/'bf6900_elemental_combat.js'))
 assert page.evaluate('BFGlobalElementalCombatV6900.normalize("Fire")')=='Fire'
 prior_types=page.evaluate('S.party.map(p=>p.unitId)')
 prior_elements=page.evaluate('S.enemies.map(e=>e.element??null)')
 page.evaluate("""()=>{S.party.forEach(p=>{if(p.active)p.unitId=10011});
   S.enemies[0].element='Water';S.enemies[1].element='Earth';
   S.enemies[2].element='Light';update()}""")
 assert page.evaluate('BFGlobalBattleFocusV3100.lookup("elemental")?.slot')==1
 assert page.evaluate('BFGlobalBattleFocusV3100.refresh().canQueue') is True
 assert not page.locator('#bf3100-options button[data-strategy="elemental"]').is_disabled()
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("elemental")') is True
 assert page.evaluate('BFGlobalBattleFocusV3100.snapshot().strategy')=='elemental'
 assert page.evaluate('S.party.filter(p=>p.active&&p.hp>0).every(p=>p.action?.kind==="attack"&&p.action.target===1)')
 assert page.evaluate('S.busy') is False
 # The new distinct MANUAL focus action uses source-listed player
 # elements to avoid fighting heavily resistant foes in real demo combat.
 # Unlike Element Weakness, it stays usable without a verified advantage.
 page.evaluate("""()=>{S.enemies[1].element='Thunder';
   S.enemies[2].element='Light';update()}""")
 assert page.evaluate('BFGlobalBattleFocusV3100.lookup("elemental")') is None
 assert page.evaluate('BFGlobalBattleFocusV3100.lookup("element-safe")?.slot')==2
 assert not page.locator('#bf3100-options button[data-strategy="element-safe"]').is_disabled()
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("element-safe")') is True
 assert page.evaluate('BFGlobalBattleFocusV3100.snapshot().strategy')=='element-safe'
 assert page.evaluate('S.party.filter(p=>p.active&&p.hp>0).every(p=>p.action?.target===2)')
 assert page.evaluate('S.busy') is False
 # Unknown living foe or ally element must disable the new strategy
 # without moving S.target, overwriting queued native actions, or saving.
 manual_guard=page.evaluate("""()=>{const old=S.enemies[2].element;
   const unit=S.party[0].unitId;
   const before={target:S.target,actions:S.party.map(u=>JSON.stringify(u.action)),
     save:localStorage.getItem('bf_global_offline_demo_v7'),player:JSON.stringify(P)};
   const result={};
   try{
     S.enemies[2].element='Unknown';
     result.unknownFoe=BFGlobalBattleFocusV3100.lookup('element-safe')===null&&
       !BFGlobalBattleFocusV3100.queueFocus('element-safe');
     S.enemies[2].element=old;
     S.party[0].unitId=999999;
     result.unknownAlly=BFGlobalBattleFocusV3100.lookup('element-safe')===null&&
       !BFGlobalBattleFocusV3100.queueFocus('element-safe');
   }finally{S.enemies[2].element=old;S.party[0].unitId=unit}
   result.safe=S.target===before.target&&
     S.party.every((u,i)=>JSON.stringify(u.action)===before.actions[i])&&
     localStorage.getItem('bf_global_offline_demo_v7')===before.save&&
     JSON.stringify(P)===before.player&&!S.busy;
   return result;
 }""")
 assert manual_guard=={'unknownFoe':True,'unknownAlly':True,'safe':True},manual_guard
 # The source element provider can be missing, throw, or return an invalid
 # 2x multiplier. All three must fail closed, not guess a target.
 safe_failures=page.evaluate("""()=>{const original=window.BFGlobalElementalCombatV6900;
   const cases=[];
   const target=S.target,orders=S.party.map(p=>JSON.stringify(p.action));
   const before=localStorage.getItem('bf_global_offline_demo_v7');
   try{
     for(const provider of [null,
       {normalize:original.normalize,multiplier:()=>{throw Error('source unreadable')}},
       {normalize:original.normalize,multiplier:()=>2}]){
       window.BFGlobalElementalCombatV6900=provider;
       cases.push(BFGlobalBattleFocusV3100.lookup('element-safe')===null&&
         BFGlobalBattleFocusV3100.queueFocus('element-safe')===false);
     }
     return {cases,unchanged:S.target===target&&
       orders.every((x,i)=>x===JSON.stringify(S.party[i].action))&&
       localStorage.getItem('bf_global_offline_demo_v7')===before};
   }finally{window.BFGlobalElementalCombatV6900=original}
 }""")
 assert safe_failures=={'cases':[True,True,True],'unchanged':True},safe_failures
 # Restore original element assumptions before exercising the existing
 # Weakness Focus and negative-guard regression suite.
 page.evaluate("""()=>{S.enemies[1].element='Earth';
   S.enemies[2].element='Light';update()}""")
 # Return to the original Element Weakness strategy after the new separate
 # Fewest Resists action. Later assertions inspect refresh().target, which
 # reports the CURRENT selected strategy (not lookup('elemental')).
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("elemental")') is True
 assert page.evaluate('BFGlobalBattleFocusV3100.snapshot().strategy')=='elemental'
 # A broken optional elemental provider must not crash the native command
 # tray, change the selected target, queue an action or write the v7 save.
 broken_elemental=page.evaluate("""()=>{
   const original=window.BFGlobalElementalCombatV6900;
   const beforeTarget=S.target, beforeOrders=S.party.map(p=>JSON.stringify(p.action));
   const beforeSave=localStorage.getItem('bf_global_offline_demo_v7');
   try{
     const cases=[];
     for(const provider of [
       {normalize:original.normalize,multiplier:()=>{throw Error('multiplier unavailable')}},
       {normalize:()=>{throw Error('normalization unavailable')},multiplier:original.multiplier},
       {normalize:value=>{if(value==='Earth')throw Error('foe normalization unavailable');
         return original.normalize(value);},multiplier:original.multiplier}
     ]){
       window.BFGlobalElementalCombatV6900=provider;
       const lookup=BFGlobalBattleFocusV3100.lookup('elemental');
       const queued=BFGlobalBattleFocusV3100.queueFocus('elemental');
       const refreshed=BFGlobalBattleFocusV3100.refresh();
       cases.push({lookupNull:lookup===null,queued,refreshed:refreshed.target===null,
         targetSame:S.target===beforeTarget,
         ordersSame:beforeOrders.every((a,i)=>a===JSON.stringify(S.party[i].action)),
         saveSame:localStorage.getItem('bf_global_offline_demo_v7')===beforeSave});
     }
     return cases;
   }finally{window.BFGlobalElementalCombatV6900=original;
     BFGlobalBattleFocusV3100.refresh();}
 }""")
 expected_broken={'lookupNull':True,'queued':False,'refreshed':True,
   'targetSame':True,'ordersSame':True,'saveSame':True}
 assert broken_elemental==[expected_broken]*3,broken_elemental
 elemental_orders=page.evaluate('S.party.map(p=>JSON.stringify(p.action))')
 # Without a source-verified weakness, do not guess or overwrite orders.
 page.evaluate("S.enemies[1].element='Water';update()")
 assert page.evaluate('BFGlobalBattleFocusV3100.lookup("elemental")') is None
 assert page.evaluate('BFGlobalBattleFocusV3100.refresh().target') is None
 assert page.locator('#bf3100-options button[data-strategy="elemental"]').is_disabled()
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("elemental")') is False
 assert page.evaluate('S.party.map(p=>JSON.stringify(p.action))')==elemental_orders
 # Two known Earth foes tie on ally advantages: lowest HP%, then slot.
 page.evaluate("""()=>{S.enemies[0].element='Earth';
   S.enemies[1].element='Earth';S.enemies[2].element='Water';update()}""")
 assert page.evaluate('BFGlobalBattleFocusV3100.lookup("elemental")?.slot')==0
 # Unknown enemy types do not become guessed weaknesses.
 page.evaluate("""()=>S.enemies.forEach(e=>e.element='Unknown')""")
 assert page.evaluate('BFGlobalBattleFocusV3100.lookup("elemental")') is None
 page.evaluate("""v=>{S.party.forEach((p,i)=>p.unitId=v.types[i]);
    S.enemies.forEach((e,i)=>{if(v.elements[i]===null)delete e.element;
      else e.element=v.elements[i]});update()}""",
    {'types':prior_types,'elements':prior_elements})
 # Any invalid living foe must block the WHOLE manual focus plan rather
 # than silently skipping it and targeting an ambiguous native button.
 # Keep synthetic corruption in one synchronous browser task, so the
 # normal battle renderer never observes these deliberately invalid rows.
 results=page.evaluate("""()=>{const original=S.enemies;
   const seed=original[0],strategies=['lowest-hp','lowest-hp-percent','highest-hp','highest-hp-percent','highest-atk','lowest-def','wounded-threat','wounded-armor','elemental','element-safe'];
   try{
     S.enemies=[
       {...seed,slot:0,name:'Zero max',hp:5,maxHp:0,atk:9999,def:-99},
       {...seed,slot:1,name:'Infinite HP',hp:Infinity,maxHp:100,atk:9998,def:-98},
       {...seed,slot:-1,name:'Bad slot',hp:2,maxHp:100,atk:9997,def:-97},
       {...seed,slot:3,name:'Valid target',hp:175,maxHp:200,atk:50,def:50}
     ];
     const valid=strategies.map(kind=>BFGlobalBattleFocusV3100.lookup(kind)?.slot);
     S.enemies=S.enemies.slice(0,3);
     const invalid=strategies.map(kind=>BFGlobalBattleFocusV3100.lookup(kind));
     const rejected=BFGlobalBattleFocusV3100.focus('highest-atk')===false;
     return {valid,invalid,rejected};
   }finally{S.enemies=original;}
 }""")
 assert results['valid']==[None]*10,results
 assert results['invalid']==[None]*10,results
 assert results['rejected'],results
 # Wounded player tactics: 50% is inclusive, unknown ATK/DEF
 # anywhere in a live roster rejects the whole plan, and zero wounded
 # enemies must not cause an arbitrary fallback or mutate existing orders.
 finisher_cases=page.evaluate("""()=>{const original=S.enemies,oldTarget=S.target,
   oldOrders=S.party.map(p=>JSON.stringify(p.action)),
   saved=localStorage.getItem('bf_global_offline_demo_v7'),
   beforePlayer=JSON.stringify(P),seed=original[0],
   api=BFGlobalBattleFocusV3100;
   try{
     S.enemies=[
       {...seed,slot:0,name:'Fifty percent threat',hp:50,maxHp:100,atk:200,def:90},
       {...seed,slot:1,name:'Wounded low armor',hp:25,maxHp:100,atk:110,def:10},
       {...seed,slot:2,name:'Healthy high threat',hp:70,maxHp:100,atk:900,def:1}
     ];
     const boundary={threat:api.lookup('wounded-threat')?.slot,
       armor:api.lookup('wounded-armor')?.slot};
     S.enemies[0].hp=51;
     const crossed={threat:api.lookup('wounded-threat')?.slot,
       armor:api.lookup('wounded-armor')?.slot};
     S.enemies[1].hp=76;
     const none={threat:api.lookup('wounded-threat'),
       armor:api.lookup('wounded-armor'),
       attack:api.queueFocus('wounded-threat'),
       burst:api.queueFocus('wounded-armor','burst')};
     S.enemies[1].hp=25;
     S.enemies[2].atk=undefined;
     const brokenAttack={lookup:api.lookup('wounded-threat'),
       queued:api.queueFocus('wounded-threat')};
     S.enemies[2].atk=900;S.enemies[2].def=undefined;
     const brokenDefense={lookup:api.lookup('wounded-armor'),
       queued:api.queueFocus('wounded-armor')};
     S.enemies[2].def=1;S.enemies[2].hp=101;
     const impossible={lookup:api.lookup('wounded-threat'),
       queued:api.queueFocus('wounded-threat')};
     return {boundary,crossed,none,brokenAttack,brokenDefense,impossible,
       sameTarget:oldTarget===S.target,
       sameOrders:oldOrders.every((a,i)=>a===JSON.stringify(S.party[i].action)),
       sameSave:saved===localStorage.getItem('bf_global_offline_demo_v7'),
       samePlayer:beforePlayer===JSON.stringify(P),noTurn:!S.busy};
   }finally{S.enemies=original;api.refresh()}
 }""")
 assert finisher_cases=={
  'boundary':{'threat':0,'armor':1},
  'crossed':{'threat':1,'armor':1},
  'none':{'threat':None,'armor':None,'attack':False,'burst':False},
  'brokenAttack':{'lookup':None,'queued':False},
  'brokenDefense':{'lookup':None,'queued':False},
  'impossible':{'lookup':None,'queued':False},
  'sameTarget':True,'sameOrders':True,'sameSave':True,
  'samePlayer':True,'noTurn':True},finisher_cases
 # Targeting and queued orders must remain untouched if ANY living record
 # is corrupt, including text-coerced Infinity or a duplicate valid slot.
 # Validate all seven focus strategies and actual queueFocus player controls.
 gated=page.evaluate("""()=>{const original=S.enemies,seed=original[0];
   const originalTarget=S.target;
   const savedActions=S.party.map(p=>JSON.stringify(p.action));
   const cases=[
     [{...seed,slot:0,hp:5,maxHp:0},{...seed,slot:1,hp:45,maxHp:100}],
     [{...seed,slot:0,hp:'Infinity',maxHp:100},{...seed,slot:1,hp:45,maxHp:100}],
     [{...seed,slot:0,hp:Infinity,maxHp:100},{...seed,slot:1,hp:45,maxHp:100}],
     [{...seed,slot:1,hp:5,maxHp:100},{...seed,slot:1,hp:45,maxHp:100}],
     [{...seed,slot:-1,hp:5,maxHp:100},{...seed,slot:1,hp:45,maxHp:100}]
   ];
   try{
     return cases.map(foes=>{
       S.enemies=foes;
       const looked=['lowest-hp','lowest-hp-percent','highest-hp','highest-hp-percent','highest-atk','lowest-def','wounded-threat','wounded-armor','elemental']
         .map(k=>BFGlobalBattleFocusV3100.lookup(k));
       const focused=BFGlobalBattleFocusV3100.focus('highest-hp');
       const queued=BFGlobalBattleFocusV3100.queueFocus('highest-hp-percent','burst');
       return {looked,focused,queued,targetUnchanged:S.target===originalTarget,
         actionsUnchanged:savedActions.every((a,i)=>a===JSON.stringify(S.party[i].action))};
     });
   }finally{S.enemies=original;S.target=originalTarget;}
 }""")
 assert len(gated)==5,gated
 assert all(x['looked']==[None]*9 and x['focused'] is False and
            x['queued'] is False and x['targetUnchanged'] and
            x['actionsUnchanged'] for x in gated),gated
 # A living foe with an unknown ATK or DEF is never silently dropped from
 # the corresponding manual focus priority. Both actual commands and the
 # displayed focus buttons fail closed; valid HP-based focus still works.
 unknown_stat=page.evaluate("""()=> {
   const original=S.enemies,seed=original[0],beforeTarget=S.target,
     orders=S.party.map(p=>JSON.stringify(p.action)),
     saved=localStorage.getItem('bf_global_offline_demo_v7'),
     before=JSON.stringify(P);
   try{
     S.enemies=[
       {...seed,slot:0,name:'Known foe',hp:40,maxHp:100,atk:30,def:40},
       {...seed,slot:1,name:'Unknown foe',hp:75,maxHp:100,atk:undefined,def:undefined}
     ];
     const highest=BFGlobalBattleFocusV3100.lookup('highest-atk');
     const lowest=BFGlobalBattleFocusV3100.lookup('lowest-def');
     const hp=BFGlobalBattleFocusV3100.lookup('lowest-hp')?.slot;
     BFGlobalBattleFocusV3100.refresh();
     const buttons={
       atk:document.querySelector('#bf3100-options button[data-strategy="highest-atk"]').disabled,
       def:document.querySelector('#bf3100-options button[data-strategy="lowest-def"]').disabled,
       hp:document.querySelector('#bf3100-options button[data-strategy="lowest-hp"]').disabled
     };
     const denied=[
       BFGlobalBattleFocusV3100.focus('highest-atk')===false,
       BFGlobalBattleFocusV3100.focus('lowest-def')===false,
       BFGlobalBattleFocusV3100.queueFocus('highest-atk')===false,
       BFGlobalBattleFocusV3100.queueFocus('lowest-def','burst')===false
     ];
     return {highest,lowest,hp,buttons,denied,
       selectedSame:S.target===beforeTarget,
       ordersSame:orders.every((s,i)=>s===JSON.stringify(S.party[i].action)),
       saveSame:localStorage.getItem('bf_global_offline_demo_v7')===saved,
       playerSame:before===JSON.stringify(P),noTurn:!S.busy};
   }finally{S.enemies=original;BFGlobalBattleFocusV3100.refresh();}
 }""")
 assert unknown_stat=={
   'highest':None,'lowest':None,'hp':0,
   'buttons':{'atk':True,'def':True,'hp':False},
   'denied':[True]*4,'selectedSame':True,'ordersSame':True,
   'saveSame':True,'playerSame':True,'noTurn':True},unknown_stat
 # v333R1: eligibility can flip while the currently selected target and
 # source-elemental focus remain unchanged. Refresh MUST recalculate every
 # button's disabled state, not just the selected strategy.
 refreshed=page.evaluate("""()=>{
   const original=S.enemies,seed=original[0],oldTarget=S.target,
     beforeP=JSON.stringify(P),beforeSave=localStorage.getItem('bf_global_offline_demo_v7'),
     orders=S.party.map(u=>JSON.stringify(u.action));
   try{
     S.enemies=[
       {...seed,slot:0,name:'Known',hp:40,maxHp:100,atk:30,def:40,element:'Unknown'},
       {...seed,slot:1,name:'Changing',hp:75,maxHp:100,atk:50,def:20,element:'Unknown'}
     ];
     const ids=['highest-atk','lowest-def'].map(k=>
       document.querySelector('#bf3100-options button[data-strategy="'+k+'"]'));
     const get=()=>ids.map(b=>b.disabled);
     BFGlobalBattleFocusV3100.refresh();
     const enabled=get().every(v=>v===false);
     S.enemies[1].atk=undefined;S.enemies[1].def=undefined;
     BFGlobalBattleFocusV3100.refresh();
     const blocked=get().every(v=>v===true);
     S.enemies[1].atk=50;S.enemies[1].def=20;
     BFGlobalBattleFocusV3100.refresh();
     const restored=get().every(v=>v===false);
     return {enabled,blocked,restored,targetSame:oldTarget===S.target,
       ordersSame:orders.every((a,i)=>a===JSON.stringify(S.party[i].action)),
       saveSame:beforeSave===localStorage.getItem('bf_global_offline_demo_v7'),
       playerSame:beforeP===JSON.stringify(P),busy:S.busy};
   }finally{S.enemies=original;BFGlobalBattleFocusV3100.refresh();}
 }""")
 assert refreshed=={'enabled':True,'blocked':True,'restored':True,
   'targetSame':True,'ordersSame':True,'saveSame':True,
   'playerSame':True,'busy':False},refreshed
 # With an entirely valid roster, percentage ranking still differs from
 # absolute HP ranking; ties retain the prior lower-slot ordering.
 ranks=page.evaluate("""()=>{const original=S.enemies,seed=original[0];
   try{
     S.enemies=[
       {...seed,slot:0,hp:10,maxHp:20},
       {...seed,slot:1,hp:100,maxHp:1000},
       {...seed,slot:2,hp:600,maxHp:1000},
       {...seed,slot:3,hp:50,maxHp:500},
       {...seed,slot:4,hp:300,maxHp:500}
     ];
     return {absolute:BFGlobalBattleFocusV3100.lookup('lowest-hp')?.slot,
       relative:BFGlobalBattleFocusV3100.lookup('lowest-hp-percent')?.slot,
       highest:BFGlobalBattleFocusV3100.lookup('highest-hp')?.slot,
       highestPercent:BFGlobalBattleFocusV3100.lookup('highest-hp-percent')?.slot};
   }finally{S.enemies=original;}
 }""")
 assert ranks=={'absolute':0,'relative':1,'highest':2,'highestPercent':2},ranks
 assert page.evaluate('P.version')==7
 after=page.evaluate("""()=>({p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 # The fixture explicitly selects a mission, so compare save for implicit writes, not transient P.lastMission.
 assert after['save']==before['save']
 page.evaluate('S.busy=true')
 assert page.evaluate('BFGlobalBattleFocusV3100.focus("highest-atk")') is False
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("lowest-hp")') is False
 page.evaluate('S.busy=false')
 page.locator('#auto').check()
 assert page.evaluate('BFGlobalBattleFocusV3100.queueFocus("lowest-hp")') is False
 page.locator('#auto').uncheck()
 page.evaluate('finish(false)')
 assert page.evaluate('BFGlobalBattleFocusV3100.focus("lowest-def")') is False
 assert not errors,errors
 browser.close()
print('PASS v31.00: ten manual focus strategies, 50% wounded threat/armor finishers, native queue and v7 save isolation')
