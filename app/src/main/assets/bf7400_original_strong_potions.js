/* BF_GLOBAL_ORIGINAL_STRONG_POTIONS_V7400 */
(() => {
 'use strict';
 // Original 2022 Global item master: #20001 and #20002 each heal one
 // living ally for a fixed base 1000 / 2000. Stock and Guard are DEMO.
 const originalPotion=window.BFGlobalDemoPotionV4200;
 const turns=window.BFGlobalItemTurnReservationsV4500;
 if(window.BFGlobalOriginalStrongPotionsV7400||!originalPotion||!turns||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof update!=='function'||typeof msg!=='function')return;
 const parent=document.getElementById('bf4200-items');
 const mode=document.getElementById('mode');
 if(!parent||!mode)return;
 const source=Object.freeze({
  archive:'mst-decoded.zip',file:'3-mst-translated/F_ITEM_MST_Ver1027.json',
  sha256:'0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474',
  items:Object.freeze([
   Object.freeze({itemId:20001,name:'強回復薬',healing:1000,
     battleEffectGroupId:520,skillTypeId:2,targetType:1,itemTargetArea:1,
     passiveSkillInfo:'1000,1000,0,0',itemMaxEquipped:7,itemMaxStack:99}),
   Object.freeze({itemId:20002,name:'超回復薬',healing:2000,
     battleEffectGroupId:520,skillTypeId:2,targetType:1,itemTargetArea:1,
     passiveSkillInfo:'2000,2000,0,0',itemMaxEquipped:5,itemMaxStack:99})
  ])
 });
 const css=document.createElement('style');css.id='bf7400-style';
 css.textContent='#bf7400-potions{margin:10px 0;padding:8px;border:1px solid #acb9cb;border-radius:6px;background:#233e47}'+
  '#bf7400-potions summary{cursor:pointer;min-height:36px;font-weight:750}'+
  '#bf7400-potions[hidden]{display:none!important}'+
  '#bf7400-potions label{display:block;margin:4px 0}'+
  '#bf7400-potions select{min-height:44px;width:100%;background:#294956;color:#fff;border:1px solid #9facbb;border-radius:5px;padding:6px}'+
  '#bf7400-potions button{width:100%;min-height:44px;margin:7px 0;background:#335f59;color:#fff;border:1px solid #a8c6ae;border-radius:5px}'+
  '#bf7400-potions button:disabled{opacity:.5}';
 document.head.append(css);
 const panel=document.createElement('details');panel.id='bf7400-potions';
 const title=document.createElement('summary');title.textContent='SOURCE RECOVERY POTIONS · 1,000 / 2,000 HP';
 const stockInfo=document.createElement('strong');stockInfo.id='bf7400-stock';
 const pick=document.createElement('select');pick.id='bf7400-item';
 pick.setAttribute('aria-label','Choose original recovery potion');
 const actor=document.createElement('select');actor.id='bf7400-actor';
 actor.setAttribute('aria-label','Choose acting unit using recovery potion');
 const target=document.createElement('select');target.id='bf7400-target';
 target.setAttribute('aria-label','Choose wounded ally receiving recovery potion');
 const use=document.createElement('button');use.id='bf7400-use';use.type='button';
 use.textContent='RECOVER HP · RESERVE DEMO GUARD TURN';
 const note=document.createElement('small');
 note.textContent='Original item IDs, single-ally targets, and 1000 / 2000 source healing are recorded in the 2022 master. One temporary charge for each potion and an acting-unit Guard turn are DEMO, not original inventory.';
 const label=(name,input)=>{const l=document.createElement('label');l.textContent=name;l.append(input);return l;};
 panel.append(title,stockInfo,label('Original recovery item',pick),
   label('Potion user',actor),label('Wounded recipient',target),use,note);parent.append(panel);
 let battle=S,last='';
 const stock=new Map();
 function reset(){stock.clear();for(const item of source.items)stock.set(item.itemId,1);}
 reset();
 function sync(){if(battle!==S){battle=S;reset();last='';}}
 function legalActor(i){
   const p=S.party?.[i];
   return Number.isInteger(i)&&i>=0&&i<6&&!!p&&p.active&&p.hp>0&&
     !p.action&&turns.free(i);
 }
 function legalTarget(i){
   const p=S.party?.[i];
   return Number.isInteger(i)&&i>=0&&i<6&&!!p&&p.active&&
     Number.isFinite(p.hp)&&p.hp>0&&Number.isFinite(p.maxHp)&&p.hp<p.maxHp;
 }
 function legalItem(itemId){return source.items.find(x=>x.itemId===itemId)||null;}
 function allowed(){return S.mode==='archive'&&!S.busy&&!S.over&&!S.auto;}
 function snapshot(){
   sync();
   const actors=Object.freeze(Array.from({length:6},(_,i)=>i).filter(legalActor));
   const recipients=Object.freeze(Array.from({length:6},(_,i)=>i).filter(legalTarget));
   const counts=Object.freeze(source.items.map(x=>Object.freeze({
     itemId:x.itemId,remaining:stock.get(x.itemId)
   })));
   return Object.freeze({source,mode:S.mode,round:S.round,actors,recipients,stock:counts,
     available:allowed()&&actors.length>0&&recipients.length>0&&counts.some(x=>x.remaining>0)});
 }
 function choices(select,items){
   const old=select.value;
   select.replaceChildren(...items.map(([id,text])=>{
     const option=document.createElement('option');option.value=String(id);
     option.textContent=text;return option;
   }));
   if(items.some(x=>String(x[0])===old))select.value=old;
 }
 function refresh(){
   const state=snapshot();panel.hidden=S.mode!=='archive';
   const key=JSON.stringify({mode:S.mode,round:S.round,busy:S.busy,over:S.over,auto:S.auto,
     party:S.party?.map(p=>p&&[p.active,p.hp,p.maxHp,p.action?.kind||null]),
     stock:state.stock,locks:turns.snapshot().reservations});
   if(last===key)return state;last=key;
   choices(pick,source.items.filter(x=>stock.get(x.itemId)>0).map(x=>[
     x.itemId,'#'+x.itemId+' · '+x.healing+' source base HP'
   ]));
   choices(actor,state.actors.map(i=>[i,(i+1)+'. '+S.party[i].name]));
   choices(target,state.recipients.map(i=>[i,(i+1)+'. '+S.party[i].name]));
   stockInfo.textContent='DEMO session charges · #20001 '+stock.get(20001)+'/1 · #20002 '+stock.get(20002)+'/1';
   use.disabled=!state.available||!legalActor(Number(actor.value))||
     !legalTarget(Number(target.value))||stock.get(Number(pick.value))!==1;
   actor.disabled=use.disabled;target.disabled=use.disabled;pick.disabled=!state.available;
   return state;
 }
 function usePotion(actorId,targetId,itemId){
   sync();
   const item=legalItem(itemId);
   if(!allowed()||!item||stock.get(itemId)!==1||
      !legalActor(actorId)||!legalTarget(targetId))return false;
   if(!turns.reserve(actorId,'strong-potion-demo'))return false;
   const caster=S.party[actorId],recipient=S.party[targetId];
   const healed=Math.min(item.healing,recipient.maxHp-recipient.hp);
   recipient.hp+=healed;
   caster.action={kind:'guard',target:S.target};
   stock.set(itemId,0);
   msg('2022 original item #'+itemId+': '+recipient.name+' restores '+healed+
      ' DEMO HP; '+caster.name+' Guards (temporary item charge).');
   update();last='';refresh();return true;
 }
 use.addEventListener('click',()=>usePotion(Number(actor.value),Number(target.value),Number(pick.value)));
 mode.addEventListener('change',()=>{last='';refresh();});
 pick.addEventListener('change',()=>{last='';refresh();});
 document.getElementById('reset')?.addEventListener('click',()=>{last='';refresh();});
 window.setInterval(()=>{if(!document.hidden)refresh()},900);
 window.BFGlobalOriginalStrongPotionsV7400=Object.freeze({
   source,snapshot,refresh,usePotion
 });
 refresh();
})();
