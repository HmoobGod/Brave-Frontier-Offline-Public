/* BF_GLOBAL_ORIGINAL_EVENT_COMPOSITE_STAGE_V3600 */
(() => {
 'use strict';
 const events=window.BFGlobalOriginalEventsV2200;
 const backgrounds=window.BFOriginalEventStageV2700;
 const frames=window.BFGlobalEventExpressionsV2900;
 const positions=window.BFGlobalScenePlacementV3400;
 if(window.BFGlobalEventCompositeV3600||!events||!backgrounds||!frames||
    !positions||!window.BFGlobalDialogueTimelineV3500||
    typeof P==='undefined'||P.version!==7)return;
 const reader=document.getElementById('bf2200-reader');
 const background=document.getElementById('bf2700-stage');
 const portraitBlock=document.getElementById('bf2600-art');
 const message=document.getElementById('bf2200-text');
 const selector=document.getElementById('bf2200-scenes');
 if(!reader||!background||!portraitBlock||!message||!selector)return;
 const style=document.createElement('style');style.id='bf3600-css';
 style.textContent=[
  '#bf3600-actor{position:absolute;z-index:2;bottom:18px;height:80%;width:46%;',
  'object-fit:contain;object-position:center bottom;pointer-events:none;',
  'filter:drop-shadow(0 4px 6px #000b)}',
  '#bf3600-label{position:absolute;top:7px;left:7px;right:7px;z-index:3;',
  'background:#09192ccf;border:1px solid #b09b72;border-radius:5px;',
  'padding:5px 7px;color:#f5e7c9;text-align:center;font:700 10px/1.4 system-ui,sans-serif}',
  '#bf2700-stage-caption{z-index:3}'
 ].join('');document.head.append(style);
 const actor=document.createElement('img');actor.id='bf3600-actor';
 actor.alt='Original 2022 character event expression, source-relative approximate positioning';
 actor.decoding='async';
 const label=document.createElement('small');label.id='bf3600-label';
 background.append(actor,label);
 let last=null;
 function snapshot(){
   const s=events.snapshot();
   const b=backgrounds.snapshot(),f=frames.snapshot(),p=positions.snapshot();
   const okay=reader.open&&b.available&&!!p.speaker&&
     b.scene===s.source&&f.source===s.source&&p.source===s.source&&
     f.step===s.step&&p.step===s.step&&p.speaker===f.character&&
     /^navi_chara[123]_[0-9]\.png$/.test(f.image||'');
   return Object.freeze({available:!!okay,source:s.source||null,step:s.step||0,
     character:okay?f.character:null,image:okay?f.image:null,
     background:okay?b.background:null,
     x:okay?p.x:null,y:okay?p.y:null,side:okay?p.side:null,
     originalSceneCoordinates:!!okay,visualPlacement:'responsive approximation'});
 }
 function refresh(){
   const s=snapshot(),key=JSON.stringify(s);
   if(last===key)return s;last=key;
   actor.hidden=label.hidden=!s.available;
   // Hide the separate duplicate portrait only while a recovered background
   // and a matching source expression are both available.
   portraitBlock.style.display=s.available?'none':'';
   if(!s.available){actor.removeAttribute('src');return s;}
   const src='content/event/'+s.image;
   if(actor.getAttribute('src')!==src)actor.setAttribute('src',src);
   actor.style.left=s.side==='left'?'2%':'auto';
   actor.style.right=s.side==='right'?'2%':'auto';
   label.textContent='2022 ORIGINAL '+s.character.toUpperCase()+
     ' · source X '+s.x+' Y '+s.y+
     ' · approximated mobile staging (native renderer transformation unknown)';
   return s;
 }
 new MutationObserver(refresh).observe(message,{subtree:true,childList:true,characterData:true});
 reader.addEventListener('toggle',refresh);
 selector.addEventListener('change',()=>queueMicrotask(refresh));
 refresh();
 window.BFGlobalEventCompositeV3600=Object.freeze({snapshot,refresh});
})();
