/* BF_GLOBAL_2022_STLAMIA_ENCOUNTER_REFERENCE_EXTENSION_V10900 */
(() => {
 'use strict';
 // Extends the read-only v108 mission-reference audit to all 106 first
 // three-region 2022 Global missions. Raw numbers are NOT enemy or wave IDs.
 const prior=window.BFGlobalEncounterReferencesV10800;
 const st=window.BF_STLAMIA_QUEST_DATA_V090;
 const master='d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83';
 if(window.BFGlobalEncounterReferencesV10900||!prior||!st||
   prior.summary?.archivedMissions!==70||prior.summary.sha256!==master||
   st.schema!=='bf-global-st-lamia-2022-original-quests-v090'||
   st.provenance?.missionMasterSha256!==master||
   !Array.isArray(st.quests)||st.quests.length!==36||
   typeof P==='undefined'||P.version!==7)return;
 const panel=document.getElementById('bf10800-encounter-ledger');
 const select=document.getElementById('bf10800-mission');
 const detail=document.getElementById('bf10800-raw');
 if(!panel||!select||!detail)return;
 const freeze=Object.freeze;
 // Exact source patterns extracted from F_MISSION_MST_1_Ver1118.json.
 // Rows 300..365 were checked against the original 2022 archive SHA.
 const patterns=freeze([
   [300,5,'3:30100,0:30101'],
   [310,5,'3:30200,1:30201'],
   [320,5,'3:30300,2:30301'],
   [330,5,'1:30400,0:30401'],
   [340,5,'3:30500,0:30501'],
   [350,5,'3:30600,0:30601'],
   [360,6,'3:30700']
 ]);
 const rows=[];
 for(const [start,count,raw] of patterns){
   const refs=prior.parseOpaque(raw);
   if(!refs||count<1||count>6)return;
   for(let i=0;i<count;i++){
     const id=start+i;
     const q=st.quests.find(x=>x.missionId===id);
     if(!q||q.dungeonId!==start||prior.lookup(id))return;
     rows.push(freeze({missionId:id,region:'St. Lamia',raw,
       refs,tokenCount:refs.length,nativeWaveIdentitiesKnown:false,
       nativeEnemyIdsKnown:false,nativeAIScriptsKnown:false,
       rewardsDecoded:false}));
   }
 }
 if(rows.length!==36||st.quests.some(q=>!rows.some(r=>r.missionId===q.missionId)))return;
 const stMap=new Map(rows.map(r=>[r.missionId,r]));
 if(stMap.size!==36)return;
 const mergedRefs=new Set();
 for(const row of rows)for(const ref of row.refs)mergedRefs.add(ref.opaqueRef);
 function lookup(id){
   if(!Number.isSafeInteger(id))return null;
   return prior.lookup(id)||stMap.get(id)||null;
 }
 function references(token){
   const first=prior.references(token);
   if(typeof token!=='string'||!/^[0-9]+$/.test(token))return first;
   return freeze([...first,...rows.filter(row=>row.refs.some(r=>r.opaqueRef===token))
     .map(r=>r.missionId)]);
 }
 const summary=freeze({
   sourceYear:2022,sha256:master,
   sourceFile:'3-mst-translated/F_MISSION_MST_1_Ver1118.json',
   archivedMissions:106,mistralMissions:34,morganMissions:36,
   stLamiaMissions:36,stLamiaDistinctOpaqueRefs:mergedRefs.size,
   meaningDecoded:false,gameplayMutation:false,
   sourceLimit:'No native wave/enemy/AI/loot decoder in these mission tokens'
 });
 const title=panel.querySelector('summary');
 if(title)title.textContent='2022 GLOBAL ENCOUNTER REFS · 106 MISSION RECORDS';
 const intro=panel.querySelector('p');
 if(intro)intro.textContent='Verified raw mission-master references across Mistral, Morgan and St. Lamia. '+
   'The meaning of every colon-separated numeric pair remains undecoded: '+
   'NOT confirmed native enemy identities, wave formations, AI or rewards.';
 for(const r of rows){
   const option=document.createElement('option');
   option.value=String(r.missionId);
   option.textContent='St. Lamia · Mission '+r.missionId;
   select.append(option);
 }
 function refresh(){
   const row=lookup(Number(select.value));
   detail.textContent=row?('Mission '+row.missionId+' · '+row.region+
      ' · raw source tokens: '+row.raw+
      ' · '+row.tokenCount+' opaque reference pairs'):
      'No verified source record';
   return row;
 }
 select.addEventListener('change',refresh);
 refresh();
 window.BFGlobalEncounterReferencesV10900=freeze({
   summary,lookup,references,refresh,patterns
 });
})();
