/* BF_GLOBAL_2022_AMDAHL_ENCOUNTER_EVIDENCE_V15100 */
(() => {
 'use strict';
 // Source-only extension. Numeric tokens are opaque. No native wave, enemy,
 // scripted AI, drops or 400-series playable quest is inferred.
 const previous=window.BFGlobalEncounterReferencesV10900;
 const art=window.BFAmdahlOriginalArtV14900;
 const master='d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83';
 const canon='f35a7b06bc9e6fae6facc1fd77422f74c04798da4fb87f64a2737a0483a572c3';
 if(window.BFGlobalEncounterReferencesV15100||
    typeof P==='undefined'||P.version!==7||
    typeof QUESTS==='undefined'||!Array.isArray(QUESTS)||QUESTS.length!==106||
    !previous||previous.summary?.archivedMissions!==106||
    previous.summary.sha256!==master||previous.summary.meaningDecoded!==false||
    !art||art.entries?.length!==7||
    art.source?.sourceYear!==2022||
    art.source.originalGameplayEnabled!==false||
    art.source.decodedEnemyWaves!==false)return;
 const sourceRows=[[400,400,365,8,"3:50100,0:50101","The Scars of War"],[401,400,400,8,"3:50100,0:50101","Abandoned Ruins"],[402,400,401,9,"3:50100,0:50101","Presence of Flames"],[403,400,402,10,"3:50100,0:50101","Of Thunder and Flames"],[404,400,403,11,"3:50100,0:50101","In Comes a Fire God"],[410,410,404,8,"3:50200,1:50201,0:50202","Party On Board"],[411,410,410,8,"3:50200,1:50201,0:50202","Venture Inside"],[412,410,411,9,"3:50200,1:50201,0:50202","Dragon's Roar"],[413,410,412,10,"3:50200,1:50201,0:50202","Frozen Blades"],[414,410,413,11,"3:50200,1:50201,0:50202","A Water God Appears"],[420,420,414,8,"3:50300,1:50301,1:50302","Windswept Prairie"],[421,420,420,8,"3:50300,1:50301,1:50302","The Graceful Figure"],[422,420,421,9,"3:50300,1:50301,1:50302","From Forest's Shadow"],[423,420,422,10,"3:50300,1:50301,1:50302","Princess of the Pond"],[424,420,423,11,"3:50300,1:50301,1:50302","The Gallant Earth God"],[430,430,424,8,"2:50400,1:50401","The Rotting Bridge"],[431,430,430,8,"2:50400,1:50401","Enlightenment of the Ages"],[432,430,431,9,"2:50400,1:50401","Where Thunder Pulses"],[433,430,432,10,"2:50400,1:50401","Lightning Quick Attack"],[434,430,433,11,"2:50400,1:50401","A Thunder God Strikes"],[440,440,434,9,"1:50500","Forest Sanctuary"],[441,440,440,9,"1:50500","Descending Force"],[442,440,441,10,"1:50500","Radiant Helix"],[443,440,442,11,"1:50500","Hades Blast"],[444,440,443,12,"1:50500","Light God's Progression"],[450,450,444,9,"0:50600,1:50601","Never Ending Rain"],[451,450,450,9,"0:50600,1:50601","Dark Night Requiem"],[452,450,451,10,"0:50600,1:50601","A Thirst for Blood"],[453,450,452,11,"0:50600,1:50601","Pure Magic Barrier"],[454,450,453,12,"0:50600,1:50601","A Dark God Emerges"],[460,460,454,9,"1:50700","The Commander's Power"],[461,460,460,9,"1:50700","The Commander's Skill"],[462,460,461,10,"1:50700","The Princess' Ball"],[463,460,462,11,"1:50700","Dark Surge"],[464,460,463,12,"1:50700","Light Pulse"],[465,460,464,12,"1:50700","Malevolent Ceremony"]];
 if(sourceRows.length!==36||new Set(sourceRows.map(r=>r[0])).size!==36||
    QUESTS.some(q=>q.missionId>=400&&q.missionId<=465))return;
 const panel=document.getElementById('bf10800-encounter-ledger');
 const select=document.getElementById('bf10800-mission');
 const detail=document.getElementById('bf10800-raw');
 if(!panel||!select||!detail||select.options.length!==106)return;
 const freeze=Object.freeze;
 const rows=[],used=new Set();
 for(let i=0;i<sourceRows.length;i++){
   const [id,dungeon,requires,waves,raw,name]=sourceRows[i];
   // The last Amdahl dungeon contains six, not five, mission IDs.
   const sequence=i<30?400+10*Math.floor(i/5)+(i%5):460+(i-30);
   if(id!==sequence||used.has(id)||dungeon!==400+10*Math.floor(i<30?i/5:6)||
      requires!==(i===0?365:sourceRows[i-1][0])||
      !Number.isSafeInteger(waves)||waves<1||waves>30||
      typeof name!=='string'||name.length<1||name.length>140||
      typeof raw!=='string'||!/^\d+:\d+(?:,\d+:\d+)*$/.test(raw)||
      previous.lookup(id))return;
   const originalDungeon=art.lookup(dungeon);
   if(!originalDungeon||originalDungeon.firstMissionId!==dungeon)return;
   const refs=raw.split(',').map(pair=>{
     const parts=pair.split(':');
     return freeze({opaqueLabel:parts[0],opaqueRef:parts[1]});
   });
   if(refs.length>8||refs.some(t=>!/^\d+$/.test(t.opaqueRef)))return;
   used.add(id);
   rows.push(freeze({missionId:id,dungeonId:dungeon,requires,
      originalSourceWaveCount:waves,name,region:'Amdahl',raw,
      refs:freeze(refs),tokenCount:refs.length,
      nativeWaveIdentitiesKnown:false,nativeEnemyIdsKnown:false,
      nativeAIScriptsKnown:false,rewardsDecoded:false,playable:false}));
 }
 if(rows.length!==36||art.entries.some(d=>!rows.some(r=>r.dungeonId===d.id)))return;
 const byId=new Map(rows.map(r=>[r.missionId,r]));
 const added=[];
 for(const row of rows){
   const option=document.createElement('option');
   option.value=String(row.missionId);
   option.textContent='Amdahl · Mission '+row.missionId+' · '+row.name;
   added.push(option);
 }
 select.append(...added);
 function lookup(id){
   return Number.isSafeInteger(id)?previous.lookup(id)||byId.get(id)||null:null;
 }
 function references(token){
   const prior=previous.references(token);
   if(typeof token!=='string'||!/^\d+$/.test(token))return freeze([...prior]);
   return freeze([...prior,...rows.filter(row=>row.refs.some(ref=>ref.opaqueRef===token))
     .map(row=>row.missionId)]);
 }
 function refresh(){
   const id=Number(select.value),row=byId.get(id);
   if(row){
     detail.textContent='Mission '+id+' · Amdahl · '+row.name+
       ' · '+row.originalSourceWaveCount+' source-counted waves'+
       ' · opaque group references: '+row.raw+
       ' · NO decoded enemy formations, AI, loot or playable Amdahl quest.';
   }
   return row||previous.lookup(id)||null;
 }
 select.addEventListener('change',refresh);
 const summaryEl=panel.querySelector('summary');
 if(summaryEl)summaryEl.textContent='2022 GLOBAL ENCOUNTER REFS · 142 SOURCE MISSIONS';
 const note=panel.querySelector('p');
 if(note)note.textContent='Original 2022 Global Mistral, Morgan, St. Lamia and Amdahl '+
   'mission source references. Amdahl adds 36 source-only records, not playable '+
   'quests. Numeric tokens are opaque: NO enemy identities, formations, AI or loot.';
 refresh();
 const summary=freeze({sourceYear:2022,sourceFile:'3-mst-translated/F_MISSION_MST_1_Ver1118.json',
   sha256:master,amdahlQuestCanonicalSha256:canon,
   archivedMissions:142,playableMissions:106,amdahlSourceOnlyMissions:36,
   amdahlDungeons:7,meaningDecoded:false,nativeWaveIdentitiesKnown:false,
   gameplayMutation:false,saveMutation:false});
 window.BFGlobalEncounterReferencesV15100=freeze({summary,lookup,references,refresh});
})();
