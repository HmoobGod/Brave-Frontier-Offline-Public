/* BF_GLOBAL_ORIGINAL_EVENT_PORTRAITS_V2600 */
(() => {
 'use strict';
 if(window.BFGlobalOriginalEventPortraitsV2600 ||
    !window.BFGlobalOriginalEventsV2200 ||
    typeof P==='undefined'||P.version!==7)return;
 const panel=document.getElementById('bf2200-reader');
 const sceneTitle=document.getElementById('bf2200-title');
 const selector=document.getElementById('bf2200-scenes');
 if(!panel||!sceneTitle||!selector)return;
 const images=Object.freeze({
   Tilith:'content/event/navi_chara1_0.png',
   Karl:'content/event/navi_chara2_0.png',
   Seria:'content/event/navi_chara3_0.png'
 });
 const style=document.createElement('style');style.id='bf2600-style';
 style.textContent=[
  '#bf2600-art{display:grid;grid-template-columns:minmax(0,140px) minmax(0,1fr);',
  'gap:10px;padding:10px 0;align-items:center}',
  '#bf2600-portrait{height:170px;width:100%;object-fit:contain;object-position:center bottom}',
  '#bf2600-portrait-controls{display:flex;flex-wrap:wrap;gap:6px}',
  '#bf2600-portrait-controls button{border:1px solid #ae9970;border-radius:5px;',
  'color:#fff;background:#30485d;padding:6px 8px;min-height:35px}',
  '#bf2600-portrait-controls button[aria-pressed=true]{border-color:#f4da91;',
  'outline:1px solid #f4da91}',
  '#bf2600-art small{color:#d4dee5;font:11px/1.5 system-ui}',
  '@media(max-width:370px){#bf2600-art{grid-template-columns:105px minmax(0,1fr)}',
  '#bf2600-portrait{height:145px}}'
 ].join('');document.head.append(style);
 const box=document.createElement('div');box.id='bf2600-art';
 box.setAttribute('aria-label','Original 2022 source event character illustrations');
 const img=document.createElement('img');img.id='bf2600-portrait';img.alt='';
 const detail=document.createElement('div');
 const label=document.createElement('strong');label.id='bf2600-character';
 const controls=document.createElement('div');controls.id='bf2600-portrait-controls';
 const notice=document.createElement('small');
 notice.textContent='Original 2022 source character image. Static archival preview only: expression changes and original cutscene motion are not restored.';
 detail.append(label,controls,notice);box.append(img,detail);sceneTitle.after(box);
 let choice=null,lastKey='';
 function candidates(){
   const scene=window.BFGlobalOriginalEventsV2200.snapshot().chosen;
   if(!scene||!scene.startsWith('dungeon:'))return [];
   const id=Number(scene.slice(8));
   if(!Number.isInteger(id))return [];
   if(id>=20&&id<=80||id===210||id>=300&&id<=340)return id===340?['Tilith','Seria']:['Tilith'];
   if([200,220,230,240,250,260,360].includes(id))return [240,250,260].includes(id)?['Karl','Seria']:['Karl'];
   return [];
 }
 function refresh(){
   const present=candidates();
   box.hidden=!present.length;
   if(!present.length){choice=null;lastKey='';return Object.freeze({visible:false,character:null,options:[]})}
   const key=present.join('|');
   if(key!==lastKey){choice=present[0];lastKey=key;}
   if(!present.includes(choice))choice=present[0];
   img.src=images[choice];img.alt='Original 2022 '+choice+' event illustration';
   label.textContent=choice;
   controls.replaceChildren();
   for(const name of present){
     const button=document.createElement('button');button.type='button';
     button.textContent=name;button.setAttribute('aria-pressed',String(choice===name));
     button.addEventListener('click',()=>{choice=name;refresh()});
     controls.append(button);
   }
   return Object.freeze({visible:true,character:choice,options:Object.freeze(present.slice()),source:images[choice]});
 }
 new MutationObserver(refresh).observe(sceneTitle,{childList:true,characterData:true});
 selector.addEventListener('change',refresh);
 refresh();
 window.BFGlobalOriginalEventPortraitsV2600=Object.freeze({refresh,
   get snapshot(){return refresh()}});
})();