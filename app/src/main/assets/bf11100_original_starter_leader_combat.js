/* BF_GLOBAL_ORIGINAL_STARTER_LEADER_COMBAT_V11100 */
(() => {
 'use strict';
 // Connect strictly source-qualified 2022 starter leader stat percentages to
 // freshly constructed ORIGINAL-MISSION demo party units, never to progression.
 // The underlying level/type stats and damage formula are still DEMO.
 const source=window.BFGlobalStarterLeaderSourceV11000;
 const original=window.playerUnit;
 if(window.BFGlobalStarterLeaderCombatV11100||!source||
    typeof original!=='function'||typeof source.bonusFor!=='function'||
    typeof effectiveUnit!=='function'||typeof P==='undefined'||P.version!==7||
    typeof S==='undefined'||!Array.isArray(P.squad)||
    !String(original).includes('const uid=P.squad[i]')||
    !String(original).includes('src.stats.hp+grow*30'))return;
 const mode=document.getElementById('mode');
 const host=document.getElementById('bf2000-run')||
   document.getElementById('squadpicker');
 if(!mode||!host)return;
 const freeze=Object.freeze;
 const built=new WeakMap();
 let applied=0,skipped=0;
 function fromSource(leaderBase,targetId){
   if(!Number.isSafeInteger(leaderBase)||!P.roster?.includes(leaderBase)||
      !Number.isSafeInteger(targetId))return null;
   const form=effectiveUnit(leaderBase);
   if(!Number.isSafeInteger(form?.id))return null;
   const b=source.bonusFor(form.id,targetId);
   return b?.originalEffect===true&&b.appliedToLiveBattle===false&&
     b.sameElement===true&&Number.isInteger(b.atkPercent)&&
     Number.isInteger(b.hpPercent)&&b.atkPercent>=0&&b.atkPercent<=50&&
     b.hpPercent>=0&&b.hpPercent<=10?b:null;
 }
 function apply(unit,slot){
   if(!unit||typeof unit!=='object'||built.has(unit)||
      mode.value!=='archive'||!unit.active||
      !Number.isSafeInteger(slot)||slot<0||slot>=6||
      !Number.isSafeInteger(unit.unitId)||
      P.squad[slot]!==unit.baseId||!P.roster.includes(unit.baseId)||
      !Number.isSafeInteger(unit.atk)||unit.atk<1||
      !Number.isSafeInteger(unit.maxHp)||unit.maxHp<1||
      unit.hp!==unit.maxHp){skipped++;return unit;}
   const bonus=fromSource(P.squad[0],unit.unitId);
   if(!bonus||(!bonus.atkPercent&&!bonus.hpPercent)){
     skipped++;return unit;
   }
   const startAtk=unit.atk,startHp=unit.maxHp;
   // Deterministic floor in the DEMO stat model: original F_LEADER_SKILL
   // percentages are proven, the full native stat-rounding order is not.
   const nextAtk=Math.floor(startAtk*(100+bonus.atkPercent)/100);
   const nextHp=Math.floor(startHp*(100+bonus.hpPercent)/100);
   if(!Number.isSafeInteger(nextAtk)||nextAtk<=0||
      !Number.isSafeInteger(nextHp)||nextHp<=0||
      nextAtk>1e9||nextHp>1e9){skipped++;return unit;}
   unit.atk=nextAtk;unit.maxHp=nextHp;unit.hp=nextHp;
   const row=freeze({slot,baseId:unit.baseId,unitId:unit.unitId,
     leaderId:bonus.leaderId,originalAtk:startAtk,originalHp:startHp,
     effectiveAtk:nextAtk,effectiveHp:nextHp,
     atkPercent:bonus.atkPercent,hpPercent:bonus.hpPercent,
     originalSource:true,nativeStatRoundingVerified:false});
   built.set(unit,row);applied++;
   return unit;
 }
 window.playerUnit=function(i){
   const unit=original.apply(this,arguments);
   // v113 optional original 2022 cap runs BEFORE the source leader bonus.
   // Absent v113, retain v111's previously verified native behavior.
   window.BFGlobalOriginalUnitLevelCapsV11300?.apply?.(unit,i);
   return apply(unit,i);
 };
 function snapshot(){
   const party=Array.isArray(S.party)?S.party:[];
   const rows=party.map(u=>built.get(u)).filter(Boolean);
   return freeze({mode:S.mode,sourceQualified:S.mode==='archive',
     appliedPartyUnits:rows.length,appliedBuilders:applied,
     skippedBuilders:skipped,rows:freeze(rows),
     saveFieldsAdded:0,trainingUnaffected:true,
     baseStatsAndDamageFormulaStillDemo:true,
     exactOriginalLeaderPercentages:true,
     nativeDamageAndRoundingNotFullyRecovered:true});
 }
 const panel=document.createElement('details');
 panel.id='bf11100-leader-combat';
 panel.style.cssText='margin:7px 2px;padding:9px;border:1px solid #97bba9;'+
   'border-radius:6px;background:#1b3337;color:#f0f5ee;font:12px/1.5 system-ui,sans-serif';
 const heading=document.createElement('summary');
 heading.textContent='ORIGINAL LEADER SKILL EFFECTS · SOURCE-GATED';
 heading.style.cssText='min-height:36px;cursor:pointer;font-weight:800';
 const totals=document.createElement('p');totals.id='bf11100-counts';
 const rows=document.createElement('ol');rows.id='bf11100-rows';
 const note=document.createElement('small');
 note.textContent='Original 2022 starter leader ATK/HP percentages are applied '+
   'once when a new archive DEMO party is created. Only 30 source-verified '+
   'forms and matching elements qualify. No training changes; no save writes. '+
   'Higher 4★–6★ forms qualify only when the original evolution '+
   'assets have actually been packaged by the build pipeline. '+
   'Base level/type stats, rounding order and damage formula remain DEMO, '+
   'not fully reconstructed original Brave Frontier mechanics.';
 panel.append(heading,totals,rows,note);host.after(panel);
 function refresh(){
   const s=snapshot();panel.hidden=s.mode!=='archive';
   totals.textContent=s.appliedPartyUnits+' squad units with source-verified '+
     'leader stat effects this battle (DEMO baseline)';
   rows.replaceChildren();
   if(panel.open)for(const r of s.rows){
     const li=document.createElement('li');
     li.textContent='Slot '+(r.slot+1)+' · #'+r.unitId+' · ATK '+
       r.originalAtk+' → '+r.effectiveAtk+' (+'+r.atkPercent+'%) · HP '+
       r.originalHp+' → '+r.effectiveHp+' (+'+r.hpPercent+'%)';
     rows.append(li);
   }
   return s;
 }
 panel.addEventListener('toggle',refresh);
 document.getElementById('reset')?.addEventListener('click',()=>setTimeout(refresh,0));
 mode.addEventListener('change',()=>setTimeout(refresh,0));
 const timer=setInterval(()=>{if(!document.hidden&&panel.open)refresh();},2200);
 window.addEventListener('pagehide',()=>clearInterval(timer),{once:true});
 window.BFGlobalStarterLeaderCombatV11100=freeze({source:freeze({
   archive:'2022 F_UNIT_MST_1/2_Ver1084.json + F_LEADER_SKILL_MST_Ver749.json',
   forms:30,leaderIds:18,scope:'new archive DEMO party units only',
   trainingChanges:false,saveFieldsAdded:0,nativeRoundingVerified:false}),
   fromSource,apply,snapshot,refresh
 });
 source.refresh?.();
 refresh();
})();