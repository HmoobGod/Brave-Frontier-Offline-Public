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
 const element=btn('ELEMENT ADVANTAGE','bf2100-elements',()=>elementAttacks());
 const fire=btn('EXECUTE QUEUED TURN','bf2100-execute',()=>executeTurn());
 const foot=document.createElement('small');foot.id='bf2100-info';
 foot.textContent='Optional quick controls use the original demo buttons. Spread Attacks distributes allies across living foes. Element Advantage queues normal attacks against enemies with source-verified weaknesses, while keeping the player-selected target for unmatched allies. Paid item reservations keep Guard. Nothing executes until Execute is pressed; unknown elements are never invented.';
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
   const squad=active();
   if(squad.some(p=>!Number.isInteger(p.id)||!slots.children[p.id]||slots.children[p.id].disabled))return false;
   // Preserve the same paid item turns that native Execute already enforces.
   const reservations=window.BFGlobalItemTurnReservationsV4500?.snapshot()?.reservations??[];
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
 function executeTurn(){
   if(!snapshot().canExecute||execute.disabled)return false;
   execute.click();signature='';refresh();return true;
 }
 function refresh(){
   const st=snapshot(),key=JSON.stringify(st);
   if(key===signature)return st;
   signature=key;
   status.textContent='Wave '+(st.wave+1)+' · Round '+st.round+
     ' · '+st.queued+'/'+st.alive+' commands ready · '+st.bbReady+' BB ready'+
     (st.auto?' · Auto Battle enabled':'');
   attacks.disabled=guards.disabled=bursts.disabled=spread.disabled=!st.canQueue;
   element.disabled=!elementPlan();
   fire.disabled=!st.canExecute;
   const group=document.createDocumentFragment();
   for(const e of st.foes){
     const b=document.createElement('button');b.type='button';
     b.textContent=e.name+' · '+e.hp+'/'+e.maxHp+' HP';
     b.setAttribute('aria-pressed',String(e.slot===st.selected));
     b.disabled=!st.canQueue;b.dataset.bf2100Target=String(e.slot);
     b.addEventListener('click',()=>setTarget(e.slot));group.append(b);
   }
   targets.replaceChildren(group);return st;
 }
 new MutationObserver(refresh).observe(document.getElementById('meta')||area,
   {subtree:true,childList:true,characterData:true});
 document.querySelector('.bf-navbar')?.addEventListener('click',refresh);
 window.setInterval(()=>{if(!document.hidden)refresh()},800);
 refresh();
 window.BFGlobalBattleCommandsV2100=Object.freeze({snapshot,refresh,setTarget,queueAll,spreadAttacks,elementPlan,elementAttacks,executeTurn});
})();
