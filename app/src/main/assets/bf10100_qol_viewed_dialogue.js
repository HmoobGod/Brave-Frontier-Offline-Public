/* BF_GLOBAL_QOL_VIEWED_DIALOGUE_SKIP_V10100 */
(() => {
 'use strict';
 // Archive reader only: no original event triggers, unlocks, or P changes.
 const readerApi=window.BFGlobalOriginalEventsV2200;
 const timeline=window.BFGlobalDialogueTimelineV3500;
 const playback=window.BFGlobalStoryPlaybackV3300;
 const panel=document.getElementById('bf2200-reader');
 const nav=document.getElementById('bf2200-nav');
 const next=document.getElementById('bf2200-next');
 const scenes=document.getElementById('bf2200-scenes');
 if(window.BFGlobalQoLViewedDialogueV10100||!readerApi||!timeline||!playback||
   !panel||!nav||!next||!scenes||typeof P==='undefined'||P.version!==7)return;
 const freeze=Object.freeze;
 const key='bf_global_offline_qol_viewed_scenes_v101';
 const limit=40;
 function sceneValid(id){
   if(typeof id!=='string'||!/^(clear|dungeon):[1-9][0-9]{0,3}$/.test(id))return false;
   const [kind,number]=id.split(':');
   return !!readerApi.lookup(kind,Number(number));
 }
 function load(){
   try{
     const data=JSON.parse(localStorage.getItem(key)||'null');
     if(!data||data.version!==1||!Array.isArray(data.viewed))return new Set();
     return new Set(data.viewed.slice(-limit).filter(sceneValid));
   }catch(_){return new Set();}
 }
 let viewed=load(),message='Complete a story scene once to unlock quick skipping.';
 function persist(){
   try{localStorage.setItem(key,JSON.stringify({version:1,
     viewed:[...viewed].slice(-limit)}));return true;}
   catch(_){return false;}
 }
 function remember(scene){
   if(!sceneValid(scene)||viewed.has(scene))return false;
   const nextSet=new Set([...viewed,scene].slice(-limit));
   const old=viewed;viewed=nextSet;
   if(!persist()){viewed=old;return false;}
   message='Scene completed. Quick skip now available on replay.';
   render();return true;
 }
 function observed(){
   const s=readerApi.snapshot();
   if(!panel.open||!s||!s.chosen||!s.lines||s.step!==s.lines)return false;
   return remember(s.chosen);
 }
 const ui=document.createElement('div');ui.id='bf10100-viewed-dialogue';
 ui.style.cssText='margin:8px 0;padding:8px;border-top:1px solid #a98d6b;'+
   'font:12px/1.5 system-ui,sans-serif;color:#f3e6d0';
 const heading=document.createElement('strong');heading.textContent='QoL · PREVIOUSLY VIEWED DIALOGUE';
 const quick=document.createElement('button');quick.type='button';
 quick.id='bf10100-skip';quick.textContent='SKIP VIEWED SCENE ›';
 quick.style.cssText='display:block;min-height:42px;margin:7px 0;'+
   'padding:8px 11px;border-radius:5px;border:1px solid #bb9f77;'+
   'background:#644a33;color:#fff;font-weight:800';
 const note=document.createElement('small');note.id='bf10100-note';
 ui.append(heading,quick,note);nav.after(ui);
 function state(){
   const s=readerApi.snapshot();
   return freeze({scene:s?.chosen||null,step:s?.step||0,lines:s?.lines||0,
     viewed:!!s?.chosen&&viewed.has(s.chosen),
     storedCount:viewed.size,available:!!panel.open&&!!s?.chosen&&
       !!s.lines&&s.step<s.lines&&viewed.has(s.chosen)});
 }
 function render(){
   const s=state();
   quick.disabled=!s.available;
   note.textContent=message+' · '+s.storedCount+' scenes marked as completed'+
     (s.viewed?' · This scene has been read before':'');
   return s;
 }
 function skip(){
   const s=state();
   if(!s.available)return false;
   playback.pause();
   // Use existing unlock-gated original navigation. No direct mutation.
   if(!timeline.jump(s.lines))return false;
   const after=readerApi.snapshot();
   const ok=after.chosen===s.scene&&after.step===s.lines;
   if(ok){message='Previously viewed dialogue skipped to its last page.';render();}
   return ok;
 }
 quick.addEventListener('click',skip);
 next.addEventListener('click',()=>queueMicrotask(observed));
 scenes.addEventListener('change',()=>queueMicrotask(render));
 panel.addEventListener('toggle',()=>{if(panel.open){observed();render()}});
 document.querySelector('.bf-navbar')?.addEventListener('click',render);
 // Story autoplay and direct timeline navigation change the text without
 // user clicks; observe the same archive-controlled source DOM.
 const textBox=document.getElementById('bf2200-text');
 if(textBox)new MutationObserver(()=>{
   observed();render();
 }).observe(textBox,{subtree:true,childList:true,characterData:true});
 render();
 window.BFGlobalQoLViewedDialogueV10100=freeze({
   state,remember,skip,observed,render,
   get viewed(){return freeze([...viewed])}
 });
})();
