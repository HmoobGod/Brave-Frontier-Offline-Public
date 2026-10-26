/* BF_GLOBAL_SOURCE_NORMAL_CRYSTAL_CHECKS_V8200 */
(()=>{
 'use strict';
 // Original 2022 F_UNIT_MST dropCheckCount field (per normal hit), paired
 // only with 71 validated source hit profiles from v700 and v81 core.
 // Does not invent BB/SBB checks, crystal pickups, resistances or rewards.
 const core=window.BFGlobalOriginalCrystalDropCoreV8100;
 if(window.BFGlobalNormalCrystalChecksV8200||!core||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined')return;
 const recorded=Object.freeze([[10011,2],[10012,2],[10013,2],[10014,3],[10015,3],[10021,2],[10022,2],[10024,2],[10025,2],[10041,2],[10042,2],[20011,3],[20012,3],[20013,3],[20014,3],[20015,4],[20021,2],[20022,2],[20023,2],[20024,2],[20025,2],[20041,2],[20042,2],[30011,3],[30012,3],[30013,3],[30014,4],[30015,5],[30021,2],[30022,2],[30023,2],[30024,2],[30025,2],[30041,2],[30042,2],[40011,8],[40012,8],[40013,7],[40014,6],[40015,8],[40021,2],[40022,2],[40023,2],[40024,2],[40025,2],[40041,2],[40042,2],[50011,8],[50012,8],[50013,6],[50014,6],[50015,6],[50021,2],[50022,2],[50023,2],[50024,2],[50025,3],[50041,2],[50042,2],[60011,8],[60012,8],[60013,6],[60014,6],[60015,6],[60021,3],[60022,3],[60023,3],[60024,3],[60025,3],[60041,2],[60042,2]]);
 const source=Object.freeze({
   archive:'mst-decoded.zip',
   tableParts:Object.freeze([
     Object.freeze({file:'F_UNIT_MST_1_Ver1084.json',sha256:'1146f09489a07b9187cd3f04bf7dc3ef3bb74e35385869534671af95bf8ea645'}),
     Object.freeze({file:'F_UNIT_MST_2_Ver1084.json',sha256:'0696ccda59fccf48598c5267eaeb8a306e994618384151cead38cec6a9195b2b'})
   ]),
   column:'dropCheckCount',profileCount:71,
   bcBasePercent:35,hcBasePercent:10,
   sourceBoundary:'Normal attack drop checks are original, but enemy BC/HC resistance, crystals reaching particular allies and health/BB pickup amounts are unknown. No battle HP, BB or inventory mutations.'
 });
 if(recorded.length!==71||new Set(recorded.map(r=>r[0])).size!==71)return;
 const counts=new Map();
 for(const [unitId,count] of recorded){
   if(!Number.isSafeInteger(unitId)||!Number.isSafeInteger(count)||
      count<=0||count>20||core.hitCount(unitId)===null)return;
   counts.set(unitId,count);
 }
 if(core.hitCount(10023)!==null||counts.get(10011)!==2||
    counts.get(40011)!==8||counts.get(30015)!==5)return;
 function lookup(unitId){
   if(!Number.isSafeInteger(unitId)||!counts.has(unitId))return null;
   const normalHits=core.hitCount(unitId);
   if(normalHits===null)return null;
   const perHit=counts.get(unitId),totalChecks=perHit*normalHits;
   return Object.freeze({
     unitId,normalHits,checksPerHit:perHit,totalDropChecks:totalChecks,
     expectedBattleCrystals:totalChecks*source.bcBasePercent/100,
     expectedHeartCrystals:normalHits*source.hcBasePercent/100
   });
 }
 function rollNormal(unitId,{overkill=false,random=Math.random}={}){
   const data=lookup(unitId);
   if(!data||typeof overkill!=='boolean'||typeof random!=='function')return null;
   const battleCrystals=core.sampleBC(data.totalDropChecks,{overkill,random});
   const heartCrystals=core.sampleHC(unitId,{overkill,random});
   if(battleCrystals===null||heartCrystals===null)return null;
   return Object.freeze({
     ...data,overkill,battleCrystals,heartCrystals,
     status:'Source baseline drop rolls only; no pickup, healing or BB-gauge effect'
   });
 }
 function snapshot(){
   return Object.freeze({source,mode:S.mode,round:S.round,
     party:Object.freeze((S.party||[]).filter(p=>p?.active&&p.hp>0)
       .map(p=>lookup(p.unitId)).filter(Boolean))});
 }
 window.BFGlobalNormalCrystalChecksV8200=Object.freeze({
   source,lookup,rollNormal,snapshot
 });
})();