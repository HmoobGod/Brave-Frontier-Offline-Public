/* BF_GLOBAL_QOL_EVOLUTION_NEEDS_V10400 */
(() => {
 'use strict';
 // 2022 source recipes are reference evidence, not native drop locations.
 // Current P.materials is the independent DEMO catalyst inventory.
 const evo=window.BFOriginalEvolutionV1000;
 const archive=window.BFGlobalUnitArchive;
 if(window.BFGlobalQoLEvolutionNeedsV10400||!evo||!archive||
   typeof P==='undefined'||P.version!==7||
   typeof effectiveUnit!=='function'||!Array.isArray(P.roster))return;
 const host=document.getElementById('evoinventory');
 if(!host)return;
 const freeze=Object.freeze;
 function nonnegative(n){return Number.isSafeInteger(n)&&n>=0?n:0}
 // Conservative DEMO eligibility preview: never executes evolution or training.
 // A missing/throwing Roadmap is "unknown", not a promise that a unit can evolve.
 function demoCostsReady(baseId,from,to){
   try{
     const plan=window.BF_EvolutionRoadmapV039?.plan?.(baseId);
     if(!plan||plan.complete||plan.unavailable||plan.current?.id!==from||
       plan.target?.id!==to||!Array.isArray(plan.materials)||
       !Number.isSafeInteger(plan.demoZel)||plan.demoZel<0||
       !Number.isSafeInteger(P.zel)||P.zel<plan.demoZel||
       typeof demoLevel!=='function')return false;
     const exp=P.unitExp?.[baseId];
     if(!Number.isSafeInteger(exp)||exp<0||demoLevel(exp)<2)return false;
     return plan.materials.every(item=>Number.isSafeInteger(item.required)&&
       item.required>=0&&Number.isSafeInteger(item.owned)&&
       item.owned>=item.required);
   }catch{return false;}
 }
 function entries(){
   const out=[];
   // A malformed/duplicated roster must not inflate displayed owned recipes.
   const seen=new Set();
   for(const baseId of P.roster){
     if(!Number.isSafeInteger(baseId)||baseId<=0||seen.has(baseId))continue;
     seen.add(baseId);
     let current,recipes;
     try{
       current=effectiveUnit(baseId);
       if(!current||!Number.isSafeInteger(current.id)||current.id<=0)continue;
       recipes=evo.sourceRecipes(current.id);
     }catch(_){continue;}
     if(!Array.isArray(recipes))continue;
     for(const recipe of recipes){
       // Incomplete or corrupt source recipes are UNKNOWN, not material
       // complete. Never silently discard a missing material ID and report
       // a false 0-missing or playable-ready outcome.
       if(!recipe||!Number.isSafeInteger(recipe.target)||recipe.target<=0||
         !Array.isArray(recipe.materials)||!recipe.materials.length||
         recipe.materials.some(raw=>!Number.isSafeInteger(raw?.id)||raw.id<=0))
         continue;
       let target;
       try{target=archive.find(recipe.target);}catch(_){continue;}
       if(!target)continue;
       const needs=new Map();
       for(const raw of recipe.materials){
         const prior=needs.get(raw.id)||{
           id:raw.id,name:String(raw.name||'').slice(0,80),
           required:0,owned:nonnegative(P.materials?.[raw.id])};
         prior.required++;needs.set(raw.id,prior);
       }
       const materials=[...needs.values()].map(item=>freeze({
         ...item,missing:Math.max(0,item.required-item.owned)
       }));
       let origin;
       try{origin=archive.find(current.id);}catch(_){origin=null;}
       out.push(freeze({baseId,from:current.id,to:recipe.target,
         fromName:String(origin?.name||current.name||'Unit'),
         toName:String(target?.name||'Unit #'+recipe.target),
         archivedZel:nonnegative(recipe.zel),archivedKarma:nonnegative(recipe.karma),
         materials:freeze(materials),
         missingCount:materials.reduce((n,item)=>n+item.missing,0),
         demoCostsReady:demoCostsReady(baseId,current.id,recipe.target)}));
     }
   }
   return freeze(out);
 }
 function snapshot(){
   const rows=entries();
   return freeze({ownedBases:new Set(P.roster.filter(id=>
     Number.isSafeInteger(id)&&id>0)).size,recordedPaths:rows.length,
     readyMaterialPaths:rows.filter(x=>x.missingCount===0).length,
     demoCostsReadyPaths:rows.filter(x=>x.demoCostsReady).length,
     paths:rows,source:'2022 original recipe archive; local DEMO material counts',
     changesInventory:false});
 }
 const panel=document.createElement('details');panel.id='bf10400-evolution-needs';
 panel.style.cssText='padding:10px;margin:10px 2px;background:#1b3241;color:#f6eedb;'+
   'border:1px solid #b4a17b;border-radius:6px;font:12px/1.5 system-ui,sans-serif';
 const heading=document.createElement('summary');
 heading.textContent='QoL · OWNED UNIT EVOLUTION MATERIAL NEEDS';
 heading.style.cssText='font-weight:800;cursor:pointer;min-height:36px';
 const status=document.createElement('p');status.id='bf10400-summary';
 const controls=document.createElement('div');
 controls.style.cssText='display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:8px 0';
 const label=document.createElement('label');
 label.textContent='Show paths: ';
 const filter=document.createElement('select');filter.id='bf10400-filter';
 filter.setAttribute('aria-label','Filter owned unit evolution paths');
 filter.style.cssText='min-height:44px;max-width:100%;background:#314f69;color:white;border:1px solid #bca277;border-radius:5px;padding:8px';
 for(const [value,text] of [
   ['all','All recorded paths'],['demo','DEMO costs/level covered'],
   ['materials','All archived materials held'],['missing','Missing archived materials']]){
   const option=document.createElement('option');option.value=value;
   option.textContent=text;filter.append(option);
 }
 label.append(filter);
 const training=document.createElement('button');training.type='button';
 training.id='bf10400-training-shortcut';
 training.textContent='OPEN DEMO TRAINING';
 training.style.cssText='min-height:44px;background:#314f69;color:#fff;border:1px solid #bca277;border-radius:5px;padding:8px';
 controls.append(label,training);
 const results=document.createElement('div');results.id='bf10400-rows';
 const note=document.createElement('small');
 note.textContent='Reference only: exact recovered 2022 recipe entries compared with DEMO '+
   'catalyst inventory. Original drop locations, native evolution costs and '+
   'unrecovered recipe links are not inferred. Material-complete is not a guarantee '+
   'of playable evolution. DEMO readiness requires an exact Roadmap match, '+
   'level 2, demo Zel and materials; final restrictions still apply. '+
   'Invalid or incomplete source recipes are excluded rather than shown '+ 
   'as material-complete. Training only navigates; nothing is consumed or saved.';
 panel.append(heading,status,controls,results,note);host.after(panel);
 let previous='';
 function refresh(){
   const s=snapshot();
   const signature=JSON.stringify({open:panel.open,filter:filter.value,paths:s.paths});
   if(signature===previous)return s;
   previous=signature;
   const visible=s.paths.filter(row=>filter.value==='all'||
     (filter.value==='demo'&&row.demoCostsReady)||
     (filter.value==='materials'&&row.missingCount===0)||
     (filter.value==='missing'&&row.missingCount>0));
   status.textContent=s.recordedPaths+' source-listed next-form recipes · '+
     s.readyMaterialPaths+' with all archived materials · '+
     s.demoCostsReadyPaths+' appear DEMO level/cost ready · '+visible.length+' shown';
   results.replaceChildren();
   if(!panel.open)return s;
   if(!visible.length){
     const empty=document.createElement('p');
     empty.textContent='No recorded evolution paths match this filter.';
     results.append(empty);
   }
   for(const row of visible.slice(0,72)){
     const block=document.createElement('div');
     block.style.cssText='border-top:1px solid #687d89;padding:7px 0';
     const title=document.createElement('strong');
     title.textContent=row.fromName+' → '+row.toName+
       ' · '+row.missingCount+' missing (DEMO inventory)';
     block.append(title);
     const cost=document.createElement('small');
     cost.textContent='Recorded original reference · '+row.archivedZel+
       ' Zel · '+row.archivedKarma+' Karma';
     block.append(cost);
     for(const mat of row.materials){
       const line=document.createElement('div');
       line.textContent=(mat.name||'Material')+' #'+mat.id+
         ' · '+mat.owned+'/'+mat.required+' held · '+mat.missing+' missing';
       block.append(line);
     }
     results.append(block);
   }
   return s;
 }
 panel.addEventListener('toggle',()=>{previous='';refresh()});
 filter.addEventListener('change',()=>{previous='';refresh()});
 training.addEventListener('click',()=>{
   try{
     if(window.BF_homeNav?.go?.('units')===false)return;
     window.BFInnerScreens?.setTab?.('training');
   }catch{/* Optional navigation may not be mounted; never spend resources. */}
 });
 document.querySelector('.bf-navbar')?.addEventListener('click',()=>{
   if(panel.open)refresh();
 });
 const timer=setInterval(()=>{if(panel.open&&!document.hidden)refresh()},2000);
 window.addEventListener('pagehide',()=>clearInterval(timer),{once:true});
 refresh();
 window.BFGlobalQoLEvolutionNeedsV10400=freeze({snapshot,refresh});
})();
