/* BF_GLOBAL_2022_LORD_STATS_REFERENCE_V11600 */
(()=>{
 'use strict';
 // Exact original 2022 level-one and Lord-max stat endpoints.
 // NOT a level interpolation, type roll, HP change or combat calculation.
 const original=window.BFGlobalOriginalLordStatsDataV11600;
 if(window.BFGlobalOriginalLordStatsV11600||
   !original||original.schema!=='bf-global-2022-playable-lord-stat-endpoints-v116'||
   original.unitCount!==72||original.rawUnitTypeCount!==6||
   original.liveStatsChanged!==false||original.saveFieldsAdded!==0||
   original.nativeGrowthAndRoundingVerified!==false||
   original.source?.archiveSha256!==
      '69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'||
   typeof P==='undefined'||P.version!==7||!Array.isArray(P.squad)||
   !Array.isArray(P.roster)||typeof effectiveUnit!=='function')return;
 const host=document.getElementById('squadpicker');
 if(!host)return;
 const freeze=Object.freeze;
 const byId=new Map();
 for(const entry of original.rows){
   if(!Number.isSafeInteger(entry.unitId)||byId.has(entry.unitId)||
      !Number.isSafeInteger(entry.maxLevel)||entry.maxLevel<1||
      !Number.isSafeInteger(entry.expPatternId)||
      !entry.base||!entry.lordAtMax)return;
   const base={},lord={};
   for(const key of ['hp','atk','def','rec']){
     const a=entry.base[key],b=entry.lordAtMax[key];
     if(!Number.isSafeInteger(a)||!Number.isSafeInteger(b)||a<1||
        b<a)return;
     base[key]=a;lord[key]=b;
   }
   byId.set(entry.unitId,freeze({
     unitId:entry.unitId,maxLevel:entry.maxLevel,
     expPatternId:entry.expPatternId,
     base:freeze(base),lordAtMax:freeze(lord)
   }));
 }
 if(byId.size!==72||byId.get(10011)?.base.hp!==1030||
    byId.get(10011)?.lordAtMax.hp!==1948||
    byId.get(10015)?.lordAtMax.hp!==5313||
    byId.get(60015)?.lordAtMax.hp!==5942)return;
 const rawType=freeze(original.unitTypeRaw.map(entry=>freeze({...entry})));
 if(rawType.length!==6||rawType[1].unitTypeHpRaw!=='5,10')return;
 function lookup(unitId){
   return Number.isSafeInteger(unitId)?byId.get(unitId)||null:null;
 }
 function endpoint(unitId,level){
   const row=lookup(unitId);
   if(!row||!Number.isSafeInteger(level))return null;
   if(level===1)return freeze({unitId,level,exactOriginalLordEndpoint:true,stats:row.base});
   if(level===row.maxLevel)return freeze({unitId,level,exactOriginalLordEndpoint:true,stats:row.lordAtMax});
   // Mid-level stats need a verified original type and leveling formula.
   return null;
 }
 function snapshot(){
   const slots=P.squad.slice(0,6).map((baseId,index)=>{
     if(!Number.isSafeInteger(baseId)||!P.roster.includes(baseId))
       return freeze({slot:index,baseId,formId:null,reference:null});
     const current=effectiveUnit(baseId);
     const id=Number.isSafeInteger(current?.id)?current.id:null;
     return freeze({slot:index,baseId,formId:id,reference:lookup(id)});
   });
   return freeze({source:freeze({archive:'mst-decoded.zip',
       originalUnitMaster:'2022 F_UNIT_MST_1/2_Ver1084.json',
       originalUnitTypeMaster:'2022 F_UNIT_TYPE_MST_Ver52.json',
       formCount:72,typeCount:6,
       baseAndLordMaxEndpointsVerified:true,
       nativeMidlevelGrowthVerified:false,
       typeRollsApplied:false,liveBattleStatsModified:false,
       savedProgressModified:false}),
     slots:freeze(slots)});
 }
 const panel=document.createElement('details');
 panel.id='bf11600-original-lord-stats';
 panel.style.cssText='margin:9px 2px;padding:10px;border:1px solid #8eafa9;'+
   'border-radius:7px;background:#24333d;color:#edf2ef;'+
   'font:12px/1.5 system-ui,sans-serif';
 const title=document.createElement('summary');
 title.textContent='ORIGINAL 2022 UNIT BASE / LORD STATS · 72 FORMS';
 title.style.cssText='min-height:36px;font-weight:800;cursor:pointer';
 const lead=document.createElement('p');
 lead.textContent='Source-verified HP, ATK, DEF and REC at level 1 '+
   'and max-level Lord type. Battle level scaling is still DEMO.';
 const list=document.createElement('div');list.id='bf11600-rows';
 const caution=document.createElement('small');
 caution.textContent='Read-only 2022 F_UNIT_MST reference. No mid-level interpolation, '+
   'unit-type roll, saved EXP, battle stats or rewards are changed. '+
   'Unknown form IDs have no inferred stats.';
 panel.append(title,lead,list,caution);host.after(panel);
 function fmt(stats){
   return 'HP '+stats.hp+' · ATK '+stats.atk+' · DEF '+stats.def+
     ' · REC '+stats.rec;
 }
 function refresh(){
   const current=snapshot();
   list.replaceChildren();
   if(panel.open)for(const slot of current.slots){
     const line=document.createElement('div');
     line.style.cssText='border-top:1px solid #506976;padding:6px 0';
     if(!slot.reference){
       line.textContent='Slot '+(slot.slot+1)+': no source-verified active unit form';
     }else{
       const r=slot.reference;
       const head=document.createElement('b');
       head.textContent='Slot '+(slot.slot+1)+' · #'+r.unitId+
         ' · original max Lv. '+r.maxLevel;
       const base=document.createElement('div');
       base.textContent='Lv. 1: '+fmt(r.base);
       const max=document.createElement('div');
       max.textContent='Lord at max Lv.: '+fmt(r.lordAtMax);
       line.append(head,base,max);
     }
     list.append(line);
   }
   return current;
 }
 panel.addEventListener('toggle',refresh);
 host.addEventListener('click',()=>{if(panel.open)refresh();});
 const timer=setInterval(()=>{if(panel.open&&!document.hidden)refresh();},2500);
 window.addEventListener('pagehide',()=>clearInterval(timer),{once:true});
 window.BFGlobalOriginalLordStatsV11600=freeze({
   source:snapshot().source,lookup,endpoint,snapshot,refresh,
   unitTypesRaw:rawType
 });
 refresh();
})();