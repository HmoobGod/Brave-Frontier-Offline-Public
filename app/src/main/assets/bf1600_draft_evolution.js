/* BF_GLOBAL_ARCHIVE_DRAFT_EVOLUTION_V1600 */
(() => {
 'use strict';
 if(window.BFGlobalDraftEvolutionV1600 || !window.BFGlobalEvolutionChainV1500 ||
   !window.BFEvolutionMaterialPlannerV1400 || !window.BFOriginalEvolutionV1000 ||
   !window.BFArchiveDraftV800 || !window.BFGlobalUnitArchive ||
   !window.BFTacticalRoundsV300 || typeof P==='undefined'||P?.version!==7)return;
 const paths=window.BFGlobalEvolutionChainV1500,
   draft=window.BFArchiveDraftV800,
   recipes=window.BFOriginalEvolutionV1000,
   catalog=window.BFGlobalUnitArchive,
   trial=window.BFTacticalRoundsV300;
 const host=document.getElementById('bf1500-chain');
 if(!host || catalog.count!==2291 || paths.sourceHopCount<100 ||
   typeof draft.replace!=='function' || typeof draft.eligible!=='function')return;
 const eligible=id=>Number.isInteger(id)&&draft.eligible(id)&&!!catalog.find(id);
 const draftReady=()=>trial.snapshot===null&&!(typeof S!=='undefined'&&S?.busy);
 const recipeRoute=(from,to)=>{
   if(!eligible(from)||!eligible(to)||from===to)return null;
   const result=paths.findRoute(from,to,12);
   if(!result||result.steps.length<1||result.steps.length>12 ||
     result.path.length!==result.steps.length+1 ||
     result.path[0]!==from||result.path.at(-1)!==to)return null;
   // Every intermediate form must be an eligible archive-draft form; no
   // shortcut via catalog forms without positive playable base stats.
   for(let i=0;i<result.steps.length;i++){
     const r=result.steps[i];
     if(!eligible(r.from)||!eligible(r.to)||r.from!==result.path[i]||
       r.to!==result.path[i+1])return null;
     const source=recipes.sourceRecipe(r.from,r.to);
     if(!source||source.zel!==r.zel||source.karma!==r.karma||
       JSON.stringify(source.materials)!==JSON.stringify(r.materials))return null;
   }
   return result;
 };
 let history=[];
 let from=null,to=null;
 const record=()=>history.map(row=>({
   from:row.from,to:row.to,steps:row.steps,
   cost:{...row.cost,materials:row.cost.materials.map(m=>({...m}))},
   path:row.path.slice()
 }));
 const currentRoute=()=>from!==null&&to!==null?recipeRoute(from,to):null;
 const name=id=>catalog.find(id)?.name||('#'+id);
 const el=(tag,txt)=>{const node=document.createElement(tag);node.textContent=txt;return node;};
 function available(fromId){
   if(!eligible(fromId)||!draft.selected.includes(fromId))return [];
   const selected=new Set(draft.selected);
   return paths.reachable(fromId,12,500).filter(row=>
     !selected.has(row.id)&&eligible(row.id)&&recipeRoute(fromId,row.id)!==null);
 }
 function evolve(fromId,toId){
   if(!Number.isInteger(fromId)||!Number.isInteger(toId)||
     !draftReady()||!draft.selected.includes(fromId)||
     draft.selected.includes(toId))return false;
   const route=recipeRoute(fromId,toId);
   if(!route||!draft.replace(fromId,toId))return false;
   const item={from:fromId,to:toId,steps:route.steps.length,
     path:route.path.slice(),cost:{
       zel:route.totals.zel,karma:route.totals.karma,
       materials:route.totals.materials.map(row=>({...row}))
     }};
   history.push(item);if(history.length>20)history.shift();
   from=toId;to=null;
   paths.refresh();window.BFEvolutionMaterialPlannerV1400.refresh();
   refresh();return true;
 }
 function undo(){
   if(!history.length||!draftReady())return false;
   const last=history.at(-1);
   if(!draft.selected.includes(last.to)||draft.selected.includes(last.from)||
     !draft.replace(last.to,last.from))return false;
   history.pop();from=last.from;to=last.to;
   paths.refresh();window.BFEvolutionMaterialPlannerV1400.refresh();
   refresh();return true;
 }
 const style=document.createElement('style');style.id='bf1600-evo-style';
 style.textContent=[
   '#bf1600-draft-evolution{margin:8px 0;padding:10px;',
   'background:#1b3147;border:1px solid #bfa273;',
   'border-radius:7px;color:#f4e7d3;font:12px/1.5 system-ui,sans-serif}',
   '#bf1600-draft-evolution>summary{font:bold 14px Georgia,serif;',
   'cursor:pointer;min-height:38px}',
   '#bf1600-draft-evolution select,#bf1600-draft-evolution button{',
   'width:100%;box-sizing:border-box;min-height:40px;margin:4px 0;',
   'color:#fff;background:#30516b;border:1px solid #baa57e;',
   'border-radius:5px;padding:7px}',
   '#bf1600-draft-evolution button:disabled{opacity:.45}',
   '#bf1600-draft-evolution .bf1600-card{padding:7px;margin:5px 0;',
   'background:#2a4057;border-radius:5px}',
   '#bf1600-draft-evolution .bf1600-warn{color:#ffe0a9}'
 ].join('');
 document.head.append(style);
 const panel=document.createElement('details');panel.id='bf1600-draft-evolution';
 const heading=el('summary','EVOLVE ARCHIVE DRAFT · VERIFIED 2022 RECIPES · v16.00');
 const warning=el('p','Temporary source-recipe evolution ONLY for the optional archive draft. This does not consume materials, Zel or Karma, improve owned units or grant original game rewards. Trials and all damage formulas are synthetic.');
 warning.className='bf1600-warn';
 const fromSel=document.createElement('select');fromSel.id='bf1600-from';
 fromSel.setAttribute('aria-label','Temporarily drafted source form');
 const toSel=document.createElement('select');toSel.id='bf1600-to';
 toSel.setAttribute('aria-label','Verified recipe evolution destination');
 const summary=el('div','');summary.id='bf1600-route-summary';
 const advance=document.createElement('button');advance.type='button';
 advance.id='bf1600-apply';advance.textContent='EVOLVE TEMPORARY DRAFT FORM';
 const undoButton=document.createElement('button');undoButton.type='button';
 undoButton.id='bf1600-undo';undoButton.textContent='UNDO LAST DRAFT EVOLUTION';
 const feedback=el('p','');feedback.id='bf1600-feedback';
 const historyView=el('div','');historyView.id='bf1600-history';
 panel.append(heading,warning,fromSel,toSel,summary,advance,undoButton,feedback,historyView);
 host.after(panel);
 function options(sel,list,empty){
   sel.replaceChildren();
   const placeholder=document.createElement('option');placeholder.value='';
   placeholder.textContent=empty;sel.append(placeholder);
   for(const item of list){
     const opt=document.createElement('option');opt.value=String(item.id);
     opt.textContent=item.label;sel.append(opt);
   }
 }
 function choose(fromId,toId){
   if(!draft.selected.includes(fromId)||!eligible(fromId)||
     !available(fromId).some(r=>r.id===toId))return false;
   from=fromId;to=toId;refresh();return true;
 }
 function refresh(){
   const selected=draft.selected.filter(eligible);
   if(!selected.includes(from))from=selected[0]??null;
   options(fromSel,selected.map(id=>({id,label:name(id)+' · #'+id})),
     'Select a source form in the archive draft');
   fromSel.value=from===null?'':String(from);
   const rows=from===null?[]:available(from);
   if(!rows.some(row=>row.id===to))to=rows[0]?.id??null;
   options(toSel,rows.map(r=>({id:r.id,
     label:name(r.id)+' · #'+r.id+' · '+r.steps+' sourced stage(s)'})),
     'No eligible documented evolution recipe path');
   toSel.value=to===null?'':String(to);
   summary.replaceChildren();
   const route=currentRoute();
   if(route){
     const card=el('div','');card.className='bf1600-card';
     card.append(el('strong',route.path.map(name).join(' → ')),
       el('p',route.steps.length+' original 2022 recipe step(s) · '+
         route.totals.zel+' SOURCE Zel · '+route.totals.karma+' SOURCE Karma'));
     for(const mat of route.totals.materials)
       card.append(el('small',(mat.name||'Original material')+
         ' · #'+mat.id+' (type '+mat.type+') ×'+mat.count));
     summary.append(card);
   }else summary.append(el('p','Choose a drafted form with a fully documented eligible 2022 recipe path.'));
   advance.disabled=!draftReady()||!route;
   undoButton.disabled=!draftReady()||!history.length||
     !draft.selected.includes(history.at(-1).to)||
     draft.selected.includes(history.at(-1).from);
   feedback.textContent=draftReady()?
     'Source costs shown for reference only. The replacement keeps the same temporary party slot.':
     'Exit the current training battle before changing the temporary draft.';
   historyView.replaceChildren();
   historyView.append(el('strong','TEMPORARY EVOLUTION HISTORY · '+history.length+'/20'));
   for(const item of history.slice(-6).reverse()){
     const card=el('div','');card.className='bf1600-card';
     card.textContent=name(item.from)+' → '+name(item.to)+
       ' · '+item.steps+' source recipe stages (no source resources spent)';
     historyView.append(card);
   }
   return rows.length;
 }
 fromSel.addEventListener('change',()=>{
   const id=Number(fromSel.value);
   from=fromSel.value&&draft.selected.includes(id)?id:null;to=null;refresh();
 });
 toSel.addEventListener('change',()=>{
   const id=Number(toSel.value);
   to=toSel.value&&available(from).some(r=>r.id===id)?id:null;refresh();
 });
 advance.addEventListener('click',()=>{if(currentRoute())evolve(from,to);else refresh();});
 undoButton.addEventListener('click',undo);
 panel.addEventListener('toggle',()=>{if(panel.open)refresh();});
 document.querySelector('.bf-navbar')?.addEventListener('click',()=>{if(panel.open)refresh();});
 refresh();
 window.BFGlobalDraftEvolutionV1600=Object.freeze({
   get selected(){return {from,to};},
   get history(){return record();},
   get activeRoute(){const r=currentRoute();return r?{
     from:r.from,to:r.to,path:r.path.slice(),steps:r.steps.map(s=>({
       ...s,materials:s.materials.map(m=>({...m}))})),
     totals:{...r.totals,materials:r.totals.materials.map(m=>({...m}))}
   }:null;},
   available,choose,evolve,undo,refresh
 });
})();
