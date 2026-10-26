/* BF_GLOBAL_ORIGINAL_CRYSTAL_DROP_CORE_V8100 */
(()=>{
 'use strict';
 // Original Global BC base 35% per DROP CHECK, HC base 10% per HIT.
 // A 2022 sourced damage-hit timeline does NOT establish BC drop-check
 // count: do not replace missing BC values with hit count.
 const hits=window.BFOriginalHitSequenceV700;
 if(window.BFGlobalOriginalCrystalDropCoreV8100||!hits||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined')return;
 const source=Object.freeze({
   unitHitSource:'2022 F_UNIT normal hit frame and damage weight archive',
   originalHitCatalog:71,
   bcBasePercent:35,hcBasePercent:10,overkillMultiplier:2,
   bcReference:'https://bravefrontierglobal.fandom.com/wiki/Drop_Rate',
   hcReference:'https://bravefrontierglobal.fandom.com/wiki/Drop_Rate_Boost',
   sourceBoundary:'The separate v82 source has recovered normal attack BC dropCheckCount. Skill BB/SBB checks, enemy crystal resistances, passive bonuses, pickup distribution and original healing per Heart Crystal remain unknown.',
   effects:'Pure probabilistic core only: does not spawn crystals, heal HP, fill BB gauges, change inventory or award rewards.'
 });
 function hitCount(unitId){
   if(!Number.isSafeInteger(unitId))return null;
   const sourceHits=hits.get(unitId);
   if(!Array.isArray(sourceHits)||!sourceHits.length||sourceHits.length>200||
      !sourceHits.every(row=>Array.isArray(row)&&row.length===2&&
        Number.isSafeInteger(row[0])&&row[0]>=0&&
        Number.isSafeInteger(row[1])&&row[1]>=0&&row[1]<=100)||
      sourceHits.reduce((sum,row)=>sum+row[1],0)!==100)return null;
   return sourceHits.length;
 }
 function integerRoll(random=Math.random){
   if(typeof random!=='function')return null;
   const sample=random();
   return Number.isFinite(sample)&&sample>=0&&sample<1?
     Math.floor(sample*101):null;
 }
 function chance(percent,random=Math.random){
   if(!Number.isFinite(percent)||percent<0)return null;
   if(percent===0)return false;
   if(percent>=100)return true;
   // The Global community mechanics reference states the RNG is an
   // integer from 0..100, inclusively, with <= chance to drop a crystal.
   const roll=integerRoll(random);
   return roll===null?null:roll<=percent;
 }
 function sampleChecks(checks,basePercent,overkill=false,random=Math.random){
   if(!Number.isSafeInteger(checks)||checks<0||checks>400||
      !Number.isFinite(basePercent)||basePercent<0||basePercent>100||
      typeof overkill!=='boolean')return null;
   const rate=Math.min(100,basePercent*(overkill?2:1));
   let generated=0;
   for(let i=0;i<checks;i++){
     const dropped=chance(rate,random);
     if(dropped===null)return null;
     if(dropped)generated++;
   }
   return generated;
 }
 function sampleHC(unitId,{overkill=false,random=Math.random}={}){
   const count=hitCount(unitId);
   return count===null?null:sampleChecks(count,source.hcBasePercent,overkill,random);
 }
 function sampleBC(dropChecks,{overkill=false,random=Math.random}={}){
   // DO NOT infer dropChecks from hitCount. Some BF skills roll multiple
   // BC checks per hit, and the archive has not decoded that value.
   return sampleChecks(dropChecks,source.bcBasePercent,overkill,random);
 }
 function expected(unitId){
   const count=hitCount(unitId);
   if(count===null)return null;
   return Object.freeze({
     unitId,normalHits:count,expectedHeartCrystals:count*source.hcBasePercent/100,
     expectedBattleCrystals:window.BFGlobalNormalCrystalChecksV8200?.lookup(unitId)?.expectedBattleCrystals??null,
     unknownBattleCrystalChecks:!window.BFGlobalNormalCrystalChecksV8200?.lookup(unitId),
     interpretation:'No enemy resistances, extra hits or status passives assumed.'
   });
 }
 function snapshot(){
   return Object.freeze({source,mode:S.mode,round:S.round,
     playable:Object.freeze((S.party||[]).filter(p=>p?.active&&p.hp>0)
       .map(p=>expected(p.unitId)).filter(Boolean))});
 }
 window.BFGlobalOriginalCrystalDropCoreV8100=Object.freeze({
   source,hitCount,integerRoll,chance,sampleHC,sampleBC,expected,snapshot
 });
})();