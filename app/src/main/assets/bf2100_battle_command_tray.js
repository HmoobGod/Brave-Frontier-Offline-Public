/* BF_GLOBAL_BATTLE_COMMAND_TRAY_V2100 */
(() => {
 'use strict';
 if(window.BFGlobalBattleCommandsV2100 || !window.BFGlobalStoryBattleV2000 ||
    typeof S==='undefined'||typeof P==='undefined'||P.version!==7)return;
 const area=document.querySelector('.actionbar');
 const slots=document.getElementById('slots');
 const targetList=document.getElementById('targets');
 const attack=document.getElementById('attack');
 const guard=document.getElementById('guard');
 const burst=document.getElementById('burst');
 const execute=document.getElementById('execute');
 const auto=document.getElementById('auto');
 const battle=document.getElementById('battle');
 if(!area||!slots||!targetList||!attack||!guard||!burst||!execute||!auto||!battle)return;
 const css=document.createElement('style');css.id='bf2100-style';
 css.textContent=[
  '#bf2100-tray{padding:11px;margin:10px 0;border:1px solid #a88b59;',
  'border-radius:8px;background:#1b3044;color:#f5e9d4;font:12px/1.5 system-ui,sans-serif}',
  '#bf2100-tray h3{font:800 15px Georgia,serif;margin:0 0 5px;color:#ffe4b7}',
  '#bf2100-status{margin:5px 0;font-weight:700}',
  '#bf2100-targets{display:flex;flex-wrap:wrap;gap:6px;margin:9px 0}',
  '#bf2100-targets button{padding:6px 8px;background:#243c54;color:#fff;',
  'border:1px solid #74869c;border-radius:5px;min-height:37px}',
  '#bf2100-targets button[aria-pressed=true]{border-color:#f6d786;outline:1px solid #f6d786}',
  '#bf2100-buttons{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}',
  '#bf2100-buttons button{padding:8px 5px;min-height:44px;background:#6d4e2d;',
  'border:1px solid #bba06e;border-radius:5px;color:white;font-weight:bold}',
  '#bf2100-buttons button:disabled,#bf2100-targets button:disabled{opacity:.45}',
  '#bf2100-info{display:block;margin-top:7px;color:#cad6df}'
 ].join('');document.head.append(css);
 const panel=document.createElement('section');panel.id='bf2100-tray';
 panel.setAttribute('aria-label','Squad battle command shortcuts');
 const title=document.createElement('h3');title.textContent='SQUAD COMMANDS · DEMO COMBAT';
 const status=document.createElement('p');status.id='bf2100-status';
 status.setAttribute('aria-live','polite');
 const targets=document.createElement('div');targets.id='bf2100-targets';
 targets.setAttribute('role','group');targets.setAttribute('aria-label','Choose demo enemy target');
 const actions=document.createElement('div');actions.id='bf2100-buttons';
 const btn=(label,id,callback)=>{
   const b=document.createElement('button');b.type='button';b.id=id;
   b.textContent=label;b.addEventListener('click',callback);actions.append(b);return b;
 };
 const attacks=btn('QUEUE ALL ATTACKS','bf2100-attacks',()=>queueAll('attack'));
 const guards=btn('QUEUE ALL GUARDS','bf2100-guards',()=>queueAll('guard'));
 const bursts=btn('READY BB + ATTACK','bf2100-bursts',()=>queueAll('burst'));
 const spread=btn('SPREAD ATTACKS','bf2100-spread',()=>spreadAttacks());
 const spreadBB=btn('SPREAD READY BB','bf2100-spread-bb',()=>spreadBursts());
 const element=btn('ELEMENT ADVANTAGE','bf2100-elements',()=>elementAttacks());
 const elementBB=btn('ELEMENT + BB IF READY','bf2100-element-bb',()=>elementBursts());
 const protect=btn('PROTECT WOUNDED · 40% HP','bf2100-protect',()=>protectWounded());
 const fire=btn('EXECUTE QUEUED TURN','bf2100-execute',()=>executeTurn());
 const foot=document.createElement('small');foot.id='bf2100-info';
 foot.textContent='Optional demo shortcuts use native player controls. Spread Attacks distributes targets; Spread Ready BB distributes ready Brave Bursts and Attacks; Element Advantage uses source-known weaknesses, with an optional ready-BB variant. Protect Wounded Guards living allies at or below 40% HP and queues normal attacks for healthier allies. Paid item turns still Guard. Nothing executes until you choose Execute. No original 2022 enemy AI or damage formula is claimed.';
 panel.append(title,status,targets,actions,foot);area.before(panel);
 let signature='';
 const active=()=>Array.isArray(S.party)?S.party.filter(p=>p&&p.active&&p.hp>0):[];
 const enemies=()=>Array.isArray(S.enemies)?S.enemies.filter(e=>e&&e.hp>0):[];
 const ready=()=>!S.busy&&!S.over&&!S.auto&&active().length>0&&enemies().length>0;
 function snapshot(){
   const squad=active(),foes=enemies();
   return Object.freeze({
     missionId:typeof QUEST!=='undefined'?QUEST.missionId:null,
     wave:S.wave,round:S.round,busy:!!S.busy,over:!!S.over,auto:!!S.auto,
     selected:S.target,foes:foes.map(e=>Object.freeze({slot:e.slot,name:e.name,hp:e.hp,maxHp:e.maxHp})),
     alive:squad.length,queued:squad.filter(p=>!!p.action).length,
     bbReady:squad.filter(p=>p.bb>=100).length,canQueue:ready(),
     canExecute:!S.busy&&!S.over&&!S.auto&&squad.length>0&&squad.every(p=>!!p.action)
   });
 }
 function setTarget(slot){
   if(!ready()||!Number.isInteger(slot))return false;
   // The core may render only living enemy buttons after a KO, or retain
   // disabled placeholders for defeated enemies. Never map a surviving
   // enemy slot through an unverified index in the wrong button list.
   const all=Array.isArray(S.enemies)?S.enemies:[];
   // Recheck the entire live target roster before translating native button
   // indices. A corrupt/duplicate live slot makes its mapping ambiguous even
   // if the requested target happens to be valid.
   const living=all.filter(e=>e&&e.hp>0);
   if(living.some(e=>!Number.isFinite(e.hp)||!Number.isFinite(e.maxHp)||
      e.maxHp<=0||!Number.isSafeInteger(e.slot)||e.slot<0)||
      new Set(living.map(e=>e.slot)).size!==living.length||
      !living.some(e=>e.slot===slot))return false;
   const rendered=Array.from(targetList.children);
   if(!rendered.every(b=>b.tagName==='BUTTON'))return false;
   const source=rendered.length===all.length?all:
     rendered.length===living.length?living:null;
   if(!source)return false;
   const index=source.findIndex(e=>e?.slot===slot&&e.hp>0);
   const nativeButton=index>=0?rendered[index]:null;
   if(!nativeButton||nativeButton.disabled)return false;
   nativeButton.click();signature='';refresh();
   return S.target===slot;
 }
 function queueAll(mode){
   if(!['attack','guard','burst'].includes(mode)||!ready())return false;
   const squad=active(),ids=squad.map(p=>p.id);
   // Prevent a duplicate or malformed player slot from receiving two orders
   // while a different living teammate is left unqueued.
   if(squad.some(p=>!Number.isSafeInteger(p.id)||p.id<0||
      !Number.isFinite(p.hp)||!Number.isFinite(p.maxHp)||p.maxHp<=0||
      !slots.children[p.id]||slots.children[p.id].disabled)||
      new Set(ids).size!==ids.length)return false;
   // Offensive queue shortcuts rely on the native enemy slot map. An invalid
   // living foe must cancel the WHOLE operation before any ally order changes.
   // Guard-only commands retain their original defensive behavior.
   if(mode!=='guard'){
     if(!Array.isArray(S.enemies))return false;
     const living=S.enemies.filter(e=>e&&e.hp>0);
     if(S.enemies.some(e=>e&&e.hp>0&&!Number.isFinite(e.hp))||
        !living.length||living.some(e=>!Number.isFinite(e.hp)||
          !Number.isFinite(e.maxHp)||e.maxHp<=0||
          !Number.isSafeInteger(e.slot)||e.slot<0)||
        new Set(living.map(e=>e.slot)).size!==living.length)return false;
     // The queue must use a currently living, enabled native target button.
     // Otherwise a stale selected slot (e.g. the enemy KO'd last turn) could
     // silently queue the squad against an enemy that cannot be attacked.
     if(!Number.isSafeInteger(S.target)||S.target<0||
        !living.some(e=>e.slot===S.target))return false;
     const rendered=Array.from(targetList.children);
     if(!rendered.every(b=>b.tagName==='BUTTON'))return false;
     const mapped=rendered.length===S.enemies.length?S.enemies:
       rendered.length===living.length?living:null;
     const position=mapped?.findIndex(e=>e?.slot===S.target&&e.hp>0)??-1;
     if(position<0||!rendered[position]||rendered[position].disabled)return false;
   }
   // Preserve paid item turns, validating the optional reservation snapshot
   // before issuing any native player click.
   const reservations=window.BFGlobalItemTurnReservationsV4500?.snapshot()?.reservations??[];
   if(!Array.isArray(reservations)||reservations.some(r=>
       !Number.isSafeInteger(r?.slot)||r.slot<0))return false;
   const reserved=new Set(reservations.map(r=>r.slot));
   for(const p of squad){
     const slot=slots.children[p.id];if(!slot||slot.disabled)return false;
     slot.click();
     // Curse already rejects the native BB click. Use Attack instead so a
     // blocked burst does not leave the rest of the squad partially queued.
     const canBurst=p.bb>=100&&window.BFGlobalCurseBBLockV5900?.cursed(p.id)!==true;
     const command=mode==='guard'||reserved.has(p.id)?guard:mode==='burst'&&canBurst?burst:attack;
     if(command.disabled)return false;
     command.click();
     if(p.action?.kind!==(command===burst?'burst':command===guard?'guard':'attack'))return false;
   }
   signature='';refresh();return true;
 }
 // Manually spread single-target attacks around surviving foes instead of
 // focusing every ally on the same enemy. Use only the native player buttons.
 // Existing item-turn reservations keep their Guard actions, and no turn is
 // executed without the player's separate Execute command.
 // Player manual split-target BB plan. Plan the COMPLETE live roster and
 // owned squad before pressing any native player buttons. No hidden Execute,
 // AI changes, save writes, or speculative original 2022 combat math.
 function spreadBurstPlan(){
   if(!ready()||S.mode!=='archive'||!Array.isArray(S.enemies))return null;
   const all=S.enemies;
   if(all.some(e=>e&&e.hp>0&&!Number.isFinite(e.hp)))return null;
   const living=all.filter(e=>e&&Number.isFinite(e.hp)&&e.hp>0);
   if(!living.length||living.some(e=>!Number.isFinite(e.maxHp)||e.maxHp<=0||
       !Number.isSafeInteger(e.slot)||e.slot<0)||
       new Set(living.map(e=>e.slot)).size!==living.length)return null;
   const rendered=Array.from(targetList.children);
   if(!rendered.every(b=>b.tagName==='BUTTON'))return null;
   const source=rendered.length===all.length?all:
     rendered.length===living.length?living:null;
   if(!source)return null;
   const squad=active(),ids=squad.map(p=>p.id);
   if(!squad.length||squad.some(p=>!Number.isSafeInteger(p.id)||p.id<0||
       !Number.isFinite(p.hp)||!Number.isFinite(p.maxHp)||p.maxHp<=0||
       !slots.children[p.id]||slots.children[p.id].disabled)||
       new Set(ids).size!==ids.length)return null;
   const reservations=window.BFGlobalItemTurnReservationsV4500?.snapshot()?.reservations??[];
   if(!Array.isArray(reservations)||reservations.some(r=>
       !Number.isSafeInteger(r?.slot)||r.slot<0))return null;
   const reserved=new Set(reservations.map(r=>r.slot));
   let index=0;
   const orders=[];
   for(const p of squad){
     if(reserved.has(p.id)){
       if(guard.disabled)return null;
       orders.push(Object.freeze({slot:p.id,kind:'guard',target:null}));
       continue;
     }
     const foe=living[index++%living.length];
     const nativeIndex=source.findIndex(e=>e?.slot===foe.slot&&e.hp>0);
     if(nativeIndex<0||!rendered[nativeIndex]||rendered[nativeIndex].disabled)
       return null;
     const canBurst=Number.isFinite(p.bb)&&p.bb>=100&&
       window.BFGlobalCurseBBLockV5900?.cursed(p.id)!==true;
     orders.push(Object.freeze({slot:p.id,kind:canBurst?'burst':'attack',
       target:foe.slot}));
   }
   return Object.freeze(orders);
 }
 function spreadBursts(){
   const plan=spreadBurstPlan();
   if(!plan)return false;
   for(const order of plan){
     if(!ready())return false;
     if(order.target!==null&&!setTarget(order.target))return false;
     const slot=slots.children[order.slot];
     if(!slot||slot.disabled)return false;
     slot.click();
     // Native BB readiness is rechecked after selecting each actual actor.
     // If BB becomes disabled, use an ordinary Attack; never force a burst.
     const kind=order.kind==='burst'&&burst.disabled?'attack':order.kind;
     const command=kind==='guard'?guard:kind==='burst'?burst:attack;
     if(command.disabled)return false;
     command.click();
     const p=S.party.find(u=>u?.id===order.slot);
     if(!p||p.action?.kind!==kind||
         (kind!=='guard'&&p.action.target!==order.target))return false;
   }
   signature='';refresh();return true;
 }
 function spreadAttacks(){
   if(!ready()||!Array.isArray(S.enemies))return false;
   const squad=active(),living=enemies();
   if(!living.length||living.some(e=>!Number.isFinite(e.hp)||e.hp<=0||
      !Number.isFinite(e.maxHp)||e.maxHp<=0||
      !Number.isSafeInteger(e.slot)||e.slot<0))return false;
   if(new Set(living.map(e=>e.slot)).size!==living.length)return false;
   if(squad.some(p=>!Number.isSafeInteger(p.id)||p.id<0||
      !slots.children[p.id]||slots.children[p.id].disabled))return false;
   const reservations=window.BFGlobalItemTurnReservationsV4500?.snapshot()?.reservations??[];
   if(!Array.isArray(reservations))return false;
   const reserved=new Set(reservations.map(r=>r.slot));
   let attackIndex=0;
   for(const p of squad){
     if(!ready())return false;
     if(!reserved.has(p.id)){
       const target=living[attackIndex%living.length];
       if(!setTarget(target.slot))return false;
       attackIndex++;
     }
     const slot=slots.children[p.id];if(!slot||slot.disabled)return false;
     slot.click();
     const command=reserved.has(p.id)?guard:attack;
     if(command.disabled)return false;
     command.click();
     if(p.action?.kind!==(command===guard?'guard':'attack'))return false;
     if(command===attack&&p.action.target!==living[(attackIndex-1)%living.length].slot)
       return false;
   }
   signature='';refresh();return true;
 }
 // Optional source-backed elemental matchup planner for the PLAYER squad.
 // Never infer a demo foe's missing type or change enemy AI/damage rules.
 // Preflight the entire plan before clicking any native player command.
 function elementPlan(){
   const element=window.BFGlobalElementalCombatV6900;
   if(!ready()||S.mode!=='archive'||!element||
      typeof element.normalize!=='function'||
      typeof element.multiplier!=='function'||
      typeof UNIT_BY_ID==='undefined'||typeof UNIT_BY_ID.get!=='function'||
      !Array.isArray(S.enemies))return null;
   const squad=active(),all=S.enemies,living=enemies();
   // The native slot map includes every living record; silently excluding
   // Infinity / coercible HP would permit a partially mapped player turn.
   if(all.some(e=>e&&e.hp>0&&!Number.isFinite(e.hp)))return null;
   if(living.some(e=>!Number.isFinite(e.hp)||e.hp<=0||
      !Number.isFinite(e.maxHp)||e.maxHp<=0||
      !Number.isSafeInteger(e.slot)||e.slot<0))return null;
   if(!living.length||new Set(living.map(e=>e.slot)).size!==living.length)return null;
   const rendered=Array.from(targetList.children);
   if(!rendered.every(b=>b.tagName==='BUTTON'))return null;
   const source=rendered.length===all.length?all:
     rendered.length===living.length?living:null;
   if(!source)return null;
   const reservations=window.BFGlobalItemTurnReservationsV4500?.snapshot()?.reservations??[];
   if(!Array.isArray(reservations)||reservations.some(r=>!Number.isSafeInteger(r.slot)))return null;
   const reserved=new Set(reservations.map(r=>r.slot));
   const ids=squad.map(p=>p.id);
   if(new Set(ids).size!==ids.length||squad.some(p=>
      !Number.isFinite(p.hp)||!Number.isFinite(p.maxHp)||p.maxHp<=0))
     return null;
   const plan=[];
   let advantageous=false;
   for(const p of squad){
     if(!Number.isSafeInteger(p.id)||p.id<0||
        !slots.children[p.id]||slots.children[p.id].disabled)return null;
     if(reserved.has(p.id)){
       plan.push(Object.freeze({slot:p.id,target:null,reserved:true}));continue;
     }
     const allyType=element.normalize(UNIT_BY_ID.get(p.unitId)?.element);
     if(!allyType)return null;
     const matches=living.filter(e=>element.normalize(e.element)&&
       element.multiplier(allyType,e.element)===1.5);
     matches.sort((a,b)=>a.hp-b.hp||a.slot-b.slot);
     const chosen=matches[0]||living.find(e=>e.slot===S.target);
     if(!chosen)return null;
     if(matches.length)advantageous=true;
     const index=source.findIndex(e=>e?.slot===chosen.slot&&e.hp>0);
     if(index<0||!rendered[index]||rendered[index].disabled)return null;
     plan.push(Object.freeze({slot:p.id,target:chosen.slot,reserved:false}));
   }
   return advantageous?Object.freeze(plan):null;
 }
 function elementAttacks(){
   const plan=elementPlan();
   if(!plan)return false;
   for(const order of plan){
     if(!ready())return false;
     if(!order.reserved&&!setTarget(order.target))return false;
     const slot=slots.children[order.slot];if(!slot||slot.disabled)return false;
     slot.click();
     const command=order.reserved?guard:attack;
     if(command.disabled)return false;
     command.click();
     const p=S.party.find(u=>u?.id===order.slot);
     if(!p||p.action?.kind!==(order.reserved?'guard':'attack')||
        (!order.reserved&&p.action.target!==order.target))return false;
   }
   signature='';refresh();return true;
 }
 // Optional manual elemental action: keep each ally's verified source
 // weakness target while issuing their native BB if the ready, noncursed
 // action is legal. Unknown BB status falls back to Attack. Item-turn
 // reservations continue to Guard; no turn is auto-executed.
 function elementBursts(){
   const plan=elementPlan();
   if(!plan)return false;
   for(const order of plan){
     if(!ready())return false;
     if(!order.reserved&&!setTarget(order.target))return false;
     const slot=slots.children[order.slot];if(!slot||slot.disabled)return false;
     slot.click();
     const p=S.party.find(u=>u?.id===order.slot);
     if(!p)return false;
     const canBurst=!order.reserved&&Number.isFinite(p.bb)&&p.bb>=100&&
       window.BFGlobalCurseBBLockV5900?.cursed(p.id)!==true&&!burst.disabled;
     const command=order.reserved?guard:canBurst?burst:attack;
     if(command.disabled)return false;
     command.click();
     if(p.action?.kind!==(command===guard?'guard':command===burst?'burst':'attack')||
        (!order.reserved&&p.action.target!==order.target))return false;
   }
   signature='';refresh();return true;
 }
 // Manual defensive turn planner. Use only existing native player Guard and
 // Attack buttons; do not modify HP, turn outcome, enemy AI or rewards.
 // Read-only planning keeps the UI refresh path free of hidden battle clicks.
 function woundedPlan(){
   if(!ready()||!Array.isArray(S.party)||!Array.isArray(S.enemies))return null;
   const squad=active(),ids=squad.map(p=>p.id);
   if(squad.some(p=>!Number.isFinite(p.hp)||!Number.isFinite(p.maxHp)||
      p.maxHp<=0||!Number.isSafeInteger(p.id)||p.id<0||
      !slots.children[p.id]||slots.children[p.id].disabled)||
      new Set(ids).size!==ids.length)return null;
   const wounded=new Set(squad.filter(p=>p.hp/p.maxHp<=0.40).map(p=>p.id));
   if(!wounded.size)return null; // Normal Queue All Attacks covers healthy squads.
   const reservations=window.BFGlobalItemTurnReservationsV4500?.snapshot()?.reservations??[];
   if(!Array.isArray(reservations)||reservations.some(r=>!Number.isSafeInteger(r.slot)||
      r.slot<0))return null;
   const reserved=new Set(reservations.map(r=>r.slot));
   const orders=squad.map(p=>Object.freeze({slot:p.id,
      kind:wounded.has(p.id)||reserved.has(p.id)?'guard':'attack'}));
   if(orders.some(order=>order.kind==='attack')){
     // Match native target button shape without pressing any controls yet.
     const all=S.enemies,living=enemies();
     if(!living.length||living.some(e=>!Number.isFinite(e.hp)||!Number.isFinite(e.maxHp)||
       e.maxHp<=0||!Number.isSafeInteger(e.slot)||e.slot<0)||
       new Set(living.map(e=>e.slot)).size!==living.length)return null;
     const rendered=Array.from(targetList.children);
     if(!rendered.every(b=>b.tagName==='BUTTON'))return null;
     const source=rendered.length===all.length?all:
       rendered.length===living.length?living:null;
     const index=source?.findIndex(e=>e?.slot===S.target&&e.hp>0)??-1;
     if(index<0||!rendered[index]||rendered[index].disabled)return null;
   }
   return Object.freeze({target:S.target,orders:Object.freeze(orders)});
 }
 function protectWounded(){
   const plan=woundedPlan();
   if(!plan)return false;
   if(plan.orders.some(order=>order.kind==='attack')&&!setTarget(plan.target))
     return false;
   for(const order of plan.orders){
     if(!ready())return false;
     const slot=slots.children[order.slot],command=order.kind==='guard'?guard:attack;
     if(!slot||slot.disabled||command.disabled)return false;
     slot.click();command.click();
     const p=S.party.find(u=>u?.id===order.slot);
     if(!p||p.action?.kind!==order.kind||
        (order.kind==='attack'&&p.action.target!==plan.target))return false;
   }
   signature='';refresh();return true;
 }
 // The separate Execute shortcut is a second safety boundary. A living
 // foe may have been KO'd or a party command changed after it was queued.
 // Preserve the native Execute button for valid manual Guard, item and BB
 // turns; reject only demonstrably stale normal-attack target mappings.
 function queuedAttacksSafe(){
   if(!snapshot().canExecute||!Array.isArray(S.party)||!Array.isArray(S.enemies))
     return false;
   const squad=active(),ids=squad.map(p=>p.id);
   if(!squad.length||squad.some(p=>!Number.isSafeInteger(p.id)||p.id<0||
      S.party[p.id]!==p||!p.action||!Number.isFinite(p.hp)||p.hp<=0||
      !Number.isFinite(p.maxHp)||p.maxHp<=0)||
      new Set(ids).size!==squad.length)return false;
   const offensive=squad.filter(p=>p.action.kind==='attack');
   if(!offensive.length)return true;
   const all=S.enemies;
   if(all.some(e=>e&&e.hp>0&&!Number.isFinite(e.hp)))return false;
   const living=all.filter(e=>e&&Number.isFinite(e.hp)&&e.hp>0);
   if(!living.length||living.some(e=>!Number.isFinite(e.maxHp)||e.maxHp<=0||
      !Number.isSafeInteger(e.slot)||e.slot<0)||
      new Set(living.map(e=>e.slot)).size!==living.length)return false;
   const rendered=Array.from(targetList.children);
   if(!rendered.every(b=>b.tagName==='BUTTON'))return false;
   const mapped=rendered.length===all.length?all:
     rendered.length===living.length?living:null;
   if(!mapped)return false;
   return offensive.every(p=>{
     const target=p.action.target;
     if(!Number.isSafeInteger(target)||target<0)return false;
     const idx=mapped.findIndex(e=>e?.slot===target&&e.hp>0);
     return idx>=0&&!!rendered[idx]&&!rendered[idx].disabled;
   });
 }
 function executeTurn(){
   if(!queuedAttacksSafe()||execute.disabled)return false;
   execute.click();signature='';refresh();return true;
 }
 function refresh(){
   const st=snapshot(),key=JSON.stringify([st,active().map(p=>[p.id,p.hp,p.maxHp])]);
   if(key===signature)return st;
   signature=key;
   status.textContent='Wave '+(st.wave+1)+' · Round '+st.round+
     ' · '+st.queued+'/'+st.alive+' commands ready · '+st.bbReady+' BB ready'+
     (st.auto?' · Auto Battle enabled':'');
   attacks.disabled=guards.disabled=bursts.disabled=spread.disabled=!st.canQueue;
   spreadBB.disabled=!spreadBurstPlan();
   fire.disabled=!st.canExecute;
   const group=document.createDocumentFragment();
   for(const e of st.foes){
     const b=document.createElement('button');b.type='button';
     b.textContent=e.name+' · '+e.hp+'/'+e.maxHp+' HP';
     b.setAttribute('aria-pressed',String(e.slot===st.selected));
     b.disabled=!st.canQueue;b.dataset.bf2100Target=String(e.slot);
     b.addEventListener('click',()=>setTarget(e.slot));group.append(b);
   }
   targets.replaceChildren(group);
   // Plan validation requires the current native target buttons, not the
   // previous render. Ally HP is part of the refresh key above so crossing
   // the wounded threshold updates the button without a round change.
   const elementReady=!!elementPlan();
   element.disabled=elementBB.disabled=!elementReady;
   protect.disabled=!woundedPlan();
   return st;
 }
 new MutationObserver(refresh).observe(document.getElementById('meta')||area,
   {subtree:true,childList:true,characterData:true});
 document.querySelector('.bf-navbar')?.addEventListener('click',refresh);
 window.setInterval(()=>{if(!document.hidden)refresh()},800);
 refresh();
 window.BFGlobalBattleCommandsV2100=Object.freeze({snapshot,refresh,setTarget,queueAll,spreadAttacks,spreadBurstPlan,spreadBursts,elementPlan,elementAttacks,elementBursts,woundedPlan,protectWounded,queuedAttacksSafe,executeTurn});
})();
