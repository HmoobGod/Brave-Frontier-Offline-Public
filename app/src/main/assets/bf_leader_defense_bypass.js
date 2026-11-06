/* BF_GLOBAL_RUIN_GOD_DEFENSE_COMPONENT */
(() => {
 'use strict';
 const profiles=window.BFGlobalPlayableLeadersV11200;
 const english=window.BFGlobalOriginalLeaderEnglishV11400;
 const normal=window.BFGlobalAllNormalCrystalChecksV8400;
 const previousPerform=window.performUnit,previousDamage=window.prototypeDamage;
 if(window.BFGlobalLeaderDefenseBypass||!profiles?.lookup||!english?.lookup||
    !normal?.lookup||typeof previousPerform!=='function'||
    typeof previousDamage!=='function'||typeof effectiveUnit!=='function'||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined')return;
 function leader(){
  if(S.mode!=='archive'||S.over||!Array.isArray(P.squad)||
     !Array.isArray(P.roster)||!P.roster.includes(P.squad[0]))return null;
  const base=P.squad[0],form=effectiveUnit(base),actor=S.party?.[0];
  if(form?.id!==60025||actor?.baseId!==base||actor.unitId!==form.id||
     actor.active!==true)return null;
  const raw=profiles.lookup(form.id),text=english.lookup(1314);
  if(raw?.unitId!==60025||raw.lsId!==1314||raw.skillTypeRaw!=='31@29'||
     raw.passiveSkillInfoRaw!=='50,0,0,0,0,0@15'||
     text?.originalEnglishName!=="Ruin God's Epidemic"||
     text.originalEnglishDescription!=="Huge boost to damage produced during Spark & adds chance of ignoring an opponent's Def when attacking")return null;
  return Object.freeze({unitId:60025,leaderSkillId:1314,chancePercent:15,
    sparkImplemented:false,scope:'Source-qualified single-hit normals only'});
 }
 function eligible(unit){
  if(!leader()||unit?.action?.kind!=='attack'||unit.active!==true||unit.hp<=0||
     !Number.isSafeInteger(unit.id)||unit.id<0||unit.id>=6||
     S.party?.[unit.id]!==unit||!profiles.lookup(unit.unitId)||
     normal.lookup(unit.unitId)?.normalHits!==1||
     !Number.isSafeInteger(unit.action.target)||typeof pickTarget!=='function')return null;
  const target=pickTarget(unit.action.target);
  return target?{battle:S,unit,slot:unit.id,target,attempted:false}:null;
 }
 function roll(random=Math.random){
  if(typeof random!=='function')return null;
  const r=random();
  return Number.isFinite(r)&&r>=0&&r<1?r<0.15:null;
 }
 let context=null;
 window.prototypeDamage=function(...args){
  const c=context;
  if(!c||c.attempted||S!==c.battle||S.party?.[c.slot]!==c.unit||
     c.unit.action?.kind!=='attack'||c.unit.hp<=0||c.target.hp<=0||!leader()||
     !Number.isSafeInteger(args[0])||args[0]<=0||
     !Number.isSafeInteger(args[1])||args[1]<0||args[1]!==c.target.def)
   return previousDamage.apply(this,args);
  c.attempted=true;
  if(roll()===true){
   // Change only the input to the existing DEMO formula, never enemy stats.
   const bypass=args.slice();bypass[1]=0;
   return previousDamage.apply(this,bypass);
  }
  return previousDamage.apply(this,args);
 };
 window.performUnit=async function(unit,token){
  const prior=context;context=eligible(unit);
  try{return await previousPerform.apply(this,arguments);}
  finally{context=prior;}
 };
 window.BFGlobalLeaderDefenseBypass=Object.freeze({leader,roll,
  source:Object.freeze({unitId:60025,leaderSkillId:1314,
   skillTypeRaw:'31@29',passiveSkillInfoRaw:'50,0,0,0,0,0@15',
   chancePercent:15,normalHitRequirement:1,sparkImplemented:false,
   savedFieldsAdded:0,nativeDamageFormulaRecovered:false})});
})();
