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
 const inspect=document.createElement('button');inspect.type='button';inspect.id='bf2600-inspect';inspect.textContent='INSPECT ORIGINAL PORTRAIT';inspect.style.cssText='min-height:44px;max-width:100%;white-space:normal';detail.append(inspect);
 const dialog=document.createElement('dialog');dialog.id='bf2600-inspector';dialog.setAttribute('aria-label','Original source portrait inspection');dialog.style.cssText='box-sizing:border-box;max-width:calc(100vw - 24px);max-height:90vh;background:#172b3b;color:white';
 const enlarged=document.createElement('img');enlarged.id='bf2600-inspector-image';enlarged.style.cssText='max-width:100%;max-height:60vh;object-fit:contain';
 const caption=document.createElement('p');caption.id='bf2600-inspector-caption';
 const close=document.createElement('button');close.type='button';close.textContent='CLOSE PORTRAIT';close.style.minHeight='44px';dialog.append(enlarged,caption,close);document.body.append(dialog);let inspectedScene=null,inspectedCharacter=null;
 function closeInspector(){if(dialog.open)dialog.close();}
 close.addEventListener('click',closeInspector);dialog.addEventListener('close',()=>{enlarged.removeAttribute('src');if(panel.open&&inspect.getClientRects().length)inspect.focus();});
 enlarged.addEventListener('error',()=>{if(dialog.open){enlarged.hidden=true;caption.textContent='Source portrait file unavailable; no replacement artwork inferred.';}});
 function openPortrait(){try{const api=window.BFGlobalOriginalEventsV2200,state=api.snapshot(),parts=/^(dungeon):([1-9][0-9]*)$/.exec(state.chosen||'');
   if(!panel.open||P.version!==7||S.busy!==false||S.auto!==false||!parts||!candidates().includes(choice)||typeof dialog.showModal!=='function'||dialog.open)return false;
   const source=api.lookup(parts[1],Number(parts[2]));if(source?.source!=='content/event/'+state.source||source.lines.length!==state.lines)return false;
   const repeat=window.BFGlobalQoLQuestRepeatV9800;if(repeat&&(typeof repeat.statusSnapshot!=='function'||repeat.statusSnapshot()?.active!==false))return false;
   inspectedScene=state.chosen;inspectedCharacter=choice;enlarged.hidden=false;enlarged.src=images[choice];enlarged.alt='Original 2022 '+choice+' source portrait';caption.textContent=choice+' · '+images[choice]+' · Original source pixels; native cutscene placement/timing not inferred.';dialog.showModal();close.focus();return true;
 }catch(_){return false;}}
 inspect.addEventListener('click',openPortrait);
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
   if(dialog.open&&(window.BFGlobalOriginalEventsV2200.snapshot().chosen!==inspectedScene||choice!==inspectedCharacter||!present.includes(inspectedCharacter)))closeInspector();
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
 window.BFGlobalOriginalEventPortraitsV2600=Object.freeze({refresh,openPortrait,
   get snapshot(){return refresh()}});
})();