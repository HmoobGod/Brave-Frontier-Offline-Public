/* BF_GLOBAL_SOURCE_ATK_ITEM_V4400 */
(() => {
 'use strict';
 if(window.BFGlobalSourceAtkItemV4400||
    !window.BFGlobalSourcePartyHealV4300||
    !window.BFGlobalDemoPotionV4200||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof update!=='function'||typeof msg!=='function'||
    typeof currentAtkBoost!=='function')return;
 const parent=document.getElementById('bf4200-items');
 const execute=document.getElementById('execute');
 const mode=document.getElementById('mode');
 if(!parent||!execute||!mode)return;
 const source=Object.freeze({
   file:'3-mst-translated/F_ITEM_MST_Ver1027.json',
   sha256:'0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474',
   itemId:20400,name:'強化薬',effectGroupId:400,
   targetType:1,itemTargetArea:1,itemMaxEquipped:10,
   atkPercent:30,durationTurns:3
 });
 const css=document.createElement('style');css.id='bf4400-style';
 css.textContent=[
  '#bf4400-item{margin:9px 0 0;padding:9px;border:1px solid #b8a47b;',
  'border-radius:6px;background:#3c3328}',
  '#bf4400-item summary{cursor:pointer;font:700 13px Georgia,serif;',
  'min-height:34px;padding:5px 0}',
  '#bf4400-item[hidden]{display:none!important}',
  '#bf4400-reference{color:#f0e0bd}'
 ].join('');document.head.append(css);
 const panel=document.createElement('details');panel.id='bf4400-item';
 const heading=document.createElement('summary');
 heading.textContent='ORIGINAL ATK +30% ITEM · EXPERIMENTAL';
 const sourceLabel=document.createElement('small');sourceLabel.id='bf4400-reference';
 sourceLabel.textContent='Archived 2022 item #20400 · '+source.name+
   ' · source effect: +30% ATK to one ally for 3 turns.';
 const status=document.createElement('strong');status.id='bf4400-status';
 const actor=document.createElement('select');actor.id='bf4400-actor';
 actor.setAttribute('aria-label','Choose unit to spend its action using the buff item');
 const recipient=document.createElement('select');recipient.id='bf4400-recipient';
 recipient.setAttribute('aria-label','Choose living ally to receive source +30% ATK');
 const use=document.createElement('button');use.type='button';use.id='bf4400-use';
 use.textContent='USE DEMO ATK ITEM (+30% ATK · 3 ROUNDS; GUARD TURN)';
 const note=document.createElement('small');
 note.textContent='One temporary charge per mission. Source percentage/duration recovered; DEMO action timing and no-stacking rule. The user’s source item inventory is not loaded or spent. KO units cannot benefit.';
 panel.append(heading,sourceLabel,status,actor,recipient,use,note);parent.append(panel);
 let battle=S,round=S.round,remaining=1,last='';
 const used=new Map();
 function sync(){
   if(S!==battle){battle=S;round=S.round;remaining=1;used.clear();last='';}
   else if(S.round!==round){round=S.round;used.clear();last='';}
 }
 function allowed(){
   return S.mode==='archive'&&!S.busy&&!S.over&&!S.auto&&remaining>0;
 }
 function canAct(i){
   const p=S.party?.[i];
   return Number.isInteger(i)&&i>=0&&i<6&&!!p&&
     p.active&&p.hp>0&&!p.action&&used.get(i)!==S.round&&
     (!window.BFGlobalItemTurnReservationsV4500||window.BFGlobalItemTurnReservationsV4500.free(i));
 }
 function canBenefit(i){
   const p=S.party?.[i];
   return Number.isInteger(i)&&i>=0&&i<6&&!!p&&p.active&&p.hp>0&&
     currentAtkBoost(p)===0;
 }
 function snapshot(){
   sync();const actors=Array.from({length:6},(_,i)=>i).filter(canAct);
   const targets=Array.from({length:6},(_,i)=>i).filter(canBenefit);
   return Object.freeze({source,remaining,round:S.round,
     eligibleActors:Object.freeze(actors),eligibleRecipients:Object.freeze(targets),
     available:allowed()&&actors.length>0&&targets.length>0});
 }
 function refresh(){
   const info=snapshot();
   panel.hidden=S.mode!=='archive';
   const key=JSON.stringify({mode:S.mode,round:S.round,remaining,
     busy:S.busy,auto:S.auto,over:S.over,party:S.party?.map(p=>[
       p.name,p.hp,p.active,p.action?.kind||null,currentAtkBoost(p)])});
   if(key===last)return info;last=key;
   function rebuild(select,indices){
     const previous=select.value;
     const options=indices.map(i=>{
       const row=document.createElement('option');
       row.value=String(i);row.textContent=(i+1)+'. '+S.party[i].name;
       return row;
     });
     select.replaceChildren(...options);
     if(indices.some(i=>String(i)===previous))select.value=previous;
   }
   rebuild(actor,info.eligibleActors);
   rebuild(recipient,info.eligibleRecipients);
   status.textContent='Temporary ATK item charges: '+remaining+' / 1';
   use.disabled=!info.available;
   actor.disabled=use.disabled;recipient.disabled=use.disabled;
   return info;
 }
 function useAtkItem(actorId,recipientId){
   sync();
   if(!allowed()||!canAct(actorId)||!canBenefit(recipientId))return false;
   const caster=S.party[actorId],ally=S.party[recipientId];
   const itemTurns=window.BFGlobalItemTurnReservationsV4500;
   if(itemTurns&&!itemTurns.reserve(actorId,'atk-item-demo'))return false;
   // Apply only unbuffed allies: original stacking and refresh rules are unknown.
   ally.atkBuff={pct:source.atkPercent,
     untilRound:S.round+source.durationTurns-1};
   caster.action={kind:'guard',target:S.target};
   used.set(actorId,S.round);remaining=0;
   msg('ARCHIVED 2022 ITEM #20400: '+ally.name+' receives source +30% ATK'+
     ' for 3 DEMO rounds. '+caster.name+' uses Guard as turn cost.');
   update();last='';refresh();return true;
 }
 function enforceGuards(){
   sync();
   if(S.mode!=='archive'||S.over)return;
   for(const [slot,r] of used){
     const p=S.party?.[slot];
     if(r===S.round&&p?.active&&p.hp>0)
       p.action={kind:'guard',target:S.target};
   }
   update();last='';refresh();
 }
 use.addEventListener('click',()=>useAtkItem(Number(actor.value),Number(recipient.value)));
 execute.addEventListener('click',enforceGuards,true);
 mode.addEventListener('change',refresh);
 window.setInterval(()=>{if(!document.hidden)refresh()},750);
 window.BFGlobalSourceAtkItemV4400=Object.freeze({
   snapshot,refresh,useAtkItem,enforceGuards,get source(){return source}
 });
 refresh();
})();