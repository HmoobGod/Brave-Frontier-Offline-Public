/* BF_GLOBAL_SOURCE_PARTY_DEF_ITEM_V5300 */
(() => {
 'use strict';
 // Source #50600: all living allies +50% DEF for three turns.
 // Temporary stock, Guard and DEF-buff collision policies are DEMO-only.
 const turns=window.BFGlobalItemTurnReservationsV4500;
 const single=window.BFGlobalSourceDefItemV4900;
 const double=window.BFGlobalSourceDoubleDefV5200;
 if(window.BFGlobalSourcePartyDefV5300||!turns||!single||!double||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof update!=='function'||typeof msg!=='function')return;
 const container=document.getElementById('bf4200-items');
 const mode=document.getElementById('mode');
 if(!container||!mode)return;
 const source=Object.freeze({
   file:'3-mst-translated/F_ITEM_MST_Ver1027.json',
   sha256:'0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474',
   itemId:50600,name:'総防薬',battleEffectGroupId:410,
   targetType:1,itemTargetArea:2,skillTypeId:5,
   passiveSkillInfo:'0,0,50,0,0,3',
   itemMaxEquipped:5,defPercent:50,duration:3,
   effect:'All living allies DEF +50% for three turns'
 });
 const style=document.createElement('style');style.id='bf5300-style';
 style.textContent=[
  '#bf5300-def{margin:9px 0 0;padding:9px;border:1px solid #a4c3e4;',
  'border-radius:6px;background:#263d52}',
  '#bf5300-def[hidden]{display:none!important}',
  '#bf5300-def summary{cursor:pointer;font:700 13px Georgia,serif;min-height:34px;padding:5px 0}',
  '#bf5300-status{color:#e0efff}'
 ].join('');document.head.append(style);
 const panel=document.createElement('details');panel.id='bf5300-def';
 const title=document.createElement('summary');title.textContent='ORIGINAL PARTY DEF +50% · EXPERIMENTAL';
 const description=document.createElement('small');
 description.textContent='2022 source item #50600 · '+source.name+
   ' · all living allies +50% DEF for three turns.';
 const status=document.createElement('strong');status.id='bf5300-status';
 const actor=document.createElement('select');actor.id='bf5300-actor';
 actor.setAttribute('aria-label','Choose acting unit for party DEF item');
 const use=document.createElement('button');use.type='button';use.id='bf5300-use';
 use.textContent='BUFF LIVING ALLIES +50% DEF · DEMO GUARD';
 const note=document.createElement('small');
 note.textContent='Source-backed DEF percentage, duration and party target. DEMO one-charge stock and Guard cost; existing DEF buffs are left unchanged to prevent stacking conflicts.';
 panel.append(title,description,status,actor,use,note);container.append(panel);
 let battle=S,remaining=1,last='';
 const buffs=new Map();
 function sync(){
   if(S!==battle){battle=S;remaining=1;buffs.clear();last='';}
   for(const [slot,b] of buffs){
     if(S.party?.[slot]!==b.unit||S.round>b.untilRound){
       if(b.unit&&Number.isFinite(b.baseDef))b.unit.def=b.baseDef;
       buffs.delete(slot);last='';
     }
   }
 }
 function isBuffed(slot){sync();return buffs.has(slot);}
 function allowed(){return S.mode==='archive'&&!S.busy&&!S.over&&!S.auto&&remaining>0;}
 function canAct(i){
   const p=S.party?.[i];
   return Number.isInteger(i)&&i>=0&&i<6&&!!p&&p.active&&
     p.hp>0&&!p.action&&turns.free(i);
 }
 function canBenefit(i){
   const p=S.party?.[i];
   return Number.isInteger(i)&&i>=0&&i<6&&!!p&&p.active&&p.hp>0&&
     Number.isFinite(p.def)&&p.def>=0&&!buffs.has(i)&&!double.isBuffed(i)&&
     !single.snapshot().activeBuffs.some(b=>b.slot===i);
 }
 function snapshot(){
   sync();
   const actors=Array.from({length:6},(_,i)=>i).filter(canAct);
   const recipients=Array.from({length:6},(_,i)=>i).filter(canBenefit);
   return Object.freeze({source,remaining,round:S.round,
     eligibleActors:Object.freeze(actors),eligibleRecipients:Object.freeze(recipients),
     activeBuffs:Object.freeze(Array.from(buffs,([slot,b])=>
       Object.freeze({slot,baseDef:b.baseDef,untilRound:b.untilRound}))),
     available:allowed()&&actors.length>0&&recipients.length>0});
 }
 function refresh(){
   const st=snapshot();panel.hidden=S.mode!=='archive';
   const key=JSON.stringify({mode:S.mode,round:S.round,remaining,busy:S.busy,
     auto:S.auto,over:S.over,party:S.party?.map(p=>[
       p.name,p.active,p.hp,p.def,p.action?.kind||null]),
     locks:turns.snapshot().reservations,buffs:st.activeBuffs});
   if(key===last)return st;last=key;
   const previous=actor.value;
   actor.replaceChildren(...st.eligibleActors.map(i=>{
     const opt=document.createElement('option');opt.value=String(i);
     opt.textContent=(i+1)+'. '+S.party[i].name;return opt;
   }));
   if(st.eligibleActors.some(i=>String(i)===previous))actor.value=previous;
   status.textContent='Temporary party DEF charges: '+remaining+
     ' / 1 · Eligible allies: '+st.eligibleRecipients.length;
   use.disabled=!st.available;actor.disabled=use.disabled;return st;
 }
 function usePartyDef(actorId){
   sync();
   if(!allowed()||!canAct(actorId))return false;
   const recipients=Array.from({length:6},(_,i)=>i).filter(canBenefit);
   if(!recipients.length)return false;
   if(!turns.reserve(actorId,'party-def-demo'))return false;
   const untilRound=S.round+source.duration-1;
   for(const slot of recipients){
     const unit=S.party[slot],baseDef=unit.def;
     unit.def=Math.round(baseDef*(100+source.defPercent)/100);
     buffs.set(slot,{unit,baseDef,untilRound});
   }
   S.party[actorId].action={kind:'guard',target:S.target};
   remaining=0;
   msg('SOURCE 2022 #50600: '+recipients.length+
     ' living allies gain +50% DEF for 3 DEMO turns; actor Guards.');
   update();last='';refresh();return true;
 }
 use.addEventListener('click',()=>usePartyDef(Number(actor.value)));
 mode.addEventListener('change',refresh);
 window.setInterval(()=>{if(!document.hidden)refresh()},750);
 window.BFGlobalSourcePartyDefV5300=Object.freeze({source,snapshot,refresh,usePartyDef,isBuffed});
 refresh();
})();
