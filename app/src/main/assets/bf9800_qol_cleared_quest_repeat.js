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
 // Legacy embeds may have no router. With the app router, repeating belongs
 // to Quest only; changing screens must not leave unattended battles running.
 const onQuest=()=>!window.BF_homeNav||window.BF_homeNav.current==='quest';
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
 // Longer opt-in runs are still finite and remain subject to the exact
 // saved-clear, active Auto, foreground, quest-change and defeat gates.
 for(const n of [1,2,5,10,20,50]){
   const opt=document.createElement('option');opt.value=String(n);
   opt.textContent=n+' additional clears';picker.append(opt);
 }
 // Preserve the original two-clear default after adding the opt-in one-clear choice.
 picker.value='2';
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
 // Preserve v98 compatibility with older embedded pages lacking the
 // original 2022 campaign gate. On the current Android page, refuse
 // unattended repeats if ANY authenticated source wave tuple or live
 // Energy/reward/prerequisite field is inconsistent. A recorded wave count
 // is not evidence of original enemy formations, AI or drop schedules.
 function sourceQuestMatches(missionId){
   const campaign=window.BFGrandGaiaCampaignV100;
   if(!campaign)return true;
   if(!Number.isSafeInteger(missionId)||missionId<=0||
      typeof campaign.waveReadiness!=='function')return false;
   try{
     const row=campaign.waveReadiness(missionId);
     if(!row||row.missionId!==missionId||
        !Number.isSafeInteger(row.verifiedWaveCount)||
        row.verifiedWaveCount<1||
        !Number.isSafeInteger(QUEST?.battles)||
        QUEST.missionId!==missionId||
        QUEST.battles!==row.verifiedWaveCount||
        (Number.isSafeInteger(S.totalWaves)&&
          S.totalWaves!==row.verifiedWaveCount))return false;
     if(typeof campaign.sourceEconomyReadiness==='function'&&
        campaign.sourceEconomyReadiness()===false)return false;
     return true;
   }catch(_){return false;}
 }
 function hasCommittedReceipt(s){
   // v322: only a committed canonical v7 clear count authorizes unattended
   // replay. Older embedded/mock result providers may lack this read-only
   // API; keep their preexisting behavior without writing storage here.
   const receipt=results.committedClearCount;
   if(typeof receipt!=='function')return true;
   if(!Number.isSafeInteger(s?.missionId)||
      !Number.isSafeInteger(s?.clears)||s.clears<1)return false;
   try{return receipt(s.missionId)===s.clears;}
   catch(_){return false;}
 }
 function statusSnapshot(){
   return freeze({active:!!session,missionId:session?.missionId||null,
     target:session?.target||0,completed:session?.completed??complete,
     reason});
 }
 function update(){
   const s=results.snapshot();
   const cleared=Number(s?.clears)>0;
   const eligible=!session&&onQuest()&&!document.hidden&&!S.busy&&
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
   // An already-checked but DISABLED native control is not proof that the
   // newly replayed battle can execute Auto. Allow the native victory state
   // (disabled + unchecked) only when clearing Auto before replay.
   if(auto.checked===on)return (!on||!auto.disabled)&&(!on||S.auto!==false);
   // Native controls can become disabled or reject a click while the
   // archive battle changes phase. Never assume Auto actually toggled.
   if(auto.disabled)return false;
   internalToggle=true;
   try{auto.click();}finally{internalToggle=false;}
   // A checked DOM checkbox is not an authoritative running Auto engine.
   // Fail closed if native combat explicitly reports Auto OFF.
   return auto.checked===on&&(!on||!auto.disabled)&&(!on||S.auto!==false);
 }
 function stop(why='Stopped',restore=true){
   const previous=session;
   if(previous){complete=previous.completed;session=null;}
   reason=why;
   // Player pressing Stop restores their own earlier Auto preference.
   // Unexpected aborts (defeat, failed save, changed quest or invalid clear)
   // must DISARM native Auto too, otherwise the repeat session stops while
   // the engine can continue unattended in subsequent rounds.
   if(previous){
     const wanted=restore?previous.autoWasEnabled:false;
     const toggled=setAuto(wanted);
     if(!wanted&&(!toggled||S.auto===true)){
       // The native checkbox may be DISABLED while still checked. Native
       // click() cannot clear it then, so fail closed in transient battle
       // state as well. Pending native timers inspect S.auto before acting.
       // This never changes P, reward calculations or the v7 save.
       S.auto=false;
       auto.checked=false;
     }
   }
   update();return !!previous;
 }
 function playAgain(){
   if(!session)return false;
   if(!onQuest()){leaveQuest();return false;}
   const s=results.snapshot();
   if(S.busy||S.mode!=='archive'||!s?.done||!s.victory||
      !s.archive||!s.stored||s.missionId!==session.missionId||
      QUEST?.missionId!==session.missionId||!s.canReplay||
      !sourceQuestMatches(session.missionId)){
     stop('Stopped: replay prerequisites changed',false);return false;
   }
   // Reset Auto at a completed result, then activate it on the fresh run.
   // A completed native result may disable its Auto checkbox until the
   // NEXT battle starts. Clear only an enabled, checked toggle before replay;
   // the authoritative enabled/checked gate is AFTER replayBattle().
   if(!setAuto(false)){
     stop('Stopped: native Auto control unavailable',false);return false;
   }
   if(!results.replayBattle()||S.over||
      QUEST?.missionId!==session.missionId){
     stop('Stopped: native mission replay failed',false);return false;
   }
   if(!setAuto(true)){
     // The native replay already started, but Auto cannot drive it. Disarm
     // the repeat session immediately; never queue an unattended next run.
     stop('Stopped: native Auto could not start',false);return false;
   }
   reason='Battle in progress';update();return true;
 }
 function start(count=Number(picker.value)){
   if(session||!Number.isSafeInteger(count)||
      ![1,2,5,10,20,50].includes(count))return false;
   const s=results.snapshot();
   if(!onQuest()||document.hidden||S.busy||S.mode!=='archive'||
      !s?.done||!s.victory||!s.archive||!s.stored||!s.canReplay||
      s.missionId!==QUEST?.missionId||
      !Number.isSafeInteger(s.clears)||s.clears<1||
      !hasCommittedReceipt(s)||!sourceQuestMatches(s.missionId))return false;
   session={missionId:s.missionId,target:count,completed:0,
     lastClear:s.clears,autoWasEnabled:auto.checked};
   complete=0;reason='Preparing replay';
   return playAgain();
 }
 function poll(){
   if(!session){update();return false;}
   if(!onQuest())return leaveQuest();
   if(document.hidden)return stop('Stopped: app left foreground',false);
   const s=results.snapshot();
   if(!s||s.missionId!==session.missionId||
      QUEST?.missionId!==session.missionId||
      S.mode!=='archive'||!s.archive)
     return stop('Stopped: quest or mode changed',false);
   if(!sourceQuestMatches(session.missionId))
     return stop('Stopped: verified 2022 quest record changed',false);
   // Native finish() deliberately unchecks Auto after every result, including
   // victory. Only treat Auto-off as cancellation while a battle is ongoing.
   if(!s.done){
     if(!auto.checked||S.auto===false)
       return stop('Stopped: Auto Battle disabled',false);
     update();return true;
   }
   if(!s.victory)return stop('Stopped: battle lost',false);
   if(!s.stored)return stop('Stopped: game save unavailable',false);
   if(!hasCommittedReceipt(s))
     return stop('Stopped: latest clear not committed to v7 save',false);
   if(!Number.isSafeInteger(s.clears)||s.clears<=session.lastClear)
     return stop('Stopped: new clear not confirmed',false);
   // One completed native battle can only earn one additional quest clear.
   // A jump by more than one is ambiguous (e.g. a save or replay race):
   // disarm Auto rather than counting it as a legitimate repeat.
   if(s.clears!==session.lastClear+1)
     return stop('Stopped: unexpected saved clear count',false);
   session.completed++;
   session.lastClear=s.clears;
   if(session.completed>=session.target)
     return stop('Finished '+session.target+' additional clears',true);
   return playAgain();
 }
 function leaveQuest(){
   const stopped=stop('Stopped: left Quest',false);
   if(stopped)setAuto(false); // Cancels the native timer; an in-flight round finishes.
   return stopped;
 }
 window.addEventListener('bf-route-change',()=>{
   if(session&&!onQuest())leaveQuest();
   else update();
 });
 go.addEventListener('click',()=>start());
 halt.addEventListener('click',()=>stop('Stopped by player',true));
 auto.addEventListener('change',()=>{
   if(session&&!internalToggle&&!auto.checked)stop('Stopped: Auto Battle disabled',false);
 });
 document.addEventListener('visibilitychange',()=>{
   // Browser-only background events must cancel native Auto as well as the
   // repeat session. Without this, poll() sleeps while hidden but Auto can
   // continue unattended after the foreground session is disarmed.
   if(document.hidden&&session){
     stop('Stopped: app left foreground',false);setAuto(false);
   }
 });
 // Native Activity pause can occur with document.hidden still false.
 // Cancel the whole replay session before any queued clear can start another.
 window.addEventListener('bf-native-background',()=>{
   if(session){stop('Stopped: Android background',false);setAuto(false);}
 });
 window.addEventListener('pagehide',()=>{
   if(session){stop('Stopped: page closed',false);setAuto(false);}
 });
 setInterval(()=>{if(!document.hidden)poll();},900);
 update();
 window.BFGlobalQoLQuestRepeatV9800=freeze({start,poll,stop,statusSnapshot});
})();
