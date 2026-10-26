/* BF_GLOBAL_SICKNESS_RECOVERY_V6500 */
(() => {
 'use strict';
 // BF Global community documentation: Sickness (status code 3) subtracts
 // 50% REC for 3 player turns. The native healing/heart-crystal formula and
 // rounding are not recovered; this does not alter flat DEMO item heals.
 const ailments=window.BFGlobalOriginalAilmentStateV5700;
 if(window.BFGlobalSicknessRecoveryV6500||!ailments||
    !window.BFGlobalStatusRemedyCommandV6400||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof performUnit!=='function'||typeof enemyPhase!=='function')return;
 const previousPerform=window.performUnit;
 const previousEnemy=window.enemyPhase;
 const source=Object.freeze({
   statusCode:3,name:'Sickness',stat:'REC',penaltyPercent:50,
   observedPlayerTurns:3,cureItemId:20210,
   statusEvidence:'3-mst-translated/F_ITEM_MST_Ver1027.json',
   reference:'https://bravefrontierglobal.fandom.com/wiki/Status_Infliction',
   interpretation:'Community-documented REC penalty; demo rounding, no native healing formula'
 });
 let battle=S;
 const ages=new WeakMap();
 function sync(){if(battle!==S)battle=S;}
 function sick(slot){
   sync();
   const p=S.party?.[slot];
   return S.mode==='archive'&&!S.over&&Number.isInteger(slot)&&
     slot>=0&&slot<6&&!!p&&p.active&&p.hp>0&&
     ailments.codesFor(slot).includes(3);
 }
 function track(slot){
   const p=S.party?.[slot];if(!sick(slot)||!p)return null;
   const generation=ailments.tokenFor(slot,3);if(generation===null)return null;
   let age=ages.get(p);
   if(!age||age.generation!==generation){
     age={generation,firstRound:S.round,lastRound:null};
     ages.set(p,age);
   }
   return age;
 }
 function effectiveRecovery(slot){
   const rec=S.party?.[slot]?.rec;
   if(!Number.isFinite(rec))return null;
   return sick(slot)?Math.max(0,Math.round(rec*.5)):rec;
 }
 async function withSicknessRecovery(callback){
   if(typeof callback!=='function')throw new TypeError('callback required');
   sync();
   const current=S,changes=[];
   if(S.mode!=='archive'||S.over)return callback();
   for(let slot=0;slot<6;slot++){
     if(!sick(slot))continue;
     const unit=S.party[slot];if(!Number.isFinite(unit.rec))continue;
     track(slot);
     const before=unit.rec,now=Math.max(0,Math.round(before*.5));
     unit.rec=now;changes.push({unit,before,now});
   }
   try{return await callback();}
   finally{
     // If another effect modified REC in the interim, preserve that change.
     for(const {unit,before,now} of changes)
       if(unit.rec===now)unit.rec=before;
     if(S===current&&changes.length&&typeof update==='function')update();
   }
 }
 function expireAfterTurn(round=S.round){
   sync();
   if(S.mode!=='archive'||S.over||round!==S.round)return Object.freeze([]);
   const cleared=[];
   for(let slot=0;slot<6;slot++){
     const p=S.party?.[slot];
     if(!sick(slot)){if(p)ages.delete(p);continue;}
     const age=track(slot);
     if(!age||age.lastRound===round)continue;
     age.lastRound=round;
     if(round>=age.firstRound+2){
       if(ailments.removeCode(slot,3))cleared.push(slot);
       if(p)ages.delete(p);
     }
   }
   return Object.freeze(cleared);
 }
 window.performUnit=async function(p,token){
   return withSicknessRecovery(()=>previousPerform.call(this,p,token));
 };
 window.enemyPhase=async function(...args){
   const current=S,round=S.round;
   const result=await previousEnemy.apply(this,args);
   if(S===current&&S.round===round&&!S.over)expireAfterTurn(round);
   return result;
 };
 function snapshot(){
   sync();
   return Object.freeze({source,mode:S.mode,round:S.round,
     sickSlots:Object.freeze(Array.from({length:6},(_,i)=>i).filter(sick)),
     performHooked:window.performUnit!==previousPerform,
     enemyHooked:window.enemyPhase!==previousEnemy});
 }
 window.BFGlobalSicknessRecoveryV6500=Object.freeze({
   source,snapshot,sick,effectiveRecovery,withSicknessRecovery,expireAfterTurn
 });
})();
