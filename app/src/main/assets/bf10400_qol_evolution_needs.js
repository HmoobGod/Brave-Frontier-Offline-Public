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
 function entries(){
   const out=[];
   for(const baseId of P.roster){
     if(!Number.isSafeInteger(baseId))continue;
     const current=effectiveUnit(baseId);
     if(!current||!Number.isSafeInteger(current.id))continue;
     const recipes=evo.sourceRecipes(current.id);
     for(const recipe of recipes){
       if(!Number.isSafeInteger(recipe.target)||!archive.find(recipe.target)||
         !Array.isArray(recipe.materials))continue;
       const needs=new Map();
       for(const raw of recipe.materials){
         if(!Number.isSafeInteger(raw?.id)||raw.id<=0)continue;
         const prior=needs.get(raw.id)||{
           id:raw.id,name:String(raw.name||'').slice(0,80),
           required:0,owned:nonnegative(P.materials?.[raw.id])};
         prior.required++;needs.set(raw.id,prior);
       }
       const materials=[...needs.values()].map(item=>freeze({
         ...item,missing:Math.max(0,item.required-item.owned)
       }));
       out.push(freeze({baseId,from:current.id,to:recipe.target,
         fromName:String(archive.find(current.id)?.name||current.name||'Unit'),
         toName:String(archive.find(recipe.target)?.name||'Unit #'+recipe.target),
         archivedZel:nonnegative(recipe.zel),archivedKarma:nonnegative(recipe.karma),
         materials:freeze(materials),
         missingCount:materials.reduce((n,item)=>n+item.missing,0)}));
     }
   }
   return freeze(out);
 }
 function snapshot(){
   const rows=entries();
   return freeze({ownedBases:P.roster.length,recordedPaths:rows.length,
     readyMaterialPaths:rows.filter(x=>x.missingCount===0).length,
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
 const results=document.createElement('div');results.id='bf10400-rows';
 const note=document.createElement('small');
 note.textContent='Reference only: exact recovered 2022 recipe entries compared with DEMO '+
   'catalyst inventory. Original drop locations, native evolution costs and '+
   'unrecovered recipe links are not inferred. Nothing is consumed or saved.';
 panel.append(heading,status,results,note);host.after(panel);
 let previous='';
 function refresh(){
   const s=snapshot();
   const signature=JSON.stringify({open:panel.open,paths:s.paths});
   if(signature===previous)return s;
   previous=signature;
   status.textContent=s.recordedPaths+' source-listed next-form recipes · '+
     s.readyMaterialPaths+' with all archived material IDs present in demo inventory';
   results.replaceChildren();
   if(!panel.open)return s;
   for(const row of s.paths.slice(0,72)){
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
 document.querySelector('.bf-navbar')?.addEventListener('click',()=>{
   if(panel.open)refresh();
 });
 const timer=setInterval(()=>{if(panel.open&&!document.hidden)refresh()},2000);
 window.addEventListener('pagehide',()=>clearInterval(timer),{once:true});
 refresh();
 window.BFGlobalQoLEvolutionNeedsV10400=freeze({snapshot,refresh});
})();
