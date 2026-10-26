/* BF_GLOBAL_STATUS_REMEDY_COMMAND_V6400 */
(() => {
 'use strict';
 // 2022 source-backed ailment remedy IDs and cure scopes, but NOT original
 // inventory, crafting, item use timing, or item quantity.
 const ail=window.BFGlobalOriginalAilmentStateV5700;
 const turns=window.BFGlobalItemTurnReservationsV4500;
 if(window.BFGlobalStatusRemedyCommandV6400||!ail||!turns||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof update!=='function'||typeof msg!=='function')return;
 const parent=document.getElementById('bf4200-items');
 const mode=document.getElementById('mode');
 if(!parent||!mode)return;
 const cureItems=ail.source.cureItems;
 const names=Object.freeze({
   20200:'Poison cure',20210:'Weakness / Sickness / Injury cure',
   20220:'Curse cure',20230:'Paralysis cure',50200:'All-ailment cure'
 });
 const css=document.createElement('style');css.id='bf6400-style';
 css.textContent='#bf6400-remedies{margin:9px 0;padding:9px;border:1px solid #9ea5c5;border-radius:6px;background:#292e42;color:#f7f4e5}'+
  '#bf6400-remedies[hidden]{display:none!important}#bf6400-remedies summary{cursor:pointer;min-height:36px;font-weight:700}'+
  '#bf6400-remedies label{display:block;margin-top:6px}#bf6400-remedies select,#bf6400-use{width:100%;min-height:43px;box-sizing:border-box;background:#263e51;border:1px solid #94a5b7;color:white;border-radius:5px;padding:7px}'+
  '#bf6400-use{margin-top:8px;font-weight:700}#bf6400-use:disabled{opacity:.55}';
 document.head.append(css);
 const panel=document.createElement('details');panel.id='bf6400-remedies';
 const heading=document.createElement('summary');
 heading.textContent='ORIGINAL STATUS REMEDIES · DEMO ITEM COMMAND';
 const status=document.createElement('strong');status.id='bf6400-stock';
 const remedy=document.createElement('select');remedy.id='bf6400-item';
 remedy.setAttribute('aria-label','Choose source-identified ailment cure item');
 const actor=document.createElement('select');actor.id='bf6400-actor';
 actor.setAttribute('aria-label','Choose acting unit for remedy');
 const target=document.createElement('select');target.id='bf6400-target';
 target.setAttribute('aria-label','Choose afflicted ally to cure');
 const use=document.createElement('button');use.id='bf6400-use';use.type='button';
 use.textContent='CURE STATUS · RESERVE GUARD';
 const note=document.createElement('small');
 note.textContent='Original item IDs and curable ailments are verified against the 2022 translated item master. Charges (one per remedy per battle), Guard action, item ownership and target availability are DEMO behavior, not original inventory or timing.';
 function labeled(text,element){const label=document.createElement('label');label.textContent=text;label.append(element);return label;}
 panel.append(heading,status,labeled('Remedy',remedy),
  labeled('Acting ally',actor),labeled('Afflicted ally',target),use,note);parent.append(panel);
 let battle=S,last='';
 const stock=new Map();
 function reset(){stock.clear();for(const x of cureItems)stock.set(x.itemId,1);}
 reset();
 function sync(){if(S!==battle){battle=S;reset();last='';}}
 function validItem(itemId){return cureItems.find(x=>x.itemId===itemId)||null;}
 function ready(){return S.mode==='archive'&&!S.busy&&!S.over&&!S.auto;}
 function canAct(i){
   const p=S.party?.[i];
   return Number.isInteger(i)&&i>=0&&i<6&&!!p&&p.active&&p.hp>0&&
     !p.action&&turns.free(i);
 }
 function canCure(i,itemId){
   const item=validItem(itemId),p=S.party?.[i];
   return !!item&&Number.isInteger(i)&&i>=0&&i<6&&!!p&&p.active&&p.hp>0&&
     ail.codesFor(i).some(code=>item.codes.includes(code));
 }
 function snapshot(){
   sync();
   const availableItems=cureItems.filter(item=>stock.get(item.itemId)>0&&
     Array.from({length:6},(_,i)=>i).some(i=>canCure(i,item.itemId)));
   return Object.freeze({
     round:S.round,mode:S.mode,
     stock:Object.freeze(cureItems.map(item=>Object.freeze({itemId:item.itemId,remaining:stock.get(item.itemId)}))),
     availableItems:Object.freeze(availableItems.map(item=>item.itemId)),
     actors:Object.freeze(Array.from({length:6},(_,i)=>i).filter(canAct)),
     available:ready()&&availableItems.length>0
   });
 }
 function choices(select,entries){
   const keep=select.value;
   select.replaceChildren(...entries.map(e=>{
     const o=document.createElement('option');o.value=String(e[0]);o.textContent=e[1];return o;
   }));
   if(entries.some(e=>String(e[0])===keep))select.value=keep;
 }
 function refresh(){
   const s=snapshot(),ailments=ail.snapshot().units;
   panel.hidden=S.mode!=='archive'||ailments.length===0;
   const key=JSON.stringify({mode:S.mode,busy:S.busy,over:S.over,auto:S.auto,
     round:S.round,units:ailments.map(u=>[u.slot,u.codes]),
     stock:s.stock,actors:s.actors,
     party:S.party?.map(p=>p&&[p.active,p.hp,p.action?.kind||null]),
     locks:turns.snapshot().reservations});
   if(last===key)return s;last=key;
   choices(remedy,s.availableItems.map(id=>[id,'#'+id+' · '+names[id]+' (1 DEMO charge)']));
   const itemId=Number(remedy.value);
   choices(actor,s.actors.map(i=>[i,(i+1)+'. '+S.party[i].name]));
   choices(target,Array.from({length:6},(_,i)=>i).filter(i=>canCure(i,itemId))
     .map(i=>[i,(i+1)+'. '+S.party[i].name]));
   status.textContent='Temporary remedies: '+s.stock.filter(e=>e.remaining>0).length+'/5 · afflicted allies '+ailments.length;
   use.disabled=!s.available||!canAct(Number(actor.value))||
     !canCure(Number(target.value),itemId);
   return s;
 }
 function useRemedy(actorId,targetId,itemId){
   sync();
   if(!ready()||!validItem(itemId)||stock.get(itemId)!==1||
      !canAct(actorId)||!canCure(targetId,itemId))return false;
   if(!turns.reserve(actorId,'status-remedy-demo'))return false;
   const result=ail.cure(targetId,itemId);
   // Synchronous cure follows successful reservation, so its code intersection
   // cannot change between validation and execution.
   if(!result||!result.removed.length)return false;
   stock.set(itemId,0);
   const p=S.party[actorId],recipient=S.party[targetId];
   p.action={kind:'guard',target:S.target};
   msg('2022 remedy #'+itemId+': '+recipient.name+' cleared '+
     result.removed.map(code=>ail.labels[code]).join(', ')+
     '; '+p.name+' Guards (DEMO item charge).');
   update();last='';refresh();return true;
 }
 use.addEventListener('click',()=>useRemedy(Number(actor.value),Number(target.value),Number(remedy.value)));
 remedy.addEventListener('change',()=>{last='';refresh();});
 actor.addEventListener('change',()=>{last='';refresh();});
 target.addEventListener('change',()=>{last='';refresh();});
 mode.addEventListener('change',()=>{last='';refresh();});
 window.setInterval(()=>{if(!document.hidden)refresh()},800);
 window.BFGlobalStatusRemedyCommandV6400=Object.freeze({
   source:ail.source, snapshot, refresh, useRemedy
 });
 refresh();
})();
