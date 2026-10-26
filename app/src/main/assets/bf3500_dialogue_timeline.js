/* BF_GLOBAL_ORIGINAL_DIALOGUE_TIMELINE_V3500 */
(() => {
 'use strict';
 const archive=window.BFGlobalOriginalEventsV2200;
 const playback=window.BFGlobalStoryPlaybackV3300;
 if(window.BFGlobalDialogueTimelineV3500||!archive||!playback||
    !window.BFGlobalScenePlacementV3400||typeof P==='undefined'||P.version!==7)return;
 const reader=document.getElementById('bf2200-reader');
 const text=document.getElementById('bf2200-text');
 const previous=document.getElementById('bf2200-prev');
 const next=document.getElementById('bf2200-next');
 const control=document.getElementById('bf2200-nav');
 const scene=document.getElementById('bf2200-scenes');
 if(!reader||!text||!previous||!next||!control||!scene)return;
 const css=document.createElement('style');css.id='bf3500-css';
 css.textContent=[
  '#bf3500-timeline{padding:11px 0;border-top:1px solid #8f805f;margin-top:12px;',
  'font:12px/1.5 system-ui,sans-serif;color:#f7ead6}',
  '#bf3500-timeline label{display:block;font-weight:750;margin-bottom:7px}',
  '#bf3500-timeline input{box-sizing:border-box;min-height:44px;width:88px;',
  'color:white;background:#14263a;border:1px solid #af9775;padding:8px}',
  '#bf3500-timeline button{min-height:44px;margin-left:9px;padding:9px 12px;',
  'border:1px solid #c6a77b;border-radius:5px;color:white;background:#655030;font-weight:800}',
  '#bf3500-timeline button:disabled{opacity:.45}',
  '#bf3500-bar{height:9px;width:100%;margin:9px 0;accent-color:#c7a96d}',
  '#bf3500-status{display:block;color:#d6e7ec;margin:5px 0}',
  '#bf3500-timeline small{display:block;color:#b9c9d6}'
 ].join('');document.head.append(css);
 const panel=document.createElement('section');panel.id='bf3500-timeline';
 panel.setAttribute('aria-label','Optional original story line navigator');
 const label=document.createElement('label');label.htmlFor='bf3500-line';label.textContent='ORIGINAL STORY · JUMP TO LINE';
 const line=document.createElement('input');line.id='bf3500-line';line.type='number';
 line.inputMode='numeric';line.min='1';line.step='1';line.value='1';
 line.setAttribute('aria-label','Original dialogue line number');
 const go=document.createElement('button');go.id='bf3500-go';go.type='button';go.textContent='GO TO LINE ›';
 const progress=document.createElement('progress');progress.id='bf3500-bar';
 progress.max=1;progress.value=0;progress.setAttribute('aria-label','Read-only story scene page position');
 const status=document.createElement('output');status.id='bf3500-status';
 status.setAttribute('aria-live','polite');
 const note=document.createElement('small');
 note.textContent='Navigates only unlocked original archived dialogue. No saved story bookmarks, extra unlocks, reward or combat changes. Scene pages and expression art remain source-linked.';
 panel.append(label,line,go,progress,status,note);control.after(panel);
 function snapshot(){
   const a=archive.snapshot();
   const available=reader.open&&!!a?.source&&a.lines>0;
   return Object.freeze({available,source:a?.source||null,
     step:available?a.step:0,lines:available?a.lines:0,
     playing:playback.snapshot().playing});
 }
 function refresh(){
   const s=snapshot();panel.hidden=!s.available;
   if(s.available){
     line.max=String(s.lines);
     if(document.activeElement!==line)line.value=String(s.step);
     progress.max=s.lines;progress.value=s.step;
     status.textContent='Line '+s.step+' of '+s.lines+
       ' · '+(s.playing?'Auto-playing':'Manual reading');
   }
   go.disabled=!s.available;
   return s;
 }
 function jump(target){
   const s=snapshot();
   if(!s.available||!Number.isInteger(target)||target<1||target>s.lines)return false;
   playback.pause();
   // Use the existing, unlock-gated reader rather than changing private state.
   const moving=target>s.step?next:previous;
   for(let i=0;i<Math.abs(target-s.step);i++){
     if(moving.disabled||archive.snapshot().source!==s.source)return false;
     moving.click();
   }
   const result=archive.snapshot();
   refresh();
   return result.source===s.source&&result.step===target;
 }
 go.addEventListener('click',()=>{if(!jump(Number(line.value)))refresh()});
 line.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();go.click()}});
 scene.addEventListener('change',()=>queueMicrotask(refresh));
 reader.addEventListener('toggle',refresh);
 new MutationObserver(refresh).observe(text,{childList:true,subtree:true,characterData:true});
 refresh();
 window.BFGlobalDialogueTimelineV3500=Object.freeze({snapshot,refresh,jump});
})();
