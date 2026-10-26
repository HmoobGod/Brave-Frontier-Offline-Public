/* BF_GLOBAL_PARALYSIS_ACTION_LOCK_V6000 */
(() => {
 'use strict';
 // Global-era community reference: Paralysis prevents acting, player duration 3 turns.
 // No original enemy infliction proc rates or animations are invented.
 const ailments=window.BFGlobalOriginalAilmentStateV5700;
 if(window.BFGlobalParalysisActionLockV6000||!ailments||
    !window.BFGlobalCurseBBLockV5900||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof performUnit!=='function'||typeof enemyPhase!=='function')return;
 const previousUnit=window.performUnit;
 const previousEnemy=window.enemyPhase;
 let battle=S;
 const ages=new WeakMap();
 function sync(){if(S!==battle)battle=S;}
 function paralyzed(slot){
  sync();
  return S.mode==='archive'&&!S.over&&Number.isInteger(slot)&&
    slot>=0&&slot<6&&ailments.codesFor(slot).includes(6);
 }
 function track(slot){
  if(!paralyzed(slot))return null;
  const p=S.party?.[slot];if(!p)return null;
  const generation=ailments.tokenFor(slot,6);
  if(generation===null)return null;
  let age=ages.get(p);
  if(!age||age.generation!==generation){
    age={generation,firstRound:S.round,lastRound:null};ages.set(p,age);
  }
  return age;
 }
 function canExecute(slot){return !paralyzed(slot);}
 function expireAfterTurn(round=S.round){
  sync();
  if(S.mode!=='archive'||S.over||round!==S.round)return Object.freeze([]);
  const cleared=[];
  for(let slot=0;slot<6;slot++){
   if(!paralyzed(slot))continue;
   const age=track(slot);
   if(!age||age.lastRound===round)continue;
   age.lastRound=round;
   if(round>=age.firstRound+2){
     if(ailments.removeCode(slot,6))cleared.push(slot);
     ages.delete(S.party[slot]);
   }
  }
  return Object.freeze(cleared);
 }
 window.performUnit=async function(p,token){
  const slot=p?.id;
  if(paralyzed(slot)){
   track(slot);
   if(typeof msg==='function')msg('PARALYSIS: '+p.name+' cannot act this turn.');
   return;
  }
  return previousUnit.call(this,p,token);
 };
 window.enemyPhase=async function(...args){
  const activeBattle=S,round=S.round;
  const result=await previousEnemy.apply(this,args);
  if(S===activeBattle&&S.round===round&&!S.over)expireAfterTurn(round);
  return result;
 };
 function snapshot(){
  sync();
  return Object.freeze({round:S.round,mode:S.mode,
   paralyzedSlots:Object.freeze(Array.from({length:6},(_,i)=>i).filter(paralyzed)),
   actionHooked:window.performUnit!==previousUnit,
   enemyHooked:window.enemyPhase!==previousEnemy});
 }
 window.BFGlobalParalysisActionLockV6000=Object.freeze({
  snapshot,paralyzed,canExecute,expireAfterTurn
 });
})();