/* BF_AMDAHL_ORIGINAL_OPAQUE_MISSION_FIELDS_V20900 */
(() => {
 'use strict';
 // Original 2022 *source strings*, not decoded enemy waves, loot, NPCs or sound playback.
 const guide=window.BFAmdahlSourceQuestGuideV20600;
 const refs=window.BFGlobalEncounterReferencesV15100;
 const MASTER_SHA256='d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83';
 const QUEST_SHA256='f35a7b06bc9e6fae6facc1fd77422f74c04798da4fb87f64a2737a0483a572c3';
 const diagnostic=reason=>{
   // No player/save details or source row bodies: only stable reason labels.
   if(typeof console!=='undefined' && typeof console.warn==='function')
     console.warn('BF211 Amdahl source-only pane unavailable: '+reason);
 };
 // Expected onPageFinished repetitions are silent and idempotent.
 if(window.BFAmdahlOriginalOpaqueFieldsV20900)return;
 if(typeof P==='undefined'||P.version!==7||
   typeof QUESTS==='undefined'||!Array.isArray(QUESTS)||QUESTS.length!==106){
   diagnostic('unsupported v7 player or playable-quest catalog');return;
 }
 if(!guide||typeof guide.lookup!=='function'||guide.source?.year!==2022||
   guide.source?.playable!==false||guide.source?.saveMutation!==false||
   guide.source?.missions!==36||guide.source?.masterSha256!==MASTER_SHA256||
   guide.source?.canonicalQuestSha256!==QUEST_SHA256){
   diagnostic('v206 original guide missing or source provenance mismatch');return;
 }
 if(!refs||typeof refs.lookup!=='function'||refs.summary?.sourceYear!==2022||
   refs.summary?.sha256!==MASTER_SHA256||
   refs.summary?.amdahlQuestCanonicalSha256!==QUEST_SHA256||
   refs.summary?.amdahlSourceOnlyMissions!==36||
   refs.summary?.playableMissions!==106||
   refs.summary?.meaningDecoded!==false||
   refs.summary?.gameplayMutation!==false||
   refs.summary?.saveMutation!==false){
   diagnostic('v151 encounter evidence missing or source provenance mismatch');return;
 }
 const rows=[[400,"3:50100,0:50101","bf041_map_jewrel.mp3","bf006_btl_boss.mp3","",0],[401,"3:50100,0:50101","bf041_map_jewrel.mp3","bf006_btl_boss.mp3","",0],[402,"3:50100,0:50101","bf041_map_jewrel.mp3","bf006_btl_boss.mp3","",0],[403,"3:50100,0:50101","bf041_map_jewrel.mp3","bf006_btl_boss.mp3","",0],[404,"3:50100,0:50101","bf041_map_jewrel.mp3","bf006_btl_boss.mp3","8:0:1:0:0",0],[410,"3:50200,1:50201,0:50202","bf016_map_ghost.mp3","bf006_btl_boss.mp3","",0],[411,"3:50200,1:50201,0:50202","bf016_map_ghost.mp3","bf006_btl_boss.mp3","",0],[412,"3:50200,1:50201,0:50202","bf016_map_ghost.mp3","bf006_btl_boss.mp3","",0],[413,"3:50200,1:50201,0:50202","bf016_map_ghost.mp3","bf006_btl_boss.mp3","",0],[414,"3:50200,1:50201,0:50202","bf016_map_ghost.mp3","bf006_btl_boss.mp3","8:0:1:0:0",0],[420,"3:50300,1:50301,1:50302","bf010_map_grass.mp3","bf006_btl_boss.mp3","",0],[421,"3:50300,1:50301,1:50302","bf010_map_grass.mp3","bf006_btl_boss.mp3","",0],[422,"3:50300,1:50301,1:50302","bf010_map_grass.mp3","bf006_btl_boss.mp3","",0],[423,"3:50300,1:50301,1:50302","bf010_map_grass.mp3","bf006_btl_boss.mp3","",0],[424,"3:50300,1:50301,1:50302","bf010_map_grass.mp3","bf006_btl_boss.mp3","8:0:1:0:0",0],[430,"2:50400,1:50401","bf038_map_cordelica.mp3","bf006_btl_boss.mp3","",0],[431,"2:50400,1:50401","bf038_map_cordelica.mp3","bf006_btl_boss.mp3","",0],[432,"2:50400,1:50401","bf038_map_cordelica.mp3","bf006_btl_boss.mp3","",0],[433,"2:50400,1:50401","bf038_map_cordelica.mp3","bf006_btl_boss.mp3","",0],[434,"2:50400,1:50401","bf038_map_cordelica.mp3","bf006_btl_boss.mp3","8:0:1:0:0",0],[440,"1:50500","bf035_map_romaus.mp3","bf006_btl_boss.mp3","",0],[441,"1:50500","bf035_map_romaus.mp3","bf006_btl_boss.mp3","",0],[442,"1:50500","bf035_map_romaus.mp3","bf006_btl_boss.mp3","",0],[443,"1:50500","bf035_map_romaus.mp3","bf006_btl_boss.mp3","",0],[444,"1:50500","bf035_map_romaus.mp3","bf006_btl_boss.mp3","8:0:1:0:0",0],[450,"0:50600,1:50601","bf023_map_ruins.mp3","bf006_btl_boss.mp3","",0],[451,"0:50600,1:50601","bf023_map_ruins.mp3","bf006_btl_boss.mp3","",0],[452,"0:50600,1:50601","bf023_map_ruins.mp3","bf006_btl_boss.mp3","",0],[453,"0:50600,1:50601","bf023_map_ruins.mp3","bf006_btl_boss.mp3","",0],[454,"0:50600,1:50601","bf023_map_ruins.mp3","bf006_btl_boss.mp3","8:0:1:0:0",0],[460,"1:50700","bf036_map_vadan.mp3","bf006_btl_boss.mp3","",0],[461,"1:50700","bf036_map_vadan.mp3","bf006_btl_boss.mp3","",0],[462,"1:50700","bf036_map_vadan.mp3","bf006_btl_boss.mp3","",0],[463,"1:50700","bf036_map_vadan.mp3","bf006_btl_boss.mp3","",0],[464,"1:50700","bf036_map_vadan.mp3","bf006_btl_boss.mp3","",0],[465,"1:50700","bf036_map_vadan.mp3","bf028_map_space.mp3","8:0:1:0:0",0]];
 const seen=new Set();
 if(rows.length!==36 || rows.some(r=>{
   if(!Array.isArray(r)||r.length!==6||seen.has(r[0])||
      !Number.isSafeInteger(r[0])||!Number.isSafeInteger(r[5])||
      r[5]!==0||![r[1],r[2],r[3],r[4]].every(x=>typeof x==='string')||
      !/^(?:[0-9]+:[0-9]+)(?:,[0-9]+:[0-9]+)*$/.test(r[1])||
      !/^bf[0-9]+_[A-Za-z0-9_]+\.mp3$/.test(r[2])||
      !/^bf[0-9]+_[A-Za-z0-9_]+\.mp3$/.test(r[3])||
      (r[4]!==''&&r[4]!=='8:0:1:0:0'))return true;
   const source=guide.lookup(r[0]),old=refs.lookup(r[0]);
   if(!source||!old||old.playable!==false||old.raw!==r[1]||
      source[0]!==r[0]||old.dungeonId!==source[1])return true;
   seen.add(r[0]);return false;
 })){
   diagnostic('original 36 source mission records or joins invalid');return;
 }
 const host=document.getElementById('bf20600-amdahl-guide');
 const select=document.getElementById('bf20600-dungeon');
 const questList=document.getElementById('bf20600-quest-list');
 if(document.getElementById('bf20900-raw-mission-fields'))return;
 if(!host||!select||!questList||select.options.length!==7){
   diagnostic('original Amdahl guide DOM controls missing or incomplete');return;
 }
 const block=document.createElement('details');block.id='bf20900-raw-mission-fields';
 block.style.cssText='margin:9px 0;padding:9px;border:1px solid #7c91a1;border-radius:5px;background:#192d40';
 const header=document.createElement('summary');
 header.textContent='2022 ORIGINAL MISSION DATA · RAW REFERENCES (NOT GAMEPLAY)';
 const disclaimer=document.createElement('p');
 disclaimer.textContent='These are verbatim original 2022 encounter tokens, music filenames, NPC IDs and reward tokens. Their meanings are not decoded. This view never loads music, determines enemy rosters, awards loot or changes any saves.';
 const result=document.createElement('ol');result.id='bf20900-source-fields';
 result.style.cssText='padding-left:23px;overflow-wrap:anywhere';
 function refresh(){
   const dungeon=Number(select.value);
   if(![400,410,420,430,440,450,460].includes(dungeon))return 0;
   result.replaceChildren();
   for(const row of rows){
     if(guide.lookup(row[0])?.[1]!==dungeon)continue;
     const li=document.createElement('li');li.dataset.sourceMission=String(row[0]);
     const label=document.createElement('strong');label.textContent='Mission '+row[0];
     const content=document.createElement('p');
     content.textContent='Raw encounter: '+row[1]+' · Battle music file: '+row[2]+
       ' · Boss music file: '+row[3]+' · Raw reward token: '+(row[4]||'(empty)')+
       ' · NPC source ID: '+row[5]+' · SOURCE ONLY';
     li.append(label,content);result.append(li);
   }
   return result.children.length;
 }
 block.append(header,disclaimer,result);host.append(block);
 const observer=new MutationObserver(refresh);
 observer.observe(questList,{childList:true});
 refresh();
 window.BFAmdahlOriginalOpaqueFieldsV20900=Object.freeze({
   source:Object.freeze({sourceYear:2022,masterSha256:MASTER_SHA256,
     canonicalQuestSha256:QUEST_SHA256,originalEnemyRosterDecoded:false,
     rewardMeaningDecoded:false,gameplayMutation:false,saveMutation:false}),
   lookup:id=>Number.isSafeInteger(id)?rows.find(x=>x[0]===id)?.slice()||null:null,
   refresh
 });
})();
