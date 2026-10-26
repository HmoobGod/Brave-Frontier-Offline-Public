/* BF_GLOBAL_DEMO_POTION_COMMAND_V4200 */
(() => {
 'use strict';
 if(window.BFGlobalDemoPotionV4200 ||
    typeof P==='undefined'||P.version!==7||
    typeof S==='undefined'||typeof QUESTS==='undefined'||QUESTS.length!==106||
    typeof update!=='function'||typeof msg!=='function'||
    !window.BFGlobalLiveQuestBannerV4100)return;
 const hud=document.getElementById('bf2000-run');
 const mode=document.getElementById('mode');
 const executeButton=document.getElementById('execute');
 const questinfo=document.getElementById('questinfo');
 if(!hud||!mode||!executeButton||!questinfo)return;
 const css=document.createElement('style');css.id='bf4200-style';
 css.textContent=[
  '#bf4200-items{margin:9px 0;padding:10px;border:1px solid #8caa95;',
  'border-radius:7px;background:#193b35;color:#f4f8e7;font:12px/1.5 system-ui,sans-serif}',
  '#bf4200-items h4{font:700 14px Georgia,serif;margin:0 0 5px}',
  '#bf4200-items select,#bf4200-items button{min-height:44px;',
  'box-sizing:border-box;border:1px solid #b4d1ba;border-radius:5px;',
  'background:#254e46;color:#fff;padding:8px}',
  '#bf4200-items select{width:100%;margin:5px 0}',
  '#bf4200-items button{font-weight:800;width:100%}',
  '#bf4200-items button:disabled{opacity:.5}',
  '#bf4200-items small{display:block;color:#d3e5d5;margin-top:5px}',
  '#bf4200-items[hidden]{display:none!important}'
 ].join('');document.head.append(css);
 const panel=document.createElement('section');panel.id='bf4200-items';
 const title=document.createElement('h4');title.textContent='ORIGINAL POTION #20000 · BATTLE COMMAND (DEMO INVENTORY)';
 const remainingText=document.createElement('strong');remainingText.id='bf4200-stock';
 const target=document.createElement('select');target.id='bf4200-unit';
 target.setAttribute('aria-label','Choose wounded squad member for demo potion');
 const use=document.createElement('button');use.type='button';use.id='bf4200-use';
 use.textContent='USE DEMO POTION (+500 HP; GUARD TURN)';
 // Real 2022 one-ally Potion #20000, not the older +500 experimental potion.
 const original=Object.freeze({
   archive:'mst-decoded.zip',file:'3-mst-translated/F_ITEM_MST_Ver1027.json',
   sha256:'0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474',
   itemId:20000,name:'回復薬',battleEffectGroupId:520,
   targetType:1,itemTargetArea:1,skillTypeId:2,
   passiveSkillInfo:'100,120,0,0',baseLow:100,baseHigh:120,
   itemMaxStack:99,itemMaxEquipped:10
 });
 const sourceStatus=document.createElement('strong');sourceStatus.id='bf7200-stock';
 const sourceActor=document.createElement('select');sourceActor.id='bf7300-actor';
 sourceActor.setAttribute('aria-label','Choose the unit using the original Potion');
 const sourceTarget=document.createElement('select');sourceTarget.id='bf7300-target';
 sourceTarget.setAttribute('aria-label','Choose wounded ally to receive original Potion');
 const sourceUse=document.createElement('button');sourceUse.id='bf7200-use';sourceUse.type='button';
 sourceUse.textContent='ORIGINAL POTION #20000 · 100–120 BASE HP (DEMO GUARD)';
 const sourceNote=document.createElement('small');
 sourceNote.textContent='Source 2022 item #20000: one selected living ally, heal payload 100–120. Acting ally may differ from recipient; 100–120 uniform DEMO roll, one temporary charge, Guard turn, no saved inventory.';
 const legacy=document.createElement('details');legacy.id='bf7200-legacy';
 const legacyTitle=document.createElement('summary');
 legacyTitle.textContent='EXPAND: LEGACY +500 HP DEMO POTION';
 const note=document.createElement('small');
 note.textContent='Optional experimental item. Three temporary potions per archive battle. Restores up to 500 HP now and reserves this unit’s turn for Guard. Not original item balance, not saved inventory, and no additional rewards.';
 legacy.append(legacyTitle,remainingText,use,note);
 const legacyTargetLabel=document.createElement('label');legacyTargetLabel.textContent='Legacy demo Potion self-target';
 legacyTargetLabel.append(target);legacy.prepend(legacyTargetLabel);
 const actorLabel=document.createElement('label');actorLabel.textContent='Potion user';
 actorLabel.append(sourceActor);
 const targetLabel=document.createElement('label');targetLabel.textContent='Wounded ally to heal';
 targetLabel.append(sourceTarget);
 panel.append(title,sourceStatus,actorLabel,targetLabel,sourceUse,sourceNote,legacy);hud.append(panel);
 let previousBattle=S,remaining=3,sourceRemaining=1,round=S.round,last='';
 const used=new Map();
 function synchronize(){
   if(S!==previousBattle){
     previousBattle=S;remaining=3;sourceRemaining=1;round=S.round;used.clear();last='';
   }else if(S.round!==round){round=S.round;used.clear();last='';}
 }
 function available(){
   return S.mode==='archive'&&!S.busy&&!S.over&&!S.auto&&remaining>0;
 }
 function sourceAvailable(){
   return S.mode==='archive'&&!S.busy&&!S.over&&!S.auto&&sourceRemaining>0;
 }
 function candidate(i){
   const p=S.party?.[i];
   return Number.isInteger(i)&&i>=0&&i<6&&!!p&&
     !!p.active&&p.hp>0&&p.hp<p.maxHp&&!p.action&&
     used.get(i)!==S.round&&
     (!window.BFGlobalItemTurnReservationsV4500||window.BFGlobalItemTurnReservationsV4500.free(i));
 }
 function sourceActorEligible(i){
   const p=S.party?.[i];
   return Number.isInteger(i)&&i>=0&&i<6&&!!p&&p.active&&p.hp>0&&
     !p.action&&used.get(i)!==S.round&&
     (!window.BFGlobalItemTurnReservationsV4500||
      window.BFGlobalItemTurnReservationsV4500.free(i));
 }
 function sourceTargetEligible(i){
   const p=S.party?.[i];
   return Number.isInteger(i)&&i>=0&&i<6&&!!p&&p.active&&p.hp>0&&
     Number.isFinite(p.hp)&&Number.isFinite(p.maxHp)&&p.hp<p.maxHp;
 }
 function snapshot(){
   synchronize();
   return Object.freeze({
     sourceActors:Object.freeze(Array.from({length:6},(_,i)=>i).filter(sourceActorEligible)),
     sourceTargets:Object.freeze(Array.from({length:6},(_,i)=>i).filter(sourceTargetEligible)),
     available:available(),remaining,sourceRemaining,source:original,
     round:S.round,eligible:Object.freeze(
       Array.from({length:6},(_,i)=>i).filter(candidate)),
     battleMode:S.mode});
 }
 function refresh(){
   const info=snapshot();
   const show=S.mode==='archive';
   panel.hidden=!show;
   const key=JSON.stringify({
     mode:S.mode,remain:remaining,sourceRemaining,round:S.round,busy:S.busy,
     auto:S.auto,over:S.over,locks:window.BFGlobalItemTurnReservationsV4500?.snapshot().reservations,
     party:S.party?.map(p=>[
       p.active,p.hp,p.maxHp,p.action?.kind||null,p.name
     ])});
   if(key===last)return info;last=key;
   function updateChoices(select,ids){
     const previous=select.value;
     select.replaceChildren(...ids.map(i=>{
       const o=document.createElement('option');o.value=String(i);
       o.textContent=(i+1)+'. '+S.party[i].name;
       return o;
     }));
     if(ids.some(i=>String(i)===previous))select.value=previous;
   }
   updateChoices(sourceActor,info.sourceActors);
   updateChoices(sourceTarget,info.sourceTargets);
   const keep=target.value;
   const options=info.eligible.map(i=>{
     const p=S.party[i],option=document.createElement('option');
     option.value=String(i);
     option.textContent=(i+1)+'. '+p.name+' · '+p.hp+'/'+p.maxHp+' HP';
     return option;
   });
   target.replaceChildren(...options);
   if(info.eligible.some(i=>String(i)===keep))target.value=keep;
   remainingText.textContent='Legacy DEMO potions: '+remaining+' / 3';
   sourceStatus.textContent='Source Potion #20000: '+sourceRemaining+'/1 temporary charge';
   use.disabled=!info.available||!info.eligible.length;
   sourceUse.disabled=!sourceAvailable()||!info.sourceActors.length||!info.sourceTargets.length;
   target.disabled=use.disabled;
   sourceActor.disabled=sourceUse.disabled;
   sourceTarget.disabled=sourceUse.disabled;
   return info;
 }
 function usePotion(i){
   synchronize();
   if(!available()||!candidate(i))return false;
   const p=S.party[i],healed=Math.min(500,p.maxHp-p.hp);
   if(healed<=0)return false;
   const itemTurns=window.BFGlobalItemTurnReservationsV4500;
   if(itemTurns&&!itemTurns.reserve(i,'demo-potion'))return false;
   p.hp+=healed;
   p.action={kind:'guard',target:S.target};
   used.set(i,S.round);remaining--;
   msg(p.name+' used an EXPERIMENTAL demo Potion: +'+healed+
       ' HP; Guard reserved as the unit action. Session item '+remaining+' left.');
   update();last='';refresh();return true;
 }
 // A potion always consumes that unit's action, even if another command button
 // is tapped afterward. The native Execute click handler runs after capture.
 function useSourcePotion(actorId,targetId=actorId){
   synchronize();
   if(!sourceAvailable()||!sourceActorEligible(actorId)||!sourceTargetEligible(targetId))return false;
   const caster=S.party[actorId],recipient=S.party[targetId];
   const deficit=recipient.maxHp-recipient.hp;
   if(deficit<=0)return false;
   const turns=window.BFGlobalItemTurnReservationsV4500;
   if(turns&&!turns.reserve(actorId,'original-potion-demo'))return false;
   // Original 2022 base payload is 100..120; random distribution is a DEMO choice.
   const base=original.baseLow+
     Math.floor(Math.random()*(original.baseHigh-original.baseLow+1));
   const healed=Math.min(base,deficit);
   recipient.hp+=healed;
   caster.action={kind:'guard',target:S.target};
   sourceRemaining--;
   used.set(actorId,S.round);
   msg(caster.name+' uses original Potion #20000 on '+recipient.name+': +'+healed+
     ' DEMO HP (source 100–120 base); Guard turn, '+sourceRemaining+' source charges left.');
   update();last='';refresh();return true;
 }
 function enforceGuards(){
   synchronize();
   if(S.mode!=='archive'||S.over)return;
   for(const [slot,usedRound] of used){
     const p=S.party?.[slot];
     if(usedRound===S.round&&p?.active&&p.hp>0){
       p.action={kind:'guard',target:S.target};
     }
   }
   update();last='';refresh();
 }
 use.addEventListener('click',()=>usePotion(Number(target.value)));
 sourceUse.addEventListener('click',()=>useSourcePotion(Number(sourceActor.value),Number(sourceTarget.value)));
 executeButton.addEventListener('click',enforceGuards,true);
 mode.addEventListener('change',refresh);
 new MutationObserver(refresh).observe(questinfo,{childList:true});
 document.querySelector('.bf-navbar')?.addEventListener('click',refresh);
 window.setInterval(()=>{if(!document.hidden)refresh()},650);
 window.BFGlobalDemoPotionV4200=Object.freeze({snapshot,refresh,usePotion,useSourcePotion,enforceGuards,source:original});
 refresh();
})();