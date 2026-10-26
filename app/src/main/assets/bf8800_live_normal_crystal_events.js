/* BF_GLOBAL_LIVE_NORMAL_CRYSTAL_EVENTS_V8800 */
(() => {
 'use strict';
 // Live normal-attack drops from verified 2022 source checks and hit frames.
 // The recovered rates support production rolls, NOT native recipient pickup.
 const source=window.BFGlobalAllNormalCrystalChecksV8400;
 const core=window.BFGlobalOriginalCrystalDropCoreV8100;
 if(window.BFGlobalLiveNormalCrystalEventsV8800||!source||!core||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof window.performUnit!=='function')return;
 const host=document.getElementById('bf2000-run')||document.getElementById('log')?.parentElement;
 if(!host)return;
 const originalPerform=window.performUnit;
 const css=document.createElement('style');css.id='bf8800-style';
 css.textContent='#bf8800-crystals{margin:9px 4px;padding:9px;border:1px solid #a5bad1;border-radius:6px;background:#1e3248;color:#f5edda;font:12px/1.5 system-ui,sans-serif}'+
 '#bf8800-crystals summary{cursor:pointer;min-height:32px;font-weight:800}'+
 '#bf8800-crystals p{margin:6px 0}#bf8800-crystals ol{margin:5px 0;padding-left:23px}'+
 '#bf8800-crystals li{margin:5px 0}#bf8800-note{color:#cfdfeb;font-size:11px}';
 document.head.append(css);
 const panel=document.createElement('details');panel.id='bf8800-crystals';
 panel.setAttribute('aria-label','Live original-source normal attack crystal production');
 const heading=document.createElement('summary');heading.textContent='ORIGINAL NORMAL ATTACK BC / HC EVENTS';
 const totals=document.createElement('p');totals.id='bf8800-totals';
 const list=document.createElement('ol');list.id='bf8800-events';
 const note=document.createElement('small');note.id='bf8800-note';
 note.textContent='Actual DEMO normal attacks, source-backed 2022 normal-hit and drop-check counts: BC base 35% per check; HC base 10% per hit. Reference production only: NO verified native pickup, BB charging, HC healing, resistance, overkill detection or saving.';
 panel.append(heading,totals,list,note);host.append(panel);
 let battle=S,events=[],bc=0,hc=0;
 const freeze=Object.freeze;
 function sync(){
   if(battle!==S){battle=S;events=[];bc=0;hc=0;render();}
 }
 function snapshot(){
   sync();
   return freeze({mode:S.mode,round:S.round,wave:S.wave+1,
     observed:events.length,battleCrystals:bc,heartCrystals:hc,
     recent:freeze(events.slice(-8))});
 }
 function render(){
   totals.textContent=events.length?
     events.length+' successful source-eligible normal attacks · '+bc+' BC rolls · '+hc+' HC rolls (uncollected)':
     'No eligible normal attack events observed in this battle.';
   list.replaceChildren();
   for(const e of events.slice(-5).reverse()){
     const li=document.createElement('li');
     li.textContent='Wave '+e.wave+' · '+e.attacker+' → '+e.target+
       ' · '+e.battleCrystals+' BC / '+e.heartCrystals+' HC'+
       ' · '+e.normalHits+' sourced hits × '+e.checksPerHit+' BC checks/hit';
     list.append(li);
   }
 }
 function record(unit,target,beforeHp,wave,unitId){
   const profile=source.lookup(unitId);
   if(!profile||!Number.isFinite(beforeHp)||beforeHp<=0||
      !Number.isFinite(target.hp)||target.hp>=beforeHp)return false;
   // No observable native per-hit overkill flags: explicitly never infer x2.
   const result=source.rollNormal(unitId,{overkill:false,random:Math.random});
   if(!result||result.totalDropChecks!==profile.totalDropChecks||
      result.normalHits!==profile.normalHits||
      !Number.isInteger(result.battleCrystals)||!Number.isInteger(result.heartCrystals)||
      result.battleCrystals<0||result.battleCrystals>profile.totalDropChecks||
      result.heartCrystals<0||result.heartCrystals>profile.normalHits)return false;
   const item=freeze({unitId,attacker:String(unit.name||'Unit '+unitId),
     target:String(target.name||'Enemy'),wave,normalHits:profile.normalHits,
     checksPerHit:profile.checksPerHit,totalDropChecks:profile.totalDropChecks,
     battleCrystals:result.battleCrystals,heartCrystals:result.heartCrystals,
     overkill:false,referenceOnly:true});
   events.push(item);if(events.length>64)events.shift();
   bc+=item.battleCrystals;hc+=item.heartCrystals;render();return true;
 }
 window.performUnit=async function(unit,token){
   sync();
   const current=S,action=unit?.action,slot=unit?.id;
   const eligible=current.mode==='archive'&&!current.over&&
     Number.isInteger(slot)&&slot>=0&&slot<6&&
     current.party?.[slot]===unit&&unit.active&&unit.hp>0&&
     action?.kind==='attack'&&Number.isInteger(unit.unitId)&&
     Number.isInteger(action.target)&&
     !window.BFGlobalOriginalAilmentStateV5700?.codesFor(slot)?.includes(6);
   const enemy=eligible?current.enemies?.find(e=>e&&e.slot===action.target&&e.hp>0):null;
   const beforeHp=enemy?.hp,unitId=unit?.unitId,wave=current.wave+1;
   // Preserve the native command execution and error propagation exactly.
   const response=await originalPerform.call(this,unit,token);
   if(enemy&&S===current&&current.mode==='archive'&&
      current.party?.[slot]===unit){
     record(unit,enemy,beforeHp,wave,unitId);
   }
   return response;
 };
 document.getElementById('reset')?.addEventListener('click',()=>{sync();render()});
 document.getElementById('mode')?.addEventListener('change',()=>{sync();render()});
 render();
 window.BFGlobalLiveNormalCrystalEventsV8800=freeze({
   source:freeze({archive:'2022 F_UNIT_MST_1/2_Ver1084.json',
     allowedProfiles:2258,normalBcBasePercent:35,normalHcBasePercent:10,
     doesNotGrantPickups:true,doesNotChangeSave:true,
     scope:'Real DEMO attack events; source drop rolls; no native collection or overkill'}),
   snapshot
 });
})();
