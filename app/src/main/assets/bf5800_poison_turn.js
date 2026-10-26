/* BF_GLOBAL_POISON_TURN_V5800 */
(() => {
 'use strict';
 // Status infliction remains unavailable until actual enemy skill hooks exist.
 // Global-era community mechanics: Poison = 10% max HP per end turn,
 // player status duration 3 turns; integer rounding here remains DEMO.
 const ail=window.BFGlobalOriginalAilmentStateV5700;
 if(window.BFGlobalPoisonTurnV5800||!ail||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof enemyPhase!=='function'||typeof update!=='function')return;
 const original=window.enemyPhase;
 let battle=S;
 const tracked=new WeakMap();
 function sync(){if(S!==battle){battle=S;}}
 function processPoisonTurn(round=S.round){
  sync();
  if(S.mode!=='archive'||S.over||!Number.isInteger(round)||round!==S.round)return Object.freeze([]);
  const events=[];
  for(let slot=0;slot<6;slot++){
   const p=S.party?.[slot];
   if(!p||!p.active||p.hp<=0||!ail.codesFor(slot).includes(1))continue;
   const generation=ail.tokenFor(slot,1);
   if(generation===null)continue;
   let status=tracked.get(p);
   if(!status||status.generation!==generation){
     // A new status applied after a poison tick in this same round must not
     // take a second tick. Its fresh three-tick lifetime starts next round.
     const alreadyTicked=status?.lastTick===round;
     status={generation,firstRound:alreadyTicked?round+1:round,
       lastTick:alreadyTicked?round:null};
     tracked.set(p,status);
   }
   if(status.lastTick===round)continue; // never poison twice this round
   if(round>=status.firstRound+3){
     ail.removeCode(slot,1);continue;
   }
   status.lastTick=round;
   // 10% maximum HP is sourced from the Global status mechanics reference.
   // The original engine's fractional rounding convention is not decoded.
   const damage=Math.max(1,Math.floor(p.maxHp/10));
   const actual=Math.min(p.hp,damage);
   p.hp=Math.max(0,p.hp-damage);
   events.push(Object.freeze({slot,round,damage:actual,ko:p.hp===0}));
   if(typeof msg==='function')
     msg('POISON · '+p.name+' loses '+actual+' HP (10% max HP; DEMO rounding).');
   if(round>=status.firstRound+2&&p.hp>0){
     ail.removeCode(slot,1);
   }
  }
  if(events.length)update();
  return Object.freeze(events);
 }
 window.enemyPhase=async function(...args){
  const activeBattle=S,round=S.round;
  const value=await original.apply(this,args);
  // The native phase returns before advance to the following round.
  // Do not apply stale ticks when reset/quest switch occurs mid-animation.
  if(S===activeBattle&&S.round===round&&!S.over)
    processPoisonTurn(round);
  return value;
 };
 function snapshot(){
  sync();
  return Object.freeze({mode:S.mode,round:S.round,hooked:window.enemyPhase!==original,
   trackedPoisonSlots:Object.freeze(ail.snapshot().units.filter(u=>u.codes.includes(1)).map(u=>u.slot))});
 }
 window.BFGlobalPoisonTurnV5800=Object.freeze({snapshot,processPoisonTurn});
})();