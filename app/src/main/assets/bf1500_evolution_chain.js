/* BF_GLOBAL_EVOLUTION_CHAIN_V1500 */
(() => {
 'use strict';
 if(window.BFGlobalEvolutionChainV1500 ||
    !window.BFOriginalEvolutionV1000 || !window.BFEvolutionMaterialPlannerV1400 ||
    !window.BFArchiveDraftV800 || !window.BFGlobalUnitArchive ||
    typeof P==='undefined'||P?.version!==7)return;
 const evo=window.BFOriginalEvolutionV1000;
 const draft=window.BFArchiveDraftV800;
 const catalog=window.BFGlobalUnitArchive;
 const anchor=document.getElementById('bf1400-material-planner');
 if(!anchor||catalog.count!==2291||evo.formCount!==2291)return;
 // Every hop must have a real source-listed recipe and a matching 2022 unit ID.
 // Evolution links without recovered recipe contents are deliberately excluded.
 const byFrom=new Map();
 let sourceHopCount=0;
 const idExists=id=>Number.isInteger(id)&&catalog.find(id)!==null;
 for(const id of JSON.parse(document.getElementById('bf-global-unit-catalog-data').textContent).units.map(x=>x.id)){
   const rows=evo.sourceRecipes(id).filter(r=>idExists(r.target));
   byFrom.set(id,rows);
   sourceHopCount+=rows.length;
 }
 const getRows=id=>byFrom.get(id)||[];
 const copyRecipe=(from,r)=>({
   from,to:r.target,
   fromName:catalog.find(from)?.name||'Unknown original form',
   toName:catalog.find(r.target)?.name||'Unknown original form',
   zel:r.zel,karma:r.karma,
   materials:r.materials.map(mat=>({...mat}))
 });
 function aggregate(rows){
   const totals={zel:0,karma:0,materials:[]},counts=new Map();
   for(const row of rows){
     totals.zel+=row.zel||0;totals.karma+=row.karma||0;
     for(const mat of row.materials){
       const key=String(mat.type)+':'+String(mat.id);
       if(counts.has(key))counts.get(key).count++;
       else counts.set(key,{id:mat.id,type:mat.type,
         name:mat.name||'',count:1});
     }
   }
   totals.materials=[...counts.values()].sort((a,b)=>
     String(a.type).localeCompare(String(b.type))||Number(a.id)-Number(b.id));
   return totals;
 }
 function findRoute(from,to,maxDepth=12){
   if(!idExists(from)||!idExists(to)||!Number.isInteger(maxDepth)||
      maxDepth<0||maxDepth>12)return null;
   if(from===to)return {from,to,path:[from],steps:[],
     totals:{zel:0,karma:0,materials:[]},sourceYear:2022};
   const seen=new Set([from]),queue=[{id:from,path:[from],steps:[]}];
   for(let front=0;front<queue.length;front++){
     const current=queue[front];
     if(current.steps.length>=maxDepth)continue;
     for(const record of getRows(current.id)){
       const child=record.target;
       if(seen.has(child))continue;
       seen.add(child);
       const step=copyRecipe(current.id,record);
       const next={id:child,path:[...current.path,child],
         steps:[...current.steps,step]};
       if(child===to)return {from,to,path:next.path,steps:next.steps,
         totals:aggregate(next.steps),sourceYear:2022};
       queue.push(next);
     }
   }
   return null;
 }
 function reachable(from,maxDepth=12,maxResults=200){
   if(!idExists(from)||!Number.isInteger(maxDepth)||maxDepth<1||
     maxDepth>12||!Number.isInteger(maxResults)||maxResults<1||
     maxResults>500)return [];
   const seen=new Set([from]),out=[],queue=[{id:from,depth:0}];
   for(let front=0;front<queue.length;front++){
     const row=queue[front];
     if(row.depth>=maxDepth)continue;
     for(const recipe of getRows(row.id)){
       const target=recipe.target;
       if(seen.has(target))continue;
       seen.add(target);
       const depth=row.depth+1;
       out.push({id:target,name:catalog.find(target).name,steps:depth});
       if(out.length>=maxResults)return out;
       queue.push({id:target,depth});
     }
   }
   return out;
 }
 const style=document.createElement('style');style.id='bf1500-chain-styles';
 style.textContent=[
   '#bf1500-chain{margin:8px 0;padding:10px;',
   'background:#182e47;color:#f3e6cf;',
   'border:1px solid #c5a471;border-radius:6px;',
   'font:12px/1.5 system-ui,sans-serif}',
   '#bf1500-chain>summary{font:bold 14px Georgia,serif;cursor:pointer;',
   'min-height:36px}',
   '#bf1500-chain select,#bf1500-chain button{color:#fff;',
   'background:#31506c;border:1px solid #aa977a;',
   'padding:7px;border-radius:5px;min-height:39px}',
   '#bf1500-chain select{width:100%;margin:5px 0}',
   '.bf1500-record{padding:7px;background:#2a4157;',
   'border-radius:5px;margin:5px 0}',
   '.bf1500-record strong,.bf1500-record small{display:block}',
   '.bf1500-caution{color:#ffe0b4}'
 ].join('');
 document.head.append(style);
 const panel=document.createElement('details');panel.id='bf1500-chain';
 const summary=document.createElement('summary');
 summary.textContent='VERIFIED MULTI-STAGE EVOLUTION ROUTES · v15.00';
 const note=document.createElement('p');note.className='bf1500-caution';
 note.textContent='Strictly recorded original 2022 Global recipes. Routes exclude evolution edges with missing recipes. This is a research planner: no actual evolution, item consumption, character level, inventory or save changes.';
 const fromSel=document.createElement('select');fromSel.id='bf1500-from';
 fromSel.setAttribute('aria-label','Temporary draft original form');
 const toSel=document.createElement('select');toSel.id='bf1500-to';
 toSel.setAttribute('aria-label','Recorded reachable evolution target');
 const refreshBtn=document.createElement('button');refreshBtn.type='button';
 refreshBtn.id='bf1500-refresh';refreshBtn.textContent='REFRESH DRAFT ROUTES';
 const report=document.createElement('div');report.id='bf1500-report';
 const steps=document.createElement('div');steps.id='bf1500-steps';
 const materials=document.createElement('div');materials.id='bf1500-materials';
 panel.append(summary,note,fromSel,toSel,refreshBtn,report,steps,materials);
 anchor.after(panel);
 let from=null,to=null;
 const el=(tag,txt)=>{const node=document.createElement(tag);
   node.textContent=txt;return node;};
 function setOptions(sel,rows,placeholder){
   sel.replaceChildren();
   const none=document.createElement('option');none.value='';
   none.textContent=placeholder;sel.append(none);
   for(const row of rows){
     const opt=document.createElement('option');opt.value=String(row.id);
     opt.textContent=row.label;sel.append(opt);
   }
 }
 function showRoute(){
   report.replaceChildren();steps.replaceChildren();materials.replaceChildren();
   if(from===null||to===null){
     report.append(el('p','Choose a drafted source and a target with recorded recipe links.'));
     return null;
   }
   const route=findRoute(from,to);
   if(!route){
     report.append(el('p','No source-verified recipe path exists within 12 recorded hops.'));
     return null;
   }
   report.append(el('strong','2022 Global source path · '+route.steps.length+' recipe stages'));
   report.append(el('p',route.path.map(id=>catalog.find(id)?.name||'#'+id).join(' → ')));
   report.append(el('p','Combined RECORDED costs: '+route.totals.zel+
     ' Zel · '+route.totals.karma+' Karma'));
   for(const row of route.steps){
     const card=document.createElement('div');card.className='bf1500-record';
     card.append(el('strong',row.fromName+' → '+row.toName),
       el('small','Original forms #'+row.from+' → #'+row.to+
         ' · '+row.zel+' Zel · '+row.karma+' Karma'));
     const counts=new Map();
     for(const mat of row.materials){
       const key=String(mat.type)+':'+String(mat.id);
       const r=counts.get(key)||{...mat,count:0};
       r.count++;counts.set(key,r);
     }
     for(const mat of counts.values()){
       card.append(el('small',(mat.name||'Unnamed source material')+
         ' · #'+mat.id+' (type '+mat.type+') ×'+mat.count));
     }
     steps.append(card);
   }
   materials.append(el('strong','ALL STAGES · COMBINED ORIGINAL MATERIAL REQUIREMENTS'));
   if(!route.totals.materials.length)
     materials.append(el('p','No materials recorded for these source recipe stages.'));
   for(const mat of route.totals.materials){
     const row=document.createElement('div');row.className='bf1500-record';
     row.append(el('span',(mat.name||'Unnamed source material')+
       ' · #'+mat.id+' (type '+mat.type+') ×'+mat.count));materials.append(row);
   }
   return route;
 }
 function refresh(){
   const ids=draft.selected.filter(id=>idExists(id));
   if(!ids.includes(from))from=ids[0]??null;
   setOptions(fromSel,ids.map(id=>({id,label:catalog.find(id).name+' · #'+id})),
     'Add an original source unit in the temporary archive draft');
   fromSel.value=from===null?'':String(from);
   const destinations=from===null?[]:reachable(from);
   if(!destinations.some(x=>x.id===to))to=destinations[0]?.id??null;
   setOptions(toSel,destinations.map(x=>({id:x.id,
     label:x.name+' · #'+x.id+' · '+x.steps+' source stage(s)'})),
     'No catalog-matched source recipe path for this draft unit');
   toSel.value=to===null?'':String(to);
   showRoute();
   return destinations.length;
 }
 function choose(fromId,toId){
   if(!draft.selected.includes(fromId)||
     !reachable(fromId).some(x=>x.id===toId))return false;
   from=fromId;to=toId;refresh();return true;
 }
 fromSel.addEventListener('change',()=>{
   const id=Number(fromSel.value);
   from=fromSel.value&&draft.selected.includes(id)?id:null;
   to=null;refresh();
 });
 toSel.addEventListener('change',()=>{
   const id=Number(toSel.value);
   to=toSel.value&&from!==null&&
     reachable(from).some(x=>x.id===id)?id:null;
   showRoute();
 });
 refreshBtn.addEventListener('click',refresh);
 panel.addEventListener('toggle',()=>{if(panel.open)refresh();});
 document.querySelector('.bf-navbar')?.addEventListener('click',()=>{
   if(panel.open)refresh();
 });
 refresh();
 window.BFGlobalEvolutionChainV1500=Object.freeze({
   get sourceHopCount(){return sourceHopCount;},
   get selected(){return {from,to};},
   findRoute,reachable,choose,refresh,
   get currentRoute(){return from===null||to===null?null:findRoute(from,to);}
 });
})();
