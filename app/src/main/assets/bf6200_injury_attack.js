/* BF_GLOBAL_INJURY_ATTACK_V6200 */
(() => {
 'use strict';
 // Independent Global-era reference: Injury applies a subtractive -50% ATK.
 // Native stat-buff stacking, exact rounding, skill infliction and animations
 // are not established. This affects only the existing DEMO player attack phase.
 const ailments=window.BFGlobalOriginalAilmentStateV5700;
 if(window.BFGlobalInjuryAttackV6200||!ailments||
    !window.BFGlobalWeaknessDefenseV6100||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof performUnit!=='function'||typeof enemyPhase!=='function')return;
 const previousPerform=window.performUnit;
 const previousEnemy=window.enemyPhase;
 const source=Object.freeze({
   statusCode:4,name:'Injury',stat:'ATK',penaltyPercent:50,
   observedPlayerTurns:3,cureItemId:20210,
   statusEvidence:'3-mst-translated/F_ITEM_MST_Ver1027.json',
   reference:'https://bravefrontierglobal.fandom.com/wiki/Status_Infliction',
   interpretation:'community-documented additive -50% stat penalty; demo rounding and buff application'
 });
 let battle=S;
 const ages=new WeakMap();
 function sync(){if(S!==battle)battle=S;}
 function injured(slot){
   sync();
   return S.mode==='archive'&&!S.over&&Number.isInteger(slot)&&
     slot>=0&&slot<6&&ailments.codesFor(slot).includes(4);
 }
 function track(slot){
   if(!injured(slot))return null;
   const unit=S.party?.[slot];
   if(!unit||!unit.active||unit.hp<=0)return null;
   const token=ailments.tokenFor(slot,4);
   if(token===null)return null;
   let record=ages.get(unit);
   if(!record||record.token!==token){
     record={token,firstRound:S.round,lastRound:null};
     ages.set(unit,record);
   }
   return record;
 }
 // The documented -50% ailment is SUBTRACTIVE to positive ATK buffs,
 // not a multiplicative halving of an already-buffed attack. Existing DEMO
 // effectivePlayerAtk multiplies unit.atk by (1 + currentAtkBoost/100).
 // During the action, feed it the unique temporary base that results in
 // round(originalBase * (1 + boost% - 0.5)) after its own rounding step.
 function boostMultiplier(unit){
   const pct=typeof currentAtkBoost==='function'?Number(currentAtkBoost(unit)):0;
   return Number.isFinite(pct)&&pct>=0?1+pct/100:1;
 }
 function effectiveAttack(slot){
   const p=S.party?.[slot],atk=p?.atk;
   if(!Number.isFinite(atk))return null;
   const multiplier=boostMultiplier(p);
   return Math.max(0,Math.round(atk*(multiplier-(injured(slot)?.5:0))));
 }
 async function withInjuryAttack(slot,callback){
   if(typeof callback!=='function')throw new TypeError('callback required');
   sync();
   const unit=S.party?.[slot];
   if(!injured(slot)||!unit||!unit.active||unit.hp<=0||
      !Number.isFinite(unit.atk))return callback();
   track(slot);
   const originalAtk=unit.atk,multiplier=boostMultiplier(unit);
   const desired=Math.max(0,Math.round(originalAtk*(multiplier-.5)));
   // Keep no-buff values integer (backward-compatible single-action API).
   // With a buff, this fractional intermediate is strictly ephemeral and
   // the original effectivePlayerAtk rounds the combined additive result.
   const reducedAtk=multiplier===1?
     Math.max(0,Math.round(originalAtk*.5)):desired/multiplier;
   unit.atk=reducedAtk;
   try{return await callback();}
   finally{
     // Do not undo a real stat change made during an awaited animation.
     if(unit.atk===reducedAtk)unit.atk=originalAtk;
     if(S.party?.[slot]===unit&&typeof update==='function')update();
   }
 }
 function expireAfterTurn(round=S.round){
   sync();
   if(S.mode!=='archive'||S.over||round!==S.round)return Object.freeze([]);
   const removed=[];
   for(let slot=0;slot<6;slot++){
     const unit=S.party?.[slot];
     if(!injured(slot)){if(unit)ages.delete(unit);continue;}
     const age=track(slot);
     if(!age||age.lastRound===round)continue;
     age.lastRound=round;
     if(round>=age.firstRound+2){
       if(ailments.removeCode(slot,4))removed.push(slot);
       if(unit)ages.delete(unit);
     }
   }
   return Object.freeze(removed);
 }
 window.performUnit=async function(p,token){
   const slot=p?.id;
   if(!Number.isInteger(slot)||S.party?.[slot]!==p)
     return previousPerform.call(this,p,token);
   return withInjuryAttack(slot,()=>previousPerform.call(this,p,token));
 };
 window.enemyPhase=async function(...args){
   const activeBattle=S,round=S.round;
   const value=await previousEnemy.apply(this,args);
   if(S===activeBattle&&S.round===round&&!S.over)expireAfterTurn(round);
   return value;
 };
 function snapshot(){
   sync();
   return Object.freeze({source,mode:S.mode,round:S.round,
     injuredSlots:Object.freeze(Array.from({length:6},(_,i)=>i).filter(injured)),
     performHooked:window.performUnit!==previousPerform,
     enemyHooked:window.enemyPhase!==previousEnemy});
 }
 window.BFGlobalInjuryAttackV6200=Object.freeze({
   source,snapshot,injured,effectiveAttack,withInjuryAttack,expireAfterTurn
 });
})();
