/* BF_GLOBAL_ORIGINAL_TYPE5_ELEMENT_RESIST_V16600 */
(() => {
 'use strict';
 // Archived 2022 Global type-5 leader effect: 10% less incoming damage
 // FROM the specified enemy element. This does not authenticate DEMO waves.
 const profiles=window.BFGlobalPlayableLeadersV11200;
 const english=window.BFGlobalOriginalLeaderEnglishV11400;
 const elements=window.BFGlobalElementalCombatV6900;
 if(window.BFGlobalOriginalElementResistV16600||
    !profiles?.lookup||!english?.lookup||!elements?.normalize||
    typeof P==='undefined'||P.version!==7||
    typeof S==='undefined'||typeof effectiveUnit!=='function')return;
 const byLeader=Object.freeze({
   500:['Fire','1,10'],502:['Water','2,10'],
   504:['Earth','3,10'],506:['Thunder','4,10'],
   508:['Light','5,10'],510:['Dark','6,10']
 });
 const freeze=Object.freeze;
 let applied=0;
 function leader(){
   if(S.mode!=='archive'||S.over||!Array.isArray(P.squad)||
      !Array.isArray(P.roster)||!P.roster.includes(P.squad[0]))return null;
   const form=effectiveUnit(P.squad[0]);
   if(!Number.isSafeInteger(form?.id))return null;
   const raw=profiles.lookup(form.id);
   if(!raw||raw.unitId!==form.id||raw.skillTypeRaw!=='5')return null;
   const spec=byLeader[raw.lsId];
   if(!spec||raw.passiveSkillInfoRaw!==spec[1]||
      english.lookup(raw.lsId)?.originalEnglishDescription!==
        '10% reduction in damage from '+spec[0]+' Types')return null;
   return freeze({unitId:form.id,leaderId:raw.lsId,
     resistedElement:spec[0],reductionPercent:10});
 }
 function scaleIncoming(amount,attackerElement,target){
   if(!Number.isSafeInteger(amount)||amount<=0||
      !target||typeof target!=='object'||target.active!==true||
      !Array.isArray(S.party)||!S.party.includes(target)||target.hp<=0)
     return amount;
   const l=leader();
   if(!l||elements.normalize(attackerElement)!==l.resistedElement)
     return amount;
   // Source 10% is verified; rounding/native defense order are still DEMO.
   const reduced=Math.max(1,Math.round(amount*0.9));
   applied++;
   return reduced;
 }
 const panelHost=document.getElementById('bf11100-leader-combat')||
   document.getElementById('squadpicker');
 let panel=null,status=null;
 function refresh(){
   const l=leader();
   if(panel){
     panel.hidden=S.mode!=='archive';
     status.textContent=l?
       'Original leader #'+l.leaderId+' protects the squad: 10% less '+
       l.resistedElement+'-element enemy damage (when the enemy element is known).':
       'No source-confirmed 10% elemental-protection leader equipped.';
   }
   return freeze({mode:S.mode,leader:l,applied,
     saveFieldsAdded:0,trainingUnaffected:true,
     nativeRoundingVerified:false,unknownEnemyElementsUnaffected:true});
 }
 if(panelHost){
   panel=document.createElement('details');panel.id='bf16600-resist';
   panel.style.cssText='margin:7px 2px;padding:8px;border:1px solid #93aaa0;'+
     'border-radius:6px;color:#eef4eb;background:#20363c;'+
     'font:12px/1.5 system-ui,sans-serif';
   const title=document.createElement('summary');
   title.textContent='ORIGINAL ELEMENTAL PROTECTION · TYPE 5';
   title.style.cssText='cursor:pointer;font-weight:800;min-height:34px';
   status=document.createElement('p');status.id='bf16600-status';
   const note=document.createElement('small');
   note.textContent='Original 2022 skill descriptions and exact 10% source passive. '+
     'Only known-element incoming attacks in archive DEMO battles qualify. '+
     'No inferred 2022 enemy formations, native rounding, training changes, '+
     'new Gem rewards or save writes.';
   panel.append(title,status,note);
   panelHost.after(panel);
   document.getElementById('mode')?.addEventListener('change',refresh);
   document.getElementById('reset')?.addEventListener('click',()=>setTimeout(refresh,0));
 }
 window.BFGlobalOriginalElementResistV16600=freeze({
   source:freeze({archive:'2022 F_LEADER_SKILL_MST_Ver749 + BF1_sgtext',
     sourceQualifiedForms:12,leaderIds:6,reductionPercent:10,
     saveFieldsAdded:0,originalDamageFormulaRecovered:false}),
   leader,scaleIncoming,refresh,snapshot:refresh
 });
 refresh();
})();
