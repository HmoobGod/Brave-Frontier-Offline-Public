/* BF_GLOBAL_SOURCE_BB_GAUGE_ITEM_V4600 */
(() => {
 'use strict';
 // Original 2022 item #21000: maximum BB on a single ally.
 // Stock and Guard-turn behavior below are DEMO, not native source claims.
 const turns=window.BFGlobalItemTurnReservationsV4500;
 if(window.BFGlobalSourceBBGaugeItemV4600||!turns||
    !window.BFGlobalSourceAtkItemV4400||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof update!=='function'||typeof msg!=='function')return;
 const parent=document.getElementById('bf4200-items');
 const mode=document.getElementById('mode');
 if(!parent||!mode)return;
 const source=Object.freeze({
   file:'3-mst-translated/F_ITEM_MST_Ver1027.json',
   sha256:'0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474',
   itemId:21000,name:'武神薬',battleEffectGroupId:540,
   targetType:1,itemTargetArea:1,skillTypeId:4,
   passiveSkillInfo:'0,100',itemMaxEquipped:2,itemMaxStack:99,
   effect:'Fill one ally BB gauge to maximum'
 });
 const css=document.createElement('style');css.id='bf4600-style';
 css.textContent=[
  '#bf4600-item{margin:9px 0 0;padding:9px;border:1px solid #87a6ca;',
  'border-radius:6px;background:#1b2f4b}',
  '#bf4600-item summary{cursor:pointer;font:700 13px Georgia,serif;',
  'min-height:34px;padding:5px 0}',
  '#bf4600-item[hidden]{display:none!important}',
  '#bf4600-ref{color:#d4e7fc}'
 ].join('');document.head.append(css);
 const panel=document.createElement('details');panel.id='bf4600-item';
 const head=document.createElement('summary');
 head.textContent='ORIGINAL BB GAUGE ITEM · EXPERIMENTAL';
 const ref=document.createElement('small');ref.id='bf4600-ref';
 ref.textContent='Source item #21000 · '+source.name+
   ' · original description: fill one living ally’s BB gauge to maximum.';
 const status=document.createElement('strong');status.id='bf4600-stock';
 const actor=document.createElement('select');actor.id='bf4600-actor';
 actor.setAttribute('aria-label','Choose the unit using the BB item');
 const target=document.createElement('select');target.id='bf4600-target';
 target.setAttribute('aria-label','Choose living ally with incomplete BB gauge');
 const use=document.createElement('button');use.type='button';use.id='bf4600-use';
 use.textContent='FILL ALLY BB TO MAX · DEMO GUARD ACTION';
 const note=document.createElement('small');
 note.textContent='2022 source verifies BB maximum and one-ally scope. One temporary DEMO charge per battle; acting unit uses Guard. Native timing, actual inventory, equip limits and animations are not implemented.';
 panel.append(head,ref,status,actor,target,use,note);parent.append(panel);
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
   return Number.isInteger(i)&&i>=0&&i<6&&!!p&&p.active&&p.hp>0&&
     Number.isFinite(p.bb)&&p.bb>=0&&p.bb<100&&
    // Curse (source code 5) blocks ALL BB charging, including item #21000.
    !(window.BFGlobalOriginalAilmentStateV5700?.codesFor(i).includes(5));
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
   const info=snapshot();
   panel.hidden=S.mode!=='archive';
   const key=JSON.stringify({mode:S.mode,round:S.round,remain:remaining,
     busy:S.busy,auto:S.auto,over:S.over,party:S.party?.map(p=>[
       p.name,p.active,p.hp,p.bb,p.action?.kind||null
     ]),locked:turns.snapshot().reservations});
   if(key===last)return info;last=key;
   function rebuild(select,ids){
     const previous=select.value;
     select.replaceChildren(...ids.map(i=>{
       const opt=document.createElement('option');opt.value=String(i);
       opt.textContent=(i+1)+'. '+S.party[i].name;return opt;
     }));
     if(ids.some(i=>String(i)===previous))select.value=previous;
   }
   rebuild(actor,info.eligibleActors);
   rebuild(target,info.eligibleRecipients);
   status.textContent='Temporary source BB charges: '+remaining+' / 1';
   use.disabled=!info.available;
   actor.disabled=use.disabled;target.disabled=use.disabled;
   return info;
 }
 function useBBItem(actorId,targetId){
   sync();
   if(!allowed()||!canAct(actorId)||!canBenefit(targetId))return false;
   if(!turns.reserve(actorId,'bb-fill-demo'))return false;
   const caster=S.party[actorId],ally=S.party[targetId];
   ally.bb=100;
   caster.action={kind:'guard',target:S.target};
   remaining=0;
   msg('SOURCE 2022 #21000 BB gauge item: '+ally.name+
       ' BB at maximum; '+caster.name+' uses DEMO Guard turn.');
   update();last='';refresh();return true;
 }
 use.addEventListener('click',()=>useBBItem(Number(actor.value),Number(target.value)));
 mode.addEventListener('change',refresh);
 window.setInterval(()=>{if(!document.hidden)refresh()},800);
 window.BFGlobalSourceBBGaugeItemV4600=Object.freeze({
   source,snapshot,refresh,useBBItem
 });
 refresh();
})();
