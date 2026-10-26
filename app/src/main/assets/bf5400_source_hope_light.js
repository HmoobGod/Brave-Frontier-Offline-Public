/* BF_GLOBAL_SOURCE_HOPE_LIGHT_V5400 */
(() => {
 'use strict';
 // Original 2022 item #50100 heals all allies; numeric amount is DEMO-only.
 const turns=window.BFGlobalItemTurnReservationsV4500;
 if(window.BFGlobalSourceHopeLightV5400||!turns||!window.BFGlobalSourcePartyDefV5300||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof update!=='function'||typeof msg!=='function')return;
 const parent=document.getElementById('bf4200-items'),mode=document.getElementById('mode');
 if(!parent||!mode)return;
 const source=Object.freeze({file:'3-mst-translated/F_ITEM_MST_Ver1027.json',
   sha256:'0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474',
   itemId:50100,name:'希望の光',battleEffectGroupId:520,targetType:1,
   itemTargetArea:2,skillTypeId:2,passiveSkillInfo:'1500,1500,0,0',
   itemMaxEquipped:12,itemMaxStack:99,demoHeal:1500,
   effect:'Recover HP for all allies'});
 const style=document.createElement('style');style.id='bf5400-style';
 style.textContent='#bf5400-hope{margin:9px 0;padding:9px;border:1px solid #91b68b;border-radius:6px;background:#243d35}'+
 '#bf5400-hope[hidden]{display:none!important}#bf5400-hope summary{cursor:pointer;min-height:36px;font-weight:700}';
 document.head.append(style);
 const panel=document.createElement('details');panel.id='bf5400-hope';
 const title=document.createElement('summary');title.textContent='HOPE LIGHT · ORIGINAL PARTY HEAL (DEMO)';
 const status=document.createElement('strong');status.id='bf5400-status';
 const actor=document.createElement('select');actor.id='bf5400-actor';
 actor.setAttribute('aria-label','Choose acting unit for Hope Light');
 const use=document.createElement('button');use.type='button';use.id='bf5400-use';
 use.textContent='HEAL ALL LIVING ALLIES · DEMO GUARD';
 const note=document.createElement('small');
 note.textContent='2022 source #50100: entire allied party HP recovery. +1500 HP, 1 temporary charge and Guard action are simulated; native healing calculation and inventory are not recovered.';
 panel.append(title,status,actor,use,note);parent.append(panel);
 let battle=S,remaining=1,last='';
 function sync(){if(S!==battle){battle=S;remaining=1;last='';}}
 function allowed(){return S.mode==='archive'&&!S.busy&&!S.over&&!S.auto&&remaining>0;}
 function canAct(i){const p=S.party?.[i];return Number.isInteger(i)&&i>=0&&i<6&&
    !!p&&p.active&&p.hp>0&&!p.action&&turns.free(i);}
 function injured(){return Array.isArray(S.party)?S.party.filter(p=>p&&p.active&&
    p.hp>0&&Number.isFinite(p.hp)&&Number.isFinite(p.maxHp)&&p.hp<p.maxHp):[];}
 function snapshot(){
   sync();
   const actors=Array.from({length:6},(_,i)=>i).filter(canAct);
   const targets=Array.from({length:6},(_,i)=>i).filter(i=>injured().includes(S.party?.[i]));
   return Object.freeze({source,remaining,round:S.round,eligibleActors:Object.freeze(actors),
     eligibleRecipients:Object.freeze(targets),available:allowed()&&actors.length>0&&targets.length>0});
 }
 function refresh(){
   const st=snapshot();panel.hidden=S.mode!=='archive';
   const key=JSON.stringify({mode:S.mode,round:S.round,remaining,busy:S.busy,auto:S.auto,
     over:S.over,party:S.party?.map(p=>p&&[p.name,p.active,p.hp,p.maxHp,p.action?.kind||null]),
     locks:turns.snapshot().reservations});
   if(last===key)return st;last=key;
   const prev=actor.value;
   actor.replaceChildren(...st.eligibleActors.map(i=>{
     const option=document.createElement('option');option.value=String(i);
     option.textContent=(i+1)+'. '+S.party[i].name;return option;
   }));
   if(st.eligibleActors.some(i=>String(i)===prev))actor.value=prev;
   status.textContent='Temporary Hope Light charges '+remaining+'/1 · Injured '+st.eligibleRecipients.length;
   use.disabled=!st.available;actor.disabled=use.disabled;
   return st;
 }
 function useHopeLight(actorId){
   sync();if(!allowed()||!canAct(actorId))return false;
   const targets=injured();if(!targets.length)return false;
   if(!turns.reserve(actorId,'hope-light-demo'))return false;
   let total=0;
   for(const p of targets){const heal=Math.min(source.demoHeal,p.maxHp-p.hp);p.hp+=heal;total+=heal;}
   const caster=S.party[actorId];caster.action={kind:'guard',target:S.target};remaining=0;
   msg('2022 Hope Light #50100: '+targets.length+' allies recover '+total+
     ' DEMO HP total; '+caster.name+' Guards.');
   update();last='';refresh();return true;
 }
 use.addEventListener('click',()=>useHopeLight(Number(actor.value)));
 mode.addEventListener('change',refresh);
 window.setInterval(()=>{if(!document.hidden)refresh()},850);
 window.BFGlobalSourceHopeLightV5400=Object.freeze({source,snapshot,refresh,useHopeLight});
 refresh();
})();