/* BF_GLOBAL_MULTIHIT_CRITICAL_COMBAT_V9500 */
(() => {
 'use strict';
 // v95: source-validated original normal-hit timing/weights, plus the
 // contemporary 10% base critical chance and 150% damage reference.
 // Total pre-critical damage and all other multipliers remain DEMO.
 const source=window.BFGlobalAllNormalCrystalChecksV8400;
 const oldPerform=window.performUnit,oldSplit=window.splitDemoDamage;
 if(window.BFGlobalMultiHitCriticalV9500||!source||
   typeof oldPerform!=='function'||typeof oldSplit!=='function'||
   typeof P==='undefined'||P.version!==7||typeof S==='undefined')return;
 const freeze=Object.freeze;
 const host=document.getElementById('bf9300-critical')?.parentElement||
   document.getElementById('bf2000-run')||
   document.getElementById('log')?.parentElement;
 if(!host)return;
 const bannerHost=document.getElementById('phase')?.parentElement;
 const banner=document.createElement('div');
 banner.id='bf9500-critical-banner';banner.hidden=true;
 banner.setAttribute('role','status');banner.setAttribute('aria-live','polite');
 banner.style.cssText='margin:5px 0;padding:4px 8px;border:1px solid #e9bd6e;'+
   'border-radius:5px;background:#533c1c;color:#ffe7a4;'+
   'font:800 13px/1.4 system-ui,sans-serif;pointer-events:none';
 if(bannerHost)bannerHost.append(banner);
 let battle=S,ctx=null,events=[],criticalHits=0,visibleRound=null,visibleWave=null;
 function resetOnBattleChange(){
   if(S!==battle){battle=S;ctx=null;events=[];criticalHits=0;
     visibleRound=null;visibleWave=null;banner.hidden=true;}
 }
 function eligible(unit){
   if(S.mode!=='archive'||S.over||!unit||unit.action?.kind!=='attack'||
     !Number.isSafeInteger(unit.id)||unit.id<0||unit.id>=6||
     S.party?.[unit.id]!==unit||!unit.active||unit.hp<=0||
     !Number.isSafeInteger(unit.unitId)||!Number.isSafeInteger(unit.action.target))return null;
   const profile=source.lookup(unit.unitId);
   const original=window.BF_ARCHIVE_NORMAL_HITS?.[String(unit.unitId)];
   const target=S.enemies?.find(e=>e?.slot===unit.action.target&&e.hp>0);
   if(!profile||!Number.isSafeInteger(profile.normalHits)||profile.normalHits<2||
     profile.normalHits>64||!original||original.weightsTotal!==100||
     !Array.isArray(original.events)||original.events.length!==profile.normalHits||
     original.events.some(e=>!Array.isArray(e)||e.length!==4||
       !e.every(Number.isFinite)||e[0]<0||e[1]<0)||!target)return null;
   return {battle:S,unit,slot:unit.id,unitId:unit.unitId,target,
     original,hp:target.hp,round:S.round,wave:S.wave+1,attempted:false,
     criticals:0,rolls:0,baseTotal:0,resultTotal:0,hits:[]};
 }
 function roll(random=Math.random){
   if(typeof random!=='function')return null;
   const r=random();return Number.isFinite(r)&&r>=0&&r<1?r<0.1:null;
 }
 function criticalDamage(damage,isCritical){
   return isCritical&&Number.isSafeInteger(damage)&&damage>0?
     Math.max(1,Math.floor(damage*1.5)):damage;
 }
 window.splitDemoDamage=function(total,strikes){
   const portions=oldSplit.apply(this,arguments),local=ctx;
   if(!local||local.attempted||S!==local.battle||
      S.party?.[local.slot]!==local.unit||local.unit.action?.kind!=='attack'||
      S.mode!=='archive'||local.target.hp<=0||
      !Array.isArray(portions)||portions.length!==local.original.events.length||
      !Array.isArray(strikes)||strikes.length!==portions.length||
      strikes.some((e,i)=>!Array.isArray(e)||e.length!==4||
        e.some((x,j)=>x!==local.original.events[i][j]))||
      !portions.every(n=>Number.isSafeInteger(n)&&n>=0))return portions;
   local.attempted=true;
   local.baseTotal=portions.reduce((a,b)=>a+b,0);
   // V9600_OVERKILL_GUARD: splitDemoDamage is computed before the animated
   // hits land. Only roll a critical for a strike that can actually land
   // while the current target has HP. Never count phantom post-KO strikes.
   // This mirrors the existing DEMO application order; it does not infer
   // native overkill/extra-hit rules or change the 2022 damage weights.
   let remaining=local.target.hp;
   const modified=portions.map((damage,i)=>{
     const landed=damage>0&&remaining>0;
     const critical=landed&&roll()===true;
     if(landed)local.rolls++;
     if(critical)local.criticals++;
     const result=criticalDamage(damage,critical);
     const appliedDamage=landed?Math.min(remaining,result):0;
     remaining=Math.max(0,remaining-appliedDamage);
     local.hits.push(freeze({index:i+1,baseDamage:damage,
       landed,critical,appliedDamage,resultDamage:result}));
     return result;
   });
   local.resultTotal=modified.reduce((a,b)=>a+b,0);
   return modified;
 };
 window.performUnit=async function(unit,token){
   resetOnBattleChange();
   if(visibleRound!==null&&(S.round!==visibleRound||S.wave!==visibleWave)){
     banner.hidden=true;visibleRound=null;visibleWave=null;
   }
   const prior=ctx,local=eligible(unit);
   ctx=local;
   try {return await oldPerform.call(this,unit,token);}
   finally {
     if(local&&local.attempted&&S===local.battle&&
       S.party?.[local.slot]===local.unit&&
       Number.isFinite(local.target.hp)&&local.target.hp<local.hp){
       const e=freeze({unitId:local.unitId,slot:local.slot,
         round:local.round,wave:local.wave,hits:freeze(local.hits.slice()),
         criticals:local.criticals,rolls:local.rolls,
         baseTotal:local.baseTotal,resultTotal:local.resultTotal,
         observedHpLoss:local.hp-local.target.hp,sourceMultiHit:true,
         nativeDamageFormula:false});
       events.push(e);if(events.length>32)events.shift();
       criticalHits+=e.criticals;
       if(e.criticals){
         const label=e.criticals+' CRITICAL HIT'+(e.criticals===1?'':'S')+
           '! · unit #'+e.unitId+' · '+e.observedHpLoss+' HP damage (DEMO)';
         if(bannerHost){banner.textContent=label;banner.hidden=false;
           visibleRound=local.round;visibleWave=S.wave;}
         const log=document.getElementById('log');
         if(log){const notice=document.createElement('div');
           notice.className='bf9500-critical-notice';notice.textContent=label;
           notice.style.cssText='color:#ffe59c;font-weight:800;margin:4px 0';
           log.append(notice);}
       }
     }
     ctx=prior;render();
   }
 };
 const panel=document.createElement('details');
 panel.id='bf9500-multihit-critical';
 panel.style.cssText='margin:8px 4px;padding:8px;border:1px solid #bea778;'+
   'border-radius:6px;background:#303443;color:#fff1d5;font:12px/1.5 system-ui,sans-serif';
 const heading=document.createElement('summary');
 heading.textContent='ORIGINAL MULTI-HIT NORMAL CRITICALS';
 heading.style.cssText='cursor:pointer;min-height:34px;font-weight:800';
 const counts=document.createElement('p');counts.id='bf9500-critical-counts';
 const list=document.createElement('ol');list.id='bf9500-critical-events';
 const note=document.createElement('small');
 note.textContent='Each positive-damage source-verified normal hit rolls the base 10% critical chance and deals 150% of that hit’s DEMO damage if critical. Normal attack weights are archived. Native full damage, enemy attacks, BB/SBB, buffs, resistance and unsupported profiles remain unchanged.';
 panel.append(heading,counts,list,note);host.append(panel);
 function render(){
   panel.hidden=S.mode!=='archive';
   counts.textContent=events.length+' sourced multi-hit attacks · '+
     criticalHits+' critical hits (battle only)';
   list.replaceChildren();
   for(const e of events.slice(-5).reverse()){
     const item=document.createElement('li');
     item.textContent='Wave '+e.wave+' · unit #'+e.unitId+
       ' · '+e.criticals+'/'+e.rolls+' criticals · '+
       e.observedHpLoss+' observed DEMO HP lost';
     list.append(item);
   }
 }
 function snapshot(){
   resetOnBattleChange();
   return freeze({mode:S.mode,round:S.round,observed:events.length,
     criticalHits,source:freeze({archive:'2022 F_UNIT_MST_1/2_Ver1084.json',
       criticalChancePercent:10,criticalMultiplier:1.5,
       scope:'Source-verified normal attacks with 2+ hits; demo base damage',
       savedFieldsAdded:0}),recent:freeze(events.slice(-8))});
 }
 document.getElementById('reset')?.addEventListener('click',()=>{
   resetOnBattleChange();banner.hidden=true;visibleRound=null;render();
 });
 document.getElementById('mode')?.addEventListener('change',()=>{
   if(S.mode!=='archive')banner.hidden=true;
   render();
 });
 window.BFGlobalMultiHitCriticalV9500=freeze({
   source:freeze({mechanics:'https://bravefrontierglobal.fandom.com/wiki/Damage',
     scope:'Original multi-hit normal-attack critical chance/multiplier on DEMO base',
     excluded:'BB/SBB, unsupported weights, enemies, saved mastery, native damage'}),
   roll,criticalDamage,snapshot
 });
 render();
})();
