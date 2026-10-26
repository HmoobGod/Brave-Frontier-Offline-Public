/* BF_GLOBAL_ORIGINAL_EVENT_STAGE_V2700 */
(() => {
 'use strict';
 const archive=window.BFGlobalOriginalEventsV2200;
 if(window.BFOriginalEventStageV2700||!archive||
    typeof archive.snapshot!=='function'||typeof archive.lookup!=='function')return;
 const reader=document.getElementById('bf2200-reader');
 const message=document.getElementById('bf2200-text');
 if(!reader||!message)return;
 // One-to-one joins verified against the PARAM id=1 bg1 commands in the archived
 // content/event/map[1-3]-dungeon*.txt scripts; 20 original JPGs are packaged.
 // The missing/mismatched map3-dungeon6 remains intentionally unsupported.
 const sourceBackgrounds=Object.freeze({
  'map1-dungeon1.txt':'dungeon_battle_10200.jpg',
  'map1-dungeon2.txt':'dungeon_battle_10300.jpg',
  'map1-dungeon3.txt':'dungeon_battle_10400.jpg',
  'map1-dungeon4.txt':'dungeon_battle_10500.jpg',
  'map1-dungeon5.txt':'dungeon_battle_10600.jpg',
  'map1-dungeon6.txt':'dungeon_battle_10700.jpg',
  'map1-dungeon7.txt':'dungeon_battle_10800.jpg',
  'map2-dungeon1.txt':'dungeon_battle_20100.jpg',
  'map2-dungeon2.txt':'dungeon_battle_20200.jpg',
  'map2-dungeon3.txt':'dungeon_battle_20300.jpg',
  'map2-dungeon4.txt':'dungeon_battle_20400.jpg',
  'map2-dungeon5.txt':'dungeon_battle_20500.jpg',
  'map2-dungeon6.txt':'dungeon_battle_20600.jpg',
  'map2-dungeon7.txt':'dungeon_battle_20700.jpg',
  'map3-dungeon1.txt':'dungeon_battle_30100.jpg',
  'map3-dungeon2.txt':'dungeon_battle_30200.jpg',
  'map3-dungeon3.txt':'dungeon_battle_30300.jpg',
  'map3-dungeon4.txt':'dungeon_battle_30400.jpg',
  'map3-dungeon5.txt':'dungeon_battle_30500.jpg',
  'map3-dungeon7.txt':'dungeon_battle_30700.jpg'
 });
 if(Object.keys(sourceBackgrounds).length!==20)return;
 const css=document.createElement('style');css.id='bf2700-stage-style';
 css.textContent=[
   '#bf2700-stage{margin:10px 0 4px;position:relative;overflow:hidden;',
   'aspect-ratio:640/440;border:1px solid #a89778;border-radius:7px;background:#081423}',
   '#bf2700-art{display:block;width:100%;height:100%;object-fit:contain}',
   '#bf2700-stage-caption{position:absolute;bottom:0;left:0;right:0;',
   'background:linear-gradient(transparent,#071321eb);color:#fff;padding:20px 9px 8px;',
   'font:700 11px/1.3 system-ui,sans-serif;text-shadow:0 1px 2px black}',
   '#bf2700-note{color:#cad4dd;font:11px/1.4 system-ui,sans-serif;margin:4px 0 9px}'
 ].join('');
 document.head.append(css);
 const stage=document.createElement('figure');stage.id='bf2700-stage';
 const image=document.createElement('img');image.id='bf2700-art';
 image.loading='lazy';image.decoding='async';
 image.setAttribute('alt','Recovered original 2022 Global dungeon background');
 const caption=document.createElement('figcaption');caption.id='bf2700-stage-caption';
 stage.append(image,caption);
 const note=document.createElement('p');note.id='bf2700-note';
 note.textContent='Original archived event background (2022). Static scene preview only; source cutscene motion, expression frames and timing are not yet reproduced.';
 message.before(stage,note);
 let last='';
 function snapshot(){
   const state=archive.snapshot();
   const scene=state?.source||null;
   const background=scene?sourceBackgrounds[scene]||null:null;
   return Object.freeze({scene,background,available:!!background,step:state?.step||0,
     count:Object.keys(sourceBackgrounds).length});
 }
 function refresh(){
   const state=snapshot();
   const tag=(state.background||'none')+'|'+(state.step||0);
   if(tag!==last){
     last=tag;
     stage.hidden=note.hidden=!state.available;
     if(state.available){
       const file='content/dungeon/'+state.background;
       if(image.getAttribute('src')!==file)image.setAttribute('src',file);
       caption.textContent=state.background.replace('dungeon_battle_','Original dungeon ')+' · Frame '+state.step;
     }else{
       image.removeAttribute('src');
       caption.textContent='';
     }
   }
   return state;
 }
 const selector=document.getElementById('bf2200-scenes');
 const prev=document.getElementById('bf2200-prev');
 const next=document.getElementById('bf2200-next');
 [selector,prev,next].forEach(el=>el?.addEventListener('change',refresh));
 [prev,next].forEach(el=>el?.addEventListener('click',()=>queueMicrotask(refresh)));
 new MutationObserver(refresh).observe(message,{childList:true,subtree:true,characterData:true});
 reader.addEventListener('toggle',refresh);
 refresh();
 window.BFOriginalEventStageV2700=Object.freeze({snapshot,refresh,backgroundFor(source){
   return Object.prototype.hasOwnProperty.call(sourceBackgrounds,source)?sourceBackgrounds[source]:null;
 }});
})();