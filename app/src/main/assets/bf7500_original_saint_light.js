/* BF_GLOBAL_ORIGINAL_SAINT_LIGHT_V7500 */
(() => {
 'use strict';
 // Exact 2022 item #20101: all allies +1000 base HP.
 // Native inventory/item turn cost and unknown REC scaling remain DEMO.
 const turns=window.BFGlobalItemTurnReservationsV4500;
 if(window.BFGlobalOriginalSaintLightV7500||!turns||
    !window.BFGlobalSourcePartyHealV4300||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof update!=='function'||typeof msg!=='function')return;
 const source=Object.freeze({
   archive:'mst-decoded.zip',
   file:'3-mst-translated/F_ITEM_MST_Ver1027.json',
   sha256:'0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474',
   itemId:20101,name:'聖者の光',
   battleEffectGroupId:520,targetType:1,itemTargetArea:2,skillTypeId:2,
   passiveSkillInfo:'1000,1000,0,0',baseHeal:1000,
   itemMaxStack:99,itemMaxEquipped:3
 });
 const parent=document.getElementById('bf4200-items');
 const mode=document.getElementById('mode');
 if(!parent||!mode)return;
 const css=document.createElement('style');css.id='bf7500-style';
 css.textContent='#bf7500-saint-light{padding:8px;margin:9px 0;border:1px solid #a5b9b0;border-radius:6px;background:#1c413d}'+
  '#bf7500-saint-light[hidden]{display:none!important}#bf7500-saint-light summary{cursor:pointer;font-weight:750;min-height:35px}'+
  '#bf7500-saint-light select,#bf7500-saint-light button{width:100%;min-height:44px;box-sizing:border-box;color:white;background:#245047;border-radius:5px;border:1px solid #b1cbbb;padding:7px;margin:5px 0}'+
  '#bf7500-saint-light button:disabled{opacity:.5}';
 document.head.append(css);
 const panel=document.createElement('details');panel.id='bf7500-saint-light';
 const title=document.createElement('summary');
 title.textContent='SAINT LIGHT #20101 · SOURCE PARTY HEAL';
 const status=document.createElement('strong');status.id='bf7500-stock';
 const actor=document.createElement('select');actor.id='bf7500-actor';
 actor.setAttribute('aria-label','Choose acting ally to use Saint Light');
 const use=document.createElement('button');use.type='button';use.id='bf7500-use';
 use.textContent='HEAL ALL LIVING INJURED ALLIES · DEMO GUARD';
 const note=document.createElement('small');
 note.textContent='Exact 2022 item #20101 heals every living ally for up to 1000 base HP. KO stays KO. One temporary charge and acting Guard cost are simulated, not source inventory or native item timing.';
 panel.append(title,status,actor,use,note);parent.append(panel);
 let battle=S,remaining=1,last='';
 function sync(){if(battle!==S){battle=S;remaining=1;last='';}}
 function allowed(){return S.mode==='archive'&&!S.busy&&!S.over&&!S.auto&&remaining===1;}
 function canAct(i){
   const p=S.party?.[i];
   return Number.isInteger(i)&&i>=0&&i<6&&!!p&&p.active&&p.hp>0&&
     !p.action&&turns.free(i);
 }
 function recipients(){
   return (S.party||[]).filter(p=>p?.active&&Number.isFinite(p.hp)&&p.hp>0&&
     Number.isFinite(p.maxHp)&&p.hp<p.maxHp);
 }
 function snapshot(){
   sync();
   const actors=Object.freeze(Array.from({length:6},(_,i)=>i).filter(canAct));
   const targets=recipients();
   return Object.freeze({source,remaining,round:S.round,mode:S.mode,actors,
     recipientCount:targets.length,available:allowed()&&actors.length>0&&targets.length>0});
 }
 function refresh(){
   const st=snapshot();panel.hidden=S.mode!=='archive';
   const key=JSON.stringify({mode:S.mode,round:S.round,busy:S.busy,over:S.over,auto:S.auto,
      remaining,party:S.party?.map(p=>p&&[p.hp,p.maxHp,p.active,p.action?.kind||null]),
      locks:turns.snapshot().reservations});
   if(key===last)return st;last=key;
   const keep=actor.value;
   actor.replaceChildren(...st.actors.map(i=>{
     const option=document.createElement('option');option.value=String(i);
     option.textContent=(i+1)+'. '+S.party[i].name;return option;
   }));
   if(st.actors.some(i=>String(i)===keep))actor.value=keep;
   status.textContent='Temporary source item #20101 charges '+remaining+
     '/1 · injured living allies '+st.recipientCount;
   use.disabled=!st.available||!canAct(Number(actor.value));
   actor.disabled=use.disabled;
   return st;
 }
 function useSaintLight(actorId){
   sync();
   if(!allowed()||!canAct(actorId))return false;
   const targets=recipients();
   if(!targets.length)return false;
   if(!turns.reserve(actorId,'saint-light-demo'))return false;
   let total=0;
   for(const p of targets){
     const heal=Math.min(source.baseHeal,p.maxHp-p.hp);
     p.hp+=heal;total+=heal;
   }
   const caster=S.party[actorId];
   caster.action={kind:'guard',target:S.target};
   remaining=0;
   msg('2022 Saint Light #20101: '+targets.length+' allies healed '+
      total+' total DEMO HP; '+caster.name+' Guards.');
   update();last='';refresh();return true;
 }
 use.addEventListener('click',()=>useSaintLight(Number(actor.value)));
 mode.addEventListener('change',()=>{last='';refresh();});
 document.getElementById('reset')?.addEventListener('click',()=>{last='';refresh();});
 window.setInterval(()=>{if(!document.hidden)refresh()},850);
 window.BFGlobalOriginalSaintLightV7500=Object.freeze({source,snapshot,refresh,useSaintLight});
 refresh();
})();
