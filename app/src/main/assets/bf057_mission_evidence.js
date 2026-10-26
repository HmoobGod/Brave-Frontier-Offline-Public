/* BF_ORIGINAL_MISSION_EVIDENCE_V057 */
(() => {
 'use strict';
 if(window.BFOriginalMissionEvidence) return;
 // 2022 master-source rows. Every field except missionId is an opaque reference.
 const source=__BF_MISSION_EVIDENCE_ROWS__;
 if(!source || source.schema!=='bf-global-2022-mistral-raw-mission-evidence-v056' ||
    !Array.isArray(source.rows) || source.rows.length!==34) return;
 const expected=[1,2,10,11,12,20,21,22,23,30,31,32,33,40,41,42,43,
                 50,51,52,53,60,61,62,63,70,71,72,73,81,82,83,84,85];
 function parseTokens(raw) {
   if(typeof raw!=='string' || !/^[0-9]+:[0-9]+(?:,[0-9]+:[0-9]+)*$/.test(raw))
      return null;
   const pairs=raw.split(',').map(part=>part.split(':'));
   if(pairs.some(pair=>pair.length!==2 || !pair.every(x=>Number.isSafeInteger(Number(x)))))
     return null;
   // Labels are deliberate. The native meaning of these integers is unknown.
   return pairs.map(([opaqueLabel,opaqueRef])=>Object.freeze({opaqueLabel,opaqueRef}));
 }
 const map=new Map();
 for(let i=0;i<expected.length;i++){
    const row=source.rows[i];
    if(!row || row.missionId!==expected[i] || map.has(row.missionId) ||
       parseTokens(row.rawEncounterRef)===null ||
       typeof row.rawMimicInfo!=='string' || typeof row.rawRewards!=='string' ||
       typeof row.rawCutscene!=='string' || row.rawMissionNpcId!=='0') return;
    map.set(row.missionId,Object.freeze({...row}));
 }
 const facts=Object.freeze({
   sourceFile:source.source.file,
   sourceSha256:source.source.fileSha256,
   classifications:source.source.limitations.slice(),
   archiveSha256:source.source.archiveSha256
 });
 window.BFOriginalMissionEvidence=Object.freeze({
   count:map.size,
   missionIds:Object.freeze(expected.slice()),
   lookup(id){return map.get(id)||null},
   parseOpaqueReferences:parseTokens,
   facts
 });
})();
