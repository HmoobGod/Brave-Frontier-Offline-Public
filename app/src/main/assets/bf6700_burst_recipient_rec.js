/* BF_GLOBAL_BURST_RECIPIENT_RECOVERY_V6700 */
(() => {
 'use strict';
 // Source Lv1 BB base HP range + community-documented recipient TOTAL REC.
 // The exact healer REC coefficient, buff interactions and rounding remain
 // unresolved. This module deliberately adds only the known recipient term.
 if(window.BFGlobalBurstRecipientRecoveryV6700||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined')return;
 const source=Object.freeze({
  type:'BB burst healing (2022 skillTypeId 2)',
  level:1,baseRange:Object.freeze([600,800]),
  archivedSkillIds:Object.freeze([20041,30041,40041,50041]),
  wiki:'https://bravefrontierglobal.fandom.com/wiki/Burst_Healing',
  originalData:'3-mst-translated/F_SKILL_LEVEL_MST_1_Ver1487.json',
  interpretation:'additive recipient REC supported; healer coefficient and exact rounding unverified'
 });
 function healAmount(base,ally){
   // No synthetic heal if the battle is outside its source-backed quest mode.
   if(S.mode!=='archive'||S.over||
      !Number.isFinite(base)||base<0||!ally||
      !Number.isFinite(ally.rec)||ally.rec<0)return base;
   // ally.rec is the live stat, so v65 Sickness and future verified REC buffs
   // can be reflected without mutating persistent unit statistics or saves.
   const sourceBase=window.BFGlobalOriginalHealBBLevelsV6800?.baseHeal(base)??base;
   return Math.max(0,Math.round(sourceBase)+Math.max(0,Math.round(ally.rec)));
 }
 window.BFGlobalBurstRecipientRecoveryV6700=Object.freeze({source,healAmount});
})();
