/* BF_GLOBAL_ORIGINAL_EVOLUTION_PATHS_V1000 */
(() => {
 'use strict';
 if(window.BFOriginalEvolutionV1000 || !window.BFGlobalUnitArchive ||
   !window.BFArchiveDraftV800 || !window.BFOptionalLabsHubV900 ||
   typeof P==='undefined'||P?.version!==7)return;
 const source=document.getElementById('bf-global-unit-catalog-data');
 const anchor=document.getElementById('bf800-draft');
 if(!source||!anchor||BFGlobalUnitArchive.count!==2291)return;
 let archive;
 try{archive=JSON.parse(source.textContent);}catch(_){return;}
 if(archive.schema!=='bf-global-unit-archive-2022-v1'||
   archive.units?.length!==2291)return;
 const units=archive.units,byId=new Map(units.map(u=>[u.id,u]));
 if(byId.size!==2291)return;
 const parent=new Map(units.map(u=>[u.id,[]]));
 let edges=0;
 for(const u of units){
   if(!Array.isArray(u.evo)||u.evo.some(id=>!byId.has(id)))return;
   for(const child of u.evo){
     parent.get(child).push(u.id);edges++;
   }
 }
 if(edges<10||!byId.has(10011))return;
 const next=id=>byId.get(Number(id))?.evo.slice()||[];
 function sourceRecipes(id){
   if(!byId.has(Number(id)))return [];
   const row=BFGlobalUnitArchive.originalRecord(Number(id));
   return Array.isArray(row?.recipes)?row.recipes.map(recipe=>({
     target:recipe.target,zel:recipe.zel,karma:recipe.karma,
     materials:Array.isArray(recipe.materials)?recipe.materials.map(mat=>({
       id:mat.id,type:mat.type,name:mat.name||''})):[]
   })):[];
 }
 function sourceRecipe(from,to){
   if(!byId.has(Number(to)))return null;
   return sourceRecipes(from).find(x=>x.target===Number(to))||null;
 }
 const previous=id=>(parent.get(Number(id))||[]).slice().sort((a,b)=>a-b);
 function descendants(id,maxDepth=12,maxNodes=100){
   if(!Number.isSafeInteger(Number(id))||!byId.has(Number(id))||
      !Number.isInteger(maxDepth)||maxDepth<0||maxDepth>20)return [];
   const out=[],seen=new Set([Number(id)]);
   const queue=[{id:Number(id),depth:0,from:null}];
   while(queue.length && out.length<maxNodes){
     const cur=queue.shift();out.push(cur);
     if(cur.depth>=maxDepth)continue;
     for(const child of next(cur.id)){
       if(seen.has(child))continue;
       seen.add(child);queue.push({id:child,depth:cur.depth+1,from:cur.id});
     }
   }
   return out;
 }
 const el=document.createElement('style');el.id='bf1000-evolution-styles';
 el.textContent=[
  '#bf1000-evolution{margin:8px 0;padding:8px;background:#1b3349;',
  'border:1px solid #9fa8ae;border-radius:5px;color:#f3e7cd}',
  '#bf1000-evolution summary{cursor:pointer;min-height:36px;',
  'font:bold 14px Georgia,serif}',
  '#bf1000-evolution input,#bf1000-evolution button{',
  'background:#314e68;color:white;border:1px solid #bba273;',
  'border-radius:5px;padding:7px;min-height:38px}',
  '#bf1000-evolution input{width:100%;box-sizing:border-box}',
  '.bf1000-row{display:flex;align-items:center;gap:8px;padding:5px;',
  'border-bottom:1px solid #526b80;overflow-wrap:anywhere}',
  '.bf1000-row strong,.bf1000-row small{display:block}',
  '.bf1000-row small{color:#c7d4e2}',
  '.bf1000-row button{margin-left:auto}',
  '#bf1000-search-results{max-height:180px;overflow:auto}',
  '#bf1000-relations{max-height:380px;overflow:auto}',
  '.bf1000-note{color:#ffdeb0}',
  '#bf1000-detail strong{display:block;font-size:14px}'
 ].join('');
 document.head.append(el);
 const panel=document.createElement('details');panel.id='bf1000-evolution';
 const head=document.createElement('summary');
 head.textContent='2022 ORIGINAL EVOLUTION PATHS · v10.00';
 const warning=document.createElement('p');warning.className='bf1000-note';
 warning.textContent='Source-only links between recovered original 2022 Global forms. No actual evolution, leveling, material deduction or new roster unlocks are implemented.';
 const input=document.createElement('input');input.type='search';input.id='bf1000-search';
 input.placeholder='Search original unit names or IDs';input.setAttribute('aria-label','Search 2022 evolution source');
 const results=document.createElement('div');results.id='bf1000-search-results';
 const detail=document.createElement('div');detail.id='bf1000-detail';
 const relations=document.createElement('div');relations.id='bf1000-relations';
 const count=document.createElement('p');count.id='bf1000-count';
 count.className='bf1000-note';
 panel.append(head,warning,input,results,detail,relations,count);
 anchor.append(panel);
 let selected=10011;
 const line=(u,btnText,callback)=>{
   const card=document.createElement('div');card.className='bf1000-row';
   const info=document.createElement('div'),name=document.createElement('strong');
   const desc=document.createElement('small');name.textContent=u.name+' · #'+u.id;
   desc.textContent=u.rarity+'★ · 2022 Global '+u.unitMaxLevel+
     ' max level · '+u.evo.length+' source next forms';
   info.append(name,desc);card.append(info);
   if(callback){
     const b=document.createElement('button');b.type='button';b.textContent=btnText;
     b.addEventListener('click',callback);card.append(b);
   }
   return card;
 };
 function show(id=selected){
   const x=byId.get(Number(id));if(!x)return false;
   selected=x.id;detail.replaceChildren();relations.replaceChildren();
   const name=document.createElement('strong');
   name.textContent=x.name+' · #'+x.id+' · '+x.rarity+'★';
   const meta=document.createElement('p');
   meta.textContent='Original unit base HP '+x.unitBaseHp+' / ATK '+
     x.unitBaseAtk+' / DEF '+x.unitBaseDef+' / REC '+x.unitBaseRec;
   detail.append(name,meta);
   const ability=BFGlobalUnitArchive.originalRecord(x.id);
   if(ability?.bb){
     const text=document.createElement('p');
     text.textContent='2022 original Brave Burst: '+(ability.bb.name||'Unnamed');
     detail.append(text);
   }
   const draft=document.createElement('button');draft.type='button';
   draft.textContent='ADD TO TEMPORARY ARCHIVE DRAFT';
   const usable=x.unitKind===0&&
      [x.unitBaseHp,x.unitBaseAtk,x.unitBaseDef,x.unitBaseRec].every(
         v=>Number.isSafeInteger(v)&&v>0);
   draft.disabled=!usable;draft.addEventListener('click',()=>{
     if(BFArchiveDraftV800.add(x.id))draft.textContent='ADDED TO TEMPORARY DRAFT';
   });
   detail.append(draft);
   const heading=(txt)=>{
     const h=document.createElement('strong');h.textContent=txt;
     relations.append(h);
   };
   heading('DIRECT RECORDED PREVIOUS FORMS · '+previous(x.id).length);
   for(const id of previous(x.id)){
     relations.append(line(byId.get(id),'VIEW',()=>show(id)));
   }
   heading('DIRECT RECORDED NEXT FORMS · '+next(x.id).length);
   for(const id of next(x.id)){
     relations.append(line(byId.get(id),'VIEW',()=>show(id)));
   }
   const recipes=sourceRecipes(x.id);
   heading('ARCHIVED 2022 EVOLUTION RECIPES · '+recipes.length);
   if(!recipes.length){
     const p=document.createElement('p');p.textContent='No original source recipe recovered for this unit form.';
     relations.append(p);
   }
   for(const recipe of recipes){
     const to=byId.get(recipe.target),box=document.createElement('div');
     box.className='bf1000-row';
     const description=document.createElement('div');
     const title=document.createElement('strong');
     title.textContent='→ '+(to?.name||'Unmatched archived unit')+' · #'+recipe.target;
     const summary=document.createElement('small');
     summary.textContent='RECORDED SOURCE COST · '+recipe.zel+' Zel'+
       (recipe.karma?' · '+recipe.karma+' Karma':'');
     description.append(title,summary);
     const counted=new Map();
     for(const mat of recipe.materials){
       const key=mat.type+':'+mat.id;
       const group=counted.get(key)||{...mat,count:0};
       group.count++;counted.set(key,group);
     }
     const material=document.createElement('small');
     material.textContent=[...counted.values()].map(mat=>(mat.name||'Unnamed material')+
       ' · #'+mat.id+' (type '+mat.type+') ×'+mat.count).join(' · ')||
       'No source-listed materials';
     description.append(material);box.append(description);
     if(to){
       const button=document.createElement('button');button.type='button';
       button.textContent='VIEW';button.addEventListener('click',()=>show(to.id));
       box.append(button);
     }
     relations.append(box);
   }
   const chain=descendants(x.id);
   heading('RECORDED DESCENDANTS · '+Math.max(0,chain.length-1));
   for(const node of chain.slice(1)){
     const u=byId.get(node.id);
     relations.append(line(u,'VIEW',()=>show(u.id)));
   }
   count.textContent='2022 source index: '+units.length+' distinct forms · '+
     edges+' recorded next-evolution links. This view shows at most '+
     '100 descendant forms and 12 source steps; no inferred recipes or actual evolution.';
   return true;
 }
 function search(){
   const q=input.value.trim().toLocaleLowerCase();
   const rows=units.filter(u=>!q||String(u.id).includes(q)||
     u.name.toLocaleLowerCase().includes(q));
   results.replaceChildren();
   for(const u of rows.slice(0,12)){
     results.append(line(u,'INSPECT',()=>show(u.id)));
   }
   return rows.length;
 }
 input.addEventListener('input',search);
 search();show(10011);
 window.BFOriginalEvolutionV1000=Object.freeze({
   get formCount(){return units.length;},
   get linkCount(){return edges;},
   get selectedId(){return selected;},
   next,previous,descendants,sourceRecipes,sourceRecipe,show,search
 });
})();
