/* BF_GLOBAL_2022_STARTER_LEADER_SKILL_SOURCE_V11000 */
(() => {
 'use strict';
 // 2022 original starter-only leader data. Read-only until native stat
 // creation, formation and reset lifecycles are source-verified.
 if(window.BFGlobalStarterLeaderSourceV11000||
   typeof P==='undefined'||P.version!==7||!Array.isArray(P.roster)||
   !Array.isArray(P.squad)||typeof effectiveUnit!=='function')return;
 const host=document.getElementById('squadpicker');
 if(!host)return;
 const freeze=Object.freeze;
 const source=freeze({
   master:'2022 F_LEADER_SKILL_MST_Ver749.json',
   leaderSha256:'65e591557264d656be2408e9c426ef35050b960f1736a488da8f0a55a5e845fe',
   unitMasterSha256:'1146f09489a07b9187cd3f04bf7dc3ef3bb74e35385869534671af95bf8ea645',
   archiveSha256:'69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9',
   sourceUnitForms:30,sourceLeaderSkills:18,
   nativeBattleStatsModified:false,savedFieldsAdded:0,
   limitation:'Strict 30 starter forms only. No live stat changes without original party construction and level/type lifecycle verification.'
 });
 const byUnit=new Map();
 const atk=[25,25,50,50,50],hp=[0,0,0,0,10];
 for(let element=1;element<=6;element++){
   for(let index=0;index<5;index++){
     const unitId=element*10000+11+index;
     const lsId=100+(element-1)*10+(index<2?0:index<4?1:2);
     const passive=element+',0,'+atk[index]+',0,0,0,'+hp[index];
     byUnit.set(unitId,freeze({unitId,element,lsId,skillTypeId:2,
       passive,atkPercent:atk[index],hpPercent:hp[index]}));
   }
 }
 if(byUnit.size!==30||byUnit.get(10011)?.passive!=='1,0,25,0,0,0,0'||
    byUnit.get(10015)?.passive!=='1,0,50,0,0,0,10'||
    byUnit.get(60015)?.lsId!==152)return;
 function lookup(unitId){
   return Number.isSafeInteger(unitId)?byUnit.get(unitId)||null:null;
 }
 function bonusFor(leaderId,targetId){
   const leader=lookup(leaderId),target=lookup(targetId);
   if(!leader||!target)return null;
   const same=leader.element===target.element;
   return freeze({leaderId,targetId,sameElement:same,
     atkPercent:same?leader.atkPercent:0,hpPercent:same?leader.hpPercent:0,
     originalEffect:true,appliedToLiveBattle:false});
 }
 function currentForm(baseId){
   if(!Number.isSafeInteger(baseId)||!P.roster.includes(baseId))return null;
   const value=effectiveUnit(baseId);
   return Number.isSafeInteger(value?.id)?value.id:null;
 }
 function snapshot(){
   const leaderBase=P.squad[0],leaderId=currentForm(leaderBase);
   const leader=lookup(leaderId),slots=[];
   for(const baseId of P.squad.slice(0,6)){
     const currentId=currentForm(baseId);
     slots.push(freeze({baseId,currentId,
       effect:leader&&currentId!==null?bonusFor(leaderId,currentId):null}));
   }
   return freeze({leaderBase:leaderBase??null,leaderId,
     leaderSupported:!!leader,leader,slots:freeze(slots),
     source,nativeLeaderBuffsApplied:false});
 }
 const panel=document.createElement('details');panel.id='bf11000-leader-audit';
 panel.style.cssText='padding:10px;margin:10px 2px;border:1px solid #9daaaa;'+
   'border-radius:7px;background:#1b3039;color:#edf5e9;'+
   'font:12px/1.5 system-ui,sans-serif';
 const heading=document.createElement('summary');
 heading.textContent='ORIGINAL STARTER LEADER SKILLS · 2022 SOURCE';
 heading.style.cssText='min-height:37px;font-weight:800;cursor:pointer';
 const status=document.createElement('p');status.id='bf11000-summary';
 const targets=document.createElement('div');targets.id='bf11000-targets';
 const caution=document.createElement('small');
 caution.textContent='2022 original data for 30 starter unit forms only. '+
   'ATK +25%/+50% and 6★ HP +10% for same-element units. '+
   'Source-qualified preview, NOT applied to combat yet. '+
   'Unknown leaders and other unit forms fail closed. '+
   'No squad, HP, ATK, save or rewards are changed.';
 panel.append(heading,status,targets,caution);host.after(panel);
 // Source-qualified Home leader preview; the same archived v110 lookup drives
 // the existing Units details. Never invent effects for unknown leaders.
 const homeParty=document.querySelector('#bf-home .bf-scene-squad #bf-scene-party');
 const homeLeader=homeParty?document.createElement('p'):null;
 if(homeLeader){
   homeLeader.id='bf11000-home-leader';
   homeLeader.setAttribute('role','status');
   homeLeader.setAttribute('aria-live','polite');
   homeLeader.style.cssText='box-sizing:border-box;width:100%;max-width:100%;'+
     'min-width:0;margin:7px 0;padding:8px 10px;background:#293244;'+
     'border:1px solid #a89166;color:#f4e4bd;font:700 11px/1.5 system-ui,sans-serif;'+
     'overflow-wrap:anywhere';
   homeParty.before(homeLeader);
 }
 const elements=freeze(['','Fire','Water','Earth','Thunder','Light','Dark']);
 function refresh(){
   const state=snapshot();
   const archiveCombat=!!window.BFGlobalStarterLeaderCombatV11100;
   caution.textContent=archiveCombat?
     'Original 2022 source effects for 30 starter forms. Matching-element '+
     'ATK/HP bonuses are applied to NEW archive DEMO squads; training is '+
     'unchanged. Native damage, stat rounding and other leaders remain unverified.':
     '2022 original data for 30 starter unit forms only. '+
     'ATK +25%/+50% and 6★ HP +10% for same-element units. '+
     'Source-qualified preview, NOT applied to combat yet. '+
     'Unknown leaders and other unit forms fail closed. '+
     'No squad, HP, ATK, save or rewards are changed.';
   status.textContent=state.leader?
     ('Slot 1 leader form #'+state.leaderId+' · Leader Skill #'+
       state.leader.lsId+' · matching element +'+
       state.leader.atkPercent+'% ATK / +'+
       state.leader.hpPercent+'% max HP '+(archiveCombat?'(archive DEMO battles)':'(reference only)')):
     'Selected leader is not among the 30 source-verified starter forms.';
   if(homeLeader){
     if(!state.leader){
       homeLeader.textContent='2022 ORIGINAL LEADER SKILL · '+ 
         'UNVERIFIED FOR CURRENT LEADER (30 starter forms supported)';
     }else{
       const matched=state.slots.filter(slot=>slot.effect?.sameElement===true).length;
       homeLeader.textContent='2022 LEADER SKILL · '+elements[state.leader.element]+
         ' · ATK +'+state.leader.atkPercent+'%'+
         (state.leader.hpPercent?' · HP +'+state.leader.hpPercent+'%':'')+
         ' · '+matched+' matching squad unit(s) · '+
         (archiveCombat?'new archive DEMO battles':'source preview only');
     }
   }
   targets.replaceChildren();
   if(panel.open){
     state.slots.forEach((slot,i)=>{
       const line=document.createElement('div');
       line.textContent='Squad slot '+(i+1)+' · Unit #'+
         (slot.currentId??'?')+' · '+
         (slot.effect?('ATK +'+slot.effect.atkPercent+
           '% / HP +'+slot.effect.hpPercent+'% '+(archiveCombat?'(new archive battles)':'(not applied)')):
           'No verified leader bonus in this subset');
       targets.append(line);
     });
   }
   return state;
 }
 panel.addEventListener('toggle',refresh);
 host.addEventListener('click',()=>{if(panel.open)refresh();});
 document.querySelector('.bf-navbar')?.addEventListener('click',refresh);
 window.addEventListener('bf-route-change',refresh);
 const timer=setInterval(()=>{if(!document.hidden&&panel.open)refresh();},2200);
 window.addEventListener('pagehide',()=>clearInterval(timer),{once:true});
 refresh();
 window.BFGlobalStarterLeaderSourceV11000=freeze({
   source,lookup,bonusFor,snapshot,refresh
 });
})();
