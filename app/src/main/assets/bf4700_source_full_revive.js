/* BF_GLOBAL_SOURCE_FULL_REVIVE_ITEM_V4700 */
(() => {
 'use strict';
 // Original source item #52400 fully restores one incapacitated ally.
 // Session stock, Guard reservation, and newly revived turn lock are DEMO.
 const turns=window.BFGlobalItemTurnReservationsV4500;
 if(window.BFGlobalSourceFullReviveV4700||!turns||
    !window.BFGlobalSourceBBGaugeItemV4600||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof update!=='function'||typeof msg!=='function')return;
 const parent=document.getElementById('bf4200-items');
 const execute=document.getElementById('execute');
 const mode=document.getElementById('mode');
 if(!parent||!execute||!mode)return;
 const source=Object.freeze({
   file:'3-mst-translated/F_ITEM_MST_Ver1027.json',
   sha256:'0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474',
   itemId:52400,name:'復活薬',battleEffectGroupId:610,
   targetType:1,itemTargetArea:1,skillTypeId:12,
   passiveSkillInfo:'100',itemMaxEquipped:2,itemMaxStack:99,
   effect:'Revive one KO ally with full HP'
 });
 const css=document.createElement('style');css.id='bf4700-style';
 css.textContent=[
   '#bf4700-revive{margin:9px 0 0;padding:9px;border:1px solid #e0be8d;',
   'border-radius:6px;background:#3d2832}',
   '#bf4700-revive summary{cursor:pointer;font:700 13px Georgia,serif;',
   'min-height:34px;padding:5px 0}',
   '#bf4700-revive[hidden]{display:none!important}',
   '#bf4700-ref{color:#ffe4bc}'
 ].join('');document.head.append(css);
 const panel=document.createElement('details');panel.id='bf4700-revive';
 const head=document.createElement('summary');
 head.textContent='ORIGINAL FULL-HP REVIVE · EXPERIMENTAL';
 const ref=document.createElement('small');ref.id='bf4700-ref';
 ref.textContent='Archived 2022 item #52400 · '+source.name+
   ' · authentic effect: recover one KO ally to full HP.';
 const stock=document.createElement('strong');stock.id='bf4700-stock';
 const actor=document.createElement('select');actor.id='bf4700-actor';
 actor.setAttribute('aria-label','Choose living unit to use full revive');
 const target=document.createElement('select');target.id='bf4700-target';
 target.setAttribute('aria-label','Choose knocked-out ally to revive');
 const use=document.createElement('button');use.type='button';use.id='bf4700-use';
 use.textContent='REVIVE ONE KO ALLY TO FULL HP · DEMO GUARD TURN';
 const note=document.createElement('small');
 note.textContent='Full-HP restoration is sourced; one temporary DEMO charge and both actor/recipient Guard locks are not original timing rules. No saved item inventory is consumed.';
 panel.append(head,ref,stock,actor,target,use,note);parent.append(panel);
 let battle=S,round=S.round,remaining=1,last='';
 const revived=new Map();
 function sync(){
   if(S!==battle){
     battle=S;round=S.round;remaining=1;revived.clear();last='';
   }else if(S.round!==round){
     round=S.round;revived.clear();last='';
   }
 }
 function allowed(){
   return S.mode==='archive'&&!S.busy&&!S.over&&!S.auto&&remaining>0;
 }
 function canAct(i){
   const p=S.party?.[i];
   return Number.isInteger(i)&&i>=0&&i<6&&!!p&&p.active&&
      p.hp>0&&!p.action&&turns.free(i);
 }
 function canRevive(i){
   const p=S.party?.[i];
   return Number.isInteger(i)&&i>=0&&i<6&&!!p&&p.active&&
      p.hp<=0&&Number.isFinite(p.maxHp)&&p.maxHp>0;
 }
 function snapshot(){
   sync();
   const actors=Array.from({length:6},(_,i)=>i).filter(canAct);
   const targets=Array.from({length:6},(_,i)=>i).filter(canRevive);
   return Object.freeze({source,remaining,round:S.round,
     eligibleActors:Object.freeze(actors),eligibleRecipients:Object.freeze(targets),
     available:allowed()&&actors.length>0&&targets.length>0,
     revivedThisRound:Object.freeze(Array.from(revived.keys()))});
 }
 function refresh(){
   const info=snapshot();
   panel.hidden=S.mode!=='archive';
   const key=JSON.stringify({mode:S.mode,round:S.round,remain:remaining,
     busy:S.busy,auto:S.auto,over:S.over,party:S.party?.map(p=>[
       p.name,p.active,p.hp,p.maxHp,p.action?.kind||null
     ]),locked:turns.snapshot().reservations});
   if(key===last)return info;last=key;
   function rebuild(select,ids){
     const previous=select.value;
     select.replaceChildren(...ids.map(i=>{
       const option=document.createElement('option');option.value=String(i);
       option.textContent=(i+1)+'. '+S.party[i].name;return option;
     }));
     if(ids.some(i=>String(i)===previous))select.value=previous;
   }
   rebuild(actor,info.eligibleActors);
   rebuild(target,info.eligibleRecipients);
   stock.textContent='Temporary full-revive charges: '+remaining+' / 1';
   use.disabled=!info.available;
   actor.disabled=use.disabled;target.disabled=use.disabled;
   return info;
 }
 function useFullRevive(actorId,targetId){
   sync();
   if(!allowed()||!canAct(actorId)||!canRevive(targetId))return false;
   if(!turns.reserve(actorId,'full-revive-demo'))return false;
   const caster=S.party[actorId],ally=S.party[targetId];
   ally.hp=ally.maxHp;
   // A resurrected ally also loses its DEMO action this round, including
   // eligibility for other temporary items after manual command clearing.
   turns.reserve(targetId,'revived-recipient-demo');
   // The revived ally cannot gain an attack in this DEMO round.
   ally.action={kind:'guard',target:S.target};
   revived.set(targetId,S.round);
   caster.action={kind:'guard',target:S.target};
   remaining=0;
   msg('SOURCE 2022 item #52400: '+ally.name+' revived to full HP. '+
       caster.name+' and revived ally Guard this DEMO round.');
   update();last='';refresh();return true;
 }
 function enforceRevivedGuards(){
   sync();
   if(S.mode!=='archive'||S.over)return;
   for(const [slot,atRound] of revived){
     const p=S.party?.[slot];
     if(atRound===S.round&&p?.active&&p.hp>0)
       p.action={kind:'guard',target:S.target};
   }
 }
 use.addEventListener('click',()=>useFullRevive(Number(actor.value),Number(target.value)));
 execute.addEventListener('click',enforceRevivedGuards,true);
 mode.addEventListener('change',refresh);
 window.setInterval(()=>{if(!document.hidden)refresh()},850);
 window.BFGlobalSourceFullReviveV4700=Object.freeze({
   source,snapshot,refresh,useFullRevive,enforceRevivedGuards
 });
 refresh();
})();
