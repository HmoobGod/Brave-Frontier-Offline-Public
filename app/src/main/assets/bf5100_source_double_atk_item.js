/* BF_GLOBAL_SOURCE_DOUBLE_ATK_ITEM_V5100 */
(() => {
 'use strict';
 // Original 2022 #50401: single ally's ATK doubles for three turns.
 // DEMO stock, Guard cost, stronger-buff priority and cast-round duration.
 const turns=window.BFGlobalItemTurnReservationsV4500;
 if(window.BFGlobalSourceDoubleAtkV5100||!turns||
    !window.BFGlobalSourcePartyAtkItemV5000||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof update!=='function'||typeof msg!=='function'||
    typeof currentAtkBoost!=='function')return;
 const container=document.getElementById('bf4200-items');
 const mode=document.getElementById('mode');
 if(!container||!mode)return;
 const source=Object.freeze({
   file:'3-mst-translated/F_ITEM_MST_Ver1027.json',
   sha256:'0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474',
   itemId:50401,name:'強撃薬',battleEffectGroupId:400,
   targetType:1,itemTargetArea:1,skillTypeId:5,
   passiveSkillInfo:'0,100,0,0,0,3',
   itemMaxEquipped:5,atkPercent:100,duration:3,
   effect:'Double one living ally ATK for three turns'
 });
 const style=document.createElement('style');style.id='bf5100-style';
 style.textContent=[
  '#bf5100-atk{margin:9px 0 0;padding:9px;border:1px solid #e4bb78;',
  'border-radius:6px;background:#42332b}',
  '#bf5100-atk[hidden]{display:none!important}',
  '#bf5100-atk summary{cursor:pointer;font:700 13px Georgia,serif;min-height:34px;padding:5px 0}',
  '#bf5100-note{color:#f9deb5}'
 ].join('');document.head.append(style);
 const panel=document.createElement('details');panel.id='bf5100-atk';
 const title=document.createElement('summary');
 title.textContent='ORIGINAL DOUBLE-ATK ITEM · EXPERIMENTAL';
 const description=document.createElement('small');description.id='bf5100-note';
 description.textContent='Original #50401 · '+source.name+
   ' · doubles one living ally ATK for three turns.';
 const stock=document.createElement('strong');stock.id='bf5100-stock';
 const actor=document.createElement('select');actor.id='bf5100-actor';
 actor.setAttribute('aria-label','Choose living unit to use the double-ATK item');
 const target=document.createElement('select');target.id='bf5100-recipient';
 target.setAttribute('aria-label','Choose one ally to receive double ATK');
 const use=document.createElement('button');use.type='button';use.id='bf5100-use';
 use.textContent='DOUBLE ONE ALLY ATK · DEMO GUARD ACTION';
 const warning=document.createElement('small');
 warning.textContent='2022 item effect and duration are source-backed. Temporary charge, Guard cost and replacement of weaker boosts are DEMO; inventory is not saved or spent.';
 panel.append(title,description,stock,actor,target,use,warning);
 container.append(panel);
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
 function canBenefit(i){
   const p=S.party?.[i];
   return Number.isInteger(i)&&i>=0&&i<6&&!!p&&p.active&&
      p.hp>0&&currentAtkBoost(p)<source.atkPercent;
 }
 function snapshot(){
   sync();
   const actors=Array.from({length:6},(_,i)=>i).filter(canAct);
   const targets=Array.from({length:6},(_,i)=>i).filter(canBenefit);
   return Object.freeze({source,remaining,round:S.round,
      eligibleActors:Object.freeze(actors),eligibleRecipients:Object.freeze(targets),
      available:allowed()&&actors.length>0&&targets.length>0});
 }
 function refresh(){
   const data=snapshot();panel.hidden=S.mode!=='archive';
   const signature=JSON.stringify({mode:S.mode,round:S.round,
      busy:S.busy,over:S.over,auto:S.auto,remaining,
      party:S.party?.map(p=>[p.name,p.active,p.hp,p.action?.kind||null,currentAtkBoost(p)]),
      reservations:turns.snapshot().reservations});
   if(signature===last)return data;last=signature;
   function choices(select,ids){
     const prev=select.value;
     select.replaceChildren(...ids.map(i=>{
       const opt=document.createElement('option');opt.value=String(i);
       opt.textContent=(i+1)+'. '+S.party[i].name;return opt;
     }));
     if(ids.some(i=>String(i)===prev))select.value=prev;
   }
   choices(actor,data.eligibleActors);choices(target,data.eligibleRecipients);
   stock.textContent='Temporary double-ATK charges: '+remaining+' / 1';
   use.disabled=!data.available;
   actor.disabled=use.disabled;target.disabled=use.disabled;
   return data;
 }
 function useDoubleAtk(actorId,targetId){
   sync();
   if(!allowed()||!canAct(actorId)||!canBenefit(targetId))return false;
   if(!turns.reserve(actorId,'double-atk-demo'))return false;
   const caster=S.party[actorId],ally=S.party[targetId];
   ally.atkBuff={pct:source.atkPercent,
      untilRound:S.round+source.duration-1};
   caster.action={kind:'guard',target:S.target};
   remaining=0;
   msg('SOURCE 2022 #50401: '+ally.name+' ATK doubled for 3 DEMO turns; '+
       caster.name+' spends Guard.');
   update();last='';refresh();return true;
 }
 use.addEventListener('click',()=>useDoubleAtk(Number(actor.value),Number(target.value)));
 mode.addEventListener('change',refresh);
 window.setInterval(()=>{if(!document.hidden)refresh()},800);
 window.BFGlobalSourceDoubleAtkV5100=Object.freeze({source,snapshot,refresh,useDoubleAtk});
 refresh();
})();
