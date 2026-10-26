/* BF_GLOBAL_DEMO_BATTLE_RESULTS_V3000 */
(() => {
 'use strict';
 const story=window.BFGlobalStoryBattleV2000;
 const scenes=window.BFGlobalOriginalEventsV2200;
 if(window.BFGlobalBattleResultsV3000 || !story || !scenes ||
    typeof S==='undefined'||typeof P==='undefined'||P.version!==7 ||
    typeof QUESTS==='undefined'||QUESTS.length!==106 || !window.BFGlobalQuestText)return;
 const nativeResult=document.getElementById('resultpanel');
 const output=document.getElementById('results');
 const retry=document.getElementById('reset');
 if(!nativeResult||!output||!retry)return;
 const css=document.createElement('style');css.id='bf3000-style';
 css.textContent=[
  '#bf3000-result{border-top:1px solid #a88d62;margin:12px 0 0;',
  'padding:12px 0 4px;color:#f5e9d4;font:12px/1.55 system-ui,sans-serif}',
  '#bf3000-result h3{margin:0 0 6px;color:#ffe1a5;font:800 17px Georgia,serif}',
  '#bf3000-reward{margin:4px 0;font-weight:700}',
  '#bf3000-meta{color:#d5dfe7;margin:6px 0}',
  '#bf3000-actions{display:flex;gap:7px;flex-wrap:wrap;margin:9px 0}',
  '#bf3000-actions button{min-height:44px;padding:8px 12px;',
  'border:1px solid #d6b682;border-radius:5px;background:#65482c;',
  'color:#fff;font-weight:750}',
  '#bf3000-actions button:disabled{opacity:.4}',
  '#bf3000-note{font:11px/1.4 system-ui,sans-serif;color:#cad5e3}'
 ].join('');
 document.head.append(css);
 const block=document.createElement('section');block.id='bf3000-result';
 block.setAttribute('aria-label','Offline demo battle result and navigation');
 const heading=document.createElement('h3');heading.id='bf3000-heading';
 const reward=document.createElement('p');reward.id='bf3000-reward';
 const meta=document.createElement('p');meta.id='bf3000-meta';
 const buttons=document.createElement('div');buttons.id='bf3000-actions';
 const make=(id,label,cb)=>{
   const b=document.createElement('button');b.id=id;b.textContent=label;
   b.type='button';b.addEventListener('click',cb);buttons.append(b);return b;
 };
 const replay=make('bf3000-replay','REPLAY MISSION ↻',()=>replayBattle());
 const next=make('bf3000-next','NEXT STORY MISSION ›',()=>advance());
 const scene=make('bf3000-scene','READ ORIGINAL CLEAR SCENE ›',()=>readScene());
 const note=document.createElement('small');note.id='bf3000-note';
 note.textContent='Offline simulated battle rewards. Original archived quest titles and reward amounts are source metadata; enemy AI, enemy waves, materials, drops, and Energy spending remain DEMO. Training grants no campaign rewards.';
 block.append(heading,reward,meta,buttons,note);
 nativeResult.append(block);
 function snapshot(){
   const q=typeof QUEST==='undefined'?null:QUEST;
   if(!q||!S)return null;
   const done=!!S.over&&!S.busy;
   const victory=done&&S.phase==='Victory';
   const archive=S.mode==='archive';
   const cleared=(P.questClears?.[q.missionId]||0)>0;
   const status=story.snapshot();
   const after=archive&&victory&&cleared?status?.nextId||null:null;
   const clearScene=archive&&victory&&cleared&&[10,11,21].includes(q.missionId)&&
       !!scenes.lookup('clear',q.missionId);
   const reference=BFGlobalQuestText.sourceFor(q);
   const party=Array.isArray(S.party)?S.party.filter(u=>u&&u.active):[];
   return Object.freeze({
     missionId:q.missionId,name:reference?.mission?.name||'Mission '+q.missionId,
     dungeon:reference?.dungeon?.name||'Dungeon '+q.dungeonId,
     done,victory,archive,clears:P.questClears?.[q.missionId]||0,
     nextId:after,clearScene,canReplay:done&&!retry.disabled,
     liveUnits:party.filter(u=>u.hp>0).length,totalUnits:party.length,
     exp:victory&&archive?q.exp:0,zel:victory&&archive?q.zel:0,
     karma:victory&&archive?q.karma:0,
     level:P.level,stored:typeof saveEnabled==='boolean'&&saveEnabled&&!saveRecoveryPending
   });
 }
 let rendered='';
 function refresh(){
   const s=snapshot();
   if(!s)return null;
   const sig=JSON.stringify(s);
   if(sig===rendered)return s;
   rendered=sig;
   block.hidden=!s.done;
   if(!s.done)return s;
   heading.textContent=(s.victory?'BATTLE CLEARED · ':'BATTLE DEFEAT · ')+s.name;
   reward.textContent=s.victory&&s.archive?
     'SIMULATED CAMPAIGN REWARDS: '+s.exp+' EXP · '+s.zel+' Zel · '+s.karma+' Karma · 1 demo summon token · 1 Training Shard':
     s.victory?'TRAINING CLEAR · No rewards or campaign progress':'DEFEAT · No rewards';
   meta.textContent=s.dungeon+' · '+s.liveUnits+'/'+s.totalUnits+' active allies survived · '+
     (s.archive?s.clears+' saved demo clears':'Training battle')+
     (s.victory&&s.archive?' · Summoner Lv.'+s.level:'')+
     (s.victory&&s.archive&&!s.stored?' · Save not confirmed; EXPORT your progress':'');
   replay.disabled=!s.canReplay;
   next.disabled=!s.nextId;next.textContent=s.nextId?'NEXT MISSION '+s.nextId+' ›':'NEXT STORY MISSION ›';
   scene.disabled=!s.clearScene;
   scene.hidden=!s.clearScene;
   return s;
 }
 function replayBattle(){
   const s=snapshot();if(!s?.canReplay||S.busy)return false;
   retry.click();rendered='';refresh();
   return !S.over&&!S.busy&&QUEST.missionId===s.missionId;
 }
 function advance(){
   const s=snapshot();if(!s||!s.nextId||!s.done||!s.victory||!s.archive)return false;
   const moved=story.advance();
   if(moved){rendered='';refresh();}
   return !!moved&&QUEST.missionId===s.nextId;
 }
 function readScene(){
   const s=snapshot();if(!s?.done||!s.clearScene)return false;
   const opened=scenes.read('clear',s.missionId);
   if(opened)document.getElementById('bf2200-reader')?.scrollIntoView({
     block:'start',behavior:'smooth'
   });
   return !!opened;
 }
 new MutationObserver(refresh).observe(output,{childList:true,characterData:true,subtree:true});
 document.getElementById('questinfo')&&
   new MutationObserver(refresh).observe(document.getElementById('questinfo'),{childList:true,subtree:true});
 document.querySelector('.bf-navbar')?.addEventListener('click',refresh);
 window.setInterval(()=>{if(!document.hidden)refresh();},850);
 refresh();
 window.BFGlobalBattleResultsV3000=Object.freeze({snapshot,refresh,replayBattle,advance,readScene});
})();
