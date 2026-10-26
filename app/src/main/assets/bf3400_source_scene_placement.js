/* BF_GLOBAL_SOURCE_SCENE_PLACEMENT_V3400 */
(() => {
 'use strict';
 const frames=window.BFGlobalEventExpressionsV2900;
 if(window.BFGlobalScenePlacementV3400||!frames||!window.BFGlobalStoryPlaybackV3300||
    typeof P==='undefined'||P.version!==7)return;
 const stage=document.getElementById('bf2600-art');
 const portrait=document.getElementById('bf2600-portrait');
 const message=document.getElementById('bf2200-text');
 const title=document.getElementById('bf2600-character');
 if(!stage||!portrait||!message||!title||stage.children.length<2)return;
 const info=document.createElement('small');info.id='bf3400-position';
 info.style.cssText='display:block;margin:6px 0;color:#eed5a2;font:11px/1.5 system-ui,sans-serif';
 stage.children[1].append(info);
 // Exact source PARAM,id=2 chrN x/y pairs recovered from the twenty supported
 // 2022 Global content/event/map[1-3]-dungeon*.txt scripts. The renderer's
 // native stage coordinate origin and animation curves remain unverified.
 const coords=Object.freeze({
   Tilith:Object.freeze({x:60,y:30,side:'right'}),
   Karl:Object.freeze({x:-110,y:-40,side:'left'}),
   Seria:Object.freeze({x:-50,y:20,side:'left'})
 });
 const supported=/^map[123]-dungeon[1-7]\.txt$/;
 function snapshot(){
   const frame=frames.snapshot();
   const person=frame?.character;
   const source=frame?.source;
   const p=person&&source&&supported.test(source)&&source!=='map3-dungeon6.txt'?coords[person]:null;
   return Object.freeze({
     source:source||null,step:frame?.step||0,
     speaker:p?person:null,x:p?.x??null,y:p?.y??null,
     side:p?.side||null,stageLabel:p?'2022 SCRIPT x '+p.x+' / y '+p.y:null
   });
 }
 let signature='';
 function refresh(){
   const s=snapshot(),key=JSON.stringify(s);
   if(signature===key)return s;signature=key;
   info.hidden=!s.side;
   if(!s.side)return s;
   // Approximate a two-column mobile arrangement from signed X coordinate.
   // Do not claim this is the original pixel-perfect stage transform.
   if(s.side==='right'){
     stage.style.gridTemplateColumns='minmax(0,1fr) minmax(0,140px)';
     portrait.style.gridColumn='2';stage.children[1].style.gridColumn='1';
   }else{
     stage.style.gridTemplateColumns='minmax(0,140px) minmax(0,1fr)';
     portrait.style.gridColumn='1';stage.children[1].style.gridColumn='2';
   }
   portrait.style.gridRow='1';stage.children[1].style.gridRow='1';
   info.textContent=s.stageLabel+' · source-relative '+s.side+
     ' · responsive approximation (original motion and pixel mapping not restored)';
   return s;
 }
 new MutationObserver(refresh).observe(message,{childList:true,subtree:true,characterData:true});
 new MutationObserver(refresh).observe(title,{childList:true,characterData:true});
 document.getElementById('bf2200-scenes')?.addEventListener('change',()=>queueMicrotask(refresh));
 refresh();
 window.BFGlobalScenePlacementV3400=Object.freeze({snapshot,refresh,lookup(name){
   return coords[name]||null;
 }});
})();
