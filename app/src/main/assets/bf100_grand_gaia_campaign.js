/* BF_GRAND_GAIA_CAMPAIGN_V100 */
(() => {
 'use strict';
 if(window.BFGrandGaiaCampaignV100) return;
 if(!window.BFMistralMap || !window.BFMorganMapV080 || !window.BFStLamiaMapV090 ||
    !window.BFQuestAreas || typeof QUESTS==='undefined' || QUESTS.length!==106) return;
 const regions=Object.freeze([
  Object.freeze({name:'Mistral',key:'mistral',ids:[1,10,20,30,40,50,60,70,80],required:0}),
  Object.freeze({name:'Morgan',key:'morgan',ids:[200,210,220,230,240,250,260],required:85}),
  Object.freeze({name:'St. Lamia',key:'stlamia',ids:[300,310,320,330,340,350,360],required:265})
 ]);
 const tabs=document.querySelector('.bf080-region-tabs');
 const list=document.getElementById('questlist');
 if(!tabs || !list || tabs.querySelectorAll('button').length!==3)return;
 const idset=new Set(regions.flatMap(r=>r.ids));
 if(idset.size!==23 || QUESTS.some(q=>!idset.has(q.dungeonId)))return;
 const style=document.createElement('style');
 style.id='bf100-campaign-style';
 style.textContent=[
  '#bf100-campaign{padding:12px 10px;margin:10px 0;border:1px solid #bb9860;',
  'border-radius:8px;background:linear-gradient(165deg,#182b44,#192233);color:#f6e9d5}',
  '#bf100-campaign h3{margin:0;font:800 16px Georgia,serif;letter-spacing:.03em}',
  '#bf100-campaign .bf100-subtitle{display:block;font:11px/1.5 Arial,sans-serif;color:#e1d0b6}',
  '.bf100-overall{margin:7px 0;font:700 13px Arial,sans-serif}',
  '.bf100-region-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));',
  'gap:7px;margin-top:8px}',
  '.bf100-region{display:flex;flex-direction:column;min-height:75px;padding:8px 5px;',
  'gap:4px;background:#253951;border:1px solid #8b9ab3;border-radius:5px;',
  'color:#fff;cursor:pointer;text-align:center}',
  '.bf100-region strong{font:700 12px Arial,sans-serif}',
  '.bf100-region small{font:11px Arial,sans-serif;color:#ddd}',
  '.bf100-region[aria-pressed=true]{border-color:#a3edfc;outline:1px solid #9edff0}',
  '.bf100-region progress{width:100%;height:7px;accent-color:#80cddc}',
  '#bf100-campaign .bf100-foot{display:block;margin-top:7px;',
  'font:10px/1.45 Arial,sans-serif;color:#c6d3dd}'
 ].join('');
 document.head.append(style);
 const section=document.createElement('section');
 section.id='bf100-campaign';
 section.setAttribute('aria-label','Source-backed offline Grand Gaia story progress');
 const header=document.createElement('h3');
 header.textContent='GRAND GAIA · CAMPAIGN PROGRESS';
 const hint=document.createElement('small');
 hint.className='bf100-subtitle';
 hint.textContent='Three original regions · 23 dungeons · 106 archived missions';
 const total=document.createElement('p');
 total.className='bf100-overall';
 total.setAttribute('aria-live','polite');
 const grid=document.createElement('div');grid.className='bf100-region-grid';
 const footer=document.createElement('small');
 footer.className='bf100-foot';
 footer.textContent='Original quest data and scenery. Battle enemies, AI, drops and combat calculations remain DEMO; archive Energy is not spent.';
 const controls=new Map();
 for(const region of regions){
   const button=document.createElement('button');
   button.type='button';button.className='bf100-region';
   button.dataset.bfCampaignRegion=region.key;
   const name=document.createElement('strong');name.textContent=region.name;
   const count=document.createElement('small');
   const bar=document.createElement('progress');
   bar.setAttribute('aria-label',region.name+' missions cleared');
   button.append(name,count,bar);
   button.addEventListener('click',()=>{
     if(region.key==='mistral')tabs.children[0].click();
     else if(region.key==='morgan')tabs.children[1].click();
     else tabs.children[2].click();
     refresh();
   });
   controls.set(region.key,{button,count,bar});
   grid.append(button);
 }
 section.append(header,hint,total,grid,footer);
 tabs.before(section);
 function summary(){
   const entries=regions.map(r=>{
     const quests=QUESTS.filter(q=>r.ids.includes(q.dungeonId));
     const cleared=quests.filter(q=>(P.questClears?.[q.missionId]||0)>0).length;
     const unlocked=quests.some(q=>questUnlocked(q));
     return Object.freeze({name:r.name,key:r.key,cleared,total:quests.length,unlocked,
       required:r.required});
   });
   return Object.freeze({regions:Object.freeze(entries),
     cleared:entries.reduce((n,x)=>n+x.cleared,0),
     total:entries.reduce((n,x)=>n+x.total,0),
     dungeons:idset.size});
 }
 // When the pinned v143 original 2022 mission economy module is loaded,
 // confirm every live quest's prerequisite, energy and scalar rewards before
 // allowing ANY next-story route. A source-valid wave count alone is not
 // sufficient: a corrupted requires/energy/reward field must not unlock a
 // different mission. Older embedded pages may not load v143.
 function sourceEconomyReadiness(){
   const source=window.BFOriginalGlobalQuestEnergyV14300;
   if(!source)return null;
   if(source.source?.year!==2022||source.source?.recordCount!==106||
      source.source?.sourceSha256!==
       'a1b36659dfc80bc6e1e0e244ba52b3c6d423b239cf684439a5488bf679764a66'||
      typeof source.lookup!=='function'||!Array.isArray(QUESTS)||
      QUESTS.length!==106)return false;
   try{
     const seen=new Set();
     for(const q of QUESTS){
       if(!q||!Number.isSafeInteger(q.missionId)||seen.has(q.missionId))
         return false;
       seen.add(q.missionId);
       const row=source.lookup(q.missionId);
       if(!Array.isArray(row)||row.length!==8||
          row.some(v=>!Number.isSafeInteger(v)||v<0))return false;
       if(row[0]!==q.missionId||row[1]!==q.dungeonId||
          row[2]!==q.requires||row[3]!==q.battles||
          row[4]!==q.energy||row[5]!==q.exp||
          row[6]!==q.zel||row[7]!==q.karma)return false;
     }
     return seen.size===106;
   }catch(_){return false;}
 }
 // Read-only next playable mission, following source catalog order and real unlocks.
 // Never synthesize a fight, award a clear, or modify canonical v7 progress.
 function nextPlayable(){
   if(typeof P!=='object' || !P || !P.questClears || typeof questUnlocked!=='function'||
      sourceEconomyReadiness()===false)return null;
   // Validate the entire source catalog and clear ledger before selecting a mission.
   // An invalid later record must not be hidden by an earlier playable mission.
   const seen=new Set();
   for(const q of QUESTS){
     if(!q || !Number.isSafeInteger(q.missionId) || seen.has(q.missionId) ||
        !idset.has(q.dungeonId) || !Number.isSafeInteger(q.battles) || q.battles<1)return null;
     seen.add(q.missionId);
     const count=P.questClears[q.missionId];
     if(count!==undefined && (!Number.isSafeInteger(count) || count<0))return null;
   }
   for(const q of QUESTS){
     if((P.questClears[q.missionId]||0)===0 && questUnlocked(q))
       return Object.freeze({missionId:q.missionId,dungeonId:q.dungeonId,
         name:String(q.name||''),battles:q.battles});
   }
   return null;
 }
 // Frozen 2022 original mission master wave-count triples: missionId,
 // dungeonId, waveCount; recovered from source_data/v142 pinned to
 // ZIP 69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9.
 // Mission master SHA-256: d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83.
 // This is source evidence for counts ONLY, not enemy waves or AI.
 const verifiedWaveRows=Object.freeze([[1,1,3],[2,1,3],[10,10,5],[11,10,5],[12,10,6],[20,20,5],[21,20,5],[22,20,5],[23,20,6],[30,30,5],[31,30,5],[32,30,5],[33,30,6],[40,40,5],[41,40,5],[42,40,5],[43,40,6],[50,50,5],[51,50,5],[52,50,5],[53,50,6],[60,60,6],[61,60,6],[62,60,6],[63,60,7],[70,70,6],[71,70,6],[72,70,6],[73,70,7],[81,80,7],[82,80,7],[83,80,7],[84,80,7],[85,80,8],[200,200,7],[201,200,7],[202,200,8],[203,200,8],[204,200,9],[210,210,7],[211,210,7],[212,210,8],[213,210,8],[214,210,9],[220,220,7],[221,220,7],[222,220,8],[223,220,8],[224,220,9],[230,230,7],[231,230,7],[232,230,8],[233,230,8],[234,230,9],[240,240,7],[241,240,7],[242,240,8],[243,240,8],[244,240,9],[250,250,7],[251,250,7],[252,250,8],[253,250,8],[254,250,9],[260,260,9],[261,260,9],[262,260,9],[263,260,9],[264,260,9],[265,260,10],[300,300,8],[301,300,8],[302,300,9],[303,300,9],[304,300,11],[310,310,8],[311,310,8],[312,310,9],[313,310,9],[314,310,11],[320,320,8],[321,320,8],[322,320,9],[323,320,9],[324,320,11],[330,330,8],[331,330,8],[332,330,9],[333,330,9],[334,330,11],[340,340,8],[341,340,8],[342,340,9],[343,340,9],[344,340,11],[350,350,8],[351,350,8],[352,350,9],[353,350,9],[354,350,11],[360,360,10],[361,360,10],[362,360,11],[363,360,11],[364,360,11],[365,360,12]].map(Object.freeze));
 const verifiedWaveById=new Map(verifiedWaveRows.map(r=>[r[0],r]));
 // Read-only source-wave readiness for the 106 archived missions. A wave
 // count is not evidence of its enemy formation, drops, or native combat AI.
 // Refuse inconsistent catalog rows rather than silently inventing waves.
 function waveReadiness(missionId){
   if(!Number.isSafeInteger(missionId)||missionId<0||
      !Array.isArray(QUESTS)||QUESTS.length!==106)return null;
   // A corrupt later row must not certify an earlier mission. Validate
   // the entire historical catalog, including unique IDs, before readiness.
   if(verifiedWaveRows.length!==106||verifiedWaveById.size!==106)return null;
   const seen=new Set();
   for(const row of QUESTS){
     if(!row||!Number.isSafeInteger(row.missionId)||row.missionId<0||
        seen.has(row.missionId)||!idset.has(row.dungeonId)||
        !Number.isSafeInteger(row.battles))return null;
     const expected=verifiedWaveById.get(row.missionId);
     // A changed but still plausible runtime wave count must never be
     // promoted to verified source evidence, even for an unrelated row.
     if(!expected||row.dungeonId!==expected[1]||
        row.battles!==expected[2])return null;
     seen.add(row.missionId);
   }
   const source=verifiedWaveById.get(missionId);
   if(!source)return null;
   return Object.freeze({missionId,dungeonId:source[1],
     verifiedWaveCount:source[2],enemyFormationsVerified:false,
     dropsVerified:false,nativeMultiWaveEnabled:false});
 }
 function refresh(){
   const info=summary();
   total.textContent=info.cleared+' / '+info.total+' original missions cleared';
   // The pinned 2022 mission master authenticates counts, NOT enemy rosters.
   // Report coverage only when the complete live catalog still matches source.
   const sourceReady=waveReadiness(QUESTS[0]?.missionId);
   const waveTotal=sourceReady?
     verifiedWaveRows.reduce((sum,row)=>sum+row[2],0):null;
   footer.textContent=waveTotal===null?
     '2022 source wave-count verification unavailable; no native formations certified.':
     '2022 source-verified: '+verifiedWaveRows.length+' missions · '+waveTotal+
     ' wave counts. Enemy formations, drops and native multi-wave combat NOT verified. '+
     'Archive Energy is not spent.';
   for(const r of info.regions){
     const {button,count,bar}=controls.get(r.key);
     const locked=!r.unlocked;
     count.textContent=r.cleared+' / '+r.total+(locked?' · LOCKED':'');
     bar.max=r.total;bar.value=r.cleared;
     button.title=locked?
       ('Complete Mission '+r.required+' to unlock '+r.name):
       ('Open '+r.name+' original area map');
     const selected=r.key==='mistral'?!document.querySelector('.bf-mistral-map')?.hidden:
       r.key==='morgan'?!document.getElementById('bf080-morgan-map')?.hidden:
       !document.getElementById('bf090-stlamia-map')?.hidden;
     button.setAttribute('aria-pressed',String(selected));
     button.setAttribute('aria-label',r.name+', '+r.cleared+' of '+r.total+
       ' missions cleared'+(locked?', locked':''));
   }
   return info;
 }
 new MutationObserver(refresh).observe(list,{childList:true});
 tabs.addEventListener('click',refresh);
 refresh();
 window.BFGrandGaiaCampaignV100=Object.freeze({summary,refresh,nextPlayable,waveReadiness,sourceEconomyReadiness,
    get missionCount(){return 106},get dungeonCount(){return 23}});
 // The Home navigation loads before this source-backed campaign module in
 // Android. Refresh only its display after the verified provider is ready.
 try { window.BFGlobalHome?.refreshStory?.(); } catch (_) {}
})();
