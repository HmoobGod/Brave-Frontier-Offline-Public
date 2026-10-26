/* BF_GLOBAL_SOURCE_STRONG_LIFE_V5500 */
(() => {
 'use strict';
 // Original 2022 item #50001, one-ally HP restoration. +1500 is DEMO math.
 const turns=window.BFGlobalItemTurnReservationsV4500;
 if(window.BFGlobalSourceStrongLifeV5500||!turns||!window.BFGlobalSourceHopeLightV5400||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof update!=='function'||typeof msg!=='function')return;
 const parent=document.getElementById('bf4200-items'),mode=document.getElementById('mode');
 if(!parent||!mode)return;
 const source=Object.freeze({file:'3-mst-translated/F_ITEM_MST_Ver1027.json',
   sha256:'0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474',
   itemId:50001,name:'強生命薬',battleEffectGroupId:520,
   targetType:1,itemTargetArea:1,skillTypeId:2,passiveSkillInfo:'1500,1500,0,0',
   itemMaxStack:99,itemMaxEquipped:5,demoHeal:1500,
   effect:'Recover HP for one ally'});
 const css=document.createElement('style');css.id='bf5500-style';
 css.textContent='#bf5500-life{margin:9px 0;padding:9px;border:1px solid #a4ceaa;border-radius:6px;background:#233b31}'+
 '#bf5500-life[hidden]{display:none!important}#bf5500-life summary{min-height:36px;cursor:pointer;font-weight:700}';
 document.head.append(css);
 const panel=document.createElement('details');panel.id='bf5500-life';
 const title=document.createElement('summary');title.textContent='STRONG LIFE POTION · ORIGINAL SINGLE-ALLY HEAL (DEMO)';
 const state=document.createElement('strong');state.id='bf5500-stock';
 const actor=document.createElement('select');actor.id='bf5500-actor';
 actor.setAttribute('aria-label','Choose acting unit for Strong Life Potion');
 const target=document.createElement('select');target.id='bf5500-target';
 target.setAttribute('aria-label','Choose injured living ally to heal');
 const use=document.createElement('button');use.type='button';use.id='bf5500-use';
 use.textContent='RESTORE ONE ALLY HP · DEMO GUARD TURN';
 const note=document.createElement('small');
 note.textContent='2022 source #50001 heals one ally, payload 1500,1500,0,0. +1500 DEMO HP, item charge, Guard cost and rounding are not the original decoded formula.';
 panel.append(title,state,actor,target,use,note);parent.append(panel);
 let battle=S,remaining=1,last='';
 function sync(){if(S!==battle){battle=S;remaining=1;last='';}}
 function allowed(){return S.mode==='archive'&&!S.busy&&!S.over&&!S.auto&&remaining>0;}
 function canAct(i){const p=S.party?.[i];return Number.isInteger(i)&&i>=0&&i<6&&
   !!p&&p.active&&p.hp>0&&!p.action&&turns.free(i);}
 function canBenefit(i){const p=S.party?.[i];return Number.isInteger(i)&&i>=0&&i<6&&
   !!p&&p.active&&Number.isFinite(p.hp)&&p.hp>0&&Number.isFinite(p.maxHp)&&p.hp<p.maxHp;}
 function snapshot(){
   sync();
   const a=Array.from({length:6},(_,i)=>i).filter(canAct);
   const t=Array.from({length:6},(_,i)=>i).filter(canBenefit);
   return Object.freeze({source,remaining,round:S.round,eligibleActors:Object.freeze(a),
     eligibleRecipients:Object.freeze(t),available:allowed()&&a.length>0&&t.length>0});
 }
 function refresh(){
   const st=snapshot();panel.hidden=S.mode!=='archive';
   const key=JSON.stringify({mode:S.mode,round:S.round,remaining,busy:S.busy,auto:S.auto,
     over:S.over,party:S.party?.map(p=>p&&[p.name,p.active,p.hp,p.maxHp,p.action?.kind||null]),
     locks:turns.snapshot().reservations});
   if(last===key)return st;last=key;
   function choices(select,ids){const previous=select.value;
     select.replaceChildren(...ids.map(i=>{const o=document.createElement('option');o.value=String(i);
       o.textContent=(i+1)+'. '+S.party[i].name;return o;}));
     if(ids.some(i=>String(i)===previous))select.value=previous;
   }
   choices(actor,st.eligibleActors);choices(target,st.eligibleRecipients);
   state.textContent='Temporary Strong Life charges '+remaining+'/1';
   use.disabled=!st.available;actor.disabled=use.disabled;target.disabled=use.disabled;
   return st;
 }
 function useStrongLife(actorId,targetId){
   sync();if(!allowed()||!canAct(actorId)||!canBenefit(targetId))return false;
   if(!turns.reserve(actorId,'strong-life-demo'))return false;
   const caster=S.party[actorId],ally=S.party[targetId];
   const heal=Math.min(source.demoHeal,ally.maxHp-ally.hp);
   ally.hp+=heal;caster.action={kind:'guard',target:S.target};remaining=0;
   msg('SOURCE 2022 #50001: '+ally.name+' +'+heal+' DEMO HP; '+caster.name+' Guards.');
   update();last='';refresh();return true;
 }
 use.addEventListener('click',()=>useStrongLife(Number(actor.value),Number(target.value)));
 mode.addEventListener('change',refresh);
 window.setInterval(()=>{if(!document.hidden)refresh()},800);
 window.BFGlobalSourceStrongLifeV5500=Object.freeze({source,snapshot,refresh,useStrongLife});
 refresh();
})();