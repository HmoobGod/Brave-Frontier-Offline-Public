/* BF_GLOBAL_2022_ENCOUNTER_REFERENCE_LEDGER_V10800 */
(() => {
 'use strict';
 // Exact opaque 2022 mission-master encounter tokens. The semantics of the
 // two numbers are NOT decoded: neither is an enemy/unit/wave declaration.
 const mistral=window.BFOriginalMissionEvidence;
 const morgan=window.BF_MORGAN_QUEST_DATA_V080;
 if(window.BFGlobalEncounterReferencesV10800||
    typeof P==='undefined'||P.version!==7||
    !mistral||mistral.count!==34||
    typeof mistral.lookup!=='function'||
    typeof mistral.parseOpaqueReferences!=='function'||
    mistral.facts?.sourceSha256!=='d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83'||
    morgan?.schema!=='bf-global-morgan-2022-original-quests-v080'||
    morgan.provenance?.missionMasterSha256!==mistral.facts.sourceSha256||
    morgan.provenance?.mastersZipSha256!=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'||
    !Array.isArray(morgan.quests)||morgan.quests.length!==36)return;
 const host=document.getElementById('bf110-journal')||
    document.getElementById('questlist');
 if(!host)return;
 const freeze=Object.freeze;
 const ids=freeze(mistral.missionIds.slice());
 if(ids.length!==34||new Set(ids).size!==34)return;
 function parseOpaque(raw){
   if(typeof raw!=='string'||!/^[0-9]+:[0-9]+(?:,[0-9]+:[0-9]+)*$/.test(raw))return null;
   const tokens=raw.split(',');
   if(!tokens.length||tokens.length>16)return null;
   const parsed=tokens.map(part=>{
     const [label,ref]=part.split(':');
     const a=Number(label),b=Number(ref);
     if(!Number.isSafeInteger(a)||!Number.isSafeInteger(b)||
        a<0||b<=0||!Number.isFinite(a)||!Number.isFinite(b))return null;
     return freeze({opaqueLabel:label,opaqueRef:ref});
   });
   return parsed.includes(null)?null:freeze(parsed);
 }
 function entry(row,region){
   if(!row||!Number.isSafeInteger(row.missionId))return null;
   const raw=row.rawEncounterRef;
   const refs=parseOpaque(raw);
   if(!refs||refs.length>8)return null;
   return freeze({missionId:row.missionId,region,raw,
     refs,tokenCount:refs.length,
     nativeWaveIdentitiesKnown:false,nativeEnemyIdsKnown:false,
     nativeAIScriptsKnown:false,rewardsDecoded:false});
 }
 const rows=[],used=new Set();
 for(const id of ids){
   const row=mistral.lookup(id);
   if(!row||row.missionId!==id||used.has(id))return;
   const v=entry(row,'Mistral');
   if(!v)return;
   const old=mistral.parseOpaqueReferences(row.rawEncounterRef);
   if(!Array.isArray(old)||old.length!==v.refs.length||
      old.some((t,i)=>t.opaqueLabel!==v.refs[i].opaqueLabel||
        t.opaqueRef!==v.refs[i].opaqueRef))return;
   used.add(id);rows.push(v);
 }
 for(const row of morgan.quests){
   if(row.missionId<200||row.missionId>299||used.has(row.missionId)||
      row.dungeonId<200||row.dungeonId>260)return;
   const v=entry(row,'Morgan');
   if(!v)return;
   used.add(row.missionId);rows.push(v);
 }
 if(rows.length!==70||used.size!==70)return;
 rows.sort((a,b)=>a.missionId-b.missionId);
 const byId=new Map(rows.map(r=>[r.missionId,r]));
 const uniqueRefs=new Set();
 for(const row of rows)for(const ref of row.refs)uniqueRefs.add(ref.opaqueRef);
 const summary=freeze({sourceYear:2022,
   sourceFile:'3-mst-translated/F_MISSION_MST_1_Ver1118.json',
   sha256:mistral.facts.sourceSha256,archivedMissions:rows.length,
   mistralMissions:34,morganMissions:36,
   distinctOpaqueRefs:uniqueRefs.size,
   meaningDecoded:false,knownWaveCountsFromSeparateFields:true,
   gameplayMutation:false});
 function lookup(id){
   return Number.isSafeInteger(id)?byId.get(id)||null:null;
 }
 function references(token){
   if(typeof token!=='string'||!/^[0-9]+$/.test(token))return freeze([]);
   return freeze(rows.filter(r=>r.refs.some(ref=>ref.opaqueRef===token))
     .map(r=>r.missionId));
 }
 const panel=document.createElement('details');panel.id='bf10800-encounter-ledger';
 panel.style.cssText='padding:10px;margin:10px 2px;border:1px solid #829eac;'+
   'border-radius:7px;background:#1c2e42;color:#ecf1fa;'+
   'font:12px/1.5 system-ui,sans-serif';
 const heading=document.createElement('summary');
 heading.textContent='2022 GLOBAL ENCOUNTER REFS · 70 MISSION RECORDS';
 heading.style.cssText='cursor:pointer;min-height:36px;font-weight:800';
 const desc=document.createElement('p');
 desc.textContent='Verified raw mission-master references for Mistral and Morgan only. '+
   'These are opaque source tokens, NOT decoded enemy IDs, wave formations, '+
   'AI instructions or rewards. Research-only; nothing changes in combat.';
 const select=document.createElement('select');select.id='bf10800-mission';
 select.setAttribute('aria-label','2022 original mission source identifier');
 select.style.cssText='background:#223b51;color:white;border:1px solid #9caebc;'+
   'padding:8px;min-height:42px;max-width:100%';
 for(const r of rows){
   const o=document.createElement('option');o.value=String(r.missionId);
   o.textContent=r.region+' · Mission '+r.missionId;
   select.append(o);
 }
 const detail=document.createElement('p');detail.id='bf10800-raw';
 const evidence=document.createElement('small');
 evidence.textContent='2022 F_MISSION_MST_1_Ver1118.json · SHA-256 '+
    summary.sha256+' · raw MISSION_8f4NYKxb field · 34 Mistral / 36 Morgan';
 panel.append(heading,desc,select,detail,evidence);
 host.after(panel);
 function refresh(){
   const e=lookup(Number(select.value));
   detail.textContent=e?('Mission '+e.missionId+' · '+e.region+
     ' · raw source tokens: '+e.raw+
     ' · '+e.tokenCount+' opaque reference pairs'):'No verified source record';
   return e;
 }
 select.addEventListener('change',refresh);
 refresh();
 window.BFGlobalEncounterReferencesV10800=freeze({summary,lookup,references,parseOpaque,refresh});
})();
