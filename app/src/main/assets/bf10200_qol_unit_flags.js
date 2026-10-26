/* BF_GLOBAL_QOL_UNIT_FLAGS_V10200 */
(() => {
 'use strict';
 // Favorite/lock markers only. Current demo has no sell/fusion/delete engine;
 // do not assert that markers protect against operations not implemented.
 if(window.BFGlobalQoLUnitFlagsV10200||typeof P==='undefined'||
   P.version!==7||!Array.isArray(P.roster))return;
 const box=document.getElementById('bf-owned-box');
 const results=document.getElementById('bf-box-results');
 const detail=document.getElementById('bf-box-detail');
 if(!box||!results||!detail)return;
 const key='bf_global_offline_qol_unit_flags_v102';
 const freeze=Object.freeze;
 function current(){
   const node=results.querySelector('.bf-box-card[aria-pressed="true"]')||
     results.querySelector('.bf-box-card');
   const id=Number(node?.dataset?.bfUnitId);
   return Number.isSafeInteger(id)&&P.roster.includes(id)?id:null;
 }
 function validId(id){return Number.isSafeInteger(id)&&id>0&&P.roster.includes(id)}
 function load(){
   try{
     const obj=JSON.parse(localStorage.getItem(key)||'null');
     if(!obj||obj.version!==1)return {favorites:[],locked:[]};
     const ids=list=>Array.isArray(list)?[...new Set(list.filter(Number.isSafeInteger).filter(x=>x>0))].slice(0,5000):[];
     return {favorites:ids(obj.favorites),locked:ids(obj.locked)};
   }catch(_){return {favorites:[],locked:[]};}
 }
 let flags=load();
 function write(favorites,locked){
   try{localStorage.setItem(key,JSON.stringify({version:1,favorites,locked}));return true}
   catch(_){return false;}
 }
 function change(id,kind,on){
   if(!validId(id)||!['favorites','locked'].includes(kind)||typeof on!=='boolean')return false;
   const fav=new Set(flags.favorites),lock=new Set(flags.locked);
   const selected=kind==='favorites'?fav:lock;
   if(on)selected.add(id);else selected.delete(id);
   const next={favorites:[...fav].sort((a,b)=>a-b),locked:[...lock].sort((a,b)=>a-b)};
   if(!write(next.favorites,next.lock))return false;
   flags=next;refresh();return true;
 }
 function state(id=current()){
   return freeze({id,owned:validId(id),
     favorite:validId(id)&&flags.favorites.includes(id),
     locked:validId(id)&&flags.locked.includes(id),
     favorites:flags.favorites.filter(validId).length,
     locks:flags.locked.filter(validId).length,
     advisoryOnly:true});
 }
 const style=document.createElement('style');style.id='bf10200-flags-style';
 style.textContent=[
   '#bf10200-flags{padding:10px;margin:9px 0;border:1px solid #c5b185;',
   'border-radius:6px;background:#253849;color:#f7eedb;',
   'font:12px/1.45 system-ui,sans-serif}',
   '#bf10200-flags button{min-height:42px;margin:4px 5px 4px 0;',
   'padding:8px 11px;color:#fff;border:1px solid #bca780;',
   'background:#40596a;border-radius:5px;font-weight:800}',
   '#bf10200-flags button:disabled{opacity:.45}',
   '#bf10200-flags p{margin:5px 0}',
   '#bf-box-results .bf-box-card[data-bf-qol-favorite="true"]::after{',
   'content:"★ FAVORITE";font-size:10px;color:#ffdda1}',
   '#bf-box-results .bf-box-card[data-bf-qol-locked="true"]::before{',
   'content:"🔒";font-size:13px}'
 ].join('');
 document.head.append(style);
 const panel=document.createElement('section');panel.id='bf10200-flags';
 const title=document.createElement('strong');
 title.textContent='QoL · UNIT FAVORITES & LOCK MARKERS';
 const info=document.createElement('p');info.id='bf10200-info';
 const favorite=document.createElement('button');favorite.id='bf10200-favorite';
 favorite.type='button';
 const locked=document.createElement('button');locked.id='bf10200-lock';
 locked.type='button';
 const caution=document.createElement('small');
 caution.textContent='Markers are stored locally and do not modify the game save. '+
   'Selling/fusion protection is not active because those mechanics are not reconstructed.';
 panel.append(title,info,favorite,locked,caution);detail.after(panel);
 function refresh(){
   const s=state();
   favorite.disabled=!s.owned;locked.disabled=!s.owned;
   favorite.textContent=s.favorite?'REMOVE FAVORITE':'MARK FAVORITE';
   locked.textContent=s.locked?'REMOVE LOCK':'MARK LOCK';
   info.textContent=(s.owned?'Selected base unit #'+s.id:'Choose an owned unit')+
     ' · '+s.favorites+' favorites · '+s.locks+' locks';
   for(const card of results.querySelectorAll('.bf-box-card')){
     const id=Number(card.dataset.bfUnitId);
     card.dataset.bfQolFavorite=String(flags.favorites.includes(id));
     card.dataset.bfQolLocked=String(flags.locked.includes(id));
   }
   return s;
 }
 favorite.addEventListener('click',()=>{
   const s=state();if(s.owned)change(s.id,'favorites',!s.favorite);
 });
 locked.addEventListener('click',()=>{
   const s=state();if(s.owned)change(s.id,'locked',!s.locked);
 });
 results.addEventListener('click',()=>queueMicrotask(refresh));
 new MutationObserver(refresh).observe(results,{
   childList:true,subtree:true,attributes:true,attributeFilter:['aria-pressed']
 });
 document.querySelector('.bf-navbar')?.addEventListener('click',refresh);
 refresh();
 window.BFGlobalQoLUnitFlagsV10200=freeze({
   key,state,change,refresh,
   get favorites(){return freeze(flags.favorites.slice())},
   get locked(){return freeze(flags.locked.slice())}
 });
})();
