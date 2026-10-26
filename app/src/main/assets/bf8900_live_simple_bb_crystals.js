/* BF_GLOBAL_LIVE_SIMPLE_BB_CRYSTAL_EVENTS_V8900 */
(() => {
 'use strict';
 // Strict source-known single-group original 2022 offensive BB profiles ONLY.
 // No native crystal recipient, pickup, or BB/HP changes are inferred.
 const source=window.BFGlobalAllBBDropChecksV8500;
 const core=window.BFGlobalOriginalCrystalDropCoreV8100;
 if(window.BFGlobalLiveSimpleBBCrystalsV8900||!source||!core||
    !window.BFGlobalLiveNormalCrystalEventsV8800||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof window.performUnit!=='function')return;
 const host=document.getElementById('bf8800-crystals')?.parentElement;
 if(!host)return;
 const prior=window.performUnit,freeze=Object.freeze;
 const box=document.createElement('details');box.id='bf8900-bb-crystals';
 box.style.cssText='margin:9px 4px;padding:9px;border:1px solid #9e9bc7;border-radius:6px;background:#202d49;color:#efeafa;font:12px/1.5 system-ui,sans-serif';
 const title=document.createElement('summary');
 title.textContent='ORIGINAL SIMPLE BB BC / HC EVENTS';
 title.style.cssText='cursor:pointer;min-height:32px;font-weight:800';
 const counts=document.createElement('p');counts.id='bf8900-counts';
 const entries=document.createElement('ol');entries.id='bf8900-events';
 const notice=document.createElement('small');notice.id='bf8900-note';
 notice.textContent='2022 verified simple offensive BB source groups only, per damaged target. Complex, multi-group or support BBs excluded. Reference production only: no verified pickup, BB/HP effect, enemy resistance or overkill.';
 box.append(title,counts,entries,notice);host.append(box);
 let battle=S,events=[],bc=0,hc=0;
 function render(){
   counts.textContent=events.length?events.length+' source-backed target records · '+bc+' BC / '+hc+' HC (uncollected)':'No source-supported offensive BB events observed.';
   entries.replaceChildren();
   for(const e of events.slice(-5).reverse()){
     const li=document.createElement('li');
     li.textContent='Wave '+e.wave+' · '+e.attacker+' BB → '+e.target+
       ' · '+e.battleCrystals+' BC / '+e.heartCrystals+' HC · '+e.simpleDamageEvents+' hits';
     entries.append(li);
   }
 }
 function sync(){if(battle!==S){battle=S;events=[];bc=0;hc=0;render();}}
 function snapshot(){sync();return freeze({mode:S.mode,round:S.round,
   observed:events.length,battleCrystals:bc,heartCrystals:hc,
   recent:freeze(events.slice(-8))});}
 window.performUnit=async function(unit,token){
   sync();const instance=S,slot=unit?.id,action=unit?.action;
   const eligible=instance.mode==='archive'&&!instance.over&&
     Number.isInteger(slot)&&slot>=0&&slot<6&&instance.party?.[slot]===unit&&
     unit.active&&unit.hp>0&&Number.isInteger(unit.unitId)&&
     action?.kind==='burst'&&Number.isFinite(unit.bb)&&unit.bb>=100&&
     !window.BFGlobalOriginalAilmentStateV5700?.codesFor(slot)?.some(c=>c===5||c===6);
   const profile=eligible?source.lookup(unit.unitId):null;
   const targets=profile?.checksPerTarget?instance.enemies.filter(e=>
     e&&Number.isInteger(e.slot)&&Number.isFinite(e.hp)&&e.hp>0)
     .map(e=>({enemy:e,preHp:e.hp})):[];
   const priorBB=unit?.bb,unitId=unit?.unitId,wave=instance.wave+1;
   const response=await prior.call(this,unit,token);
   if(instance!==S||instance.party?.[slot]!==unit||instance.mode!=='archive'||
      !profile?.simpleDamageEvents||!Number.isFinite(unit.bb)||unit.bb>=priorBB)
     return response;
   for(const {enemy,preHp} of targets){
     if(!Number.isFinite(enemy.hp)||enemy.hp>=preHp)continue;
     const rolled=source.rollPerTarget(unitId,{overkill:false,random:Math.random});
     if(!rolled||rolled.checksPerTarget!==profile.checksPerTarget||
        !Number.isInteger(rolled.battleCrystals)||rolled.battleCrystals<0||
        rolled.battleCrystals>profile.checksPerTarget)continue;
     let heartCrystals=0,valid=true;
     for(let i=0;i<profile.simpleDamageEvents;i++){
       const value=core.chance(10,Math.random);
       if(value===null){valid=false;break;}
       if(value)heartCrystals++;
     }
     if(!valid)continue;
     const item=freeze({unitId,skillId:profile.skillId,wave,
       attacker:String(unit.name||'Unit '+unitId),target:String(enemy.name||'Enemy'),
       simpleDamageEvents:profile.simpleDamageEvents,
       checksPerTarget:profile.checksPerTarget,
       battleCrystals:rolled.battleCrystals,heartCrystals,overkill:false,referenceOnly:true});
     events.push(item);if(events.length>64)events.shift();
     bc+=item.battleCrystals;hc+=item.heartCrystals;
   }
   render();return response;
 };
 document.getElementById('reset')?.addEventListener('click',()=>{sync();render()});
 document.getElementById('mode')?.addEventListener('change',()=>{sync();render()});
 render();
 window.BFGlobalLiveSimpleBBCrystalsV8900=freeze({
   source:freeze({strictOffensiveProfiles:213,bcBasePercent:35,hcBasePercent:10,
     doesNotGrantPickups:true,doesNotChangeSave:true}),snapshot
 });
})();
