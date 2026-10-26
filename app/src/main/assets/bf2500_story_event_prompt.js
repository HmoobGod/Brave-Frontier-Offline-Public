/* BF_GLOBAL_STORY_EVENT_CUE_V2500 */
(() => {
 'use strict';
 const archive=window.BFGlobalOriginalEventsV2200;
 if(window.BFGlobalStoryEventCueV2500 || !archive ||
    !window.BFGlobalStoryBattleV2000 ||
    typeof QUESTS==='undefined'||QUESTS.length!==106||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined')return;
 const host=document.getElementById('bf2200-reader'),list=document.getElementById('questlist');
 if(!host||!list)return;
 const style=document.createElement('style');style.id='bf2500-cue-style';
 style.textContent=[
  '#bf2500-cue{margin:10px 0;padding:11px;border-radius:8px;',
  'border:1px solid #b39a65;background:#213447;color:#f4ebd6;',
  'font:12px/1.5 system-ui,sans-serif}',
  '#bf2500-cue strong{display:block;font:800 14px Georgia,serif}',
  '#bf2500-cue p{margin:6px 0;color:#dce8eb}',
  '#bf2500-cue-buttons{display:flex;gap:7px;flex-wrap:wrap}',
  '#bf2500-cue button{min-height:40px;padding:8px 12px;border-radius:5px;',
  'background:#654929;border:1px solid #d4bd90;color:white;font-weight:700}'
 ].join('');document.head.append(style);
 const panel=document.createElement('section');panel.id='bf2500-cue';
 panel.setAttribute('aria-label','Original story event prompt');
 const heading=document.createElement('strong');heading.id='bf2500-cue-heading';
 const description=document.createElement('p');description.id='bf2500-cue-description';
 const actions=document.createElement('div');actions.id='bf2500-cue-buttons';
 const read=document.createElement('button');read.type='button';read.id='bf2500-read';read.textContent='READ ORIGINAL SCENE ›';
 const dismiss=document.createElement('button');dismiss.type='button';dismiss.id='bf2500-dismiss';dismiss.textContent='NOT NOW';
 actions.append(read,dismiss);panel.append(heading,description,actions);host.before(panel);
 let muted=null;
 function cue(){
   const q=typeof QUEST==='undefined'?null:QUEST;
   if(!q||E?.mode?.value!=='archive'||!!S.busy)return null;
   const cleared=(P.questClears?.[q.missionId]||0)>0;
   if(S.over&&S.phase==='Victory'&&cleared&&[10,11,21].includes(q.missionId)&&
      archive.lookup('clear',q.missionId)){
     return Object.freeze({kind:'clear',id:q.missionId,missionId:q.missionId,
       identity:'clear:'+q.missionId+':'+P.questClears[q.missionId],
       title:'ORIGINAL QUEST-CLEAR DIALOGUE AVAILABLE'});
   }
   if(!S.over&&questUnlocked(q)&&archive.lookup('dungeon',q.dungeonId)){
     return Object.freeze({kind:'dungeon',id:q.dungeonId,missionId:q.missionId,
       identity:'dungeon:'+q.missionId+':'+q.dungeonId,
       title:'ORIGINAL DUNGEON INTRODUCTION'});
   }
   return null;
 }
 function snapshot(){const state=cue();return state&&!Object.is(state.identity,muted)?state:null;}
 function refresh(){
   const state=snapshot();panel.hidden=!state;
   if(state){
     heading.textContent=state.title;
     description.textContent=state.kind==='clear'? 
       'The source mission links this message to your completed quest. It does not activate the Village features in this demo.':
       'Read the original 2022 Global dialogue recovered for this dungeon. Introduction timing and scene choreography are not restored.';
   }
   return state;
 }
 function open(){
   const state=snapshot();
   if(!state||!archive.read(state.kind,state.id))return false;
   host.scrollIntoView({block:'start',behavior:'smooth'});
   return true;
 }
 read.addEventListener('click',open);
 dismiss.addEventListener('click',()=>{const state=snapshot();if(state){muted=state.identity;refresh()}});
 new MutationObserver(refresh).observe(list,{childList:true});
 for(const id of ['questinfo','log']){
   const el=document.getElementById(id);
   if(el)new MutationObserver(refresh).observe(el,{subtree:true,childList:true,characterData:true});
 }
 document.querySelector('.bf-navbar')?.addEventListener('click',refresh);
 window.setInterval(()=>{if(!document.hidden)refresh()},900);
 refresh();
 window.BFGlobalStoryEventCueV2500=Object.freeze({snapshot,refresh,open,dismiss(){
   const state=snapshot();if(!state)return false;muted=state.identity;refresh();return true;
 }});
})();