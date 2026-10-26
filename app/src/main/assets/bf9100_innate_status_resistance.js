/* BF_GLOBAL_INNATE_STATUS_RESISTANCE_V9100 */
(() => {
 'use strict';
 // Original 2022 F_UNIT_MST_1/2_Ver1084.unitInnateStatusResist.
 // Strictly 100% innate status immunity; no invented partial roll rates.
 // In source, 2259/2291 rows are all-zero, 28 are all-100,
 // two are paralysis-only 100%, and two malformed rows are excluded.
 if(window.BFGlobalInnateStatusResistV9100||
    !window.BFGlobalOriginalAilmentStateV5700||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined')return;
 const freeze=Object.freeze;
 const all=freeze([730302,730312,730322,730332,730342,730352,730362,
   750003,750004,750005,
   87102601,87102602,87102603,87202601,87202602,87202603,
   87302601,87302602,87302603,87402601,87402602,87402603,
   87502601,87502602,87502603,87602601,87602602,87602603]);
 const para=freeze([810212,820212]);
 const malformed=freeze([820518,830328]);
 if(all.length!==28||para.length!==2||malformed.length!==2||
    (new Set([...all,...para,...malformed])).size!==32)return;
 const allSet=new Set(all),paraSet=new Set(para);
 const source=freeze({
   archive:'2022 mst-decoded.zip',
   archiveSha256:'69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9',
   tables:freeze(['F_UNIT_MST_1_Ver1084.json','F_UNIT_MST_2_Ver1084.json']),
   tableSha256:freeze(['1146f09489a07b9187cd3f04bf7dc3ef3bb74e35385869534671af95bf8ea645',
     '0696ccda59fccf48598c5267eaeb8a306e994618384151cead38cec6a9195b2b']),
   field:'unitInnateStatusResist',
   originalRows:2291,zeroResistRows:2259,allImmuneRows:28,
   paralysisOnlyRows:2,malformedExcludedRows:2,
   order:freeze(['Poison','Weakness','Sickness','Injury','Curse','Paralysis']),
   nativeEffect:'A source value of 100 prevents corresponding new DEMO ailment infliction.',
   excludes:'No enemy status logic, status-infliction chance, effect duration, saves or item state modified.'
 });
 function lookup(unitId){
   if(!Number.isSafeInteger(unitId))return null;
   if(allSet.has(unitId))return freeze({unitId,
     percentages:freeze([100,100,100,100,100,100]),sourceExact:true});
   if(paraSet.has(unitId))return freeze({unitId,
     percentages:freeze([0,0,0,0,0,100]),sourceExact:true});
   return null; // all-zero or missing/invalid source: fail open to prior DEMO engine.
 }
 function isImmune(unitId,code){
   if(!Number.isSafeInteger(code)||code<1||code>6)return false;
   return lookup(unitId)?.percentages[code-1]===100;
 }
 function immune(slot,code){
   if(S.mode!=='archive'||S.over||!Number.isSafeInteger(slot)||
      slot<0||slot>=6||!Number.isSafeInteger(code)||code<1||code>6)return false;
   const unit=S.party?.[slot];
   return !!unit&&unit.active&&unit.hp>0&&
     isImmune(unit.unitId,code);
 }
 function snapshot(){
   return freeze({mode:S.mode,round:S.round,source,
     immuneParty:freeze((S.party||[]).filter(p=>p?.active&&p.hp>0&&lookup(p.unitId))
       .map(p=>freeze({slot:p.id,unitId:p.unitId,percentages:lookup(p.unitId).percentages})))});
 }
 window.BFGlobalInnateStatusResistV9100=freeze({source,lookup,isImmune,immune,snapshot});
})();
