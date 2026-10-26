/* BF_GLOBAL_MULTISTAGE_DRAFT_BATCH_V1800 */
(() => {
 'use strict';
 if(window.BFGlobalMultistageDraftV1800 ||
   !window.BFGlobalDraftEvolutionV1600 ||
   !window.BFGlobalBatchDraftEvolutionV1700 ||
   !window.BFGlobalEvolutionChainV1500 ||
   !window.BFOriginalEvolutionV1000 || !window.BFArchiveDraftV800 ||
   !window.BFGlobalUnitArchive || !window.BFTacticalRoundsV300 ||
   typeof P==='undefined'||P?.version!==7)return;
 const evo=window.BFGlobalDraftEvolutionV1600;
 const olderBatch=window.BFGlobalBatchDraftEvolutionV1700;
 const routes=window.BFGlobalEvolutionChainV1500;
 const recipes=window.BFOriginalEvolutionV1000;
 const draft=window.BFArchiveDraftV800;
 const catalog=window.BFGlobalUnitArchive;
 const trial=window.BFTacticalRoundsV300;
 const anchor=document.getElementById('bf1700-batch');
 if(!anchor||catalog.count!==2291||routes.sourceHopCount<100)return;
 const planned=new Map(),history=[];
 let reportState='';
 const safeCopy=x=>JSON.parse(JSON.stringify(x));
 const label=id=>catalog.find(id)?.name||'#'+id;
 const eligible=id=>Number.isInteger(id)&&draft.eligible(id)&&!!catalog.find(id);
 const idle=()=>trial.snapshot===null&&!(typeof S!=='undefined'&&S?.busy);
 const originalFormRows=()=>draft.selected.filter(eligible);
 function route(from,to){
   if(!eligible(from)||!eligible(to)||from===to)return null;
   const r=routes.findRoute(from,to,12);
   if(!r||r.steps.length<2||r.steps.length>12||
     r.path.length!==r.steps.length+1 ||
     r.path[0]!==from||r.path.at(-1)!==to)return null;
   // All intermediate 2022 forms must be positively measured standard forms,
   // with exact recipe presence, source currency values and each material line.
   for(let i=0;i<r.steps.length;i++){
     const hop=r.steps[i];
     if(!eligible(hop.from)||!eligible(hop.to)||
       hop.from!==r.path[i]||hop.to!==r.path[i+1])return null;
     const original=recipes.sourceRecipe(hop.from,hop.to);
     if(!original||original.zel!==hop.zel||original.karma!==hop.karma||
       JSON.stringify(original.materials)!==JSON.stringify(hop.materials))
       return null;
   }
   return r;
 }
 function destinations(from){
   if(!eligible(from)||!draft.selected.includes(from))return [];
   const owned=new Set(draft.selected);
   return routes.reachable(from,12,500).filter(row=>
     row.steps>=2 && !owned.has(row.id) && eligible(row.id) &&
     route(from,row.id)!==null);
 }
 function prune(){
   const kept=new Set(originalFormRows());
   for(const [from,to] of planned){
     if(!kept.has(from)||!destinations(from).some(x=>x.id===to))
       planned.delete(from);
   }
 }
 function choose(from,to){
   if(!Number.isInteger(from)||!Number.isInteger(to)||
      !originalFormRows().includes(from)||
      !destinations(from).some(x=>x.id===to))return false;
   planned.set(from,to);refresh();return true;
 }
 function clear(from){
   if(!Number.isInteger(from)||!planned.delete(from))return false;
   refresh();return true;
 }
 function clearAll(){planned.clear();refresh();return true;}
 function autoSelect(){
   prune();
   const taken=new Set([...originalFormRows(),...planned.values()]);
   let added=0;
   for(const from of originalFormRows()){
     if(planned.has(from))continue;
     const choices=destinations(from).sort((a,b)=>b.steps-a.steps||a.id-b.id);
     const found=choices.find(r=>!taken.has(r.id));
     if(!found)continue;
     planned.set(from,found.id);taken.add(found.id);added++;
   }
   refresh();return added;
 }
 function analyze(){
   prune();
   const entries=[],issues=[],missing=[],destSet=new Set(),materials=new Map();
   const totals={zel:0,karma:0,materials:[]};
   const forms=originalFormRows();
   for(const from of forms){
     const to=planned.get(from);
     if(to===undefined){missing.push(from);continue;}
     if(forms.includes(to)||destSet.has(to)){
       issues.push('Duplicate or already drafted destination '+label(to));
       continue;
     }
     const sourceRoute=route(from,to);
     if(!sourceRoute){
       issues.push('Undocumented or ineligible original recipe path '+label(from)+' → '+label(to));
       continue;
     }
     destSet.add(to);
     entries.push({from,to,steps:sourceRoute.steps.length,
       path:sourceRoute.path.slice(),
       fromName:label(from),toName:label(to),
       cost:safeCopy(sourceRoute.totals)});
     totals.zel+=sourceRoute.totals.zel;
     totals.karma+=sourceRoute.totals.karma;
     for(const m of sourceRoute.totals.materials){
       const key=String(m.type)+':'+String(m.id);
       if(materials.has(key))materials.get(key).count+=m.count;
       else materials.set(key,{id:m.id,type:m.type,name:m.name||'',count:m.count});
     }
   }
   totals.materials=[...materials.values()].sort((a,b)=>
     String(a.type).localeCompare(String(b.type))||Number(a.id)-Number(b.id));
   const currentUndoDepth=evo.history.length;
   if(currentUndoDepth+entries.length>20)
     issues.push('Undo capacity: complete or reverse earlier temporary evolutions first.');
   if(olderBatch.history.length)
     issues.push('Undo earlier single-stage batches before applying multi-stage routes.');
   const valid=entries.length>0&&issues.length===0;
   return {sourceYear:2022,selected:forms,entries,missing,issues,
     totals,ready:valid&&idle(),undoCapacity:20-currentUndoDepth};
 }
 function canUndo(){
   if(!idle()||!history.length)return false;
   const last=history.at(-1),tail=evo.history.slice(-last.entries.length);
   if(tail.length!==last.entries.length)return false;
   return last.entries.every((e,i)=>tail[i].from===e.from&&
     tail[i].to===e.to&&draft.selected.includes(e.to)&&
     !draft.selected.includes(e.from));
 }
 function apply(){
   const p=analyze();
   if(!p.ready)return false;
   const before=draft.selected.slice(),depth=evo.history.length;
   let count=0;
   for(const entry of p.entries){
     if(!evo.evolve(entry.from,entry.to))break;
     count++;
   }
   if(count!==p.entries.length){
     for(let i=count-1;i>=0;i--){
       if(!evo.undo())throw new Error('Temporary evolution rollback failed');
     }
     if(depth!==evo.history.length||
       draft.selected.some((id,i)=>id!==before[i]))
       throw new Error('Temporary multi-stage batch mutation was not reversed');
     refresh();return false;
   }
   history.push({entries:safeCopy(p.entries),totals:safeCopy(p.totals),
     originalSlots:before});
   if(history.length>4)history.shift();
   planned.clear();
   reportState='Advanced '+count+' temporary forms using source-verified multi-stage routes.';
   refresh();return true;
 }
 function undo(){
   if(!canUndo())return false;
   const last=history.at(-1);
   for(let i=last.entries.length-1;i>=0;i--){
     if(!evo.undo())throw new Error('Multi-stage batch undo invariant failed');
   }
   if(draft.selected.some((x,i)=>x!==last.originalSlots[i]))
     throw new Error('Undo failed to restore original temporary draft order');
   history.pop();reportState='Restored the original temporary squad forms and slots.';
   refresh();return true;
 }
 const css=document.createElement('style');css.id='bf1800-multistage-style';
 css.textContent=[
   '#bf1800-multistage{margin:8px 0;padding:11px;background:#1a334a;',
   'border:1px solid #bca17b;border-radius:7px;color:#f2e5cf;',
   'font:12px/1.55 system-ui,sans-serif}',
   '#bf1800-multistage>summary{font:bold 14px Georgia,serif;',
   'min-height:40px;cursor:pointer}',
   '#bf1800-multistage select,#bf1800-multistage button{',
   'width:100%;min-height:40px;box-sizing:border-box;margin:4px 0;',
   'border-radius:5px;background:#31516c;color:#fff;',
   'border:1px solid #b9a27b;padding:7px}',
   '#bf1800-multistage button:disabled{opacity:.45}',
   '.bf1800-entry{background:#294257;padding:8px;',
   'border-radius:6px;margin:7px 0}',
   '.bf1800-entry strong{display:block}',
   '.bf1800-warn{color:#ffdda6}'
 ].join('');
 document.head.append(css);
 const panel=document.createElement('details');panel.id='bf1800-multistage';
 const title=document.createElement('summary');
 title.textContent='MULTI-STAGE EVOLUTION SQUAD · v18.00';
 const caution=document.createElement('p');caution.className='bf1800-warn';
 caution.textContent='ORIGINAL 2022 RECIPE PATHS, EXPERIMENTAL DRAFT ONLY. Every intermediate archived form must have a documented eligible source recipe. No real evolutions, materials, Zel or Karma are spent, and real unit levels/saves stay unchanged.';
 const autoBtn=document.createElement('button');autoBtn.type='button';
 autoBtn.id='bf1800-auto';autoBtn.textContent='AUTO-PLAN FARTHEST DOCUMENTED ROUTES';
 const clearBtn=document.createElement('button');clearBtn.type='button';
 clearBtn.id='bf1800-clear';clearBtn.textContent='CLEAR ROUTE CHOICES';
 const updateBtn=document.createElement('button');updateBtn.type='button';
 updateBtn.id='bf1800-refresh';updateBtn.textContent='REFRESH SOURCE PATHS';
 const entriesView=document.createElement('div');entriesView.id='bf1800-entries';
 const totalsView=document.createElement('div');totalsView.id='bf1800-total';
 const runBtn=document.createElement('button');runBtn.type='button';
 runBtn.id='bf1800-apply';runBtn.textContent='APPLY VERIFIED ROUTE BATCH';
 const undoBtn=document.createElement('button');undoBtn.type='button';
 undoBtn.id='bf1800-undo';undoBtn.textContent='UNDO LAST MULTI-STAGE BATCH';
 const status=document.createElement('p');status.id='bf1800-status';
 panel.append(title,caution,autoBtn,clearBtn,updateBtn,entriesView,totalsView,
   runBtn,undoBtn,status);
 anchor.after(panel);
 const node=(tag,txt)=>{const d=document.createElement(tag);d.textContent=txt;return d;};
 function refresh(){
   const p=analyze();
   entriesView.replaceChildren();
   for(const from of p.selected){
     const row=document.createElement('div');row.className='bf1800-entry';
     row.append(node('strong',label(from)+' · #'+from+' · ORIGINAL 2022'));
     const select=document.createElement('select');
     select.dataset.from=String(from);
     select.setAttribute('aria-label','Multi-stage route for '+label(from));
     const none=document.createElement('option');none.value='';
     none.textContent='Keep original temporary form';select.append(none);
     for(const d of destinations(from)){
       const opt=document.createElement('option');opt.value=String(d.id);
       opt.textContent=label(d.id)+' · #'+d.id+' · '+d.steps+' source stages';
       select.append(opt);
     }
     select.value=planned.has(from)?String(planned.get(from)):'';
     select.addEventListener('change',()=>{
       if(!select.value)clear(from);
       else choose(from,Number(select.value));
     });
     row.append(select);entriesView.append(row);
   }
   totalsView.replaceChildren();
   totalsView.append(node('strong',p.entries.length+' multi-stage source route(s) · '+
     p.totals.zel+' archived Zel · '+p.totals.karma+' archived Karma'));
   for(const e of p.entries){
     const card=node('div',e.path.map(label).join(' → ')+' · '+
       e.steps+' recipe stages');card.className='bf1800-entry';
     totalsView.append(card);
   }
   for(const mat of p.totals.materials){
     const card=node('div',(mat.name||'Original source material')+' · #'+
       mat.id+' (type '+mat.type+') ×'+mat.count);
     card.className='bf1800-entry';totalsView.append(card);
   }
   for(const msg of p.issues){
     const warning=node('p',msg);warning.className='bf1800-warn';
     totalsView.append(warning);
   }
   runBtn.disabled=!p.ready;
   undoBtn.disabled=!canUndo();
   status.textContent=!idle()?'Exit active training to edit temporary forms.':
     reportState||('No original resources spent. '+
       history.length+' reversible multi-stage batch(es) in this session.');
   return safeCopy(p);
 }
 autoBtn.addEventListener('click',autoSelect);
 clearBtn.addEventListener('click',clearAll);
 updateBtn.addEventListener('click',refresh);
 runBtn.addEventListener('click',apply);
 undoBtn.addEventListener('click',undo);
 panel.addEventListener('toggle',()=>{if(panel.open)refresh();});
 document.querySelector('.bf-navbar')?.addEventListener('click',()=>{
   if(panel.open)refresh();
 });
 refresh();
 window.BFGlobalMultistageDraftV1800=Object.freeze({
   get preview(){return safeCopy(analyze());},
   get history(){return safeCopy(history);},
   destinations:from=>safeCopy(destinations(from)),
   choose,clear,clearAll,autoSelect,apply,undo,canUndo,refresh
 });
})();
