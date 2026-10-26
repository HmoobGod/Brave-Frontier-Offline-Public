/* BF_GLOBAL_SOURCE_PARTY_ATK_ITEM_V5000 */
(() => {
 'use strict';
 // Original 2022 #50400: entire living ally party +50% ATK for 3 turns.
 // Source effect/scope only; stock, turn cost and stacking remain DEMO.
 const turns=window.BFGlobalItemTurnReservationsV4500;
 if(window.BFGlobalSourcePartyAtkItemV5000||!turns||
    !window.BFGlobalSourceDefItemV4900||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof update!=='function'||typeof msg!=='function'||
    typeof currentAtkBoost!=='function')return;
 const parent=document.getElementById('bf4200-items');
 const mode=document.getElementById('mode');
 if(!parent||!mode)return;
 const source=Object.freeze({
   file:'3-mst-translated/F_ITEM_MST_Ver1027.json',
   sha256:'0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474',
   itemId:50400,name:'総攻薬',battleEffectGroupId:400,
   targetType:1,itemTargetArea:2,skillTypeId:5,
   passiveSkillInfo:'0,50,0,0,0,3',
   itemMaxEquipped:5,itemMaxStack:99,atkPercent:50,duration:3,
   effect:'All living allies ATK +50% for three turns'
 });
 const css=document.createElement('style');css.id='bf5000-style';
 css.textContent=[
   '#bf5000-party-atk{margin:9px 0 0;padding:9px;border:1px solid #e8c988;',
   'border-radius:6px;background:#49361e}',
   '#bf5000-party-atk[hidden]{display:none!important}',
   '#bf5000-party-atk summary{cursor:pointer;font:700 13px Georgia,serif;min-height:34px;padding:5px 0}',
   '#bf5000-status{color:#ffefd0}'
 ].join('');document.head.append(css);
 const panel=document.createElement('details');panel.id='bf5000-party-atk';
 const head=document.createElement('summary');
 head.textContent='ORIGINAL ALL-ALLY ATK ITEM · EXPERIMENTAL';
 const ref=document.createElement('small');
 ref.textContent='2022 #50400 · '+source.name+' · ATK +50% to all living allies, 3 turns';
 const status=document.createElement('strong');status.id='bf5000-status';
 const actor=document.createElement('select');actor.id='bf5000-actor';
 actor.setAttribute('aria-label','Select actor for all-ally ATK item');
 const use=document.createElement('button');use.type='button';use.id='bf5000-use';
 use.textContent='BUFF LIVING ALLIES +50% ATK · DEMO GUARD COST';
 const note=document.createElement('small');
 note.textContent='Source percentage, duration and all-ally target verified. Demo one charge, Guard cost and stronger-buff priority. Does not affect save inventory.';
 panel.append(head,ref,status,actor,use,note);parent.append(panel);
 let battle=S,remaining=1,last='';
 function sync(){
   if(S!==battle){battle=S;remaining=1;last='';}
 }
 function allowed(){
   return S.mode==='archive'&&!S.busy&&!S.over&&!S.auto&&remaining>0;
 }
 function canAct(i){
   const p=S.party?.[i];
   return Number.isInteger(i)&&i>=0&&i<6&&!!p&&p.active&&
     p.hp>0&&!p.action&&turns.free(i);
 }
 function canBenefit(p){
   return !!p&&p.active&&p.hp>0&&
     currentAtkBoost(p)<source.atkPercent;
 }
 function snapshot(){
   sync();
   const actors=Array.from({length:6},(_,i)=>i).filter(canAct);
   const recipients=Array.from({length:6},(_,i)=>i).filter(i=>canBenefit(S.party?.[i]));
   return Object.freeze({source,remaining,round:S.round,
     eligibleActors:Object.freeze(actors),eligibleRecipients:Object.freeze(recipients),
     available:allowed()&&actors.length>0&&recipients.length>0});
 }
 function refresh(){
   const info=snapshot();panel.hidden=S.mode!=='archive';
   const key=JSON.stringify({mode:S.mode,round:S.round,remaining,
     busy:S.busy,auto:S.auto,over:S.over,party:S.party?.map(p=>[
       p.name,p.hp,p.action?.kind||null,currentAtkBoost(p)]),
     locked:turns.snapshot().reservations});
   if(key===last)return info;last=key;
   const previous=actor.value;
   actor.replaceChildren(...info.eligibleActors.map(i=>{
     const opt=document.createElement('option');opt.value=String(i);
     opt.textContent=(i+1)+'. '+S.party[i].name;return opt;
   }));
   if(info.eligibleActors.some(i=>String(i)===previous))actor.value=previous;
   status.textContent='Temporary all-ally ATK charges: '+remaining+' / 1'+
     ' · Eligible allies: '+info.eligibleRecipients.length;
   use.disabled=!info.available;actor.disabled=use.disabled;
   return info;
 }
 function usePartyAtk(actorId){
   sync();
   if(!allowed()||!canAct(actorId))return false;
   const targets=S.party.filter(canBenefit);
   if(!targets.length)return false;
   if(!turns.reserve(actorId,'party-atk-demo'))return false;
   let buffed=0;
   const end=S.round+source.duration-1;
   for(const ally of targets){
     // DEMO strongest-buff priority: do not overwrite stronger effects.
     ally.atkBuff={pct:source.atkPercent,untilRound:end};
     buffed++;
   }
   S.party[actorId].action={kind:'guard',target:S.target};
   remaining=0;
   msg('SOURCE 2022 #50400: '+buffed+' living allies gain +50% ATK'+
     ' for 3 DEMO turns. Actor spends Guard.');
   update();last='';refresh();return true;
 }
 use.addEventListener('click',()=>usePartyAtk(Number(actor.value)));
 mode.addEventListener('change',refresh);
 window.setInterval(()=>{if(!document.hidden)refresh()},800);
 window.BFGlobalSourcePartyAtkItemV5000=Object.freeze({source,snapshot,refresh,usePartyAtk});
 refresh();
})();
