/* BF_GLOBAL_BATCH_DRAFT_EVOLUTION_V1700 */
(() => {
 'use strict';
 if(window.BFGlobalBatchDraftEvolutionV1700 ||
   !window.BFGlobalDraftEvolutionV1600 ||
   !window.BFEvolutionMaterialPlannerV1400 ||
   !window.BFArchiveDraftV800 || !window.BFTacticalRoundsV300 ||
   !window.BFOriginalEvolutionV1000 || !window.BFGlobalUnitArchive ||
   typeof P==='undefined' || P?.version!==7)return;
 const evolution=window.BFGlobalDraftEvolutionV1600;
 const planner=window.BFEvolutionMaterialPlannerV1400;
 const draft=window.BFArchiveDraftV800;
 const trial=window.BFTacticalRoundsV300;
 const source=window.BFOriginalEvolutionV1000;
 const archive=window.BFGlobalUnitArchive;
 const anchor=document.getElementById('bf1600-draft-evolution');
 if(!anchor||archive.count!==2291)return;
 const ready=()=>trial.snapshot===null&&!(typeof S!=='undefined'&&S?.busy);
 const name=id=>archive.find(id)?.name||('#'+id);
 let batches=[];
 const clone=row=>JSON.parse(JSON.stringify(row));
 function assess(){
   const p=planner.plan,selected=new Set(draft.selected);
   const targets=new Set(),issues=[],rows=[];
   for(const entry of p.entries){
     if(!selected.has(entry.from)||selected.has(entry.to)){
       issues.push('Destination '+name(entry.to)+' is already in the temporary squad or source is absent.');
       continue;
     }
     if(targets.has(entry.to)){
       issues.push('Multiple forms would evolve into '+name(entry.to)+'.');
       continue;
     }
     const available=evolution.available(entry.from);
     const route=evolutionRoute(entry.from,entry.to);
     const archived=source.sourceRecipe(entry.from,entry.to);
     if(!available.some(x=>x.id===entry.to)||
       !route||route.steps.length!==1||!archived||
       archived.zel!==entry.zel||archived.karma!==entry.karma||
       JSON.stringify(archived.materials)!==JSON.stringify(entry.materials)){
       issues.push('No eligible single-stage source recipe: '+
         name(entry.from)+' → '+name(entry.to)+'.');
       continue;
     }
     targets.add(entry.to);
     rows.push({from:entry.from,to:entry.to,
       fromName:entry.fromName,toName:entry.toName,
       zel:entry.zel,karma:entry.karma,
       materials:entry.materials.map(x=>({...x}))});
   }
   const groups=new Map(),totals={zel:0,karma:0,materials:[]};
   for(const row of rows){
     totals.zel+=row.zel||0;totals.karma+=row.karma||0;
     for(const m of row.materials){
       const k=String(m.type)+':'+String(m.id);
       if(groups.has(k))groups.get(k).count++;
       else groups.set(k,{id:m.id,type:m.type,name:m.name||'',count:1});
     }
   }
   totals.materials=[...groups.values()].sort((a,b)=>
     String(a.type).localeCompare(String(b.type))||Number(a.id)-Number(b.id));
   return {selected:p.selected.slice(),entries:rows,missing:p.missing.slice(),
     issues,totals,ready:ready()&&rows.length>0&&issues.length===0};
 }
 // Independently pin each route to v16's already-strict source validation.
 function evolutionRoute(from,to){
   const available=evolution.available(from);
   if(!available.some(r=>r.id===to&&r.steps===1))return null;
   const r=window.BFGlobalEvolutionChainV1500?.findRoute(from,to,1);
   return r?.steps.length===1?r:null;
 }
 function canUndo(){
   if(!ready()||!batches.length)return false;
   const rows=batches.at(-1).entries,actual=evolution.history;
   if(actual.length<rows.length)return false;
   const tail=actual.slice(-rows.length);
   return rows.every((row,i)=>tail[i].from===row.from&&
     tail[i].to===row.to&&draft.selected.includes(row.to)&&
     !draft.selected.includes(row.from));
 }
 function apply(){
   const result=assess();
   if(!result.ready)return false;
   const before=draft.selected.slice();
   const depth=evolution.history.length;
   let applied=0;
   for(const row of result.entries){
     if(!evolution.evolve(row.from,row.to))break;
     applied++;
   }
   if(applied!==result.entries.length){
     for(let i=0;i<applied;i++)evolution.undo();
     if(draft.selected.some((id,i)=>id!==before[i])||
       evolution.history.length!==depth)
       throw new Error('Batch source trial rollback invariant failed.');
     refresh();return false;
   }
   const item={entries:result.entries.map(x=>clone(x)),
     totals:clone(result.totals),originalSlots:before};
   batches.push(item);
   if(batches.length>10)batches.shift();
   refresh();return true;
 }
 function undoBatch(){
   if(!canUndo())return false;
   const batch=batches.at(-1);
   for(let i=batch.entries.length-1;i>=0;i--){
     if(!evolution.undo())
       throw new Error('Verified batch trial undo invariant failed.');
   }
   batches.pop();refresh();return true;
 }
 const css=document.createElement('style');css.id='bf1700-batch-style';
 css.textContent=[
   '#bf1700-batch{padding:10px;margin:8px 0;background:#1b344a;',
   'border:1px solid #c2a476;border-radius:7px;color:#f4e9d4;',
   'font:12px/1.5 system-ui,sans-serif}',
   '#bf1700-batch>summary{font:bold 14px Georgia,serif;',
   'cursor:pointer;min-height:36px}',
   '#bf1700-batch button{min-height:41px;margin:4px 0;',
   'width:100%;border-radius:5px;padding:7px;',
   'background:#31516b;color:#fff;border:1px solid #bda780}',
   '#bf1700-batch button:disabled{opacity:.45}',
   '.bf1700-card{background:#2a445b;border-radius:6px;',
   'padding:8px;margin:6px 0;overflow-wrap:anywhere}',
   '.bf1700-note{color:#ffe0b0}'
 ].join('');
 document.head.append(css);
 const panel=document.createElement('details');panel.id='bf1700-batch';
 const header=document.createElement('summary');
 header.textContent='EVOLVE MULTIPLE TEMPORARY FORMS · v17.00';
 const caution=document.createElement('p');caution.className='bf1700-note';
 caution.textContent='OPTIONAL SOURCE-RECIPE TRAINING. Select one original 2022 recipe per drafted form in the v14 materials planner, or auto-fill below. Only fully documented, eligible, nonduplicate single-stage evolutions can be applied. All original costs are previews, never real spending.';
 const auto=document.createElement('button');auto.id='bf1700-auto';auto.type='button';
 auto.textContent='AUTO-SELECT MISSING SOURCE RECIPES';
 const refreshBtn=document.createElement('button');
 refreshBtn.id='bf1700-refresh';refreshBtn.type='button';
 refreshBtn.textContent='REFRESH SOURCE RECIPE PLAN';
 const state=document.createElement('div');state.id='bf1700-plan';
 const applyBtn=document.createElement('button');applyBtn.id='bf1700-apply';
 applyBtn.type='button';applyBtn.textContent='APPLY TEMPORARY BATCH EVOLUTION';
 const undoBtn=document.createElement('button');undoBtn.id='bf1700-undo';
 undoBtn.type='button';undoBtn.textContent='UNDO LAST TEMPORARY BATCH';
 const log=document.createElement('p');log.id='bf1700-log';
 panel.append(header,caution,auto,refreshBtn,state,applyBtn,undoBtn,log);
 anchor.after(panel);
 const dom=(tag,value)=>{const el=document.createElement(tag);el.textContent=value;return el;};
 function refresh(){
   const p=assess();
   state.replaceChildren();
   state.append(dom('strong','DOCUMENTED 2022 GLOBAL SOURCE PLAN · '+
     p.entries.length+' valid of '+p.selected.length+' temporary draft forms'));
   state.append(dom('p','Recorded preview cost: '+p.totals.zel+
     ' Zel · '+p.totals.karma+' Karma · no game resources spent'));
   for(const row of p.entries){
     const card=dom('div',row.fromName+' (#'+row.from+') → '+
       row.toName+' (#'+row.to+') · '+row.zel+' Zel');
     card.className='bf1700-card';state.append(card);
   }
   for(const m of p.totals.materials){
     const card=dom('div',(m.name||'Source material')+' · #'+m.id+
       ' (type '+m.type+') ×'+m.count);
     card.className='bf1700-card';state.append(card);
   }
   if(p.missing.length)
     state.append(dom('p',p.missing.length+' form(s) have no selected source recipe: '+
       p.missing.map(name).join(', ')+'. Those forms stay unchanged.'));
   for(const err of p.issues){
     const warning=dom('p',err);warning.className='bf1700-note';
     state.append(warning);
   }
   applyBtn.textContent='EVOLVE '+p.entries.length+' PLANNED TEMPORARY FORM(S)';
   applyBtn.disabled=!p.ready;
   undoBtn.disabled=!canUndo();
   log.textContent=!ready()?'Exit the active trial before changing any draft forms.':
     batches.length+' reversible batch(es) in this session · no game save writes.';
   return clone(p);
 }
 auto.addEventListener('click',()=>{planner.autoSelect();refresh();});
 refreshBtn.addEventListener('click',refresh);
 applyBtn.addEventListener('click',apply);
 undoBtn.addEventListener('click',undoBatch);
 panel.addEventListener('toggle',()=>{if(panel.open)refresh();});
 // Live-refresh the batch preview when a recipe is changed in the source
 // material planner, without changing any saved or temporary choices.
 document.getElementById('bf1400-material-planner')?.addEventListener('change',()=>{
   if(panel.open)refresh();
 });
 document.querySelector('.bf-navbar')?.addEventListener('click',()=>{if(panel.open)refresh();});
 refresh();
 window.BFGlobalBatchDraftEvolutionV1700=Object.freeze({
   get preview(){return clone(assess());},
   get history(){return batches.map(row=>clone(row));},
   apply,undo:undoBatch,canUndo,refresh
 });
})();
