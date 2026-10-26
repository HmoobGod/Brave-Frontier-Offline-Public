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
 const remaining=()=>QUESTS.find(q=>!cleared(q)&&questUnlocked(q))||null;
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
 const foot=document.createElement('small');
 foot.textContent='Original unlock requirements. Combat, drops and Energy spending remain offline DEMO.';
 foot.style.cssText='display:block;margin-top:7px;color:#d5dae1';
 panel.append(heading,status,meter,next,button,foot);
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
    button.disabled=!!S?.busy||!q;
    if(q){
      const source=BFGlobalQuestText.sourceFor(q);
      next.textContent='NEXT: '+(source?.mission?.name||'Mission '+q.missionId)+
         ' · '+regionName(q)+' · Mission '+q.missionId;
    }else next.textContent=s.done===106?
      'All 106 archived story missions cleared (DEMO combat).' :
      'No further mission currently unlocked. Check the preceding requirement.';
    return s;
 }
 button.addEventListener('click',()=>{
   const q=remaining();
   if(!q||S?.busy||!BFQuestAreas.choose(q))return;
   // Native tab click also hides St. Lamia when returning to other regions.
   tabs.querySelectorAll('button')[regionIndex(q)]?.click();
   refresh();
   document.getElementById('bf-quest-details')?.scrollIntoView({block:'start',behavior:'smooth'});
 });
 new MutationObserver(refresh).observe(list,{childList:true});
 document.querySelector('.bf-navbar')?.addEventListener('click',refresh);
 refresh();
 window.BFGrandGaiaContinueV101=Object.freeze({snapshot,refresh,
   get nextMission(){return remaining()?.missionId||null}});
})();
