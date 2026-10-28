/* BF_GLOBAL_2022_DUNGEON_FIRST_CLEAR_REWARD_SOURCE_V15500 */
(() => {
 'use strict';
 // Original 2022 missionRewards string: 8:0:1:0:0. Type-8 Gem meaning
 // corroborated by original Achievement rows and historical documentation.
 // NO Gem wallet, one-time claim or 2022 enemy drop semantics inferred.
 const previous=window.BFGlobalEncounterReferencesV15100;
 if(window.BFGlobalOriginalFirstClearRewardsV15500||
    !previous||previous.summary?.archivedMissions!==142||
    previous.summary?.playableMissions!==106||
    previous.summary?.meaningDecoded!==false||
    typeof P==='undefined'||P.version!==7||
    !P.questClears||typeof P.questClears!=='object'||
    typeof QUESTS==='undefined'||!Array.isArray(QUESTS)||QUESTS.length!==106)return;
 const ids=[12,23,33,43,53,63,73,85,204,214,224,234,244,254,265,
   304,314,324,334,344,354,365,404,414,424,434,444,454,465];
 if(ids.length!==29||new Set(ids).size!==29)return;
 const liveSet=new Set(QUESTS.map(q=>q.missionId));
 if(ids.slice(0,22).some(id=>!liveSet.has(id))||
    ids.slice(22).some(id=>liveSet.has(id)))return;
 const host=document.getElementById('bf10800-encounter-ledger');
 if(!host)return;
 const freeze=Object.freeze;
 const rows=freeze(ids.map((id,i)=>freeze({
   missionId:id,sourceReward:'8:0:1:0:0',
   sourceRewardType:8,sourceRewardItemId:0,sourceAmount:1,
   gemMeaningCrossCorroborated:true,
   liveInDemo:i<22,amdahlSourceOnly:i>=22,
   originalClaimMechanismKnown:false,
   liveGemGrantEnabled:false
 })));
 const byId=new Map(rows.map(r=>[r.missionId,r]));
 const source=freeze({
   year:2022,originalArchiveSha256:
     '69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9',
   originalMissionMasterSha256:'d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83',
   originalRewardRowsSha256:'de8bde1cbee451e3c1b07c8b3e47afd38bc0465787b2b4aa6f5c8a620c4c83a7',
   originalSourceRewardCount:29,liveStoryQuestRewardCount:22,
   amdahlSourceOnlyRewardCount:7,
   gemEnumCrossCorroborated:true,
   nativeFirstClearClaimSemanticsConfirmed:false,
   originalWalletMigrated:false,liveGemGrantEnabled:false,
   actualGemsGranted:0,saveMutation:false
 });
 const panel=document.createElement('details');
 panel.id='bf15500-first-clear-sources';
 panel.style.cssText='margin:10px 4px;padding:10px;border:1px solid #a58b60;'+
   'border-radius:7px;background:#3b3425;color:#f7f0d9;font:12px/1.5 system-ui';
 const title=document.createElement('summary');
 title.style.cssText='font-weight:750;cursor:pointer;min-height:38px';
 title.textContent='ORIGINAL 2022 FIRST-CLEAR REWARDS · SOURCE ONLY';
 const select=document.createElement('select');select.id='bf15500-mission';
 select.setAttribute('aria-label','Original dungeon completion reward source');
 select.style.cssText='margin:9px 0;width:100%;min-height:42px;background:#414232;color:#fff';
 for(const row of rows){
   const opt=document.createElement('option');
   opt.value=String(row.missionId);
   opt.textContent='Mission '+row.missionId+(row.amdahlSourceOnly?' · Amdahl source only':' · live demo quest');
   select.append(opt);
 }
 const detail=document.createElement('p');detail.id='bf15500-source-detail';
 const caveat=document.createElement('small');
 caveat.textContent='Original source reward code 8:0:1:0:0 is strongly corroborated '+
   'as one Gem by original milestone reward rows and historical Global descriptions. '+
   'This is NOT an enabled Gem reward. Native one-time claiming, retroactive migration, '+
   'and original enemy drops remain unverified. The seven Amdahl finales are not playable.';
 panel.append(title,select,detail,caveat);
 host.after(panel);
 function lookup(id){return Number.isSafeInteger(id)?byId.get(id)||null:null;}
 function refresh(){
   const row=lookup(Number(select.value));
   if(!row)return null;
   const n=P.questClears?.[row.missionId];
   const localClear=Number.isSafeInteger(n)&&n>0;
   detail.textContent='Mission #'+row.missionId+
     ' · archived source first-completion reward: 1 Gem (type 8; source corroborated)'+
     ' · '+(row.liveInDemo?'existing playable DEMO mission':'NON-PLAYABLE Amdahl source')+
     ' · local DEMO clear recorded: '+(localClear?'YES':'NO')+
     ' · original claim status: UNKNOWN · Gems granted here: ZERO';
   return row;
 }
 select.addEventListener('change',refresh);
 refresh();
 window.BFGlobalOriginalFirstClearRewardsV15500=freeze({source,rows,lookup,refresh});
})();
