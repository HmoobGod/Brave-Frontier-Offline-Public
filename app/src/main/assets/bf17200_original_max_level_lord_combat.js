/* BF_GLOBAL_ORIGINAL_MAX_LEVEL_LORD_COMBAT_V17200 */
(() => {
 'use strict';
 // Exact original 2022 Lord MAX endpoint only. Only 60 of 72 form max levels
 // are reachable with DEMO level cap 99; 12 max-level-100 forms skip.
 // Current EXP thresholds,
 // intermediate stat growth and all non-Lord type rolls remain DEMO.
 const source=window.BFGlobalOriginalLordStatsV11600;
 const caps=window.BFGlobalOriginalUnitLevelCapsV11500;
 if(window.BFGlobalOriginalMaxLevelLordV17200||
    !source||source.source?.formCount!==72||
    source.source?.baseAndLordMaxEndpointsVerified!==true||
    typeof source.endpoint!=='function'||!caps||
    caps.source?.forms!==72||typeof caps.lookup!=='function'||
    typeof P==='undefined'||P.version!==7||
    !Array.isArray(P.roster)||!Array.isArray(P.squad)||
    typeof effectiveUnit!=='function'||typeof demoLevel!=='function'||
    typeof S==='undefined')return;
 const mode=document.getElementById('mode');
 const host=document.getElementById('bf16800-original-level1-combat')||
   document.getElementById('squadpicker');
 if(!mode||!host)return;
 const freeze=Object.freeze;
 const audited=new WeakMap();
 let applied=0,skipped=0;
 const demoRates=freeze({hp:30,atk:12,def:8,rec:6});
 function apply(unit,slot){
   if(!unit||typeof unit!=='object'||audited.has(unit)||
      mode.value!=='archive'||!unit.active||
      !Number.isSafeInteger(slot)||slot<0||slot>=6||
      !Number.isSafeInteger(unit.baseId)||!Number.isSafeInteger(unit.unitId)||
      P.squad[slot]!==unit.baseId||!P.roster.includes(unit.baseId)||
      unit.hp!==unit.maxHp){skipped++;return unit;}
   const current=effectiveUnit(unit.baseId);
   const cap=caps.lookup(unit.unitId);
   const exp=P.unitExp?.[unit.baseId]??0;
   if(!current||current.id!==unit.unitId||!current.stats||
      !Number.isSafeInteger(cap)||cap<2||unit.level!==cap||
      !Number.isSafeInteger(exp)||exp<0||!Number.isSafeInteger(demoLevel(exp))||
      demoLevel(exp)<cap){skipped++;return unit;}
   const endpoint=source.endpoint(unit.unitId,cap);
   if(endpoint?.exactOriginalLordEndpoint!==true||
      endpoint.level!==cap||endpoint.unitId!==unit.unitId||
      source.lookup(unit.unitId)?.maxLevel!==cap){skipped++;return unit;}
   const values=endpoint.stats,raw=current.stats;
   const before={hp:unit.maxHp,atk:unit.atk,def:unit.def,rec:unit.rec};
   if(['hp','atk','def','rec'].some(k=>
      !Number.isSafeInteger(raw[k])||raw[k]<1||
      !Number.isSafeInteger(values?.[k])||values[k]<1||values[k]>100000000||
      !Number.isSafeInteger(before[k])||before[k]!==raw[k]+(cap-1)*demoRates[k])){
      skipped++;return unit;
   }
   unit.maxHp=values.hp;unit.hp=values.hp;
   unit.atk=values.atk;unit.def=values.def;unit.rec=values.rec;
   audited.set(unit,freeze({slot,baseId:unit.baseId,unitId:unit.unitId,
      maxLevel:cap,sourceYear:2022,exactLordMaxEndpoint:true,
      priorDemo:freeze(before),originalLordMax:values,
      nativeExpCurveKnown:false,nativeIntermediateGrowthKnown:false,
      sourceTypeRollsApplied:false,saveFieldsAdded:0}));
   applied++;return unit;
 }
 function snapshot(){
   const rows=Array.isArray(S.party)?S.party.map(u=>audited.get(u)).filter(Boolean):[];
   return freeze({mode:S.mode,sourceForms:72,
      reachableSourceFormsUnderDemoLevel99:60,
      maxLevel100UnreachableForms:12,
      exactLordMaxPartyUnits:rows.length,rows:freeze(rows),
      appliedBuilders:applied,skippedBuilders:skipped,
      originalLevelOneBaselinePreserved:true,
      originalMaxLevelEndpointApplied:true,
      intermediateGrowthAndExpStillDemo:true,otherTypesUnmodeled:true,
      trainedUnitsUnchanged:true,saveFieldsAdded:0});
 }
 const panel=document.createElement('details');panel.id='bf17200-original-max-lord';
 panel.style.cssText='margin:8px 3px;padding:8px;border:1px solid #a7b9bc;'+
   'border-radius:7px;background:#26383f;color:#eaf6ef;font:12px/1.5 system-ui';
 const summary=document.createElement('summary');
 summary.textContent='ORIGINAL 2022 LORD MAX-LEVEL STATS · SOURCE-VERIFIED';
 summary.style.cssText='cursor:pointer;min-height:36px;font-weight:800';
 const status=document.createElement('p');
 const list=document.createElement('ol');
 const note=document.createElement('small');
 note.textContent='Uses exact original 2022 HP/ATK/DEF/REC Lord endpoints only when '+ 
   'the currently playable unit reaches its archived source max level in '+ 
   'the existing DEMO progression. Intermediate leveling, EXP patterns, '+ 
   'non-Lord type bonuses and native damage formulas remain unverified. '+
   'Current DEMO leveling stops at 99: 12 source Lv.100 forms cannot '+
   'reach this max endpoint yet, while 60 of 72 can qualify. '+ 
   'No change to saved experience, rosters, quest rewards or training.';
 panel.append(summary,status,list,note);host.after(panel);
 function refresh(){
   const state=snapshot();panel.hidden=S.mode!=='archive';
   status.textContent=state.exactLordMaxPartyUnits+
     ' owned max-level Lord endpoints applied to this battle';
   list.replaceChildren();
   if(panel.open)for(const row of state.rows){
     const li=document.createElement('li');
     li.textContent='Slot '+(row.slot+1)+' · #'+row.unitId+
       ' · original Lv.'+row.maxLevel+' Lord HP '+row.originalLordMax.hp+
       ', ATK '+row.originalLordMax.atk+
       ', DEF '+row.originalLordMax.def+
       ', REC '+row.originalLordMax.rec;
     list.append(li);
   }
   return state;
 }
 panel.addEventListener('toggle',refresh);
 mode.addEventListener('change',refresh);
 document.getElementById('reset')?.addEventListener('click',()=>setTimeout(refresh,0));
 window.BFGlobalOriginalMaxLevelLordV17200=freeze({
   source:freeze({archive:'2022 F_UNIT_MST_1/2_Ver1084.json',
     qualifiedForms:72,reachableUnderCurrentDemoLevel99:60,
     skippedSourceLv100Forms:12,sourceLordMaxOnly:true,
     exactIntermediateGrowthClaimed:false,saveFieldsAdded:0}),
   apply,snapshot,refresh
 });
 refresh();
})();