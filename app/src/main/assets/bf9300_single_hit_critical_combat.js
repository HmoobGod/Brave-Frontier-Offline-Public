/* BF_GLOBAL_SINGLE_HIT_CRITICAL_COMBAT_V9300 */
(() => {
 'use strict';
 // Source-authenticated SINGLE HIT normal attacks only. The 2022 Global
 // UNIT master gives the normal hit count; contemporary mechanics reference
 // gives the 10% base critical chance and 150% critical damage multiplier.
 // Unknown per-hit sequences, enemy resistance, buffs and BBs are excluded.
 const source=window.BFGlobalAllNormalCrystalChecksV8400;
 const oldPerform=window.performUnit,oldDamage=window.prototypeDamage;
 if(window.BFGlobalSingleHitCriticalV9300||!source||
    typeof oldPerform!=='function'||typeof oldDamage!=='function'||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined')return;
 const freeze=Object.freeze;
 const host=document.getElementById('bf2000-run')||
   document.getElementById('bf8800-crystals')?.parentElement||
   document.getElementById('log')?.parentElement;
 if(!host)return;
 // The native combat history is collapsed; mirror verified criticals in the battle header.
 const battleHeading=document.getElementById('phase')?.parentElement;
 const banner=document.createElement('div');
 banner.id='bf9400-critical-banner';
 banner.hidden=true;
 banner.setAttribute('role','status');
 banner.setAttribute('aria-live','polite');
 banner.style.cssText='margin:5px 0;padding:4px 8px;border:1px solid #e9bd6e;'+
   'border-radius:5px;background:#533c1c;color:#ffe7a4;'+
   'font:800 13px/1.4 system-ui,sans-serif;pointer-events:none';
 if(battleHeading)battleHeading.append(banner);
 let battle=S,ctx=null,events=[],crits=0,lastBannerTurn=null,lastBannerWave=null;
 function eligible(unit){
   if(S.mode!=='archive'||S.over||S.busy===false&&unit?.action?.kind!=='attack'||
      !Number.isSafeInteger(unit?.id)||unit.id<0||unit.id>=6||
      S.party?.[unit.id]!==unit||!unit.active||unit.hp<=0||
      !Number.isSafeInteger(unit.unitId)||unit.action?.kind!=='attack'||
      !Number.isSafeInteger(unit.action.target))return null;
   const p=source.lookup(unit.unitId);
   const target=S.enemies?.find(e=>e?.slot===unit.action.target&&e.hp>0);
   if(!p||p.normalHits!==1||!target)return null;
   return {unit,slot:unit.id,unitId:unit.unitId,target,
     hp:target.hp,wave:S.wave+1,turn:S.round,battle:S,attempted:false,critical:false};
 }
 function sync(){if(S!==battle){battle=S;ctx=null;events=[];crits=0;
   lastBannerTurn=null;lastBannerWave=null;banner.hidden=true;render();}}
 function roll(random=Math.random){
   if(typeof random!=='function')return null;
   const n=random();
   return Number.isFinite(n)&&n>=0&&n<1?n<0.1:null;
 }
 function criticalDamage(damage,critical){
   return !critical||!Number.isFinite(damage)||damage<=0?
     damage:Math.max(1,Math.floor(damage*1.5));
 }
 window.prototypeDamage=function(...args){
   const damage=oldDamage.apply(this,args);
   const current=ctx;
   if(!current||current.attempted||S!==current.battle||
      S.party?.[current.slot]!==current.unit||S.mode!=='archive'||
      current.unit.action?.kind!=='attack'||current.target.hp<=0)return damage;
   current.attempted=true;
   const critical=roll();
   current.critical=critical===true;
   current.baseDamage=damage;
   const outcome=criticalDamage(damage,current.critical);
   current.resultDamage=outcome;
   return outcome;
 };
 window.performUnit=async function(unit,token){
   sync();
   // The existing demo resolves players' queued attacks through performUnit.
   // Do not use this context for unsupported multi-hit attacks/BB/heals.
   const prior=ctx,local=eligible(unit);
   // The last critical is visible through the current round only.
   // Preserve it for later party actions in the SAME round, then clear it
   // on the first action of the next round or wave (without altering combat).
   if(lastBannerTurn!==null&&
      (S.round!==lastBannerTurn||S.wave!==lastBannerWave)){
     banner.hidden=true;lastBannerTurn=null;lastBannerWave=null;
   }
   if(local)ctx=local;
   try{
     return await oldPerform.call(this,unit,token);
   }finally{
     if(local&&S===local.battle&&local.unit===S.party?.[local.slot]&&
        Number.isFinite(local.target.hp)&&local.target.hp<local.hp&&
        local.attempted){
       const item=freeze({unitId:local.unitId,slot:local.slot,wave:local.wave,
         round:local.turn,critical:local.critical,
         baseDamage:local.baseDamage,resultDamage:local.resultDamage,
         observedHpLoss:local.hp-local.target.hp,referenceOnly:false,
         sourceSingleHit:true});
       events.push(item);if(events.length>32)events.shift();
       if(item.critical){
         crits++;
         if(battleHeading){
           banner.textContent='CRITICAL HIT! · unit #'+item.unitId+
             ' · '+item.observedHpLoss+' HP damage (DEMO)';
           banner.hidden=false;
           lastBannerTurn=local.turn;
           lastBannerWave=S.wave;
         }
         // Also retain confirmed criticals in the combat history.
         // Source applies the original 10%/150% rule in v93; this is
         // feedback only, never another roll or additional damage.
         const log=document.getElementById('log');
         if(log){
           const notice=document.createElement('div');
           notice.className='bf9400-critical-notice';
           notice.textContent='CRITICAL HIT! · unit #'+item.unitId+
             ' · '+item.observedHpLoss+' HP damage (DEMO)';
           notice.style.cssText='color:#ffe59c;font-weight:800;margin:4px 0';
           log.append(notice);
         }
       }
     }
     ctx=prior;
     render();
   }
 };
 const panel=document.createElement('details');panel.id='bf9300-critical';
 panel.style.cssText='margin:8px 4px;padding:8px;border:1px solid #bea778;border-radius:6px;background:#303443;color:#fff1d5;font:12px/1.5 system-ui,sans-serif';
 const heading=document.createElement('summary');
 heading.textContent='ORIGINAL SINGLE-HIT CRITICALS';
 heading.style.cssText='cursor:pointer;min-height:34px;font-weight:800';
 const line=document.createElement('p');line.id='bf9300-critical-counts';
 const rows=document.createElement('ol');rows.id='bf9300-critical-events';
 const note=document.createElement('small');
 note.textContent='10% base critical chance; 150% damage on a critical. Gameplay-active only for sourced one-hit normal attacks. Multi-hit attacks, Brave Bursts, synthetic enemy attacks, critical buffs/resistances and full native damage remain unimplemented.';
 panel.append(heading,line,rows,note);host.append(panel);
 function snapshot(){
   sync();
   return freeze({mode:S.mode,round:S.round,observed:events.length,
      criticals:crits,source:freeze({archive:'2022 F_UNIT_MST_1/2_Ver1084.json',
        field:'damageFrames',baseChancePercent:10,multiplier:1.5,
        sourceHitRequirement:1,changesSaves:false}),
      recent:freeze(events.slice(-8))});
 }
 function render(){
   if(!panel)return;
   panel.hidden=S.mode!=='archive';
   line.textContent=events.length+' source-eligible normal attacks · '+
     crits+' critical hits (battle only)';
   rows.replaceChildren();
   for(const e of events.slice(-5).reverse()){
     const li=document.createElement('li');
     li.textContent='Wave '+e.wave+' · unit #'+e.unitId+
       ' · '+(e.critical?'CRITICAL':'normal')+
       ' · '+e.observedHpLoss+' observed DEMO HP lost';
     rows.append(li);
   }
 }
 document.getElementById('reset')?.addEventListener('click',()=>{sync();render()});
 document.getElementById('mode')?.addEventListener('change',()=>{
   if(S.mode!=='archive'){
     banner.hidden=true;lastBannerTurn=null;lastBannerWave=null;
   }
   render();
 });
 window.BFGlobalSingleHitCriticalV9300=freeze({
   source:freeze({reference:'https://bravefrontiereurope.fandom.com/wiki/Gameplay%3ABuffs%2C_Debuffs_and_Status_Ailments',
     critDamageReference:'https://bravefrontierglobal.fandom.com/wiki/Critical_Damage_Boost',
     archive:'2022 F_UNIT_MST_1/2_Ver1084.json',
     actualScope:'Source-verified single normal-hit player attacks, DEMO total damage formula',
     excluded:'Multihit timing, BBs, synthetic enemies, critical buffs/resistance, saves'}),
   roll,criticalDamage,snapshot
 });
 render();
})();
