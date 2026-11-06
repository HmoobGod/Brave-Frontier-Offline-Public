/* BF_GLOBAL_INTENSE_EDGE_CRITICAL_COMPONENT */
(() => {
 'use strict';
 // Exact archived Intense Edge critical component only. Spark is not activated.
 const profiles=window.BFGlobalPlayableLeadersV11200;
 const english=window.BFGlobalOriginalLeaderEnglishV11400;
 if(window.BFGlobalLeaderCriticalBonus||!profiles?.lookup||!english?.lookup||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof effectiveUnit!=='function')return;
 function leader(){
  if(S.mode!=='archive'||S.over||!Array.isArray(P.squad)||
     !Array.isArray(P.roster)||!P.roster.includes(P.squad[0]))return null;
  const base=P.squad[0],form=effectiveUnit(base),battleLeader=S.party?.[0];
  // Require the actual current battle leader, not a preview or a changed squad.
  if(form?.id!==10025||battleLeader?.baseId!==base||
     battleLeader.unitId!==form.id||battleLeader.active!==true)return null;
  const raw=profiles.lookup(form.id),text=english.lookup(1313);
  if(raw?.unitId!==10025||raw.lsId!==1313||raw.skillTypeRaw!=='31@34'||
     raw.passiveSkillInfoRaw!=='50,0,0,0,0,0@0.5'||
     text?.originalEnglishName!=='Intense Edge'||
     text.originalEnglishDescription!==
       'Huge boost to damage produced during Spark & slight boost to critical hit damage')return null;
  return Object.freeze({unitId:10025,leaderSkillId:1313,criticalBonus:0.5,
    sparkImplemented:false,nativeDamageFormulaRecovered:false});
 }
 function scale(baseDamage,ordinaryCriticalDamage,unit,isCritical){
  if(isCritical!==true||!Number.isSafeInteger(baseDamage)||baseDamage<1||
     !Number.isSafeInteger(ordinaryCriticalDamage)||
     ordinaryCriticalDamage!==Math.max(1,Math.floor(baseDamage*1.5))||
     !unit||unit.active!==true||unit.hp<=0||unit.action?.kind!=='attack'||
     !Number.isSafeInteger(unit.id)||S.party?.[unit.id]!==unit||
     !profiles.lookup(unit.unitId)||!leader())return ordinaryCriticalDamage;
  // Source scalar +0.5 is additive to the existing 1.5 critical multiplier.
  // Keep the existing DEMO per-hit floor; native full damage order is unknown.
  const result=Math.floor(baseDamage*2);
  return Number.isSafeInteger(result)&&result>0?result:ordinaryCriticalDamage;
 }
 window.BFGlobalLeaderCriticalBonus=Object.freeze({leader,scale,
  source:Object.freeze({unitId:10025,leaderSkillId:1313,
   skillTypeRaw:'31@34',passiveSkillInfoRaw:'50,0,0,0,0,0@0.5',
   criticalBonus:0.5,sparkImplemented:false,savedFieldsAdded:0,
   scope:'Critical component only, existing source-qualified normal attacks'})});
})();
