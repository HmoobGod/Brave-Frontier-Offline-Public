/* BF_GLOBAL_SOURCE_OFFENSIVE_BB_LEVELS_V9200 */
(() => {
 'use strict';
 // Exact primary group 2022 F_SKILL_LEVEL_MST damage modifiers for 24
 // source-known offensive BBs. Level choice is a battle-only DEMO preview.
 const original=window.BFOriginalBBPower;
 const preview=window.BFGlobalOriginalHealBBLevelsV6800;
 const prior=window.bbDamageMultiplier;
 if(window.BFGlobalSourceOffensiveBBLevelsV9200||!original||!preview||
    typeof prior!=='function'||typeof original.forUnit!=='function'||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined')return;
 const freeze=Object.freeze;
 // v30 sourced 24 offensive skills; unsupported IDs fail closed.
 // Sanity check source examples; all other units validated per invocation.
 const v1=original.forUnit(10011),v2=original.forUnit(10021);
 if(original.count!==24||!v1||!v2||v1.base!==30||v2.base!==150||
    !Array.isArray(v1.levels)||v1.levels.length!==10||
    v1.levels[9]!==75||v2.levels[9]!==240)return;
 function sourceFor(unitId,level=preview.snapshot().level){
   if(!Number.isSafeInteger(unitId)||!Number.isInteger(level)||
      level<1||level>10)return null;
   const v=original.forUnit(unitId);
   if(!v||!Array.isArray(v.levels)||v.levels.length!==10||
      !Number.isFinite(v.base)||v.levels[0]!==v.base||
      v.levels.some(x=>!Number.isFinite(x)||x<0||x>400))return null;
   return freeze({unitId,level,modifierPercent:v.levels[level-1],
     multiplier:1+v.levels[level-1]/100,primaryGroupOnly:true,
     remainingEffectsNotModeled:!!v.secondaryUnmodeled});
 }
 function multiplierFor(unit,burst){
   if(!burst||S.mode!=='archive'||S.over||!unit||
      !Number.isSafeInteger(unit.unitId))return null;
   const entry=sourceFor(unit.unitId);
   return entry?entry.multiplier:null;
 }
 const wrapper=function(unit,burst){
   const recovered=multiplierFor(unit,burst);
   return recovered===null?prior.call(this,unit,burst):recovered;
 };
 window.bbDamageMultiplier=wrapper;
 const parent=document.getElementById('bf6800-levels');
 const message=document.createElement('small');message.id='bf9200-offensive-note';
 message.textContent='Original 2022 offensive BB Lv.1–10 damage modifiers are now used in this DEMO battle for source-supported skills. The selected level is not permanent mastery; remaining effects and native damage formula are unverified.';
 if(parent)parent.append(message);
 const source=freeze({archive:'2022 F_SKILL_LEVEL_MST_1..4_Ver1487.json',
   crosscheck:'source_data/bf_global_original_bb_power_v030.json',
   supportedOffensiveSkills:24,sourceModifierLevels:10,
   fallback:'Existing Lv1 DEMO result for unsupported or inactive cases',
   scope:'Recovered primary damage modifier only; no secondary effects or saved BB mastery'});
 const snapshot=()=>freeze({mode:S.mode,level:preview.snapshot().level,
   source,starter:sourceFor(10011)});
 window.BFGlobalSourceOffensiveBBLevelsV9200=freeze({
   source,sourceFor,multiplierFor,snapshot
 });
})();
