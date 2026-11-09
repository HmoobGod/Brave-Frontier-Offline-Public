"""v21.00: queue same real demo buttons for all alive units, native target/execute, save safety."""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;A=R/'app/src/main/assets'
src=(A/'bf2100_battle_command_tray.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count('/* BF_GLOBAL_BATTLE_COMMAND_TRAY_V2100 */')==1
assert len(src.encode('utf8'))<65536
assert 'localStorage' not in src and 'saveProgress(' not in src and 'finish(true)' not in src
assert java.index('readPackagedText("bf2000_story_battle_hud.js")')<java.index('readPackagedText("bf2100_battle_command_tray.js")')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,
  executable_path=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable'),
  args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)+'\n'+str(e.stack)))
 page.evaluate("""()=>{const db={};Object.defineProperty(window,'localStorage',{configurable:true,value:{
  getItem:k=>db[k]??null,setItem:(k,v)=>db[k]=String(v),
  removeItem:k=>delete db[k],key:i=>Object.keys(db)[i]??null,
  get length(){return Object.keys(db).length}}});
  window.alert=()=>{};window.confirm=()=>true;
  HTMLMediaElement.prototype.load=()=>{};HTMLMediaElement.prototype.pause=()=>{};
  HTMLMediaElement.prototype.play=()=>Promise.resolve()}""")
 page.set_content((A/'index.html').read_text('utf8'),wait_until='load',timeout=90000)
 page.add_style_tag(path=str(A/'bf_home_nav.css'))
 for name in ('bf_home_nav.js','bf080_morgan_map.js','bf090_st_lamia_map.js',
              'bf100_grand_gaia_campaign.js','bf101_story_continue.js',
              'bf110_quest_journal.js','bf2000_story_battle_hud.js',
              'bf2100_battle_command_tray.js'):
  page.add_script_tag(path=str(A/name))
 page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
 assert page.locator('#bf2100-tray').is_visible()
 assert page.evaluate('BFGlobalBattleCommandsV2100.snapshot().alive')==6
 before=page.evaluate("""()=>({p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("fake")') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("attack")') is True
 assert page.evaluate('S.party.filter(p=>p.active&&p.hp>0).every(p=>p.action?.kind==="attack")')
 assert page.evaluate('BFGlobalBattleCommandsV2100.snapshot().queued')==6
 assert not page.locator('#bf2100-execute').is_disabled()
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("guard")') is True
 assert page.evaluate('S.party.filter(p=>p.active&&p.hp>0).every(p=>p.action?.kind==="guard")')
 # Manual offensive queues must reject an invalid, KO'd or disabled
 # current native enemy target, preserving all existing orders. Guard-only
 # still works because it does not use enemy targeting.
 stale=page.evaluate("""()=>{const before=S.party.map(p=>JSON.stringify(p.action));
   const old=S.target,enemies=S.enemies;
   const current=enemies.find(e=>e.slot===old&&e.hp>0);
   if(!current)return {badFixture:true};
   const originalHp=current.hp;
   const checks=[];
   try{
     for(const value of [-1,99999,'0',NaN]){
       S.target=value;
       checks.push({attack:BFGlobalBattleCommandsV2100.queueAll('attack'),
         burst:BFGlobalBattleCommandsV2100.queueAll('burst'),
         unchanged:before.every((x,i)=>x===JSON.stringify(S.party[i].action))});
     }
     S.target=old;current.hp=0;
     checks.push({attack:BFGlobalBattleCommandsV2100.queueAll('attack'),
       burst:BFGlobalBattleCommandsV2100.queueAll('burst'),
       unchanged:before.every((x,i)=>x===JSON.stringify(S.party[i].action))});
     current.hp=originalHp;
     const native=document.getElementById('targets').children;
     const living=enemies.filter(e=>e.hp>0);
     const mapped=native.length===enemies.length?enemies:
       native.length===living.length?living:null;
     const index=mapped?.findIndex(e=>e.slot===old)??-1;
     if(index<0)return {badFixture:true,index};
     const button=native[index],originalDisabled=button.disabled;
     try{
       button.disabled=true;
       checks.push({attack:BFGlobalBattleCommandsV2100.queueAll('attack'),
         burst:BFGlobalBattleCommandsV2100.queueAll('burst'),
         unchanged:before.every((x,i)=>x===JSON.stringify(S.party[i].action))});
     }finally{button.disabled=originalDisabled}
     return {checks};
   }finally{current.hp=originalHp;S.target=old;}
 }""")
 assert 'badFixture' not in stale,stale
 assert len(stale['checks'])==6,stale
 assert all(x=={'attack':False,'burst':False,'unchanged':True}
            for x in stale['checks']),stale
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("guard")') is True
 assert page.evaluate('S.party.filter(p=>p.active&&p.hp>0).every(p=>p.action.kind==="guard")') is True
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("attack")') is True
 # Source-verified manual HEALING BB: use exactly one genuine heal-all
 # support BB when an owned ally reaches 50% HP. Do not execute the turn.
 assert page.locator('#bf2100-heal-bb').is_visible()
 assert page.evaluate("bfOriginalBB(20041)?.target==='support'") is True
 assert page.evaluate("originalSupport(20041)?.kind==='heal_all'") is True
 original_healer_unit=page.evaluate('S.party[0].unitId')
 page.evaluate("""()=>{S.party.forEach((p,i)=>{
   if(!p.active||p.hp<=0)return;
   p.bb=i===0?100:0;p.hp=p.maxHp;
 });
 S.party[0].unitId=20041;
 S.party[1].hp=Math.floor(S.party[1].maxHp*.40);
 update();BFGlobalBattleCommandsV2100.refresh()}""")
 assert page.evaluate('BFGlobalBattleCommandsV2100.healingAvailable()') is True
 assert not page.locator('#bf2100-heal-bb').is_disabled()
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("heal")') is True
 healed_orders=page.evaluate('S.party.filter(p=>p.active&&p.hp>0).map(p=>p.action?.kind)')
 assert healed_orders==['burst']+['attack']*5,healed_orders
 assert page.evaluate('S.busy') is False
 # Repeated use with no injured allies refuses instead of wasting a healer BB.
 page.evaluate("()=>{S.party[1].hp=S.party[1].maxHp;update();BFGlobalBattleCommandsV2100.refresh()}")
 assert page.evaluate('BFGlobalBattleCommandsV2100.healingAvailable()') is False
 assert page.locator('#bf2100-heal-bb').is_disabled()
 prior_heal_orders=page.evaluate('S.party.map(p=>JSON.stringify(p.action))')
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("heal")') is False
 assert page.evaluate('S.party.map(p=>JSON.stringify(p.action))')==prior_heal_orders
 # Curse and item-turn reservations both block this healer and cannot
 # silently consume a different offensive BB or alter queued commands.
 blocks=page.evaluate("""()=>{const oldCurse=window.BFGlobalCurseBBLockV5900;
   const oldItem=window.BFGlobalItemTurnReservationsV4500;
   S.party[1].hp=Math.floor(S.party[1].maxHp*.40);
   const before=S.party.map(p=>JSON.stringify(p.action));
   try{
     window.BFGlobalCurseBBLockV5900={cursed:id=>id===0};
     const curse={available:BFGlobalBattleCommandsV2100.healingAvailable(),
       success:BFGlobalBattleCommandsV2100.queueAll('heal')};
     window.BFGlobalCurseBBLockV5900=oldCurse;
     window.BFGlobalItemTurnReservationsV4500={
       snapshot:()=>({reservations:[{slot:0}]})
     };
     const item={available:BFGlobalBattleCommandsV2100.healingAvailable(),
       success:BFGlobalBattleCommandsV2100.queueAll('heal')};
     return {curse,item,unchanged:before.every((a,i)=>a===JSON.stringify(S.party[i].action))};
   }finally{
     window.BFGlobalCurseBBLockV5900=oldCurse;
     window.BFGlobalItemTurnReservationsV4500=oldItem;
   }
 }""")
 assert blocks=={'curse':{'available':False,'success':False},
                 'item':{'available':False,'success':False},
                 'unchanged':True},blocks
 # A broken living foe or duplicate player actor must reject the entire
 # healing shortcut before selecting an actor or queueing even one action.
 bad_heal=page.evaluate("""()=>{const foes=S.enemies,party=S.party;
   const before=S.party.map(p=>JSON.stringify(p.action)),selected=S.target;
   try{
     S.enemies=[{...foes[0],slot:0,hp:Infinity,maxHp:100},
                {...foes[0],slot:1,hp:40,maxHp:100}];
     const invalidFoe=BFGlobalBattleCommandsV2100.queueAll('heal')===false;
     S.enemies=foes;
     S.party=[party[0],{...party[1],id:party[0].id},...party.slice(2)];
     const duplicateActor=BFGlobalBattleCommandsV2100.queueAll('heal')===false;
     return {invalidFoe,duplicateActor,targetUnchanged:S.target===selected,
       ordersUnchanged:before.every((a,i)=>a===JSON.stringify(party[i].action))};
   }finally{S.enemies=foes;S.party=party;S.target=selected}
 }""")
 assert bad_heal=={'invalidFoe':True,'duplicateActor':True,
                   'targetUnchanged':True,'ordersUnchanged':True},bad_heal
 # Restore the exact owned source identity and ally health for other tactics.
 page.evaluate("""id=>{S.party[0].unitId=id;
   S.party.forEach(p=>{if(p.active&&p.hp>0){p.hp=p.maxHp;p.bb=0;}});
   update();BFGlobalBattleCommandsV2100.refresh()}""",original_healer_unit)
 assert page.evaluate('BFGlobalBattleCommandsV2100.healingAvailable()') is False
 # Player-only defensive tactic: wounded allies Guard, healthy allies Attack.
 # Native buttons queue orders but do not run a turn, heal units, or award XP.
 assert page.locator('#bf2100-protect').is_visible()
 assert page.evaluate('BFGlobalBattleCommandsV2100.woundedPlan()') is None
 assert page.evaluate('BFGlobalBattleCommandsV2100.protectWounded()') is False
 page.evaluate("""()=>{S.party.forEach((p,i)=>{
   if(!p.active||p.hp<=0)return;
   p.hp=i<2?Math.max(1,Math.floor(p.maxHp*(i===0 ? 0.25 : 0.40))):p.maxHp;
 });update()}""")
 plan=page.evaluate('BFGlobalBattleCommandsV2100.woundedPlan()')
 assert plan and len(plan['orders'])==6,plan
 assert [o['kind'] for o in plan['orders']]==['guard','guard']+['attack']*4,plan
 assert not page.locator('#bf2100-protect').is_disabled()
 assert page.evaluate('BFGlobalBattleCommandsV2100.protectWounded()') is True
 actions=page.evaluate('S.party.filter(p=>p.active&&p.hp>0).map(p=>[p.action.kind,p.action.target])')
 assert [x[0] for x in actions]==['guard','guard']+['attack']*4,actions
 assert all(x[1]==plan['target'] for x in actions[2:]),actions
 assert page.evaluate('S.busy') is False
 page.evaluate("""()=>{S.party.forEach(p=>{if(p.active&&p.hp>0)p.hp=p.maxHp});update()}""")
 assert page.evaluate('BFGlobalBattleCommandsV2100.woundedPlan()') is None
 assert page.evaluate('BFGlobalBattleCommandsV2100.protectWounded()') is False
 # The original burst and target-selection shortcuts still work afterwards.
 page.evaluate('S.party[0].bb=100;update()')
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("burst")') is True
 assert page.evaluate('S.party[0].action.kind')=='burst'
 assert page.evaluate('S.party.slice(1).every(p=>p.action.kind==="attack")')
 assert page.evaluate('BFGlobalBattleCommandsV2100.snapshot().bbReady')==1
 # Offensive squad shortcuts must reject the WHOLE corrupt native foe roster
 # before the first player click; no partial orders or selected target change.
 # Keep temporary malformed state inside one synchronous browser task.
 rejected=page.evaluate("""()=>{const enemy=S.enemies,party=S.party;
   const first=enemy[0],before=S.party.map(p=>JSON.stringify(p.action));
   const selected=S.target;
   const cases=[
     [{...first,slot:0,hp:Infinity,maxHp:100},{...first,slot:1,hp:80,maxHp:100}],
     [{...first,slot:0,hp:'Infinity',maxHp:100},{...first,slot:1,hp:80,maxHp:100}],
     [{...first,slot:0,hp:20,maxHp:0},{...first,slot:1,hp:80,maxHp:100}],
     [{...first,slot:1,hp:20,maxHp:100},{...first,slot:1,hp:80,maxHp:100}],
     [{...first,slot:-1,hp:20,maxHp:100},{...first,slot:1,hp:80,maxHp:100}]
   ];
   try{
     const results=cases.map(foes=>{
       S.enemies=foes;
       const attack=BFGlobalBattleCommandsV2100.queueAll('attack');
       const burst=BFGlobalBattleCommandsV2100.queueAll('burst');
       return {attack,burst,targetUnchanged:S.target===selected,
         ordersUnchanged:before.every((a,i)=>a===JSON.stringify(S.party[i].action))};
     });
     S.enemies=enemy;
     S.party=[party[0],{...party[1],id:party[0].id},...party.slice(2)];
     const invalidAlly=BFGlobalBattleCommandsV2100.queueAll('attack');
     const allyUnchanged=before.every((a,i)=>a===JSON.stringify(party[i].action));
     return {results,invalidAlly,allyUnchanged};
   }finally{S.enemies=enemy;S.party=party;S.target=selected;}
 }""")
 assert len(rejected['results'])==5,rejected
 assert all(x['attack'] is False and x['burst'] is False and
            x['targetUnchanged'] and x['ordersUnchanged']
            for x in rejected['results']),rejected
 assert rejected['invalidAlly'] is False and rejected['allyUnchanged'],rejected
 slots=page.evaluate('BFGlobalBattleCommandsV2100.snapshot().foes.map(e=>e.slot)')
 assert slots
 assert page.evaluate('(slot)=>BFGlobalBattleCommandsV2100.setTarget(slot)',slots[-1]) is True
 assert page.evaluate('S.target')==slots[-1]
 assert page.evaluate('BFGlobalBattleCommandsV2100.setTarget(9999)') is False
 # The player can distribute manual attacks across all live enemies without
 # executing a turn, changing quest progress, or touching the canonical save.
 assert page.locator('#bf2100-spread').is_visible()
 assert page.evaluate('BFGlobalBattleCommandsV2100.spreadAttacks()') is True
 assigned=page.evaluate('S.party.filter(p=>p.active&&p.hp>0).map(p=>[p.action?.kind,p.action?.target])')
 living=page.evaluate('S.enemies.filter(e=>e.hp>0).map(e=>e.slot)')
 assert len(living)>=2
 assert assigned==[['attack',living[i%len(living)]] for i in range(len(assigned))],assigned
 assert not page.evaluate('S.busy')
 # SPREAD READY BB is manual: rotate live native targets while ready
 # player-owned actors use Burst and unready actors queue normal Attack.
 assert page.locator('#bf2100-spread-bb').is_visible()
 page.evaluate("()=>{S.party.forEach((p,i)=>{if(p.active)p.bb=i%2===0?100:0});update()}")
 plan=page.evaluate('BFGlobalBattleCommandsV2100.spreadBurstPlan()')
 assert plan and len(plan)==6,plan
 assert [o['kind'] for o in plan]==['burst','attack']*3,plan
 assert page.evaluate('BFGlobalBattleCommandsV2100.spreadBursts()') is True
 spread_bb=page.evaluate('S.party.filter(p=>p.active&&p.hp>0).map(p=>[p.action?.kind,p.action?.target])')
 assert spread_bb==[[('burst' if i%2==0 else 'attack'),living[i%len(living)]] for i in range(6)],spread_bb
 assert page.evaluate('S.busy') is False
 # A cursed actor must attack instead of spending a prohibited BB.
 cursed=page.evaluate("""()=>{const old=window.BFGlobalCurseBBLockV5900;
   window.BFGlobalCurseBBLockV5900={cursed:id=>id===0};
   try{return {success:BFGlobalBattleCommandsV2100.spreadBursts(),
     kinds:S.party.filter(p=>p.active&&p.hp>0).map(p=>p.action?.kind)}}
   finally{window.BFGlobalCurseBBLockV5900=old}
 }""")
 assert cursed['success'] and cursed['kinds']==['attack','attack','burst','attack','burst','attack'],cursed
 # Paid item reservations become Guard and do not consume a target in rotation.
 reserved=page.evaluate("""()=>{const old=window.BFGlobalItemTurnReservationsV4500;
   window.BFGlobalItemTurnReservationsV4500={snapshot:()=>({reservations:[{slot:1}]})};
   try{return {plan:BFGlobalBattleCommandsV2100.spreadBurstPlan(),
     success:BFGlobalBattleCommandsV2100.spreadBursts(),
     orders:S.party.filter(p=>p.active&&p.hp>0).map(p=>[p.action?.kind,p.action?.target])}}
   finally{window.BFGlobalItemTurnReservationsV4500=old}
 }""")
 assert reserved['success'],reserved
 assert reserved['plan'][1]=={'slot':1,'kind':'guard','target':None},reserved
 assert reserved['orders'][1][0]=='guard',reserved
 assert [o[1] for o in reserved['orders'] if o[0]!='guard']==[living[i%len(living)] for i in range(5)],reserved
 # Corrupt live enemy / duplicate actor rejects the entire queue before clicks.
 rejected_spread=page.evaluate("""()=>{const oldEnemies=S.enemies,oldParty=S.party;
   const selected=S.target,actions=S.party.map(p=>JSON.stringify(p.action));
   const e=S.enemies[0],other={...e,slot:1,hp:80,maxHp:100};
   const bad=[
     [{...e,slot:0,hp:Infinity,maxHp:100},other],
     [{...e,slot:0,hp:'Infinity',maxHp:100},other],
     [{...e,slot:0,hp:20,maxHp:0},other],
     [{...e,slot:1,hp:20,maxHp:100},other],
     [{...e,slot:-1,hp:20,maxHp:100},other]
   ];
   try{
     const failures=bad.map(foes=>{S.enemies=foes;
       return BFGlobalBattleCommandsV2100.spreadBurstPlan()===null&&
         BFGlobalBattleCommandsV2100.spreadBursts()===false&&
         S.target===selected&&actions.every((a,i)=>a===JSON.stringify(S.party[i].action));
     });
     S.enemies=oldEnemies;
     S.party=[oldParty[0],{...oldParty[1],id:oldParty[0].id},...oldParty.slice(2)];
     return {failures,duplicateRejected:BFGlobalBattleCommandsV2100.spreadBursts()===false,
       noActionChange:actions.every((a,i)=>a===JSON.stringify(oldParty[i].action))};
   }finally{S.enemies=oldEnemies;S.party=oldParty;S.target=selected}
 }""")
 assert rejected_spread['failures']==[True]*5,rejected_spread
 assert rejected_spread['duplicateRejected'] and rejected_spread['noActionChange'],rejected_spread
 # After an enemy falls, the native target list may exclude that dead slot
 # instead of retaining a disabled placeholder. The tray must select the
 # intended surviving target through the real native button either way.
 page.evaluate("""()=>{const e=S.enemies[0];
   S.enemies=[{...e,slot:0,name:'Defeated',hp:0,maxHp:100},
              {...e,slot:1,name:'Survivor A',hp:100,maxHp:100},
              {...e,slot:2,name:'Survivor B',hp:200,maxHp:200}];
   update()}""")
 assert page.evaluate('BFGlobalBattleCommandsV2100.setTarget(0)') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.setTarget(2)') is True
 assert page.evaluate('S.target')==2
 assert page.evaluate('BFGlobalBattleCommandsV2100.setTarget(1)') is True
 assert page.evaluate('S.target')==1
 assert page.evaluate('S.enemies[0].hp')==0
 assert page.evaluate('BFGlobalBattleCommandsV2100.spreadAttacks()') is True
 assigned=page.evaluate('S.party.filter(p=>p.active&&p.hp>0).map(p=>[p.action?.kind,p.action?.target])')
 assert assigned==[['attack',1 if i%2==0 else 2] for i in range(len(assigned))],assigned
 assert page.evaluate('S.enemies[0].hp')==0
 # A broken live foe (or duplicate slot) makes the native button-to-enemy
 # mapping unsafe. Fail before clicking, without exposing corrupt temporary
 # records to the browser renderer between evaluation tasks.
 invalid_results=page.evaluate("""()=>{const original=S.enemies;
   const selected=S.target,seed=original[1];
   const good={...seed,slot:2,hp:100,maxHp:200};
   const cases=[
     [{...seed,slot:1,hp:40,maxHp:0},good],
     [{...seed,slot:1,hp:Infinity,maxHp:100},good],
     [{...seed,slot:-1,hp:40,maxHp:100},good],
     [{...seed,slot:2,hp:40,maxHp:100},good],
     [{...seed,slot:1,hp:40,maxHp:undefined},good]
   ];
   try{
     return cases.map(foes=>{
       S.enemies=foes;
       return BFGlobalBattleCommandsV2100.setTarget(2);
     });
   }finally{S.enemies=original;S.target=selected;}
 }""")
 assert invalid_results==[False]*5,invalid_results
 assert page.evaluate('S.enemies[0].hp')==0
 # Source-backed elemental matchup option uses the original 2022 six-element
 # relationship, but never invents unknown demo enemy/ally elements or damage.
 assert page.locator('#bf2100-elements').is_visible()
 assert page.locator('#bf2100-element-bb').is_visible()
 assert page.evaluate('BFGlobalBattleCommandsV2100.elementPlan()') is None
 assert page.evaluate('BFGlobalBattleCommandsV2100.elementBursts()') is False
 assert page.locator('#bf2100-element-bb').is_disabled()
 page.add_script_tag(path=str(A/'bf6900_elemental_combat.js'))
 assert page.evaluate('BFGlobalElementalCombatV6900.normalize("Fire")')=='Fire'
 assert page.evaluate('UNIT_BY_ID.get(10011).element')=='Fire'
 page.evaluate("""()=>{S.party.forEach(p=>{if(p.active)p.unitId=10011});
   S.enemies[1].element='Earth';S.enemies[2].element='Water';update()}""")
 assert page.evaluate('BFGlobalBattleCommandsV2100.elementPlan().length')==6
 assert page.evaluate('BFGlobalBattleCommandsV2100.elementPlan().every(x=>x.target===1&&!x.reserved)')
 assert page.evaluate('BFGlobalBattleCommandsV2100.elementAttacks()') is True
 assigned=page.evaluate('S.party.filter(p=>p.active&&p.hp>0).map(p=>[p.action?.kind,p.action?.target])')
 assert assigned==[['attack',1] for _ in assigned],assigned
 assert not page.evaluate('S.busy')
 # The separate Element + BB option makes real native BB choices for ready
 # allies while preserving the source-confirmed target and manual Execute.
 # With BB unavailable, the remaining living allies still Attack.
 page.evaluate("""()=>{S.party.forEach((p,i)=>p.bb=i===0?100:0);update()}""")
 assert not page.locator('#bf2100-element-bb').is_disabled()
 assert page.evaluate('BFGlobalBattleCommandsV2100.elementBursts()') is True
 ready_orders=page.evaluate('S.party.filter(p=>p.active&&p.hp>0).map(p=>[p.action?.kind,p.action?.target])')
 assert ready_orders==[['burst',1]]+[['attack',1]]*(len(ready_orders)-1),ready_orders
 assert page.evaluate('S.busy') is False
 # Curse-prohibited BBs must fall back to the native Attack button rather
 # than queuing an illegal Burst or auto-executing an unrequested turn.
 curse_fallback=page.evaluate("""()=>{
   const old=window.BFGlobalCurseBBLockV5900;
   window.BFGlobalCurseBBLockV5900={cursed:id=>id===0};
   try{
     return {queued:BFGlobalBattleCommandsV2100.elementBursts(),
       actions:S.party.filter(p=>p.active&&p.hp>0).map(p=>[p.action?.kind,p.action?.target])};
   }finally{window.BFGlobalCurseBBLockV5900=old;}
 }""")
 assert curse_fallback['queued'] is True,curse_fallback
 assert curse_fallback['actions']==[['attack',1]]*6,curse_fallback
 # An unknown source ally must fail before any player orders change.
 saved_orders=page.evaluate('S.party.map(p=>JSON.stringify(p.action))')
 # The live renderer reads UNIT_BY_ID for animation on every RAF. Never
 # expose a deliberately invalid unit ID across separate evaluate calls.
 # Run the negative preflight and immediately restore source identity.
 unknown=page.evaluate("""()=>{const old=S.party[0].unitId;
   const before=S.party.map(p=>JSON.stringify(p.action));
   try{
     S.party[0].unitId=999999;
     return {noPlan:BFGlobalBattleCommandsV2100.elementPlan()===null,
       rejected:BFGlobalBattleCommandsV2100.elementAttacks()===false,
       bbRejected:BFGlobalBattleCommandsV2100.elementBursts()===false,
       unchanged:before.every((order,i)=>order===JSON.stringify(S.party[i].action))};
   }finally{S.party[0].unitId=old;}
 }""")
 assert unknown=={'noPlan':True,'rejected':True,'bbRejected':True,'unchanged':True},unknown
 assert page.evaluate('S.party.map(p=>JSON.stringify(p.action))')==saved_orders
 # With no advantageous foe, the option refuses to overwrite previous orders.
 page.evaluate("S.enemies[1].element='Water';update()")
 assert page.evaluate('BFGlobalBattleCommandsV2100.elementPlan()') is None
 assert page.evaluate('BFGlobalBattleCommandsV2100.elementAttacks()') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.elementBursts()') is False
 assert page.evaluate('S.party.map(p=>JSON.stringify(p.action))')==saved_orders
 # Restore a favorable foe before testing busy / Auto rejection.
 page.evaluate("S.enemies[1].element='Earth';update()")
 # Still only commands queued: this source-level action cannot award rewards.
 assert not page.evaluate('S.busy')
 page.evaluate('S.busy=true')
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("attack")') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.spreadAttacks()') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.spreadBursts()') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("heal")') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.elementAttacks()') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.protectWounded()') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.executeTurn()') is False
 page.evaluate('S.busy=false')
 page.locator('#auto').check()
 assert page.evaluate('BFGlobalBattleCommandsV2100.snapshot().auto') is True
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("guard")') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.spreadAttacks()') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.spreadBursts()') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("heal")') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.elementAttacks()') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.protectWounded()') is False
 page.locator('#auto').uncheck()
 page.evaluate('BFGlobalBattleCommandsV2100.refresh()')
 after=page.evaluate("""()=>({p:JSON.stringify(P),save:localStorage.getItem('bf_global_offline_demo_v7')})""")
 assert before==after,'queue commands cannot change progress or v7 save'
 # Original Execute button still powers shortcut, and cannot execute when incomplete.
 page.evaluate('S.party[0].action=null;update()')
 assert page.evaluate('BFGlobalBattleCommandsV2100.executeTurn()') is False
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("attack")') is True
 # A manually queued attack is checked AGAIN before the separate Execute
 # button. This protects against a KO or stale actor/target after queueing.
 assert page.evaluate('BFGlobalBattleCommandsV2100.queuedAttacksSafe()') is True
 stale_execution=page.evaluate("""()=>{const party=S.party,enemies=S.enemies;
   const before=party.map(p=>JSON.stringify(p.action)),chosen=party[0].action.target;
   const victim=enemies.find(e=>e.slot===chosen&&e.hp>0);
   if(!victim)return {badFixture:true};
   const health=victim.hp;
   try{
     party[0].action.target=99999;
     const invalid=BFGlobalBattleCommandsV2100.queuedAttacksSafe()===false&&
       BFGlobalBattleCommandsV2100.executeTurn()===false;
     party[0].action.target=chosen;
     victim.hp=0;
     const ko=BFGlobalBattleCommandsV2100.queuedAttacksSafe()===false&&
       BFGlobalBattleCommandsV2100.executeTurn()===false;
     victim.hp=health;
     S.party=[party[0],{...party[1],id:party[0].id},...party.slice(2)];
     const duplicate=BFGlobalBattleCommandsV2100.queuedAttacksSafe()===false&&
       BFGlobalBattleCommandsV2100.executeTurn()===false;
     return {invalid,ko,duplicate,
       noTurn:S.busy===false,
       changedOnlyDuringFixture:before.every((a,i)=>a===JSON.stringify(party[i].action))};
   }finally{
     party[0].action.target=chosen;victim.hp=health;S.party=party;
   }
 }""")
 assert stale_execution=={'invalid':True,'ko':True,'duplicate':True,
                          'noTurn':True,'changedOnlyDuringFixture':True},stale_execution
 assert page.evaluate('BFGlobalBattleCommandsV2100.queuedAttacksSafe()') is True
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("guard")') is True
 assert page.evaluate('BFGlobalBattleCommandsV2100.queuedAttacksSafe()') is True
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("attack")') is True
 page.evaluate('for(const e of S.enemies)e.hp=e.maxHp=999999')
 assert page.evaluate('BFGlobalBattleCommandsV2100.executeTurn()') is True
 assert page.evaluate('S.busy') is True
 assert page.evaluate('BFGlobalBattleCommandsV2100.queueAll("attack")') is False
 page.evaluate('reset()')
 assert page.evaluate('S.busy') is False
 assert page.evaluate('P.version')==7
 assert not errors,errors
 browser.close()
print('PASS v21.00: native manual source healing BB, BB spread, Curse/Guard, corrupt foe rejection and v7 save isolation')
