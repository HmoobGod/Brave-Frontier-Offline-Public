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
 const fire=btn('EXECUTE QUEUED TURN','bf2100-execute',()=>executeTurn());
 const foot=document.createElement('small');foot.id='bf2100-info';
 foot.textContent='Optional quick controls use the original demo buttons. Brave Bursts require a full gauge; all other allies attack. Commands do not execute until you choose Execute. No original 2022 combat AI or damage formula is claimed.';
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
   const index=S.enemies.findIndex(e=>e.slot===slot&&e.hp>0);
   if(index<0)return false;
   const nativeButton=targetList.children[index];
   if(!nativeButton||nativeButton.disabled)return false;
   nativeButton.click();signature='';refresh();
   return S.target===slot;
 }
 function queueAll(mode){
   if(!['attack','guard','burst'].includes(mode)||!ready())return false;
   const squad=active();
   if(squad.some(p=>!Number.isInteger(p.id)||!slots.children[p.id]||slots.children[p.id].disabled))return false;
   for(const p of squad){
     const slot=slots.children[p.id];if(!slot||slot.disabled)return false;
     slot.click();
     const command=mode==='guard'?guard:mode==='burst'&&p.bb>=100?burst:attack;
     if(command.disabled)return false;
     command.click();
     if(p.action?.kind!==(command===burst?'burst':command===guard?'guard':'attack'))return false;
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
   attacks.disabled=guards.disabled=bursts.disabled=!st.canQueue;
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
 window.BFGlobalBattleCommandsV2100=Object.freeze({snapshot,refresh,setTarget,queueAll,executeTurn});
})();
