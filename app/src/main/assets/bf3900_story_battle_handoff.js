/* BF_GLOBAL_STORY_TO_BATTLE_HANDOFF_V3900 */
(() => {
 'use strict';
 const events=window.BFGlobalOriginalEventsV2200;
 const cinema=window.BFGlobalCinematicReaderV3700;
 if(window.BFGlobalStoryBattleHandoffV3900||!events||!cinema||
    !window.BFGlobalBattleBackdropV3800||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined')return;
 const reader=document.getElementById('bf2200-reader');
 const controls=document.getElementById('bf2200-nav');
 const text=document.getElementById('bf2200-text');
 const battle=document.getElementById('battle');
 const mode=document.getElementById('mode');
 const questInfo=document.getElementById('questinfo');
 if(!reader||!controls||!text||!battle||!mode||!questInfo)return;
 const style=document.createElement('style');style.id='bf3900-css';
 style.textContent=[
  '#bf3900-handoff{padding:10px;margin:12px 0 4px;border:1px solid #c0a778;',
  'border-radius:6px;background:#24374a;color:#f3e9d5;',
  'font:12px/1.5 system-ui,sans-serif}',
  '#bf3900-handoff button{min-height:44px;padding:9px 12px;',
  'border:1px solid #e1c28d;border-radius:5px;',
  'background:#64502f;color:white;font-weight:800}',
  '#bf3900-handoff button:disabled{opacity:.48}',
  '#bf3900-note{display:block;margin:6px 0;color:#d0dde8}'
 ].join('');document.head.append(style);
 const panel=document.createElement('section');panel.id='bf3900-handoff';
 const button=document.createElement('button');button.type='button';
 button.id='bf3900-return';button.textContent='RETURN TO ACTIVE DEMO BATTLE ↓';
 const note=document.createElement('small');note.id='bf3900-note';
 note.textContent='Available after reading the final original intro line for your currently selected story dungeon. Returns to the existing demo battlefield without executing attacks or changing quest progress.';
 panel.append(button,note);controls.after(panel);
 function snapshot(){
   const scene=events.snapshot();
   const q=typeof QUEST==='undefined'?null:QUEST;
   const lookup=q?events.lookup('dungeon',q.dungeonId):null;
   const matched=reader.open&&mode.value==='archive'&&q&&
     !S.busy&&!S.over&&questUnlocked(q)&&lookup&&
     scene.chosen==='dungeon:'+q.dungeonId&&scene.source===lookup.source?.split('/').pop();
   return Object.freeze({
     available:!!matched,completed:!!matched&&scene.step===scene.lines,
     missionId:q?.missionId||null,dungeonId:q?.dungeonId||null,
     source:scene.source||null,step:scene.step||0,lines:scene.lines||0
   });
 }
 function refresh(){
   const s=snapshot();panel.hidden=!s.available;button.disabled=!s.completed;
   button.textContent=s.completed?'RETURN TO ACTIVE DEMO BATTLE ↓':
     'FINISH ORIGINAL INTRO TO CONTINUE';
   return s;
 }
 function returnToBattle(){
   const s=snapshot();
   if(!s.completed)return false;
   cinema.exit();
   reader.open=false;
   refresh();
   battle.scrollIntoView({block:'start',behavior:'smooth'});
   return !reader.open&&!cinema.snapshot().focused&&
     (typeof QUEST!=='undefined'?QUEST.missionId:null)===s.missionId;
 }
 button.addEventListener('click',returnToBattle);
 reader.addEventListener('toggle',refresh);
 mode.addEventListener('change',refresh);
 new MutationObserver(refresh).observe(text,{subtree:true,childList:true,characterData:true});
 new MutationObserver(refresh).observe(questInfo,{subtree:true,childList:true});
 window.BFGlobalStoryBattleHandoffV3900=Object.freeze({snapshot,refresh,returnToBattle});
 refresh();
})();
