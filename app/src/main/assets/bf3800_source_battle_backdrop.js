/* BF_GLOBAL_OPTIONAL_SOURCE_BATTLE_BACKDROP_V3800 */
(() => {
 'use strict';
 const events=window.BFGlobalOriginalEventsV2200;
 const stage=window.BFOriginalEventStageV2700;
 if(window.BFGlobalBattleBackdropV3800||!events||!stage||
    !window.BFGlobalCinematicReaderV3700||
    typeof QUESTS==='undefined'||QUESTS.length!==106||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined')return;
 const battle=document.getElementById('battle');
 const hud=document.getElementById('bf2000-run');
 const mode=document.getElementById('mode');
 const questinfo=document.getElementById('questinfo');
 if(!battle||!hud||!mode||!questinfo)return;
 const original={image:battle.style.backgroundImage,size:battle.style.backgroundSize,
   position:battle.style.backgroundPosition,repeat:battle.style.backgroundRepeat};
 const sheet=document.createElement('style');sheet.id='bf3800-css';
 sheet.textContent='#bf3800-panel{margin:9px 0;padding:10px;border:1px solid #9e8c70;'+
  'border-radius:7px;background:#162b3f;color:#f4e9d4;font:12px/1.4 system-ui,sans-serif}'+
  '#bf3800-panel label{display:flex;gap:9px;align-items:center;font-weight:800;min-height:44px}'+
  '#bf3800-panel input{width:18px;height:18px;accent-color:#b99d6b}'+
  '#bf3800-source{display:block;margin:5px 0;color:#cddfeb;font-size:11px}';
 document.head.append(sheet);
 const panel=document.createElement('section');panel.id='bf3800-panel';
 const label=document.createElement('label');label.htmlFor='bf3800-toggle';
 label.textContent='OPTIONAL ORIGINAL DUNGEON BACKDROP';
 const toggle=document.createElement('input');toggle.id='bf3800-toggle';
 toggle.type='checkbox';toggle.setAttribute('aria-label','Use archived original dungeon backdrop during demo battle');
 label.prepend(toggle);
 const source=document.createElement('small');source.id='bf3800-source';
 const note=document.createElement('small');
 note.textContent='Uses exact archived 2022 event dungeon JPG. Display only: live combat, enemies, wave count, drop tables and battle animation stay DEMO. Not an original battle renderer.';
 panel.append(label,source,note);hud.append(panel);
 let enabled=false,last='';
 function lookup(){
   const q=typeof QUEST==='undefined'?null:QUEST;
   if(!q||mode.value!=='archive'||!questUnlocked(q))return null;
   const a=events.lookup('dungeon',q.dungeonId);
   const filename=a?.source?.split('/').pop();
   const jpg=filename?stage.backgroundFor(filename):null;
   return jpg?Object.freeze({missionId:q.missionId,dungeonId:q.dungeonId,
     scene:filename,background:jpg}):null;
 }
 function snapshot(){
   const record=lookup();
   return Object.freeze({enabled,available:!!record,missionId:record?.missionId||null,
     dungeonId:record?.dungeonId||null,scene:record?.scene||null,
     background:record?.background||null,applied:enabled&&!!record});
 }
 function restore(){
   battle.style.backgroundImage=original.image;
   battle.style.backgroundSize=original.size;
   battle.style.backgroundPosition=original.position;
   battle.style.backgroundRepeat=original.repeat;
 }
 function refresh(){
   const s=snapshot(),key=JSON.stringify(s);
   if(key===last)return s;last=key;
   panel.hidden=!s.available;
   toggle.disabled=!s.available;
   toggle.checked=enabled;
   if(s.applied){
     battle.style.backgroundImage=
       'linear-gradient(180deg,rgba(8,18,31,.75),rgba(8,18,31,.9)),url("content/dungeon/'+s.background+'")';
     battle.style.backgroundSize='cover';
     battle.style.backgroundPosition='center';
     battle.style.backgroundRepeat='no-repeat';
   }else restore();
   source.textContent=s.available?
     '2022 event source '+s.scene+' · '+s.background+' · '+(s.applied?'BACKDROP ON':'BACKDROP OFF'):
     'No exact source-matched dungeon JPG for the selected mission';
   return s;
 }
 function setEnabled(value){
   if(typeof value!=='boolean'||value&&!lookup())return false;
   enabled=value;last='';refresh();return true;
 }
 toggle.addEventListener('change',()=>setEnabled(toggle.checked));
 mode.addEventListener('change',refresh);
 new MutationObserver(refresh).observe(questinfo,{subtree:true,childList:true,characterData:true});
 document.querySelector('.bf-navbar')?.addEventListener('click',refresh);
 window.setInterval(()=>{if(!document.hidden)refresh()},950);
 refresh();
 window.BFGlobalBattleBackdropV3800=Object.freeze({snapshot,refresh,setEnabled});
})();
