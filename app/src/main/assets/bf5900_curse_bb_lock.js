/* BF_GLOBAL_CURSE_BB_LOCK_V5900 */
(() => {
 'use strict';
 // Global-era status reference: Curse prevents BB activation and BB charging.
 // Native infliction rates/timing/animations remain out of scope.
 const ailments=window.BFGlobalOriginalAilmentStateV5700;
 const poison=window.BFGlobalPoisonTurnV5800;
 if(window.BFGlobalCurseBBLockV5900||!ailments||!poison||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof performUnit!=='function'||typeof enemyPhase!=='function')return;
 const originalPerform=window.performUnit;
 const originalEnemy=window.enemyPhase;
 const burstButton=document.getElementById('burst');
 if(!burstButton)return;
 let battle=S;
 const curseAges=new WeakMap();
 function sync(){if(S!==battle)battle=S;}
 function cursed(slot){
  sync();
  return S.mode==='archive'&&!S.over&&
    Number.isInteger(slot)&&slot>=0&&slot<6&&
    ailments.codesFor(slot).includes(5);
 }
 function track(slot){
  const p=S.party?.[slot];
  if(!p||!cursed(slot))return null;
  const generation=ailments.tokenFor(slot,5);
  if(generation===null)return null;
  let rec=curseAges.get(p);
  if(!rec||rec.generation!==generation){
    rec={generation,firstRound:S.round,lastRound:null};curseAges.set(p,rec);
  }
  return rec;
 }
 function blockBurst(slot){
  if(!cursed(slot))return false;
  const p=S.party[slot];
  track(slot);
  if(p?.action?.kind!=='burst')return false;
  p.action={kind:'attack',target:p.action.target};
  return true;
 }
 function preventGaugeGain(slot,before){
  if(!cursed(slot))return false;
  const p=S.party[slot];
  if(!p||!Number.isFinite(before)||!Number.isFinite(p.bb)||p.bb<=before)return false;
  p.bb=before;
  return true;
 }
 function expireAfterTurn(round=S.round){
  sync();
  if(S.mode!=='archive'||S.over||round!==S.round)return Object.freeze([]);
  const expired=[];
  for(let slot=0;slot<6;slot++){
   if(!cursed(slot))continue;
   const rec=track(slot);
   if(!rec||rec.lastRound===round)continue;
   rec.lastRound=round;
   if(round>=rec.firstRound+2){
     if(ailments.removeCode(slot,5))expired.push(slot);
     curseAges.delete(S.party[slot]);
   }
  }
  return Object.freeze(expired);
 }
 window.performUnit=async function(p,token){
  const boundBattle=S,priorBB=p?.bb,slot=p?.id;
  if(cursed(slot))blockBurst(slot);
  const value=await originalPerform.call(this,p,token);
  if(S===boundBattle&&cursed(slot)){
   if(preventGaugeGain(slot,priorBB)&&typeof update==='function')update();
  }
  return value;
 };
 window.enemyPhase=async function(...args){
  const boundBattle=S,round=S.round;
  const value=await originalEnemy.apply(this,args);
  if(S===boundBattle&&S.round===round&&!S.over)expireAfterTurn(round);
  return value;
 };
 // Native click handler is registered first; capture blocks a cursed BB.
 burstButton.addEventListener('click',event=>{
  if(!cursed(S.selected))return;
  event.preventDefault();event.stopImmediatePropagation();
  if(typeof msg==='function')msg('CURSE: Brave Burst is unavailable until cured or expired.');
  if(typeof update==='function')update();
 },true);
 function snapshot(){
  sync();
  return Object.freeze({mode:S.mode,round:S.round,cursedSlots:Object.freeze(
   Array.from({length:6},(_,i)=>i).filter(cursed)),
   performHooked:window.performUnit!==originalPerform,
   enemyHooked:window.enemyPhase!==originalEnemy});
 }
 window.BFGlobalCurseBBLockV5900=Object.freeze({
  snapshot,cursed,blockBurst,preventGaugeGain,expireAfterTurn
 });
})();