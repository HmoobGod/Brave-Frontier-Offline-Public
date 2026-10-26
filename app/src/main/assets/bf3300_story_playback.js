/* BF_GLOBAL_ORIGINAL_SCENE_PLAYBACK_V3300 */
(() => {
 'use strict';
 const archive=window.BFGlobalOriginalEventsV2200;
 if(window.BFGlobalStoryPlaybackV3300||!archive||!window.BFGlobalEventExpressionsV2900||
    typeof P==='undefined'||P.version!==7)return;
 const reader=document.getElementById('bf2200-reader');
 const next=document.getElementById('bf2200-next'),prev=document.getElementById('bf2200-prev');
 const selectScene=document.getElementById('bf2200-scenes');
 const nav=document.getElementById('bf2200-nav');
 if(!reader||!next||!prev||!selectScene||!nav)return;
 const css=document.createElement('style');css.id='bf3300-style';
 css.textContent=[
  '#bf3300-player{padding:10px 0;margin:9px 0;border-top:1px solid #a99a78;',
  'font:12px/1.45 system-ui,sans-serif;color:#f3e9d6}',
  '#bf3300-player label{display:block;margin:0 0 6px;font-weight:700}',
  '#bf3300-player select{min-height:40px;min-width:130px;margin:0 8px 0 3px;',
  'padding:5px;color:white;background:#20374c;border:1px solid #b6a082}',
  '#bf3300-player button{min-height:44px;margin:4px 7px 4px 0;padding:8px 12px;',
  'border:1px solid #d7b887;border-radius:5px;background:#63462c;color:#fff;font-weight:800}',
  '#bf3300-player button:disabled{opacity:.45}',
  '#bf3300-state{display:block;margin:5px 0;color:#d6e0e8}'
 ].join('');document.head.append(css);
 const panel=document.createElement('div');panel.id='bf3300-player';
 panel.setAttribute('aria-label','Optional offline original story dialogue playback');
 const label=document.createElement('label');label.textContent='OPTIONAL DIALOGUE PLAYBACK';
 const speed=document.createElement('select');speed.id='bf3300-speed';
 speed.setAttribute('aria-label','Dialogue page delay');
 for(const [ms,text] of [[1500,'1.5s/page'],[2500,'2.5s/page'],[4000,'4s/page']]){
   const option=document.createElement('option');option.value=String(ms);
   option.textContent=text;speed.append(option);
 }
 speed.value='2500';label.append(speed);
 const play=document.createElement('button');play.type='button';play.id='bf3300-play';
 play.textContent='PLAY ▶';
 const pauseButton=document.createElement('button');pauseButton.type='button';pauseButton.id='bf3300-pause';
 pauseButton.textContent='PAUSE ⏸';
 const skip=document.createElement('button');skip.type='button';skip.id='bf3300-end';
 skip.textContent='LAST PAGE »';
 const state=document.createElement('small');state.id='bf3300-state';
 state.setAttribute('aria-live','polite');
 const note=document.createElement('small');
 note.textContent='Uses original archived dialogue, backgrounds and expression sprites. Page delay is optional QoL, not original 2022 script timing. No quest, rewards or save modifications.';
 panel.append(label,play,pauseButton,skip,state,note);
 nav.after(panel);
 let playing=false,scene=null,timer=null;
 function snapshot(){
   const a=archive.snapshot();
   return Object.freeze({playing,source:a?.source||null,step:a?.step||0,
     lines:a?.lines||0,delay:Number(speed.value)||2500,scene});
 }
 function refresh(){
   const s=snapshot();
   const available=reader.open&&!!s.source&&s.lines>0;
   play.disabled=!available||playing||s.step>=s.lines;
   pauseButton.disabled=!playing;
   skip.disabled=!available||s.step>=s.lines;
   state.textContent=(playing?'PLAYING':'PAUSED')+' · Page '+s.step+'/'+s.lines;
   return s;
 }
 function pause(){
   playing=false;scene=null;
   if(timer!==null){clearTimeout(timer);timer=null;}
   refresh();return true;
 }
 function tick(){
   timer=null;
   if(!playing)return;
   const s=snapshot();
   if(!reader.open||document.hidden||s.source!==scene||s.step>=s.lines||next.disabled){
     pause();return;
   }
   next.click();
   const now=snapshot();
   if(now.source!==scene||now.step>=now.lines){pause();return;}
   timer=setTimeout(tick,Number(speed.value)||2500);
   refresh();
 }
 function start(){
   const s=snapshot();
   if(!reader.open||document.hidden||!s.source||s.lines<2||s.step>=s.lines)return false;
   pause();playing=true;scene=s.source;
   timer=setTimeout(tick,s.delay);refresh();return true;
 }
 function lastPage(){
   const s=snapshot();
   if(!reader.open||!s.source||s.step>=s.lines)return false;
   pause();
   for(let i=s.step;i<s.lines;i++){if(next.disabled)break;next.click();}
   refresh();
   return archive.snapshot().step===s.lines;
 }
 play.addEventListener('click',start);
 pauseButton.addEventListener('click',pause);
 skip.addEventListener('click',lastPage);
 reader.addEventListener('toggle',()=>{if(!reader.open)pause();else refresh()});
 selectScene.addEventListener('change',pause);
 prev.addEventListener('click',e=>{if(e.isTrusted)pause()});
 next.addEventListener('click',e=>{if(e.isTrusted)pause()});
 document.addEventListener('visibilitychange',()=>{if(document.hidden)pause()});
 speed.addEventListener('change',()=>{if(playing){pause();start()}else refresh()});
 refresh();
 window.BFGlobalStoryPlaybackV3300=Object.freeze({snapshot,refresh,start,pause,lastPage});
})();
