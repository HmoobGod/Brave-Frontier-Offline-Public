/* BF_GLOBAL_EVOLUTION_MATERIAL_PLANNER_V1400 */
(() => {
 'use strict';
 if(window.BFEvolutionMaterialPlannerV1400 ||
    !window.BFOriginalEvolutionV1000 || !window.BFArchiveDraftV800 ||
    !window.BFGlobalUnitArchive || !window.BFOptionalLabsHubV900 ||
    typeof P==='undefined' || P?.version!==7)return;
 const evolution=window.BFOriginalEvolutionV1000;
 const draft=window.BFArchiveDraftV800;
 const archive=window.BFGlobalUnitArchive;
 if(evolution.formCount!==2291||archive.count!==2291)return;
 const host=document.getElementById('bf1000-evolution');
 if(!host)return;
 const selections=new Map();
 const chosen=()=>draft.selected.filter(id=>Number.isInteger(id));
 const sourceOptions=id=>evolution.sourceRecipes(id).filter(r=>
   Number.isInteger(r.target)&&archive.find(r.target)!==null);
 function prune(){
   const selected=new Set(chosen());
   for(const [id,target] of selections){
     if(!selected.has(id)||!sourceOptions(id).some(r=>r.target===target))
       selections.delete(id);
   }
 }
 function selectRecipe(from,to){
   if(!Number.isInteger(from)||!Number.isInteger(to)||
     !chosen().includes(from)||!sourceOptions(from).some(r=>r.target===to))
     return false;
   selections.set(from,to);render();return true;
 }
 function clearRecipe(from){
   if(!Number.isInteger(from)||!selections.has(from))return false;
   selections.delete(from);render();return true;
 }
 function autoSelect(){
   prune();
   let assigned=0;
   for(const id of chosen()){
     if(selections.has(id))continue;
     const first=sourceOptions(id)[0];
     if(first){selections.set(id,first.target);assigned++;}
   }
   render();return assigned;
 }
 function clear(){
   selections.clear();render();return true;
 }
 function summary(){
   prune();
   const selected=chosen(),entries=[],missing=[];
   const totals={zel:0,karma:0,materials:[]},counted=new Map();
   for(const from of selected){
     const to=selections.get(from);
     const recipe=to===undefined?null:evolution.sourceRecipe(from,to);
     if(!recipe){missing.push(from);continue;}
     const original=archive.find(from),result=archive.find(to);
     if(!original||!result){missing.push(from);continue;}
     const items=recipe.materials.map(mat=>({...mat}));
     entries.push({from,to,fromName:original.name,toName:result.name,
       zel:recipe.zel,karma:recipe.karma,materials:items});
     totals.zel+=recipe.zel||0;
     totals.karma+=recipe.karma||0;
     for(const material of items){
       const key=String(material.type)+':'+String(material.id);
       const record=counted.get(key);
       if(record)record.count++;
       else counted.set(key,{id:material.id,type:material.type,
         name:material.name||'',count:1});
     }
   }
   totals.materials=[...counted.values()]
     .sort((a,b)=>String(a.type).localeCompare(String(b.type))||
       Number(a.id)-Number(b.id));
   return {selected,entries,missing,totals};
 }
 const style=document.createElement('style');style.id='bf1400-styles';
 style.textContent=[
   '#bf1400-material-planner{margin:8px 0;padding:10px;',
   'background:#183346;color:#f3e6cb;border:1px solid #bca277;',
   'border-radius:6px;font:12px/1.5 system-ui,sans-serif}',
   '#bf1400-material-planner>summary{font:bold 14px Georgia,serif;',
   'min-height:36px;cursor:pointer}',
   '#bf1400-material-planner select,#bf1400-material-planner button{',
   'background:#34506a;color:#f8f4e7;border:1px solid #ac9c7d;',
   'border-radius:5px;padding:7px;min-height:39px}',
   '#bf1400-material-planner select{width:100%}',
   '.bf1400-entry{border-top:1px solid #64798d;padding:8px 0}',
   '.bf1400-entry strong,.bf1400-entry small{display:block}',
   '.bf1400-list{padding:6px 8px;background:#2b4056;',
   'border-radius:5px;margin:5px 0}',
   '.bf1400-muted{color:#ffdfac}',
   '#bf1400-status{font-weight:bold}'
 ].join('');
 document.head.append(style);
 const panel=document.createElement('details');panel.id='bf1400-material-planner';
 const heading=document.createElement('summary');
 heading.textContent='ARCHIVED EVOLUTION MATERIAL PLAN · v14.00';
 const note=document.createElement('p');note.className='bf1400-muted';
 note.textContent='READ-ONLY 2022 Global original evolution records. Plan recipes for temporary archive-draft units and sum listed costs/materials. No owned inventory is checked and nothing is crafted, evolved, spent or saved.';
 const controls=document.createElement('div');
 const auto=document.createElement('button');auto.type='button';auto.id='bf1400-auto';
 auto.textContent='PICK FIRST RECORDED RECIPE FOR EACH';
 const reset=document.createElement('button');reset.type='button';reset.id='bf1400-reset';
 reset.textContent='CLEAR RECIPE CHOICES';
 controls.append(auto,reset);
 const status=document.createElement('p');status.id='bf1400-status';status.setAttribute('aria-live','polite');
 const cards=document.createElement('div');cards.id='bf1400-choices';
 const report=document.createElement('div');report.id='bf1400-report';
 panel.append(heading,note,controls,status,cards,report);
 host.after(panel);
 const word=(tag,value)=>{
   const el=document.createElement(tag);el.textContent=String(value);return el;
 };
 function render(){
   const data=summary();
   cards.replaceChildren();report.replaceChildren();
   status.textContent=data.entries.length+' / '+data.selected.length+
     ' source-listed evolution recipes planned · '+data.missing.length+
     ' missing/unselected. This is a hypothetical archive checklist.';
   for(const from of data.selected){
     const parent=archive.find(from),options=sourceOptions(from);
     const row=document.createElement('div');row.className='bf1400-entry';
     row.append(word('strong',(parent?.name||'Unknown form')+' · #'+from));
     if(!options.length){
       row.append(word('small','No evolution recipe with a catalog-matched target recovered.'));
     }else{
       const sel=document.createElement('select');
       sel.setAttribute('aria-label','Source evolution recipe for '+parent.name);
       const none=document.createElement('option');none.value='';
       none.textContent='Choose an archived evolution recipe';sel.append(none);
       for(const recipe of options){
         const opt=document.createElement('option');opt.value=String(recipe.target);
         opt.textContent='→ '+archive.find(recipe.target).name+' · #'+recipe.target+
           ' · '+(recipe.zel||0)+' Zel';sel.append(opt);
       }
       sel.value=selections.has(from)?String(selections.get(from)):'';
       sel.addEventListener('change',()=>{
         if(sel.value)selectRecipe(from,Number(sel.value));
         else clearRecipe(from);
       });
       row.append(sel);
     }
     cards.append(row);
   }
   const cost=document.createElement('div');cost.className='bf1400-list';
   cost.append(word('strong','ARCHIVED RECIPE TOTALS · '+data.entries.length+' planned'));
   cost.append(word('p',(data.totals.zel||0)+' recorded Zel · '+
     (data.totals.karma||0)+' recorded Karma'));
   report.append(cost);
   if(data.missing.length)
     report.append(word('p','Missing/unselected recipes for #'+data.missing.join(', #')+
       '; totals cover SELECTED source recipes only.'));
   const materials=document.createElement('div');materials.id='bf1400-materials';
   materials.append(word('strong','COMBINED ORIGINAL MATERIAL LIST'));
   if(!data.totals.materials.length)
     materials.append(word('p','No source-listed materials in current recipe choices.'));
   for(const item of data.totals.materials){
     const row=document.createElement('div');row.className='bf1400-list';
     row.append(word('span',(item.name||'Unnamed archived material')+
       ' · #'+item.id+' · type '+item.type+' ×'+item.count));
     materials.append(row);
   }
   report.append(materials);
   return data;
 }
 auto.addEventListener('click',autoSelect);
 reset.addEventListener('click',clear);
 panel.addEventListener('toggle',()=>{if(panel.open)render();});
 document.querySelector('.bf-navbar')?.addEventListener('click',()=>{
   if(panel.open)render();
 });
 render();
 window.BFEvolutionMaterialPlannerV1400=Object.freeze({
   get selected(){return chosen();},
   get plan(){return summary();},
   sourceOptions:id=>sourceOptions(id).map(r=>({
     target:r.target,zel:r.zel,karma:r.karma,
     materials:r.materials.map(x=>({...x}))
   })),
   selectRecipe,clearRecipe,autoSelect,clear,refresh:render
 });
})();
