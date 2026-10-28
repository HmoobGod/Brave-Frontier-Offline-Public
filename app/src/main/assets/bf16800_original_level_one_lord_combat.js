/* BF_GLOBAL_ORIGINAL_LEVEL1_LORD_COMBAT_V16800 */
(() => {
 'use strict';
 // 2022 original unitBase HP/ATK/DEF/REC, only the level-one Lord
 // endpoint. Original EXP curves, unit-type rolls, midlevel growth and
 // battle damage formula remain unverified; none are inferred here.
 const source=window.BFGlobalOriginalLordStatsV11600;
 if(window.BFGlobalOriginalLevelOneLordV16800||
    !source||source.source?.formCount!==72||
    source.source?.baseAndLordMaxEndpointsVerified!==true||
    typeof source.endpoint!=='function'||
    typeof P==='undefined'||P.version!==7||
    !Array.isArray(P.squad)||!Array.isArray(P.roster)||
    typeof effectiveUnit!=='function'||typeof S==='undefined')return;
 const mode=document.getElementById('mode');
 const host=document.getElementById('bf11600-original-lord-stats')||
    document.getElementById('squadpicker');
 if(!mode||!host)return;
 const freeze=Object.freeze;
 const audited=new WeakMap();
 let applied=0,skipped=0;
 function apply(unit,slot){
   if(!unit||typeof unit!=='object'||audited.has(unit)||
      mode.value!=='archive'||!unit.active||
      !Number.isSafeInteger(slot)||slot<0||slot>=6||
      !Number.isSafeInteger(unit.unitId)||!Number.isSafeInteger(unit.baseId)||
      !P.roster.includes(unit.baseId)||P.squad[slot]!==unit.baseId||
      unit.level!==1||unit.hp!==unit.maxHp||
      (P.unitExp?.[unit.baseId]??0)!==0){skipped++;return unit;}
   const selected=effectiveUnit(unit.baseId);
   const endpoint=source.endpoint(unit.unitId,1);
   if(selected?.id!==unit.unitId||!selected.stats||
      endpoint?.exactOriginalLordEndpoint!==true||
      endpoint.unitId!==unit.unitId||endpoint.level!==1){skipped++;return unit;}
   const values=endpoint.stats;
   const keys=['hp','atk','def','rec'];
   if(keys.some(k=>!Number.isSafeInteger(values[k])||
       values[k]<=0||values[k]>100000000||
       !Number.isSafeInteger(selected.stats[k])||
       selected.stats[k]<=0||
       (k==='hp'?unit.maxHp:unit[k])!==selected.stats[k])){
     skipped++;return unit;
   }
   const before=freeze({hp:unit.maxHp,atk:unit.atk,
     def:unit.def,rec:unit.rec});
   unit.maxHp=values.hp;unit.hp=values.hp;
   unit.atk=values.atk;unit.def=values.def;unit.rec=values.rec;
   audited.set(unit,freeze({slot,baseId:unit.baseId,unitId:unit.unitId,
     level:1,sourceYear:2022,sourceExactLevelOne:true,
     originalLordBase:values,priorDemo:before,
     expSaved:false,saveFieldsAdded:0}));
   applied++;
   return unit;
 }
 function snapshot(){
   const rows=Array.isArray(S.party)?
      S.party.map(unit=>audited.get(unit)).filter(Boolean):[];
   return freeze({mode:S.mode,originalLevelOnePartyUnits:rows.length,
      rows:freeze(rows),appliedBuilders:applied,skippedBuilders:skipped,
      originalSourceExactAtLevelOne:true,
      originalTypeRollsApplied:false,originalExpCurvesApplied:false,
      originalMidlevelStatsApplied:false,nativeDamageFormulaRecovered:false,
      trainingUnchanged:true,saveFieldsAdded:0});
 }
 const panel=document.createElement('details');
 panel.id='bf16800-original-level1-combat';
 panel.style.cssText='margin:8px 3px;padding:8px;border:1px solid #a8c2b7;'+
   'border-radius:7px;background:#1d393d;color:#eaf6ed;'+
   'font:12px/1.5 system-ui,sans-serif';
 const summary=document.createElement('summary');
 summary.textContent='ORIGINAL 2022 LEVEL-ONE BASE STATS · LORD';
 summary.style.cssText='cursor:pointer;min-height:36px;font-weight:800';
 const status=document.createElement('p');status.id='bf16800-live-status';
 const list=document.createElement('ol');list.id='bf16800-rows';
 const note=document.createElement('small');
 note.textContent='Exact archived 2022 HP/ATK/DEF/REC base values only for '+
   'legitimately owned zero-EXP level-one forms in NEW archive DEMO battles. '+
   'Other levels, unit-type rolls, original EXP curve, full damage and rounding '+
   'remain unverified. No training, saved EXP, roster, rewards or v7 changes.';
 panel.append(summary,status,list,note);host.after(panel);
 function refresh(){
   const state=snapshot();
   panel.hidden=S.mode!=='archive';
   status.textContent=state.originalLevelOnePartyUnits+
      ' qualifying original-source level-one forms in this battle';
   list.replaceChildren();
   if(panel.open)for(const r of state.rows){
     const li=document.createElement('li');
     li.textContent='Slot '+(r.slot+1)+' · #'+r.unitId+
       ' · original Lv.1 HP '+r.originalLordBase.hp+
       ', ATK '+r.originalLordBase.atk+
       ', DEF '+r.originalLordBase.def+
       ', REC '+r.originalLordBase.rec;
     list.append(li);
   }
   return state;
 }
 panel.addEventListener('toggle',refresh);
 mode.addEventListener('change',refresh);
 document.getElementById('reset')?.addEventListener('click',
   ()=>setTimeout(refresh,0));
 window.BFGlobalOriginalLevelOneLordV16800=freeze({
   source:freeze({archive:'2022 Global F_UNIT_MST_1/2_Ver1084.json',
     qualifiedForms:72,levelOneOnly:true,saveFieldsAdded:0,
     nativeIntermediateGrowthKnown:false,unitTypesApplied:false}),
   apply,snapshot,refresh
 });
 refresh();
})();
