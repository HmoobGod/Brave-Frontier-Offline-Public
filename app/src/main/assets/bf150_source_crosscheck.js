/* BF_GLOBAL_SOURCE_CROSSCHECK_V150 */
(() => {
 'use strict';
 if(window.BFGlobalSourceCrosscheckV150 || typeof QUESTS==='undefined' ||
    QUESTS.length!==106 || !window.BFGlobalUnitArchive ||
    !window.BFHistoricalEncountersV120 || !window.BFGlobalQuestJournalV110 ||
    !window.BFGrandGaiaCampaignV100 || !window.BFStLamiaMapV090)return;
 const encyclopedia=window.BFGlobalUnitArchive;
 const history=window.BFHistoricalEncountersV120;
 if(encyclopedia.count!==2291 || history.waves!==16 || history.enemySlots!==33 ||
   history.ids.join(',')!=='1,2,10,20')return;
 const ids=Object.freeze(history.ids.slice());
 const sources=ids.map(id=>history.lookup(id));
 if(sources.some(x=>!x || !Array.isArray(x.waves) || !x.gitBlobSha || !x.sourcePath))return;
 const prior=document.getElementById('bf120-historical-battles');
 const journal=document.getElementById('bf110-journal');
 const list=document.getElementById('questlist');
 if(!prior||!journal||!list)return;
 const style=document.createElement('style');style.id='bf150-crosscheck-style';
 style.textContent=[
  '#bf150-crosscheck,#bf150-integrity{margin:9px 2px;padding:10px;',
  'border:1px solid #9b8666;border-radius:7px;background:#1c2c3e;',
  'color:#f5e9d1;font:12px/1.5 system-ui,sans-serif}',
  '#bf150-crosscheck summary,#bf150-integrity summary{cursor:pointer;',
  'font:bold 14px Georgia,serif;min-height:28px}',
  '#bf150-select{min-height:40px;width:100%;padding:6px;',
  'border:1px solid #b9a47d;background:#192637;color:#fff}',
  '.bf150-wave{border-top:1px solid #566075;margin-top:8px;padding-top:5px}',
  '.bf150-unit{display:flex;align-items:center;gap:8px;margin:5px 0;',
  'padding:5px;background:#263a4e;border-radius:5px}',
  '.bf150-unit img,.bf150-art{width:44px;height:44px;object-fit:contain;',
  'flex:0 0 44px;border:1px solid #63788a;background:#13202f}',
  '.bf150-unit strong,.bf150-unit small{display:block}',
  '.bf150-unit small{color:#dae0e7;font-size:11px}',
  '.bf150-warning{color:#f3d49d}',
  '#bf150-refresh{min-height:40px;padding:8px 12px;border:1px solid #c1a26a;',
  'border-radius:5px;background:#344f65;color:white;font-weight:700}'
 ].join('');document.head.append(style);
 const panel=document.createElement('details');panel.id='bf150-crosscheck';
 const heading=document.createElement('summary');
 heading.textContent='2022 UNIT ID CROSS-CHECK · 2014 ENCOUNTERS';
 const warning=document.createElement('p');warning.className='bf150-warning';
 warning.textContent='Historical 2014 lineups compared only by unit ID with the 2022 Global encyclopedia. Matching IDs or thumbnails do NOT verify 2022 enemy waves, sprite animations, enemy AI, drop rates or combat.';
 const select=document.createElement('select');select.id='bf150-select';
 for(const entry of sources){
   const option=document.createElement('option');
   option.value=String(entry.id);option.textContent=entry.name+' · Mission '+entry.id;
   select.append(option);
 }
 const count=document.createElement('p');count.id='bf150-count';
 count.setAttribute('aria-live','polite');
 const waves=document.createElement('div');waves.id='bf150-waves';
 const cite=document.createElement('small');cite.id='bf150-source';
 panel.append(heading,warning,select,count,waves,cite);
 prior.after(panel);
 const integrity=document.createElement('details');integrity.id='bf150-integrity';
 const title=document.createElement('summary');
 title.textContent='OFFLINE BUILD VERIFICATION · v1.50';
 const summary=document.createElement('p');summary.id='bf150-status';
 summary.setAttribute('aria-live','polite');
 const report=document.createElement('div');report.id='bf150-report';
 const refreshButton=document.createElement('button');refreshButton.id='bf150-refresh';
 refreshButton.type='button';refreshButton.textContent='RECHECK WITHOUT CHANGING SAVE';
 const footer=document.createElement('p');footer.className='bf150-warning';
 footer.textContent='This checks packaged local content and in-memory progress. It does not claim the APK has passed testing on your Android device or that original Global combat is complete.';
 integrity.append(title,summary,report,refreshButton,footer);
 journal.after(integrity);
 const allEntries=sources.flatMap(m=>m.waves.flatMap(w=>w.enemies));
 const uniqueIds=[...new Set(allEntries.map(x=>x.unitId))];
 function identity(id){
   const enemy=allEntries.find(x=>x.unitId===Number(id));
   if(!enemy)return null;
   const original=encyclopedia.find(Number(id));
   const present=!!original;
   const exactName=present && original.name.toLocaleLowerCase()===enemy.name.toLocaleLowerCase();
   return Object.freeze({unitId:Number(id),historicName:enemy.name,
     catalogPresent:present,catalogName:original?.name||null,
     exactEnglishName:!!exactName,thumbnail:!!original?.thumbnail});
 }
 function snapshot(){
   const idsPresent=uniqueIds.filter(id=>identity(id).catalogPresent);
   const namesExact=uniqueIds.filter(id=>identity(id).exactEnglishName);
   const thumb=uniqueIds.filter(id=>identity(id).thumbnail);
   const dungeons=new Set(QUESTS.map(q=>q.dungeonId));
   const counts=[QUESTS.filter(q=>q.dungeonId<200).length,
      QUESTS.filter(q=>q.dungeonId>=200&&q.dungeonId<300).length,
      QUESTS.filter(q=>q.dungeonId>=300).length];
   const checks=Object.freeze({
     saveV7:typeof P!=='undefined' && P.version===7,
     quests106:QUESTS.length===106&&new Set(QUESTS.map(q=>q.missionId)).size===106,
     originalDungeons23:dungeons.size===23,
     regions34_36_36:counts.join(',')==='34,36,36',
     originalUnits2291:encyclopedia.count===2291,
     historicalResearch4:ids.length===4&&history.waves===16&&history.enemySlots===33
   });
   return Object.freeze({
     pass:Object.values(checks).every(Boolean),checks,regions:Object.freeze(counts),
     originalQuestCount:QUESTS.length,originalDungeonCount:dungeons.size,
     originalUnitCount:encyclopedia.count,historicalMissions:ids.length,
     historicalWaves:history.waves,historicalEntries:allEntries.length,
     distinctHistoricalUnitIds:uniqueIds.length,
     sameIdIn2022Catalog:idsPresent.length,exactEnglishNameMatches:namesExact.length,
     matchingThumbnailCount:thumb.length,
     actual2022BattleFormationsConfirmed:0
   });
 }
 function showMission(id){
   const entry=history.lookup(id);
   if(!entry)return false;
   select.value=String(entry.id);
   const local=new Set(entry.waves.flatMap(w=>w.enemies.map(e=>e.unitId)));
   count.textContent=entry.waves.length+' archived 2014 groups · '+
      entry.waves.reduce((n,w)=>n+w.enemies.length,0)+' entries · '+
      [...local].filter(id=>identity(id).catalogPresent).length+'/'+local.size+
      ' distinct IDs present in the 2022 unit catalog';
   waves.replaceChildren();
   for(const wave of entry.waves){
     const box=document.createElement('section');box.className='bf150-wave';
     const waveHeading=document.createElement('strong');
     waveHeading.textContent='2014 WAVE '+wave.wave;box.append(waveHeading);
     for(const foe of wave.enemies){
       const match=identity(foe.unitId),item=document.createElement('div');
       item.className='bf150-unit';
       if(match.thumbnail){
          const img=document.createElement('img');
          img.loading='lazy';
          img.alt='2022 catalog thumbnail, not verified 2014 combat sprite';
          img.src='content/unit_archive/unit_ills_thum_'+match.unitId+'.png';
          item.append(img);
       }else{
          const block=document.createElement('span');block.className='bf150-art';
          block.setAttribute('aria-label','No archived 2022 thumbnail confirmed');
          item.append(block);
       }
       const info=document.createElement('div'),a=document.createElement('strong');
       a.textContent=foe.name+' · 2014 unit #'+foe.unitId;
       const b=document.createElement('small');
       b.textContent='2014 recorded HP '+foe.hp+', ATK '+foe.atk+
          ', DEF '+foe.def+' · 2022 catalog: '+
          (match.catalogPresent?'ID found ('+match.catalogName+')':'ID not verified')+
          (match.exactEnglishName?' · same English name':'');
       info.append(a,b);item.append(info);box.append(item);
     }
     waves.append(box);
   }
   cite.textContent='2014 parsed source: '+entry.sourcePath+
      ' · Git blob '+entry.gitBlobSha+'. Unverified cross-era enemy/formation correspondence.';
   return true;
 }
 function renderIntegrity(){
   const s=snapshot();
   summary.textContent=(s.pass?'PASS':'CHECK REQUIRED')+
     ' · '+s.originalQuestCount+' quests · '+s.originalDungeonCount+
     ' dungeons · '+s.originalUnitCount+' archived unit forms';
   report.replaceChildren();
   const details=[
     'Mistral / Morgan / St. Lamia: '+s.regions.join(' / ')+' missions',
     '2014 reference coverage: '+s.historicalMissions+' missions / '+
       s.historicalWaves+' wave groups / '+s.historicalEntries+' enemy slots',
     '2014 distinct unit IDs found in 2022 catalog: '+
       s.sameIdIn2022Catalog+' / '+s.distinctHistoricalUnitIds,
     'Identical English names across archive years: '+s.exactEnglishNameMatches,
     '2022 archived unit thumbnails available for these IDs: '+s.matchingThumbnailCount,
     '2022 native enemy formations independently established: 0',
     ...Object.entries(s.checks).map(([k,v])=>(v?'PASS':'FAIL')+' · '+k)
   ];
   for(const line of details){const row=document.createElement('p');
     row.textContent=line;report.append(row);}
   return s;
 }
 select.addEventListener('change',()=>showMission(Number(select.value)));
 refreshButton.addEventListener('click',renderIntegrity);
 document.querySelector('.bf-navbar')?.addEventListener('click',()=>{
   if(history.lookup(QUEST?.missionId))showMission(QUEST.missionId);
 });
 new MutationObserver(()=>{
   if(history.lookup(QUEST?.missionId))showMission(QUEST.missionId);
 }).observe(list,{childList:true});
 showMission(history.lookup(QUEST?.missionId)?QUEST.missionId:ids[0]);
 renderIntegrity();
 window.BFGlobalSourceCrosscheckV150=Object.freeze({
    identity,snapshot,showMission,renderIntegrity,get coveredMissions(){return ids.slice();}
 });
})();
