/* BF_GLOBAL_ORIGINAL_UNIT_LEVEL_CAPS_V11400 */
(() => {
 'use strict';
 // The unitMaxLevel values are exact original 2022 Global master fields.
 // EXP-to-level thresholds and interim combat stat growth are still DEMO.
 const leaderCatalog=window.BFGlobalPlayableLeadersV11200;
 if(window.BFGlobalOriginalUnitLevelCapsV11400||!leaderCatalog||
    leaderCatalog.source?.forms!==72||
    typeof leaderCatalog.lookup!=='function'||
    typeof P==='undefined'||P.version!==7||!Array.isArray(P.squad)||
    !Array.isArray(P.roster)||typeof effectiveUnit!=='function'||
    typeof demoLevel!=='function'||typeof S==='undefined')return;
 const mode=document.getElementById('mode');
 const host=document.getElementById('bf11200-playable-leaders')||
   document.getElementById('squadpicker');
 if(!mode||!host)return;
 const freeze=Object.freeze;
 const first=freeze([
   freeze([12,40,60,80,100]),freeze([12,40,60,80,100]),
   freeze([12,40,60,80,100]),freeze([12,40,60,80,100]),
   freeze([30,40,60,80,100]),freeze([30,40,60,80,100])
 ]);
 const second=freeze([30,40,60,80,100]);
 const alternate=freeze([30,40]);
 const maxById=new Map();
 for(let element=1;element<=6;element++){
   for(let i=0;i<5;i++){
     maxById.set(element*10000+11+i,first[element-1][i]);
     maxById.set(element*10000+21+i,second[i]);
   }
   for(let i=0;i<2;i++)maxById.set(element*10000+41+i,alternate[i]);
 }
 if(maxById.size!==72||maxById.get(10011)!==12||
    maxById.get(50011)!==30||maxById.get(10015)!==100||
    maxById.get(60042)!==40||
    [...maxById].some(([id,cap])=>!leaderCatalog.lookup(id)||
      !Number.isSafeInteger(cap)||cap<1||cap>100))return;
 const audits=new WeakMap();
 let cappedBuilders=0,unchangedBuilders=0,rejectedBuilders=0;
 const source=freeze({
   sourceYear:2022,field:'F_UNIT_MST_1/2_Ver1084.json:unitMaxLevel',
   archiveSha256:'69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9',
   forms:72,maxLevelRange:freeze([12,100]),
   demoExpThresholdsUnchanged:true,demoStatGrowthUnchanged:true,
   saveFieldsAdded:0,trainingChanges:false
 });
 function lookup(unitId){
   return Number.isSafeInteger(unitId)?maxById.get(unitId)||null:null;
 }
 function apply(unit,slot){
   if(!unit||typeof unit!=='object'||audits.has(unit)||
      mode.value!=='archive'||!unit.active||
      !Number.isSafeInteger(slot)||slot<0||slot>=6||
      !Number.isSafeInteger(unit.unitId)||!Number.isSafeInteger(unit.baseId)||
      !P.roster.includes(unit.baseId)||P.squad[slot]!==unit.baseId){
     rejectedBuilders++;return unit;
   }
   const row=leaderCatalog.lookup(unit.unitId),cap=lookup(unit.unitId);
   const src=effectiveUnit(unit.baseId);
   if(!row||row.unitId!==unit.unitId||!cap||
      !src||src.id!==unit.unitId||!src.stats||
      !Number.isSafeInteger(unit.level)||unit.level<1||
      unit.level!==demoLevel(P.unitExp?.[unit.baseId])||
      unit.hp!==unit.maxHp||
      !['hp','atk','def','rec'].every(k=>
        Number.isSafeInteger(src.stats[k])&&src.stats[k]>=1)){
     rejectedBuilders++;return unit;
   }
   if(unit.level<=cap){unchangedBuilders++;return unit;}
   const oldGrow=unit.level-1,newGrow=cap-1;
   const rates=freeze({hp:30,atk:12,def:8,rec:6});
   if(unit.hp!==src.stats.hp+oldGrow*rates.hp||
      unit.atk!==src.stats.atk+oldGrow*rates.atk||
      unit.def!==src.stats.def+oldGrow*rates.def||
      unit.rec!==src.stats.rec+oldGrow*rates.rec){
     rejectedBuilders++;return unit;
   }
   const hp=src.stats.hp+newGrow*rates.hp;
   const atk=src.stats.atk+newGrow*rates.atk;
   const def=src.stats.def+newGrow*rates.def;
   const rec=src.stats.rec+newGrow*rates.rec;
   if(![hp,atk,def,rec].every(Number.isSafeInteger)||
      ![hp,atk,def,rec].every(n=>n>=1&&n<=1e9)){
     rejectedBuilders++;return unit;
   }
   const audit=freeze({unitId:unit.unitId,baseId:unit.baseId,slot,
     uncappedDemoLevel:unit.level,originalMaxLevel:cap,
     cappedLevel:cap,originalSourceCap:true,
     experienceChanged:false,demoStatGrowthRetained:true});
   unit.level=cap;unit.maxHp=hp;unit.hp=hp;unit.atk=atk;
   unit.def=def;unit.rec=rec;
   audits.set(unit,audit);cappedBuilders++;
   return unit;
 }
 function snapshot(){
   const rows=(Array.isArray(S.party)?S.party:[])
     .map(u=>audits.get(u)).filter(Boolean);
   return freeze({mode:S.mode,source,squadCappedThisBattle:rows.length,
     cappedBuilders,unchangedBuilders,rejectedBuilders,
     rows:freeze(rows),savedProgressChanged:false});
 }
 const panel=document.createElement('details');
 panel.id='bf11400-original-level-caps';
 panel.style.cssText='padding:10px;margin:9px 2px;border:1px solid #b5bc8f;'+
   'border-radius:6px;background:#263832;color:#f0f5e5;'+
   'font:12px/1.5 system-ui,sans-serif';
 const summary=document.createElement('summary');
 summary.textContent='ORIGINAL 2022 UNIT LEVEL CAPS · 72 FORMS';
 summary.style.cssText='min-height:36px;cursor:pointer;font-weight:800';
 const stats=document.createElement('p');stats.id='bf11400-level-status';
 const list=document.createElement('ul');list.id='bf11400-level-rows';
 const caution=document.createElement('small');
 caution.textContent='Source-verified unitMaxLevel only. Caps apply when NEW '+
   'archive demo battles construct units, before source-verified leader buffs. '+
   'No changes to existing v7 saves or stored Unit EXP. '+
   'DEMO experience thresholds and per-level stat growth are NOT '+
   'original 2022 formulas; training is unchanged.';
 panel.append(summary,stats,list,caution);host.after(panel);
 function refresh(){
   const state=snapshot();panel.hidden=state.mode!=='archive';
   stats.textContent=state.squadCappedThisBattle+
     ' active party members capped to original 2022 unit max levels';
   list.replaceChildren();
   if(panel.open)for(const row of state.rows){
     const li=document.createElement('li');
     li.textContent='Unit #'+row.unitId+' · DEMO level '+
       row.uncappedDemoLevel+' → original cap '+row.originalMaxLevel;
     list.append(li);
   }
   return state;
 }
 panel.addEventListener('toggle',refresh);
 const timer=setInterval(()=>{if(!document.hidden&&panel.open)refresh();},1800);
 window.addEventListener('pagehide',()=>clearInterval(timer),{once:true});
 window.BFGlobalOriginalUnitLevelCapsV11400=freeze({
   source,lookup,apply,snapshot,refresh
 });
 refresh();
})();