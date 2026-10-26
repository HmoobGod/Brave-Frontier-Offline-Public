/* BF_GLOBAL_SOURCE_DEF_ITEM_V4900 */
(() => {
 'use strict';
 // Original 2022 #20600: +30% DEF to one ally for three turns.
 // Action Guard, stock, expiration boundary and stacking are DEMO rules.
 const turns=window.BFGlobalItemTurnReservationsV4500;
 if(window.BFGlobalSourceDefItemV4900||!turns||
    !window.BFGlobalDemoAutoItemGuardV4800||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof update!=='function'||typeof msg!=='function')return;
 const parent=document.getElementById('bf4200-items');
 const mode=document.getElementById('mode');
 if(!parent||!mode)return;
 const source=Object.freeze({
   file:'3-mst-translated/F_ITEM_MST_Ver1027.json',
   sha256:'0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474',
   itemId:20600,name:'硬化薬',battleEffectGroupId:410,
   targetType:1,itemTargetArea:1,skillTypeId:5,
   passiveSkillInfo:'0,0,30,0,0,3',
   itemMaxEquipped:10,itemMaxStack:99,defPercent:30,duration:3,
   effect:'One ally DEF +30% for three turns'
 });
 const css=document.createElement('style');css.id='bf4900-style';
 css.textContent=[
  '#bf4900-def{margin:9px 0 0;padding:9px;border:1px solid #9db9e4;',
  'border-radius:6px;background:#253d57}',
  '#bf4900-def[hidden]{display:none!important}',
  '#bf4900-def summary{cursor:pointer;font:700 13px Georgia,serif;min-height:34px;padding:5px 0}',
  '#bf4900-status{color:#d7e8fd}'
 ].join('');document.head.append(css);
 const panel=document.createElement('details');panel.id='bf4900-def';
 const head=document.createElement('summary');head.textContent='ORIGINAL DEF ITEM · EXPERIMENTAL';
 const ref=document.createElement('small');
 ref.textContent='2022 source item #20600 · '+source.name+
  ' · one ally DEF +30% for three turns.';
 const state=document.createElement('strong');state.id='bf4900-status';
 const actor=document.createElement('select');actor.id='bf4900-actor';
 actor.setAttribute('aria-label','Choose acting unit for DEF item');
 const recipient=document.createElement('select');recipient.id='bf4900-recipient';
 recipient.setAttribute('aria-label','Choose ally receiving DEF item');
 const use=document.createElement('button');use.type='button';use.id='bf4900-use';
 use.textContent='GIVE ALLY +30% DEF · DEMO GUARD ACTION';
 const note=document.createElement('small');
 note.textContent='Original item effect and duration are sourced. DEF is applied to simulated combat. Item charge, Guard cost, rounding, stacking and cast-turn timing are DEMO.';
 panel.append(head,ref,state,actor,recipient,use,note);parent.append(panel);
 let battle=S,remaining=1,last='';
 const buffs=new Map();
 function sync(){
   if(S!==battle){
     battle=S;remaining=1;buffs.clear();last='';
   }
   for(const [slot,b] of buffs){
     if(S.party?.[slot]!==b.unit||S.round>b.untilRound){
       // Only restore the exact unit instance we changed; never touch P.
       if(b.unit&&Number.isFinite(b.baseDef))b.unit.def=b.baseDef;
       buffs.delete(slot);last='';
     }
   }
 }
 function allowed(){
   return S.mode==='archive'&&!S.busy&&!S.over&&!S.auto&&remaining>0;
 }
 function canAct(i){
   const p=S.party?.[i];
   return Number.isInteger(i)&&i>=0&&i<6&&
     !!p&&p.active&&p.hp>0&&!p.action&&turns.free(i);
 }
 function canBenefit(i){
   const p=S.party?.[i];
   return Number.isInteger(i)&&i>=0&&i<6&&!!p&&
     p.active&&p.hp>0&&Number.isFinite(p.def)&&p.def>=0&&!buffs.has(i)&&
     (!window.BFGlobalSourceDoubleDefV5200||
      !window.BFGlobalSourceDoubleDefV5200.isBuffed(i))&&
     (!window.BFGlobalSourcePartyDefV5300||
      !window.BFGlobalSourcePartyDefV5300.isBuffed(i));
 }
 function snapshot(){
   sync();
   const actors=Array.from({length:6},(_,i)=>i).filter(canAct);
   const recipients=Array.from({length:6},(_,i)=>i).filter(canBenefit);
   const activeBuffs=Object.freeze(Array.from(buffs,([slot,b])=>Object.freeze({
     slot,baseDef:b.baseDef,bonusDef:b.unit.def-b.baseDef,untilRound:b.untilRound
   })));
   return Object.freeze({source,remaining,round:S.round,activeBuffs,
     eligibleActors:Object.freeze(actors),eligibleRecipients:Object.freeze(recipients),
     available:allowed()&&actors.length>0&&recipients.length>0});
 }
 function refresh(){
   const info=snapshot();panel.hidden=S.mode!=='archive';
   const key=JSON.stringify({mode:S.mode,round:S.round,remaining,
     auto:S.auto,busy:S.busy,over:S.over,
     party:S.party?.map(p=>[p.name,p.hp,p.def,p.action?.kind||null]),
     locked:turns.snapshot().reservations,
     buffs:info.activeBuffs});
   if(key===last)return info;last=key;
   function choices(select,ids){
     const prev=select.value;
     select.replaceChildren(...ids.map(i=>{
       const option=document.createElement('option');
       option.value=String(i);option.textContent=(i+1)+'. '+S.party[i].name;
       return option;
     }));
     if(ids.some(i=>String(i)===prev))select.value=prev;
   }
   choices(actor,info.eligibleActors);
   choices(recipient,info.eligibleRecipients);
   state.textContent='Temporary DEF-item charges: '+remaining+
     ' / 1'+(info.activeBuffs.length?
       ' · DEF +30% until round '+info.activeBuffs.map(b=>b.untilRound).join(', '):'');
   use.disabled=!info.available;
   actor.disabled=use.disabled;recipient.disabled=use.disabled;
   return info;
 }
 function useDefItem(actorId,targetId){
   sync();
   if(!allowed()||!canAct(actorId)||!canBenefit(targetId))return false;
   if(!turns.reserve(actorId,'def-item-demo'))return false;
   const caster=S.party[actorId],ally=S.party[targetId];
   const baseDef=ally.def;
   const untilRound=S.round+source.duration-1;
   ally.def=Math.round(baseDef*(100+source.defPercent)/100);
   buffs.set(targetId,{unit:ally,baseDef,untilRound});
   caster.action={kind:'guard',target:S.target};
   remaining=0;
   msg('SOURCE 2022 #20600: '+ally.name+' DEF +30% until round '+
     untilRound+' (DEMO calculation); '+caster.name+' guards.');
   update();last='';refresh();return true;
 }
 use.addEventListener('click',()=>useDefItem(Number(actor.value),Number(recipient.value)));
 mode.addEventListener('change',refresh);
 window.setInterval(()=>{if(!document.hidden)refresh()},700);
 window.BFGlobalSourceDefItemV4900=Object.freeze({source,snapshot,refresh,useDefItem});
 refresh();
})();
