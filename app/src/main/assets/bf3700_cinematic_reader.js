/* BF_GLOBAL_OPTIONAL_CINEMATIC_STORY_READER_V3700 */
(() => {
 'use strict';
 const events=window.BFGlobalOriginalEventsV2200;
 if(window.BFGlobalCinematicReaderV3700||!events||
    !window.BFGlobalEventCompositeV3600||
    !window.BFGlobalDialogueTimelineV3500||
    typeof P==='undefined'||P.version!==7)return;
 const reader=document.getElementById('bf2200-reader');
 const title=document.getElementById('bf2200-title');
 if(!reader||!title||reader.tagName!=='DETAILS')return;
 const style=document.createElement('style');style.id='bf3700-css';
 style.textContent=[
  'html.bf3700-lock,body.bf3700-lock{overflow:hidden!important}',
  '#bf2200-reader.bf3700-focus{position:fixed!important;inset:0!important;',
  'height:100dvh!important;max-height:100dvh!important;width:100vw!important;',
  'box-sizing:border-box!important;z-index:9999!important;overflow-y:auto!important;',
  'margin:0!important;border-radius:0!important;padding:12px 14px 32px!important;',
  'background:#122239!important;overscroll-behavior:contain!important}',
  '#bf3700-bar{display:flex;align-items:center;gap:8px;justify-content:space-between;',
  'margin:8px 0;padding:8px 0;border-bottom:1px solid #9f8867;',
  'color:#eedbb6;font:700 11px/1.5 system-ui,sans-serif}',
  '#bf3700-toggle{min-height:44px;min-width:124px;padding:8px 12px;',
  'border:1px solid #d9b985;border-radius:6px;background:#674d30;color:#fff;font-weight:800}',
  '#bf2200-reader.bf3700-focus #bf2700-stage{max-width:640px;margin:10px auto}',
  '#bf2200-reader.bf3700-focus #bf2200-text{font-size:17px;line-height:1.7}'
 ].join('');document.head.append(style);
 const bar=document.createElement('div');bar.id='bf3700-bar';
 const caption=document.createElement('span');
 caption.textContent='OPTIONAL ORIGINAL STORY THEATER';
 const toggle=document.createElement('button');toggle.id='bf3700-toggle';
 toggle.type='button';toggle.textContent='FULL SCREEN ↗';
 toggle.setAttribute('aria-pressed','false');
 bar.append(caption,toggle);
 reader.insertBefore(bar,title);
 let focused=false;
 function snapshot(){
   const source=events.snapshot();
   return Object.freeze({focused,available:reader.open&&!!source?.source,
     source:source?.source||null,step:source?.step||0});
 }
 function refresh(){
   const s=snapshot();
   bar.hidden=!reader.open;
   toggle.disabled=!s.available&&!focused;
   toggle.textContent=focused?'EXIT THEATER ✕':'FULL SCREEN ↗';
   toggle.setAttribute('aria-pressed',String(focused));
   return s;
 }
 function exit(){
   if(!focused){refresh();return false;}
   focused=false;
   reader.classList.remove('bf3700-focus');
   document.body.classList.remove('bf3700-lock');
   document.documentElement.classList.remove('bf3700-lock');
   reader.removeAttribute('aria-label');
   refresh();return true;
 }
 function enter(){
   const s=snapshot();
   if(focused||!s.available||!reader.getClientRects().length)return false;
   focused=true;
   reader.classList.add('bf3700-focus');
   document.body.classList.add('bf3700-lock');
   document.documentElement.classList.add('bf3700-lock');
   reader.setAttribute('aria-label','Optional expanded original Global story reader');
   refresh();return true;
 }
 toggle.addEventListener('click',()=>{if(focused)exit();else enter()});
 reader.addEventListener('toggle',()=>{if(!reader.open)exit();else refresh()});
 document.addEventListener('keydown',e=>{
   if(focused&&e.key==='Escape'){e.preventDefault();exit()}
 });
 document.addEventListener('visibilitychange',()=>{if(document.hidden)exit()});
 document.querySelector('.bf-navbar')?.addEventListener('click',exit);
 refresh();
 window.BFGlobalCinematicReaderV3700=Object.freeze({snapshot,refresh,enter,exit});
})();
