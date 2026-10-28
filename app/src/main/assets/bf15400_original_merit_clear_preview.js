/* BF_GLOBAL_2022_QUEST_CLEAR_MERIT_PREVIEW_V15400 */
(() => {
 'use strict';
 // Preview source conditions against saved local DEMO clears, not an original
 // claimed-achievement ledger, native cumulative counter or Merit economy.
 const stone=window.BFGlobalOriginalLegendStoneExchangeV15300;
 if(window.BFGlobalOriginalMeritQuestPreviewV15400||
    !stone||stone.source?.archiveSha256!==
      '69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'||
    stone.source?.originalPrice!==4000||stone.source?.liveAcquisition!==false||
    typeof P==='undefined'||P.version!==7||!Array.isArray(P.roster)||
    !P.questClears||typeof P.questClears!=='object'||Array.isArray(P.questClears)||
    typeof QUESTS==='undefined'||!Array.isArray(QUESTS)||QUESTS.length!==106||
    !QUESTS.some(q=>q.missionId===365)||QUESTS.some(q=>q.missionId===90))return;
 const host=document.getElementById('bf15300-legend-stone-source');
 if(!host)return;
 const sourceRows=[[34000,10,100],[34010,100,200],[34020,1000,400],
   [34025,5000,600],[34030,10000,800],[34032,20000,1500],
   [34034,30000,2500],[34036,40000,3500],[34040,50000,5000],
   [34050,60000,6000],[34060,70000,7000]];
 if(sourceRows.length!==11||sourceRows.some((row,i)=>
    row.length!==3||!row.every(Number.isSafeInteger)||
    row[0]<34000||row[0]>34060||row[1]<10||
    row[2]<100||(i>0&&row[1]<=sourceRows[i-1][1])))return;
 const freeze=Object.freeze;
 const rows=freeze(sourceRows.map(([achievementId,threshold,merit])=>
    freeze({achievementId,originalQuestCountThreshold:threshold,
      originalMeritPointReward:merit})));
 const source=freeze({
    year:2022,
    archiveSha256:'69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9',
    achievementTableSha256:'36850eac317faf97f6196d8078b56d8a2594847eb2a727917b0d1bd1485efb56',
    sourceMilestoneCount:11,originalQuestClearAchievementType:8500,
    originalStoryClearAchievementId:35000,originalStoryClearMissionId:365,
    originalStoryClearMeritReward:100,bonusAchievementMissionId:90,
    bonusMissionInLiveCatalog:false,
    localQuestCountNotNative:true,originalAchievementClaimStatusUnknown:true,
    meritAwardEnabled:false,playableContentChanged:false,saveMutation:false
 });
 function snapshot(){
   const record=P.questClears;
   if(!record||typeof record!=='object'||Array.isArray(record))return null;
   let localClears=0;
   for(const key of Object.keys(record)){
     if(!/^[1-9]\d*$/.test(key)||!Number.isSafeInteger(Number(key)))return null;
     let count=record[key];
     if(typeof count==='string'&&/^(0|[1-9]\d*)$/.test(count))count=Number(count);
     if(!Number.isSafeInteger(count)||count<0||
        !Number.isSafeInteger(localClears+count))return null;
     localClears+=count;
   }
   const story=P.questClears[365];
   let storyCount=story===undefined?0:story;
   if(typeof storyCount==='string'&&/^(0|[1-9]\d*)$/.test(storyCount))
     storyCount=Number(storyCount);
   if(!Number.isSafeInteger(storyCount)||storyCount<0)return null;
   return freeze({
     localDemoQuestClearCount:localClears,
     creatorOfWorldClearRecorded:storyCount>0,
     sourceMilestones:freeze(rows.map(r=>freeze({
       achievementId:r.achievementId,originalRequirement:r.originalQuestCountThreshold,
       originalMeritReward:r.originalMeritPointReward,
       localDemoThresholdReached:localClears>=r.originalQuestCountThreshold,
       originalAchievementClaimed:null,claimStatusVerified:false
     }))),
     actualMeritPointsGrantedByPreview:0,saveChanged:false
   });
 }
 const panel=document.createElement('details');
 panel.id='bf15400-original-merit-progress';
 panel.style.cssText='margin:9px 4px;padding:10px;border:1px solid #7a96af;'+
   'border-radius:7px;background:#263743;color:#eef6fa;font:12px/1.55 system-ui';
 const title=document.createElement('summary');
 title.style.cssText='font-weight:750;cursor:pointer;min-height:37px';
 title.textContent='2022 ORIGINAL MERIT MILESTONES · LOCAL CLEAR PREVIEW';
 const result=document.createElement('p');result.id='bf15400-count';
 const storyline=document.createElement('p');storyline.id='bf15400-story';
 const list=document.createElement('ol');list.id='bf15400-milestones';
 const disclaimer=document.createElement('small');
 disclaimer.textContent='Original 2022 threshold/reward references, compared with local DEMO '+
    'quest-clear records only. This does NOT establish original server achievement '+
    'claims, original total quest count, or spendable Merit Points. Nothing is '+
    'claimed, granted or saved. The original bonus-dungeon achievement for '+
    'mission #90 is not locally playable.';
 panel.append(title,result,storyline,list,disclaimer);
 host.after(panel);
 function refresh(){
   const snap=snapshot();
   list.replaceChildren();
   if(!snap){
     result.textContent='Local clear records are not reliably readable.';
     storyline.textContent='No original achievement status inferred.';
     return null;
   }
   result.textContent='Local DEMO quest clears: '+
     snap.localDemoQuestClearCount.toLocaleString('en-US')+' · not original server progress';
   storyline.textContent='2022 source: "Creator of the World" (mission #365), '+
     'original 100 Merit Points · local clear recorded: '+
     (snap.creatorOfWorldClearRecorded?'YES':'NO')+
     ' · achievement claimed: UNKNOWN';
   for(const m of snap.sourceMilestones){
     const li=document.createElement('li');
     li.textContent=m.originalRequirement.toLocaleString('en-US')+
       ' quests · original '+m.originalMeritReward.toLocaleString('en-US')+
       ' Merit Points · local threshold: '+
       (m.localDemoThresholdReached?'REACHED':'not reached')+
       ' · official claim: UNKNOWN';
     list.append(li);
   }
   return snap;
 }
 panel.addEventListener('toggle',()=>{if(panel.open)refresh();});
 refresh();
 window.BFGlobalOriginalMeritQuestPreviewV15400=freeze({source,rows,snapshot,refresh});
})();
