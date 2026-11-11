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
 const retrySave=make('bf3000-retry-save','RETRY SAVE',()=>retrySaveResult());
 const backup=make('bf3000-backup','DOWNLOAD UNSAVED BACKUP',()=>downloadBackup());
 retrySave.hidden=backup.hidden=true;
 const note=document.createElement('small');note.id='bf3000-note';
 note.textContent='Offline simulated battle rewards. Original archived quest titles and reward amounts are source metadata; enemy AI, enemy waves, materials, drops, and Energy spending remain DEMO. Training grants no campaign rewards.';
 block.append(heading,reward,meta,buttons,note);
 nativeResult.append(block);
 // Read-only authoritative receipt for a specific archived quest clear.
 // The in-memory counter and saveEnabled boolean alone do not prove that
 // the latest clear was committed to the canonical version-7 save.
 function committedClearCount(missionId){
   if(!Number.isSafeInteger(missionId)||missionId<=0)return null;
   try{
     const raw=localStorage.getItem('bf_global_offline_demo_v7');
     if(typeof raw!=='string'||raw.length<2||raw.length>1048576)return null;
     const data=JSON.parse(raw),clears=data?.questClears;
     if(data?.version!==7||!clears||typeof clears!=='object'||
        Array.isArray(clears))return null;
     const n=clears[missionId]??0;
     return Number.isSafeInteger(n)&&n>=0?n:null;
   }catch(_){return null;}
 }
 function snapshot(){
   const q=typeof QUEST==='undefined'?null:QUEST;
   if(!q||!S)return null;
   const done=!!S.over&&!S.busy;
   const victory=done&&S.phase==='Victory';
   const archive=S.mode==='archive';
   const cleared=(P.questClears?.[q.missionId]||0)>0;
   const status=story.snapshot();
   // A failed canonical v7 save cannot unlock another story mission. The
   // player must first restore writable storage or export their progress.
   // A saveEnabled flag can remain true after a stale/corrupt external
   // restore or a failed write adapter. A playable archived victory is
   // committed only when the canonical v7 save contains its exact clear
   // count. Next, scene and replay must all share this gate.
   const count=P.questClears?.[q.missionId];
   const receiptOk=!archive||!victory||
     (Number.isSafeInteger(count)&&count>0&&
      committedClearCount(q.missionId)===count);
   const stored=typeof saveEnabled==='boolean'&&saveEnabled&&
     !saveRecoveryPending&&receiptOk;
   const after=archive&&victory&&cleared&&stored?status?.nextId||null:null;
   // A newly earned clear scene is also gated on committed v7 progress.
   const clearScene=archive&&victory&&cleared&&stored&&[10,11,21].includes(q.missionId)&&
       !!scenes.lookup('clear',q.missionId);
   const reference=BFGlobalQuestText.sourceFor(q);
   const party=Array.isArray(S.party)?S.party.filter(u=>u&&u.active):[];
   return Object.freeze({
     missionId:q.missionId,name:reference?.mission?.name||'Mission '+q.missionId,
     dungeon:reference?.dungeon?.name||'Dungeon '+q.dungeonId,
     done,victory,archive,clears:P.questClears?.[q.missionId]||0,
     nextId:after,clearScene,
     // Uncommitted victory rewards must remain exportable, not discarded by
     // an eager replay. Defeats and Training have no campaign payout.
     canReplay:done&&!retry.disabled&&(!victory||!archive||stored),
     liveUnits:party.filter(u=>u.hp>0).length,totalUnits:party.length,
     exp:victory&&archive?q.exp:0,zel:victory&&archive?q.zel:0,
     karma:victory&&archive?q.karma:0,
     level:P.level,stored
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
   const rescue=s.done&&s.victory&&s.archive&&!s.stored;
   retrySave.hidden=backup.hidden=!rescue;
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
 function retrySaveResult(){
   const s=snapshot();
   if(!s?.done||!s.victory||!s.archive||s.stored||S.busy||
      typeof saveProgress!=='function')return false;
   // Explicit opt-in only; use the native canonical v7 write and its usual
   // quota/recovery checks. Never claim success from a failed write.
   // A storage adapter can throw instead of returning a failed write.
   // Keep the unsaved victory and its explicit recovery controls intact.
   let ok=false;
   try{ok=saveProgress()===true;}catch(_){ok=false;}
   rendered='';refresh();
   // Retry Save may change the canonical victory receipt without rebuilding
   // the quest list. Refresh the existing read-only Continue Story shortcut
   // immediately on success or failure, never allowing optional UI failures
   // to replace the native save result or write a second save.
   try{
     const storyShortcut=window.BFGrandGaiaContinueV101;
     if(typeof storyShortcut?.refresh==='function')storyShortcut.refresh();
   }catch(_){/* Older or broken optional UI must not block save recovery. */}
   return ok&&snapshot()?.stored===true;
 }
 function downloadBackup(){
   const s=snapshot();
   if(!s?.done||!s.victory||!s.archive||s.stored||S.busy)return false;
   // Delegate to the same existing Android/browser export path; no new
   // serialization, alternate save format, or hidden storage writes.
   const action=document.getElementById('downloadsave');
   if(!action)return false;
   action.click();return true;
 }
 function replayBattle(){
   const s=snapshot();if(!s?.canReplay||S.busy)return false;
   retry.click();rendered='';refresh();
   return !S.over&&!S.busy&&QUEST.missionId===s.missionId;
 }
 function advance(){
   const s=snapshot();if(!s||!s.stored||!s.nextId||!s.done||!s.victory||!s.archive)return false;
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
 window.BFGlobalBattleResultsV3000=Object.freeze({snapshot,refresh,replayBattle,advance,readScene,committedClearCount});
})();
