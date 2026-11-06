/* BF_GLOBAL_SBB_FALLBACK_DISPATCH */
(() => {
 'use strict';
 const sbb=window.BF044SBBDemo,previous=window.performUnit;
 if(window.BFGlobalSBBFallbackDispatch||typeof previous!=='function'||
    !sbb||typeof sbb.enabled!=='function'||typeof sbb.sourceFor!=='function'||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined')return;
 function normalize(unit){
  if(S.mode!=='archive'||S.over||unit?.action?.kind!=='sbb_demo'||
     !unit.active||unit.hp<=0||!Number.isSafeInteger(unit.id)||
     S.party?.[unit.id]!==unit)return false;
  if(sbb.enabled()&&unit.bb>=100&&sbb.sourceFor(unit.unitId)?.target==='all_enemies')
   return false;
  // Same fallback/target as the prototype, before status/critical observers.
  // A late recursive performUnit call would apply Injury a second time.
  unit.action={kind:'attack',target:unit.action.target??S.target};
  return true;
 }
 window.performUnit=async function(unit,token){
  normalize(unit);
  return previous.apply(this,arguments);
 };
 window.BFGlobalSBBFallbackDispatch=Object.freeze({normalize,
  source:Object.freeze({scope:'Existing invalid/disabled experimental SBB fallback',
   nativeSBBRestored:false,savedFieldsAdded:0})});
})();
