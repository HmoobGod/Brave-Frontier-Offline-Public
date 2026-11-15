/* BF_GLOBAL_ORIGINAL_UNIT_LEVEL_CAPS_V11500 */
(() => {
 'use strict';
 // The unitMaxLevel values are exact original 2022 Global master fields.
 // EXP-to-level thresholds and interim combat stat growth are still DEMO.
 const leaderCatalog=window.BFGlobalPlayableLeadersV11200;
 if(window.BFGlobalOriginalUnitLevelCapsV11500||!leaderCatalog||
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
 panel.id='bf11300-original-level-caps';
 panel.style.cssText='padding:10px;margin:9px 2px;border:1px solid #b5bc8f;'+
   'border-radius:6px;background:#263832;color:#f0f5e5;'+
   'font:12px/1.5 system-ui,sans-serif';
 const summary=document.createElement('summary');
 summary.textContent='ORIGINAL 2022 UNIT LEVEL CAPS · 72 FORMS';
 summary.style.cssText='min-height:36px;cursor:pointer;font-weight:800';
 const stats=document.createElement('p');stats.id='bf11300-level-status';
 const list=document.createElement('ul');list.id='bf11300-level-rows';
 const caution=document.createElement('small');
 caution.textContent='Source-verified unitMaxLevel only. Caps apply when NEW '+
   'archive demo battles construct units, before source-verified leader buffs. '+
   'No changes to existing v7 saves or stored Unit EXP. '+
   'DEMO experience thresholds and per-level stat growth are NOT '+
   'original 2022 formulas; training is unchanged.';
 const squadTitle=document.createElement('h4');
 squadTitle.textContent='CURRENT SQUAD · ORIGINAL MAX LEVEL REFERENCE';
 squadTitle.style.cssText='margin:10px 0 4px;font-size:13px';
 const squadPreview=document.createElement('ul');
 squadPreview.id='bf11300-squad-cap-preview';
 squadPreview.setAttribute('aria-label','Current squad original level caps');
 const squadNote=document.createElement('small');
 squadNote.textContent='Read-only: shows DEMO training level against the original 2022 max-level field. No EXP, training, roster or save changes.';
 panel.append(summary,stats,list,squadTitle,squadPreview,squadNote,caution);host.after(panel);
 // Home is a read-only comparison, never original EXP/growth evidence.
 function homePreview(){
   try{
     if(P.version!==7||!Array.isArray(P.squad)||P.squad.length>6||
        !Array.isArray(P.roster)||!P.unitExp||typeof P.unitExp!=='object'||
        Array.isArray(P.unitExp)||
        ![Object.prototype,null].includes(Object.getPrototypeOf(P.unitExp)))return null;
     const seen=new Set();let below=0,at=0,above=0,unknown=0;
     for(const baseId of Array.from(P.squad)){
       if(!Number.isSafeInteger(baseId)||baseId<=0||seen.has(baseId)||
          !P.roster.includes(baseId))return null;
       seen.add(baseId);
       const raw=P.unitExp[baseId];
       if(raw!==undefined&&(!Number.isSafeInteger(raw)||raw<0))return null;
       const unit=effectiveUnit(baseId);
       if(!unit||!Number.isSafeInteger(unit.id)||unit.id<=0)return null;
       const cap=lookup(unit.id),level=demoLevel(raw??0);
       if(!Number.isSafeInteger(level)||level<1)return null;
       if(!cap){unknown++;continue;}
       if(level<cap)below++;else if(level===cap)at++;else above++;
     }
     return freeze({count:P.squad.length,below,at,above,unknown,
       complete:unknown===0,sourceYear:2022,demoTraining:true});
   }catch(_){return null;}
 }
 let homeLevel=null;
 function refreshHome(){
   const party=document.querySelector('#bf-home #bf-scene-party');
   if(!party)return;
   if(!homeLevel||!homeLevel.isConnected){
     homeLevel=document.createElement('p');homeLevel.id='bf11500-home-level-reference';
     homeLevel.setAttribute('role','status');homeLevel.setAttribute('aria-live','polite');
     homeLevel.setAttribute('aria-label','DEMO squad training compared with original 2022 level caps');
     homeLevel.style.cssText='box-sizing:border-box;max-width:100%;margin:7px 0;'+
       'font:12px/1.5 system-ui,sans-serif;overflow-wrap:anywhere';
     party.after(homeLevel);
   }
   const s=homePreview();
   const text=!s?'SQUAD LEVEL REFERENCE · unavailable (invalid squad or EXP).':
     !s.count?'SQUAD LEVEL REFERENCE · no squad units selected.':
     !s.complete?'SQUAD LEVEL REFERENCE · unavailable for '+s.unknown+' of '+s.count+' forms.':
     'DEMO TRAINING vs 2022 CAPS · '+s.below+' below · '+s.at+' at · '+s.above+' above'+
       ' · Original EXP/growth not restored.';
   if(homeLevel.textContent!==text)homeLevel.textContent=text;
 }
 function refresh(){
   refreshHome();
   const state=snapshot();panel.hidden=state.mode!=='archive';
   stats.textContent=state.squadCappedThisBattle+
     ' active party members capped to original 2022 unit max levels';
   list.replaceChildren();
   squadPreview.replaceChildren();
   if(panel.open){
     let occupied=0;
     for(let slot=0;slot<Math.min(6,P.squad.length);slot++){
       const baseId=P.squad[slot];
       if(!Number.isSafeInteger(baseId)||!P.roster.includes(baseId))continue;
       const unit=effectiveUnit(baseId);
       if(!unit||!Number.isSafeInteger(unit.id))continue;
       const cap=lookup(unit.id);
       if(!cap)continue;
       const level=demoLevel(P.unitExp?.[baseId]);
       if(!Number.isSafeInteger(level)||level<1)continue;
       const li=document.createElement('li');
       li.textContent='Slot '+(slot+1)+' · Unit #'+unit.id+
         ' · DEMO level '+level+' / original cap '+cap+
         (level>=cap?' · at/above source cap':' · below source cap');
       squadPreview.append(li);occupied++;
     }
     if(!occupied){
       const li=document.createElement('li');
       li.textContent='No eligible owned squad forms to preview.';
       squadPreview.append(li);
     }
   }
   if(panel.open)for(const row of state.rows){
     const li=document.createElement('li');
     li.textContent='Unit #'+row.unitId+' · DEMO level '+
       row.uncappedDemoLevel+' → original cap '+row.originalMaxLevel;
     list.append(li);
   }
   return state;
 }
 panel.addEventListener('toggle',refresh);
 window.addEventListener('bf-route-sync',refreshHome);
 const timer=setInterval(()=>{
   if(document.hidden)return;
   if(panel.open)refresh();
   else if(window.BF_homeNav?.current==='home')refreshHome();
 },1800);
 window.addEventListener('pagehide',()=>clearInterval(timer),{once:true});
 window.BFGlobalOriginalUnitLevelCapsV11500=freeze({
   source,lookup,apply,snapshot,refresh,homePreview
 });
 refresh();
})();