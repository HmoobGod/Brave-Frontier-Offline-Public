/* BF_GLOBAL_WEAKNESS_DEFENSE_V6100 */
(() => {
 'use strict';
 // Global-era community reference: Weakness subtracts 50% DEF for three
 // player turns. Original client rounding and simultaneous buffs unverified.
 // No enemy infliction rolls are added here.
 const ailments=window.BFGlobalOriginalAilmentStateV5700;
 if(window.BFGlobalWeaknessDefenseV6100||!ailments||
    !window.BFGlobalParalysisActionLockV6000||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof enemyPhase!=='function')return;
 const previousEnemy=window.enemyPhase;
 const source=Object.freeze({
   statusCode:2,name:'Weakness',stat:'DEF',penaltyPercent:50,
   observedPlayerTurns:3,cureItemId:20210,
   statusEvidence:'3-mst-translated/F_ITEM_MST_Ver1027.json',
   reference:'https://bravefrontierglobal.fandom.com/wiki/Status_Infliction',
   interpretation:'Global source community-documented subtractive DEF penalty; item percentages original, rounding DEMO'
 });
 let battle=S;
 const ages=new WeakMap();
 function sync(){if(S!==battle)battle=S;}
 function weakened(slot){
   sync();
   return S.mode==='archive'&&!S.over&&
     Number.isInteger(slot)&&slot>=0&&slot<6&&
     ailments.codesFor(slot).includes(2);
 }
 function track(slot){
   if(!weakened(slot))return null;
   const unit=S.party?.[slot];
   if(!unit||!unit.active||unit.hp<=0)return null;
   const token=ailments.tokenFor(slot,2);
   if(token===null)return null;
   let record=ages.get(unit);
   if(!record||record.token!==token){
     record={token,firstRound:S.round,lastRound:null};
     ages.set(unit,record);
   }
   return record;
 }
 // DEF item modules already apply source-verified +30%, +50%, +100%
 // to the living stat. The documented Weakness -50% modifier subtracts
 // from those bonuses against ORIGINAL base DEF; it must not halve an
 // already boosted DEF value. Read only their existing temporary records.
 // When an unknown module owns the DEF value, retain the old safe fallback.
 function documentedDefBuff(slot){
   const candidates=[
     [window.BFGlobalSourceDefItemV4900,30],
     [window.BFGlobalSourceDoubleDefV5200,100],
     [window.BFGlobalSourcePartyDefV5300,50]
   ];
   for(const [api,pct] of candidates){
     if(!api||typeof api.snapshot!=='function')continue;
     const entry=api.snapshot().activeBuffs?.find(b=>b.slot===slot);
     if(entry&&Number.isFinite(entry.baseDef)&&entry.baseDef>=0)
       return {baseDef:entry.baseDef,pct};
   }
   return null;
 }
 function effectiveDefense(slot){
   const unit=S.party?.[slot];
   if(!unit||!Number.isFinite(unit.def))return null;
   if(!weakened(slot))return unit.def;
   const documented=documentedDefBuff(slot);
   // Fetch DEF after snapshot() sync so an expired buff never supplies
   // a stale double/party DEF value from an earlier simulated round.
   const current=S.party?.[slot]?.def;
   return !Number.isFinite(current)?null:Math.max(0,Math.round(
     documented?documented.baseDef*(.5+documented.pct/100):current*.5
   ));
 }
 async function withWeaknessDefense(callback){
   if(typeof callback!=='function')throw new TypeError('callback required');
   sync();
   const instance=S,changes=[];
   if(S.mode!=='archive'||S.over)return callback();
   for(let slot=0;slot<6;slot++){
     if(!weakened(slot))continue;
     const unit=S.party[slot];
     if(!unit||!unit.active||unit.hp<=0||!Number.isFinite(unit.def))continue;
     track(slot);
     const weakenedDef=effectiveDefense(slot);
     const originalDef=unit.def;
     if(!Number.isFinite(weakenedDef))continue;
     unit.def=weakenedDef;
     changes.push({slot,unit,originalDef,weakenedDef});
   }
   try{return await callback();}
   finally{
     // Restore only the live stats we temporarily changed. Do not overwrite
     // another module's stat mutation during the awaited enemy animation.
     for(const change of changes){
       if(change.unit.def===change.weakenedDef)
         change.unit.def=change.originalDef;
     }
     if(S===instance&&changes.length&&typeof update==='function')update();
   }
 }
 function expireAfterTurn(round=S.round){
   sync();
   if(S.mode!=='archive'||S.over||round!==S.round)return Object.freeze([]);
   const cleared=[];
   for(let slot=0;slot<6;slot++){
     const unit=S.party?.[slot];
     if(!weakened(slot)){if(unit)ages.delete(unit);continue;}
     const age=track(slot);
     if(!age||age.lastRound===round)continue;
     age.lastRound=round;
     if(round>=age.firstRound+2){
       if(ailments.removeCode(slot,2))cleared.push(slot);
       if(unit)ages.delete(unit);
     }
   }
   return Object.freeze(cleared);
 }
 window.enemyPhase=async function(...args){
   const activeBattle=S,round=S.round;
   const result=await withWeaknessDefense(()=>
     previousEnemy.apply(this,args));
   if(S===activeBattle&&S.round===round&&!S.over)
     expireAfterTurn(round);
   return result;
 };
 function snapshot(){
   sync();
   return Object.freeze({source,mode:S.mode,round:S.round,
     weakenedSlots:Object.freeze(Array.from({length:6},(_,i)=>i).filter(weakened)),
     enemyHooked:window.enemyPhase!==previousEnemy});
 }
 window.BFGlobalWeaknessDefenseV6100=Object.freeze({
   source,snapshot,weakened,effectiveDefense,withWeaknessDefense,expireAfterTurn
 });
})();
