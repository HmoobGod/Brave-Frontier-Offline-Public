/* BF_GLOBAL_SOURCE_PARTY_HEAL_V4300 */
(() => {
 'use strict';
 const potion=window.BFGlobalDemoPotionV4200;
 if(window.BFGlobalSourcePartyHealV4300||!potion||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof update!=='function'||typeof msg!=='function')return;
 const parent=document.getElementById('bf4200-items');
 const execute=document.getElementById('execute');
 const mode=document.getElementById('mode');
 if(!parent||!execute||!mode)return;
 // Raw values for item 20100 from the user-supplied 2022 translated MST.
 // The original archive records base healing payload 500,500,0,0; action, inventory and native rounding are DEMO.
 const source=Object.freeze({
   file:'3-mst-translated/F_ITEM_MST_Ver1027.json',
   sha256:'0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474',
   itemId:20100,name:'祝福の光',
   battleEffectGroupId:520,targetType:1,itemTargetArea:2,skillTypeId:2,
   passiveSkillInfo:'500,500,0,0',archivedBaseHeal:500,
   itemMaxStack:99,itemMaxEquipped:3
 });
 const css=document.createElement('style');css.id='bf4300-style';
 css.textContent=[
   '#bf4300-party{margin:9px 0 0;padding:9px;border:1px solid #81aaa5;',
   'border-radius:6px;background:#17352f}',
   '#bf4300-party summary{cursor:pointer;font:700 13px Georgia,serif;',
   'padding:5px 0;min-height:34px}',
   '#bf4300-party[hidden]{display:none!important}',
   '#bf4300-source{color:#cde6de}',
   '#bf4300-recovery{color:#fff3c8}'
 ].join('');document.head.append(css);
 const panel=document.createElement('details');panel.id='bf4300-party';
 const heading=document.createElement('summary');
 heading.textContent='ORIGINAL-SCOPE PARTY HEAL · EXPERIMENTAL';
 const sourceLabel=document.createElement('small');sourceLabel.id='bf4300-source';
 sourceLabel.textContent='2022 original item #20100 · '+source.name+
   ' · 2022 base heal payload 500,500,0,0; actual native rounding unknown.';
 const status=document.createElement('strong');status.id='bf4300-status';
 const actor=document.createElement('select');actor.id='bf4300-actor';
 actor.setAttribute('aria-label','Choose the acting squad member for party heal');
 const use=document.createElement('button');use.type='button';use.id='bf4300-use';
 use.textContent='USE SOURCE PARTY HEAL (+500 BASE HP/ALLY; DEMO GUARD)';
 const note=document.createElement('small');note.id='bf4300-recovery';
 note.textContent='ARCHIVED 2022 ITEM PAYLOAD: 500 base HP per living injured ally. Guard cost, temporary stock and rounding are DEMO; KO allies stay KO and real inventory/saves are not spent.';
 panel.append(heading,sourceLabel,status,actor,use,note);
 parent.append(panel);
 let battle=S,turn=S.round,remaining=1,last='';
 const used=new Map();
 function sync(){
   if(battle!==S){battle=S;turn=S.round;remaining=1;used.clear();last='';}
   else if(turn!==S.round){turn=S.round;used.clear();last='';}
 }
 function allowed(){
   return S.mode==='archive'&&!S.busy&&!S.over&&!S.auto&&remaining>0;
 }
 function eligible(i){
   const p=S.party?.[i];
   return Number.isInteger(i)&&i>=0&&i<6&&!!p&&p.active&&
     p.hp>0&&!p.action&&used.get(i)!==S.round&&
     (!window.BFGlobalItemTurnReservationsV4500||window.BFGlobalItemTurnReservationsV4500.free(i));
 }
 function injured(){return S.party?.filter(p=>p.active&&p.hp>0&&p.hp<p.maxHp)||[];}
 function snapshot(){
   sync();
   return Object.freeze({remaining,available:allowed()&&injured().length>0,
     eligible:Object.freeze(Array.from({length:6},(_,i)=>i).filter(eligible)),
     source,round:S.round,recipients:injured().length});
 }
 function refresh(){
   const info=snapshot();
   panel.hidden=S.mode!=='archive';
   const key=JSON.stringify({mode:S.mode,remaining,round:S.round,busy:S.busy,
     auto:S.auto,over:S.over,party:S.party?.map(p=>[
     p.name,p.active,p.hp,p.maxHp,p.action?.kind||null])});
   if(key===last)return info;last=key;
   const selected=actor.value;
   const options=info.eligible.map(i=>{
     const p=S.party[i],option=document.createElement('option');
     option.value=String(i);option.textContent=(i+1)+'. '+p.name;
     return option;
   });
   actor.replaceChildren(...options);
   if(info.eligible.some(i=>String(i)===selected))actor.value=selected;
   status.textContent='Temporary party-heal charges: '+remaining+' / 1';
   use.disabled=!info.available||!info.eligible.length;
   actor.disabled=use.disabled;
   return info;
 }
 function usePartyHeal(i){
   sync();
   if(!allowed()||!eligible(i))return false;
   const recipients=injured();if(!recipients.length)return false;
   const caster=S.party[i];let total=0;
   const itemTurns=window.BFGlobalItemTurnReservationsV4500;
   if(itemTurns&&!itemTurns.reserve(i,'party-heal-demo'))return false;
   for(const p of recipients){
     const amount=Math.min(source.archivedBaseHeal,p.maxHp-p.hp);
     p.hp+=amount;total+=amount;
   }
   caster.action={kind:'guard',target:S.target};
   used.set(i,S.round);remaining=0;
   msg('ORIGINAL #20100 base 500 group recovery (DEMO item semantics): '+
       recipients.length+' allies received '+total+
       ' total DEMO HP; '+caster.name+' uses Guard for the turn.');
   update();last='';refresh();return true;
 }
 function enforceGuards(){
   sync();
   if(S.mode!=='archive'||S.over)return;
   for(const [slot,r] of used){
     const p=S.party?.[slot];
     if(r===S.round&&p?.active&&p.hp>0)
       p.action={kind:'guard',target:S.target};
   }
   update();last='';refresh();
 }
 use.addEventListener('click',()=>usePartyHeal(Number(actor.value)));
 execute.addEventListener('click',enforceGuards,true);
 mode.addEventListener('change',refresh);
 window.setInterval(()=>{if(!document.hidden)refresh()},700);
 window.BFGlobalSourcePartyHealV4300=Object.freeze({
   snapshot,refresh,usePartyHeal,enforceGuards,get source(){return source}
 });
 refresh();
})();