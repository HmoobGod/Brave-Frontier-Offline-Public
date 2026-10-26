/* BF_GLOBAL_ORIGINAL_DIALOGUE_EXPRESSIONS_V2900 */
(() => {
 'use strict';
 const archive=window.BFGlobalOriginalEventsV2200;
 const portraits=window.BFGlobalOriginalEventPortraitsV2600;
 const speaker=window.BFGlobalDialogueSpeakerV2800;
 if(window.BFGlobalEventExpressionsV2900||!archive||!portraits||!speaker||
    !window.BFOriginalEventStageV2700||typeof P==='undefined'||P.version!==7)return;
 const DATA=/* BF2900_DATA_PLACEHOLDER */null;
 if(!DATA||DATA.schema!=='bf-global-original-expression-frames-v2900'||
    DATA.scenes!==20||DATA.frames!==405||DATA.sprites!==19)return;
 const frames=DATA.rows;
 const img=document.getElementById('bf2600-portrait');
 const title=document.getElementById('bf2600-character');
 const controls=document.getElementById('bf2600-portrait-controls');
 const message=document.getElementById('bf2200-text');
 if(!img||!title||!controls||!message)return;
 const allowed={'1':'Tilith','2':'Karl','3':'Seria'};
 const filename=pair=>'navi_chara'+pair[0]+'_'+pair[1]+'.png';
 const knownImages=new Set(DATA.files);
 if(knownImages.size!==19)return;
 let count=0;
 for(const [name,sequence] of Object.entries(frames)){
   const match=/^map([123])-dungeon([1-7])\.txt$/.exec(name);
   if(!match||sequence.length%2)return;
   const region=Number(match[1]),part=Number(match[2]);
   const id=region===1?part*10+10:region===2?part*10+190:part*10+290;
   const scene=archive.lookup('dungeon',id);
   if(!scene||scene.source!=='content/event/'+name ||
      sequence.length!==scene.lines.length*2)return;
   for(let n=0;n<sequence.length;n+=2){
     const pair=sequence.slice(n,n+2);
     if(!allowed[pair[0]]||!/^[0-9]$/.test(pair[1])||
       !knownImages.has(filename(pair))||
       speaker.lookup(name,n/2+1)!==allowed[pair[0]])return;
     count++;
   }
 }
 if(count!==405||Object.keys(frames).length!==20)return;
 const notice=document.createElement('small');notice.id='bf2900-expression-note';
 notice.style.cssText='color:#e4cfaa;margin:5px 0;font:11px/1.4 system-ui,sans-serif';
 title.after(notice);
 function lookup(source,step){
   const sequence=frames[source];
   if(!sequence||!Number.isInteger(step)||step<1||step*2>sequence.length)return null;
   const pair=sequence.slice((step-1)*2,step*2);
   return Object.freeze({
     character:allowed[pair[0]],variant:Number(pair[1]),
     file:filename(pair),source
   });
 }
 function snapshot(){
   const state=archive.snapshot();
   const frame=lookup(state?.source,state?.step);
   return Object.freeze({
     source:state?.source||null,step:state?.step||0,
     character:frame?.character||null,variant:frame?.variant??null,
     image:frame?.file||null,frames:count,scenes:20,sprites:knownImages.size
   });
 }
 function refresh(){
   const state=snapshot(),image=state.image;
   notice.hidden=!image;
   controls.style.display=image?'none':'';
   if(!image)return state;
   speaker.refresh();
   const path='content/event/'+image;
   if(img.getAttribute('src')!==path)img.setAttribute('src',path);
   img.alt='Original 2022 '+state.character+' expression '+state.variant+' from '+state.source;
   notice.textContent='ORIGINAL 2022 EXPRESSION · '+state.character+
     ' · source image '+image+' · dialogue '+state.step+
     ' (still-image recreation, not original animated event playback)';
   return state;
 }
 new MutationObserver(refresh).observe(message,{childList:true,characterData:true,subtree:true});
 new MutationObserver(refresh).observe(title,{childList:true,characterData:true});
 document.getElementById('bf2200-scenes')?.addEventListener('change',()=>queueMicrotask(refresh));
 refresh();
 window.BFGlobalEventExpressionsV2900=Object.freeze({snapshot,refresh,lookup});
})();
