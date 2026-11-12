/* BF_GRAND_GAIA_CONTINUE_V101 */
(() => {
 'use strict';
 if (window.BFGrandGaiaContinueV101 ||
     typeof QUESTS==='undefined' || QUESTS.length!==106 ||
     !window.BFQuestAreas || !window.BFGlobalQuestText ||
     !window.BFMorganMapV080 || !window.BFStLamiaMapV090 ||
     !window.BFGrandGaiaCampaignV100) return;
 const tabs=document.querySelector('.bf080-region-tabs');
 const host=document.querySelector('section.questpanel .bf-quest-archive-head');
 const list=document.getElementById('questlist');
 if(!host || !list || !tabs || tabs.querySelectorAll('button').length!==3 ||
    QUESTS[0]?.missionId!==1 || QUESTS[105]?.missionId!==365) return;
 const cleared=q=>(P.questClears?.[q.missionId]||0)>0;
 // A victory visible in memory is not proof that its clear was written.
 // The v3000 results module loads after this shortcut: resolve its existing
 // read-only canonical v7 receipt on each action, never cache a stale value.
 // Older isolated embeds without v3000 retain their original save gate;
 // a present but broken receipt provider must fail closed.
 function uncommittedVictory(){
   if(S?.mode!=='archive'||!S.over||S.phase!=='Victory')return false;
   try{
     const results=window.BFGlobalBattleResultsV3000;
     if(results===undefined)return false;
     if(typeof results?.committedClearCount!=='function')return true;
     const q=typeof QUEST==='undefined'?null:QUEST;
     const count=P.questClears?.[q?.missionId];
     if(!Number.isSafeInteger(q?.missionId)||q.missionId<=0||
        !Number.isSafeInteger(count)||count<1)return true;
     return results.committedClearCount(q.missionId)!==count;
   }catch(_){return true;}
 }
 // Match the result screen: an uncommitted canonical v7 victory never
 // enables Continue Story, even if a save adapter reports success.
 const awaitingSave=()=>(
   (typeof saveRecoveryPending==='boolean'&&saveRecoveryPending)||
   (!!S?.over&&S.phase==='Victory'&&
     (typeof saveEnabled!=='boolean'||!saveEnabled))||
   uncommittedVictory()
 );
 // A player Auto battle can be alive while S.busy is briefly false between
 // turns; a bounded repeat can own a victory screen while S.over is true.
 // Never redirect either unattended action into another story mission.
 // The optional repeat module is source-tested separately and may be absent
 // on older embedded pages. If present but broken, refuse navigation.
 function unattendedOwnsNavigation(){
   if(S?.mode==='archive'&&S.auto===true&&S.over===false)return true;
   const repeat=window.BFGlobalQoLQuestRepeatV9800;
   if(!repeat)return false;
   try{return typeof repeat.statusSnapshot!=='function'||
       repeat.statusSnapshot()?.active===true;}
   catch(_){return true;}
 }
 // Continue Story must use the SAME whole-catalog validation as the
 // campaign and post-victory Next controls. A corrupt later quest clear must
 // never be bypassed just because an earlier unlocked quest is available.
 const remaining=()=>{
   if(awaitingSave()||
      typeof window.BFGrandGaiaCampaignV100?.nextPlayable!=='function')return null;
   const next=window.BFGrandGaiaCampaignV100.nextPlayable();
   if(!next)return null;
   const q=QUESTS.find(row=>row.missionId===next.missionId);
   return q&&q.dungeonId===next.dungeonId&&q.battles===next.battles&&
     !cleared(q)&&questUnlocked(q)?q:null;
 };
 // Read-only 2022 original economy preview; v143 loads after this UI.
 // No source provider or mismatched tuple means no preview, never guessed
 // costs, drops or demo rewards. This has no effect on route eligibility.
 function sourceEconomyPreview(q){
   try{
     const api=window.BFOriginalGlobalQuestEnergyV14300;
     if(!q||!api||typeof api.lookup!=='function'||
        api.source?.year!==2022||api.source?.recordCount!==106||
        api.source?.sourceSha256!=='a1b36659dfc80bc6e1e0e244ba52b3c6d423b239cf684439a5488bf679764a66'||
        api.source?.staminaEnforced!==false||api.source?.saveMutation!==false)
       return null;
     const row=api.lookup(q.missionId);
     const expected=[q.missionId,q.dungeonId,q.requires,q.battles,
       q.energy,q.exp,q.zel,q.karma];
     if(!Array.isArray(row)||row.length!==8||
        row.some((v,i)=>!Number.isSafeInteger(v)||v<0||v!==expected[i]))
       return null;
     return Object.freeze({waves:row[3],energy:row[4],
       exp:row[5],zel:row[6],karma:row[7]});
   }catch(_){return null;}
 }
 const regionIndex=q=>q.dungeonId>=300?2:q.dungeonId>=200?1:0;
 const regionName=q=>['Mistral','Morgan','St. Lamia'][regionIndex(q)];
 const panel=document.createElement('section');
 panel.id='bf101-story-continue';
 panel.setAttribute('aria-label','Continue original Global story missions');
 panel.style.cssText='padding:11px;margin:10px 2px;border:1px solid #9b8057;border-radius:8px;background:#242e3d;color:#f9ead2;font:12px/1.4 system-ui,sans-serif';
 const heading=document.createElement('strong');
 heading.textContent='GRAND GAIA · CONTINUE STORY';
 heading.style.cssText='display:block;font:800 15px Georgia,serif;margin-bottom:7px';
 const status=document.createElement('p');status.id='bf101-status';
 status.setAttribute('aria-live','polite');status.style.cssText='margin:5px 0';
 const meter=document.createElement('div');
 meter.style.cssText='height:10px;background:#101723;border:1px solid #9f8e6c;border-radius:9px;overflow:hidden';
 meter.setAttribute('role','progressbar');
 meter.setAttribute('aria-label','Archived original story missions cleared');
 const fill=document.createElement('div');fill.id='bf101-progress-fill';
 fill.style.cssText='height:100%;width:0%;background:linear-gradient(90deg,#448ba8,#b9ecff)';
 meter.append(fill);
 const next=document.createElement('p');next.id='bf101-next';
 next.style.cssText='margin:8px 0';
 const button=document.createElement('button');button.id='bf101-continue';
 button.type='button';button.textContent='CONTINUE STORY ›';
 button.style.cssText='min-height:42px;padding:8px 14px;color:#fff;background:#745529;border:1px solid #dfbc7c;border-radius:5px;font-weight:800';
 // Explicit one-time native player action: route the NEXT verified story mission
 // and click existing Auto. Never run an unattended next-quest chain.
 const autoButton=document.createElement('button');
 autoButton.type='button';autoButton.id='bf101-continue-auto';
 autoButton.textContent='CONTINUE STORY + AUTO BATTLE';
 autoButton.style.cssText='min-height:44px;margin:5px 0 0 7px;padding:8px 12px;'+
   'background:#355b50;border:1px solid #8bc4b3;color:#fff;'+
   'border-radius:5px;font-weight:800;max-width:100%';
 const foot=document.createElement('small');
 foot.textContent='Original unlock requirements. Combat, drops and Energy spending remain offline DEMO.';
 foot.style.cssText='display:block;margin-top:7px;color:#d5dae1';
 panel.append(heading,status,meter,next,button,autoButton,foot);
 host.after(panel);
 function snapshot(){
   const n=arr=>arr.filter(cleared).length;
   return Object.freeze({total:106,done:n(QUESTS),
      mistral:n(QUESTS.slice(0,34)),morgan:n(QUESTS.slice(34,70)),
      stlamia:n(QUESTS.slice(70,106)),nextMission:remaining()?.missionId||null});
 }
 function refresh(){
    const s=snapshot(),q=remaining();
    status.textContent='Mistral '+s.mistral+'/34 · Morgan '+s.morgan+
       '/36 · St. Lamia '+s.stlamia+'/36 · Total '+s.done+'/106';
    fill.style.width=(s.done*100/106).toFixed(2)+'%';
    meter.setAttribute('aria-valuemin','0');
    meter.setAttribute('aria-valuemax','106');
    meter.setAttribute('aria-valuenow',String(s.done));
    const unattended=unattendedOwnsNavigation();
    button.disabled=!!S?.busy||unattended||!q;
    autoButton.disabled=!canContinueAuto(q);
    if(awaitingSave()){
      next.textContent='VICTORY NOT SAVED · Retry Save or download an unsaved backup before continuing.';
    }else if(unattended){
      next.textContent='AUTO BATTLE / REPEAT ACTIVE · Stop Auto or finish the current run before continuing.';
    }else if(q){
      const source=BFGlobalQuestText.sourceFor(q);
      const economy=sourceEconomyPreview(q);
      next.textContent='NEXT: '+(source?.mission?.name||'Mission '+q.missionId)+
         ' · '+regionName(q)+' · Mission '+q.missionId+
         (economy?' · 2022 source reference: '+economy.waves+' waves · Energy '+
           economy.energy+' · EXP '+economy.exp+' · Zel '+economy.zel+
           ' · Karma '+economy.karma+' (DEMO credits EXP/Zel/Karma on clear; stamina not enforced)':'');
    }else next.textContent=s.done===106?
      'All 106 archived story missions cleared (DEMO combat).' :
      'No further mission currently unlocked. Check the preceding requirement.';
    return s;
 }
 // Full authenticated 2022 scalar economy and wave-COUNT only;
 // this does NOT certify any original enemy formation, AI or drop table.
 function sourceReadyForAuto(q){
   try{
     const source=window.BFGrandGaiaCampaignV100;
     if(typeof source?.waveReadiness!=='function'||
        typeof source?.sourceEconomyReadiness!=='function'||
        source.sourceEconomyReadiness()!==true)return false;
     const row=source.waveReadiness(q.missionId);
     return !!row&&row.missionId===q.missionId&&
       row.dungeonId===q.dungeonId&&
       Number.isSafeInteger(row.verifiedWaveCount)&&
       row.verifiedWaveCount===q.battles&&
       Number.isSafeInteger(q.battles)&&q.battles>0;
   }catch(_){return false;}
 }
 function canContinueAuto(q){
   try{
     if(q===undefined)q=remaining();
     const auto=document.getElementById('auto');
     const nav=window.BF_homeNav;
     if(!q||!S||S.busy||S.auto===true||awaitingSave()||
        unattendedOwnsNavigation()||document.hidden||
        nav&&nav.current!=='quest'||!auto||
        auto.type!=='checkbox'||auto.checked||
        // A completed victory/defeat disables native Auto until choosing
        // the next mission. Only a LIVE disabled checkbox blocks routing.
        (auto.disabled&&!S.over)||
        !Array.isArray(S.party)||
        // Never discard a manually queued live turn by changing missions.
        !S.over&&S.party.some(p=>p?.action)||
        !sourceReadyForAuto(q))return false;
     return true;
   }catch(_){return false;}
 }
 function disarmContinueAuto(){
   // A successful native mission selection followed by an Auto failure
   // remains a normal MANUAL battle. Do not edit rewards, P or the v7 save.
   S.auto=false;
   const auto=document.getElementById('auto');
   if(auto)auto.checked=false;
 }
 function continueAuto(){
   const q=remaining();
   if(!canContinueAuto(q))return false;
   const auto=document.getElementById('auto');
   let selected=false;
   try{selected=BFQuestAreas.choose(q)===true;}catch(_){selected=false;}
   if(!selected)return false;
   // Keep the native region tabs consistent with normal Continue Story.
   try{tabs.querySelectorAll('button')[regionIndex(q)]?.click();}
   catch(_){disarmContinueAuto();refresh();return false;}
   // Native selection/route and wave count must still match before Auto.
   if(typeof QUEST==='undefined'||QUEST?.missionId!==q.missionId||
      S.mode!=='archive'||S.busy||S.over||S.auto===true||
      !Number.isSafeInteger(S.totalWaves)||
      S.totalWaves!==q.battles||auto.disabled||auto.checked){
     disarmContinueAuto();refresh();return false;
   }
   try{auto.click();}catch(_){disarmContinueAuto();refresh();return false;}
   if(!auto.checked||auto.disabled||S.auto!==true||
      S.over||QUEST?.missionId!==q.missionId){
     disarmContinueAuto();refresh();return false;
   }
   refresh();return true;
 }
 autoButton.addEventListener('click',()=>continueAuto());
 button.addEventListener('click',()=>{
   const q=remaining();
   if(!q||S?.busy||awaitingSave()||unattendedOwnsNavigation()||
      !BFQuestAreas.choose(q))return;
   // Native tab click also hides St. Lamia when returning to other regions.
   tabs.querySelectorAll('button')[regionIndex(q)]?.click();
   refresh();
   document.getElementById('bf-quest-details')?.scrollIntoView({block:'start',behavior:'smooth'});
 });
 new MutationObserver(refresh).observe(list,{childList:true});
 document.querySelector('.bf-navbar')?.addEventListener('click',refresh);
 refresh();
 // Shared fail-closed route gate for every story navigation shortcut.
 // A disabled button is only presentation: callers must re-check on click.
 function canNavigate(){
   try{return !S?.busy&&!awaitingSave()&&!unattendedOwnsNavigation();}
   catch(_){return false;}
 }
 window.BFGrandGaiaContinueV101=Object.freeze({snapshot,refresh,canNavigate,canContinueAuto,continueAuto,
   get nextMission(){return remaining()?.missionId||null}});
})();
