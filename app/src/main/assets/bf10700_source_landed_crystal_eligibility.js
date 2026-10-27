/* BF_GLOBAL_ORIGINAL_LANDED_CRYSTAL_ELIGIBILITY_V10700 */
(() => {
 'use strict';
 // 2022 F_UNIT normal hit counts + original dropCheckCount, intersected
 // with confirmed real DEMO attacks. This audits eligibility ONLY:
 // native pickups, recipients, healing, BB charging remain unverified.
 const source=window.BFGlobalAllNormalCrystalChecksV8400;
 const one=window.BFGlobalSingleHitCriticalV9300;
 const multi=window.BFGlobalMultiHitCriticalV9500;
 if(window.BFGlobalLandedCrystalEligibilityV10700||!source||!one||!multi||
   typeof source.lookup!=='function'||typeof one.snapshot!=='function'||
   typeof multi.snapshot!=='function'||typeof P==='undefined'||P.version!==7||
   typeof S==='undefined')return;
 const host=document.getElementById('bf9000-crystal-provenance')?.parentElement||
   document.getElementById('bf2000-run');
 if(!host)return;
 const freeze=Object.freeze;
 function eligibleHit(e) {
   return !!e&&e.landed===true&&typeof e.critical==='boolean'&&
     Number.isSafeInteger(e.appliedDamage)&&e.appliedDamage>0&&
     Number.isSafeInteger(e.baseDamage)&&e.baseDamage>0&&
     Number.isSafeInteger(e.resultDamage)&&e.resultDamage>=e.appliedDamage;
 }
 function audit(event,kind) {
   if(!event||!['normal-single','normal-multi'].includes(kind)||
      !Number.isSafeInteger(event.unitId)||event.unitId<=0||
      !Number.isSafeInteger(event.wave)||event.wave<1||
      !Number.isSafeInteger(event.round)||event.round<0)return null;
   const profile=source.lookup(event.unitId);
   if(!profile||!Number.isSafeInteger(profile.normalHits)||
      !Number.isSafeInteger(profile.checksPerHit)||profile.checksPerHit<=0||
      profile.normalHits*profile.checksPerHit!==profile.totalDropChecks)return null;
   let landed=0,criticalHits=0;
   if(kind==='normal-single'){
     if(event.sourceSingleHit!==true||profile.normalHits!==1||
        !Number.isFinite(event.observedHpLoss)||event.observedHpLoss<=0||
        typeof event.critical!=='boolean')return null;
     landed=1;criticalHits=event.critical?1:0;
   }else{
     if(event.sourceMultiHit!==true||event.nativeDamageFormula!==false||
       profile.normalHits<2||profile.normalHits>64||
       !Array.isArray(event.hits)||event.hits.length!==profile.normalHits||
       !Number.isSafeInteger(event.rolls)||!Number.isSafeInteger(event.criticals)||
       !Number.isFinite(event.observedHpLoss)||event.observedHpLoss<=0)return null;
     let gap=false,applied=0;
     for(let i=0;i<event.hits.length;i++){
       const h=event.hits[i];
       if(!h||h.index!==i+1||typeof h.landed!=='boolean'||
          typeof h.critical!=='boolean'||!Number.isSafeInteger(h.appliedDamage)||
          h.appliedDamage<0||!Number.isSafeInteger(h.baseDamage)||
          h.baseDamage<0||!Number.isSafeInteger(h.resultDamage)||
          h.resultDamage<0)return null;
       if(h.landed){
         if(gap||!eligibleHit(h))return null;
         landed++;applied+=h.appliedDamage;
         if(h.critical)criticalHits++;
       }else{
         if(h.critical||h.appliedDamage!==0)return null;
         gap=true;
       }
     }
     if(landed<1||landed!==event.rolls||criticalHits!==event.criticals||
        applied!==event.observedHpLoss)return null;
   }
   const eligibleBCChecks=landed*profile.checksPerHit;
   const skippedPostKO=profile.normalHits-landed;
   return freeze({
     kind,unitId:event.unitId,round:event.round,wave:event.wave,
     sourceHits:profile.normalHits,landedHits:landed,
     skippedPostKO,checksPerHit:profile.checksPerHit,
     originalPossibleBCChecks:profile.totalDropChecks,
     eligibleBCChecks,unverifiedPostKOBCChecks:skippedPostKO*profile.checksPerHit,
     eligibleHCChecks:landed,criticalHits,
     bcRatePercent:35,hcRatePercent:10,
     overkillApplied:false,referenceOnly:true,collected:false,
     nativePickupNotImplemented:true
   });
 }
 function snapshot(){
   const oneRows=one.snapshot().recent||[];
   const multiRows=multi.snapshot().recent||[];
   const entries=[];
   for(const e of oneRows.slice(-8)){
     const value=audit(e,'normal-single');
     if(value)entries.push(value);
   }
   for(const e of multiRows.slice(-8)){
     const value=audit(e,'normal-multi');
     if(value)entries.push(value);
   }
   const totals=freeze({
     eligibleBCChecks:entries.reduce((x,e)=>x+e.eligibleBCChecks,0),
     eligibleHCChecks:entries.reduce((x,e)=>x+e.eligibleHCChecks,0),
     unverifiedPostKOBCChecks:entries.reduce((x,e)=>x+e.unverifiedPostKOBCChecks,0),
     observedAttacks:entries.length
   });
   return freeze({mode:S.mode,active:S.mode==='archive',
     totals,recent:freeze(entries),
     interpretation:'Recent source-qualified normal attacks only; no pickups or original recipient calculation',
     cumulative:false,saveFieldsAdded:0});
 }
 const panel=document.createElement('details');
 panel.id='bf10700-landed-crystals';
 panel.style.cssText='padding:10px;margin:9px 2px;border:1px solid #92adba;'+
   'border-radius:6px;background:#18353a;color:#e9f9f6;'+
   'font:12px/1.5 system-ui,sans-serif';
 const title=document.createElement('summary');
 title.textContent='SOURCE CRYSTAL CHECKS · LANDED HITS ONLY';
 title.style.cssText='cursor:pointer;min-height:36px;font-weight:800';
 const count=document.createElement('p');count.id='bf10700-totals';
 const rows=document.createElement('ol');rows.id='bf10700-rows';
 const caution=document.createElement('small');
 caution.textContent='2022 Global normal damage-hit/check records × confirmed DEMO landed strikes. '+
   'Counts only DEMO landed strikes; native overkill/post-KO mechanics remain unknown. These are potential BC/HC RNG '+
   'check counts, not collected crystals. Native pickup, overkill, '+
   'HP recovery and BB charging are NOT implemented. Older v88 ledger '+
   'may still count all sourced hits; neither ledger establishes original native overkill, and neither is collectible.';
 panel.append(title,count,rows,caution);host.append(panel);
 let last='';
 function refresh(){
   const s=snapshot();panel.hidden=s.mode!=='archive';
   const signature=JSON.stringify(s.totals)+JSON.stringify(s.recent);
   if(!panel.open||signature===last)return s;
   last=signature;
   count.textContent='Recent '+s.totals.observedAttacks+' validated attacks · '+
     s.totals.eligibleBCChecks+' potential BC checks · '+
     s.totals.eligibleHCChecks+' potential HC checks · '+
     s.totals.unverifiedPostKOBCChecks+' post-KO BC checks outside confirmed landed baseline';
   rows.replaceChildren();
   for(const e of s.recent.slice(-8)){
     const li=document.createElement('li');
     li.textContent='Wave '+e.wave+' · Unit #'+e.unitId+' · '+
       e.landedHits+'/'+e.sourceHits+' landed · '+
       e.eligibleBCChecks+' BC checks / '+e.eligibleHCChecks+
       ' HC checks; '+e.skippedPostKO+' skipped after KO';
     rows.append(li);
   }
   return s;
 }
 panel.addEventListener('toggle',()=>{last='';refresh();});
 const timer=setInterval(()=>{if(!document.hidden&&panel.open)refresh();},900);
 window.addEventListener('pagehide',()=>clearInterval(timer),{once:true});
 refresh();
 window.BFGlobalLandedCrystalEligibilityV10700=freeze({audit,snapshot,refresh,
   source:freeze({archive:'2022 F_UNIT_MST_1/2_Ver1084.json',
     dependsOn:'v93 single-hit/v95 multi-hit DEMO combat traces',
     nativeCrystalPickup:false,sourceCompatible:true})});
})();
