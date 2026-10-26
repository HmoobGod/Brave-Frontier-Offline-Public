/* BF_GLOBAL_QOL_CLEARED_QUEST_REPEAT_V9800 */
(() => {
 'use strict';
 // QoL orchestration only: replay via existing v30 result action and the
 // existing Auto Battle checkbox. No new combat, rewards, Energy or save rules.
 const results=window.BFGlobalBattleResultsV3000;
 const host=document.getElementById('bf2000-run');
 const auto=document.getElementById('auto');
 if(window.BFGlobalQoLQuestRepeatV9800||!results||
   typeof results.snapshot!=='function'||typeof results.replayBattle!=='function'||
   !host||!auto||typeof P==='undefined'||P.version!==7||
   typeof S==='undefined'||typeof QUEST==='undefined')return;
 const freeze=Object.freeze;
 let session=null,complete=0,reason='Idle',internalToggle=false;
 const panel=document.createElement('details');panel.id='bf9800-auto-repeat';
 panel.style.cssText='margin:9px 2px;padding:10px;border:1px solid #a6b986;'+
   'border-radius:7px;background:#273621;color:#eaf4d5;font:12px/1.5 system-ui,sans-serif';
 const heading=document.createElement('summary');
 heading.textContent='QoL · AUTO-REPEAT CLEARED QUESTS';
 heading.style.cssText='cursor:pointer;min-height:37px;font-weight:800';
 const note=document.createElement('p');
 note.textContent='Opt in after a real DEMO victory on an already-cleared quest. '+
   'Uses the existing replay + Auto Battle; stops on defeat, navigation, '+
   'interruption or after a chosen number of ADDITIONAL clears. '+
   'Native Energy costs and drops are not yet reconstructed.';
 const picker=document.createElement('select');picker.id='bf9800-repeat-count';
 picker.setAttribute('aria-label','Number of additional quest clears');
 picker.style.cssText='padding:7px;min-height:42px;background:#172820;'+
   'border:1px solid #a6b986;border-radius:5px;color:#f4f6e9';
 for(const n of [2,5,10]){
   const opt=document.createElement('option');opt.value=String(n);
   opt.textContent=n+' additional clears';picker.append(opt);
 }
 const go=document.createElement('button');
 go.id='bf9800-start';go.type='button';go.textContent='START AUTO-REPEAT';
 const halt=document.createElement('button');
 halt.id='bf9800-stop';halt.type='button';halt.textContent='STOP REPEATING';
 for(const b of [go,halt]){
   b.style.cssText='margin:3px;min-height:42px;padding:8px;'+
     'background:#46633a;color:white;border:1px solid #afc39c;border-radius:5px';
 }
 const status=document.createElement('p');status.id='bf9800-status';
 status.setAttribute('role','status');
 panel.append(heading,note,picker,go,halt,status);host.after(panel);
 function statusSnapshot(){
   return freeze({active:!!session,missionId:session?.missionId||null,
     target:session?.target||0,completed:session?.completed??complete,
     reason});
 }
 function update(){
   const s=results.snapshot();
   const cleared=Number(s?.clears)>0;
   const eligible=!session&&!document.hidden&&!S.busy&&
     S.mode==='archive'&&!!s?.done&&!!s.victory&&!!s.archive&&!!s.stored&&
     !!s.canReplay&&cleared&&s.missionId===QUEST?.missionId;
   go.disabled=!eligible;
   picker.disabled=!!session;halt.disabled=!session;
   status.textContent=session?
     'REPEATING MISSION '+session.missionId+' · '+session.completed+'/'+
       session.target+' additional clears complete · '+reason:
     (reason==='Idle'?'Complete a previously cleared quest to enable auto-repeat':reason);
   return statusSnapshot();
 }
 function setAuto(on){
   if(auto.checked===on)return;
   internalToggle=true;
   try{auto.click();}finally{internalToggle=false;}
 }
 function stop(why='Stopped',restore=true){
   const previous=session;
   if(previous){complete=previous.completed;session=null;}
   reason=why;
   if(restore&&previous&&!S.busy)setAuto(previous.autoWasEnabled);
   update();return !!previous;
 }
 function playAgain(){
   if(!session)return false;
   const s=results.snapshot();
   if(S.busy||S.mode!=='archive'||!s?.done||!s.victory||
      !s.archive||!s.stored||s.missionId!==session.missionId||
      QUEST?.missionId!==session.missionId||!s.canReplay){
     stop('Stopped: replay prerequisites changed',false);return false;
   }
   // Reset Auto at a completed result, then activate it on the fresh run.
   setAuto(false);
   if(!results.replayBattle()||S.over||
      QUEST?.missionId!==session.missionId){
     stop('Stopped: native mission replay failed',false);return false;
   }
   setAuto(true);
   reason='Battle in progress';update();return true;
 }
 function start(count=Number(picker.value)){
   if(session||!Number.isInteger(count)||![2,5,10].includes(count))return false;
   const s=results.snapshot();
   if(document.hidden||S.busy||S.mode!=='archive'||
      !s?.done||!s.victory||!s.archive||!s.stored||!s.canReplay||
      s.missionId!==QUEST?.missionId||
      !Number.isSafeInteger(s.clears)||s.clears<1)return false;
   session={missionId:s.missionId,target:count,completed:0,
     lastClear:s.clears,autoWasEnabled:auto.checked};
   complete=0;reason='Preparing replay';
   return playAgain();
 }
 function poll(){
   if(!session){update();return false;}
   if(document.hidden)return stop('Stopped: app left foreground',false);
   const s=results.snapshot();
   if(!s||s.missionId!==session.missionId||
      QUEST?.missionId!==session.missionId||
      S.mode!=='archive'||!s.archive)
     return stop('Stopped: quest or mode changed',false);
   // Native finish() deliberately unchecks Auto after every result, including
   // victory. Only treat Auto-off as cancellation while a battle is ongoing.
   if(!s.done){
     if(!auto.checked)return stop('Stopped: Auto Battle disabled',false);
     update();return true;
   }
   if(!s.victory)return stop('Stopped: battle lost',false);
   if(!s.stored)return stop('Stopped: game save unavailable',false);
   if(!Number.isSafeInteger(s.clears)||s.clears<=session.lastClear)
     return stop('Stopped: new clear not confirmed',false);
   session.completed++;
   session.lastClear=s.clears;
   if(session.completed>=session.target)
     return stop('Finished '+session.target+' additional clears',true);
   return playAgain();
 }
 go.addEventListener('click',()=>start());
 halt.addEventListener('click',()=>stop('Stopped by player',true));
 auto.addEventListener('change',()=>{
   if(session&&!internalToggle&&!auto.checked)stop('Stopped: Auto Battle disabled',false);
 });
 document.addEventListener('visibilitychange',()=>{
   if(document.hidden&&session)stop('Stopped: app left foreground',false);
 });
 window.addEventListener('pagehide',()=>{if(session)stop('Stopped: page closed',false)});
 setInterval(()=>{if(!document.hidden)poll();},900);
 update();
 window.BFGlobalQoLQuestRepeatV9800=freeze({start,poll,stop,statusSnapshot});
})();
