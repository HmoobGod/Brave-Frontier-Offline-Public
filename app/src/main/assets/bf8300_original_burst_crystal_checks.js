/* BF_GLOBAL_SOURCE_BURST_CRYSTAL_CHECKS_V8300 */
(()=>{
 'use strict';
 // Recovered F_SKILL_MST dropCheckCount joined to F_UNIT bbId/sbbId.
 // Strict single-group damage events permit reference per-target math only.
 // Unresolved @ multi-group skills have no guessed BC totals.
 const core=window.BFGlobalOriginalCrystalDropCoreV8100;
 const normal=window.BFGlobalNormalCrystalChecksV8200;
 if(window.BFGlobalBurstCrystalChecksV8300||!core||!normal||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined')return;
 const recorded=Object.freeze([[10011,0,10011,1,5,true],[10012,0,10012,1,5,true],[10013,0,10013,1,6,true],[10014,0,10014,1,6,true],[10015,0,10015,1,8,true],[10021,0,10021,1,null,false],[10022,0,10022,1,null,false],[10024,0,10024,1,null,false],[10025,0,10025,1,null,false],[10041,0,10041,1,5,true],[10042,0,10042,1,7,true],[20011,0,20011,1,4,true],[20012,0,20012,1,5,true],[20013,0,20013,1,7,true],[20014,0,20014,1,8,true],[20015,0,20015,1,8,true],[20021,0,20021,1,null,false],[20022,0,20022,1,null,false],[20023,0,20023,1,null,false],[20024,0,20024,1,null,false],[20025,0,20025,1,null,false],[20041,0,20041,1,1,false],[20042,0,20042,1,1,false],[30011,0,30011,1,4,true],[30012,0,30012,1,5,true],[30013,0,30013,1,5,true],[30014,0,30014,1,6,true],[30015,0,30015,1,8,true],[30021,0,30021,1,3,true],[30022,0,30022,1,3,true],[30023,0,30023,1,6,true],[30024,0,30024,1,8,true],[30025,0,30025,1,13,true],[30041,0,30041,1,1,false],[30042,0,30042,1,1,false],[40011,0,40011,1,2,true],[40012,0,40012,1,2,true],[40013,0,40013,1,5,true],[40014,0,40014,1,7,true],[40015,0,40015,1,8,true],[40021,0,40021,1,1,false],[40022,0,40022,1,1,false],[40023,0,40023,1,1,false],[40024,0,40024,1,1,false],[40025,0,40025,1,1,false],[40041,0,40041,1,1,false],[40042,0,40042,1,1,false],[50011,0,50011,1,2,true],[50012,0,50012,1,3,true],[50013,0,50013,1,4,true],[50014,0,50014,1,5,true],[50015,0,50015,1,8,true],[50021,0,50021,1,2,true],[50022,0,50022,1,3,true],[50023,0,50023,1,4,true],[50024,0,50024,1,6,true],[50025,0,50025,1,10,true],[50041,0,50041,1,1,false],[50042,0,50042,1,1,false],[60011,0,60011,1,3,true],[60012,0,60012,1,4,true],[60013,0,60013,1,4,true],[60014,0,60014,1,6,true],[60015,0,60015,1,8,true],[60021,0,60021,1,2,true],[60022,0,60022,1,3,true],[60023,0,60023,1,4,true],[60024,0,60024,1,6,true],[60025,0,60025,1,8,true],[60041,0,60041,1,null,false],[60042,0,60042,1,null,false],[10015,1,110015,1,null,false],[10025,1,110025,1,null,false],[20015,1,120015,1,null,false],[20025,1,120025,1,null,false],[30015,1,130015,1,null,false],[30025,1,130025,1,null,false],[40015,1,140015,1,null,false],[40025,1,140025,1,null,false],[50015,1,150015,1,null,false],[50025,1,150025,1,null,false],[60015,1,160015,1,null,false],[60025,1,160025,25,1,true]]);
 const source=Object.freeze({
   archive:'mst-decoded.zip',table:'F_SKILL_MST_1..9_Ver1535.json',
   field:'dropCheckCount',bbProfiles:71,sbbProfiles:12,simpleDamageGroups:61,offensiveSimpleGroups:48,
   baseBCPercent:35,
   sourceBoundary:'Skill check counts are sourced. Healing and buff effectFrames are not BC-producing damage; complex damage groups, target counts, pickup mechanics remain unresolved.',
   effects:'Read-only reference module; no battle, save or reward mutations.'
 });
 const byId=new Map();
 for(const row of recorded){
   const [unitId,kind,skillId,checks,events,isOffensiveDamage]=row;
   if(!Number.isSafeInteger(unitId)||!normal.lookup(unitId)||
      (kind!==0&&kind!==1)||!Number.isSafeInteger(skillId)||skillId<=0||
      !Number.isSafeInteger(checks)||checks<=0||checks>100||
      typeof isOffensiveDamage!=='boolean'||(isOffensiveDamage&&events===null)||
      (events!==null&&(!Number.isSafeInteger(events)||events<=0||events>200))||
      (byId.has(unitId)&&byId.get(unitId).some(r=>r[1]===kind)))return;
   if(!byId.has(unitId))byId.set(unitId,[]);
   byId.get(unitId).push(row);
 }
 if(recorded.length!==83||recorded.filter(r=>r[1]===0).length!==71||
    recorded.filter(r=>r[1]===1).length!==12||
    recorded.filter(r=>r[4]!==null).length!==61||
    recorded.filter(r=>r[5]).length!==48)return;
 function lookup(unitId,kind='BB'){
   if(!Number.isSafeInteger(unitId)||(kind!=='BB'&&kind!=='SBB'))return null;
   const row=byId.get(unitId)?.find(r=>r[1]===(kind==='BB'?0:1));
   if(!row)return null;
   const events=row[4],checksPerEvent=row[3];
   const isOffensiveDamage=row[5];
   const checksPerTarget=events===null||!isOffensiveDamage?null:events*checksPerEvent;
   return Object.freeze({unitId,kind,skillId:row[2],checksPerEvent,
     simpleDamageEvents:events,isOffensiveDamage,checksPerTarget,
     expectedBCPerTarget:checksPerTarget===null?null:checksPerTarget*source.baseBCPercent/100,
     unknownComplexDamageGroups:events===null,
     nonOffensiveEffect:events!==null&&!isOffensiveDamage,
     status:'Per-target evidence only: actual native damage-hit groups and pickup mechanics may differ'});
 }
 function rollPerTarget(unitId,kind='BB',options={}){
   if(!options||typeof options!=='object')return null;
   const {overkill=false,random=Math.random}=options;
   const profile=lookup(unitId,kind);
   if(!profile||profile.checksPerTarget===null||typeof overkill!=='boolean'||
      typeof random!=='function')return null;
   const battleCrystals=core.sampleBC(profile.checksPerTarget,{overkill,random});
   return battleCrystals===null?null:Object.freeze({
     ...profile,overkill,battleCrystals,
     status:'Reference simulation per target; no actual crystal spawn, pickup or BB gain'});
 }
 function snapshot(){return Object.freeze({source,mode:S.mode,round:S.round,
   playable:Object.freeze((S.party||[]).filter(p=>p?.active&&p.hp>0)
     .map(p=>lookup(p.unitId)).filter(Boolean))});}
 window.BFGlobalBurstCrystalChecksV8300=Object.freeze({source,lookup,rollPerTarget,snapshot});
})();
