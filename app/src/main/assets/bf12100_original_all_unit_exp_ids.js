/* BF_GLOBAL_ORIGINAL_EXP_PATTERN_IDS_V12100 — ORIGINAL 2022 SOURCE IDs ONLY. */
(()=>{
 'use strict';
 // 2-bit codes from owner's SHA256-verified 2022 F_UNIT_MST_1/2_Ver1084.json,
 // in ascending original unit ID order. Neither native EXP thresholds nor
 // leveling behavior can be inferred from these IDs alone.
 const payload=document.getElementById('bf-global-unit-catalog-data');
 if(window.BFGlobalOriginalExpPatternIdsV12100||!payload)return;
 let archive;
 try{archive=JSON.parse(payload.textContent);}catch(_){return;}
 if(archive.schema!=='bf-global-unit-archive-2022-v1'||
    !Array.isArray(archive.units)||archive.units.length!==2291)return;
 const ids=archive.units.map(u=>u.id).sort((a,b)=>a-b);
 if(new Set(ids).size!==2291||ids[0]!==1||ids[1]!==10011||
    ids[ids.length-1]!==87602603)return;
 let bytes;
 try{bytes=atob('AABVgAAAAVVZWqqqoAVaqqgUAqlWlaqCqqqQqgqqqqiqqqaKqqqqqqlWqqqqqqqpaqqqqqqqqqqqqqlqqqqqqqqqqgAAVYAAAAFVWVqqqgBVqqqoFAKqWqVqCqqqmqgqqqqoqqqqqqqqqqqlWqqqqqqWqqqqqqqqqqqqqqWqWqqqqqqqqqoAAVYAAAAFVWVqqqgBVqqqoFAKpapWoKqqqqCqqqqoqqqqqqqqqqqqVaqqqqqqlqqqqqqqqqqqWqqqqpaqqqqoAAVYAAAAFVWVqqqgBVqqqoFAKpapWoKqqqqCqqqqKqqqqqqqqqqVaqqqqqqWqqqqqqqqqqlqqqqqqqqqqgABVgAAAQVZWqqqgAAVaqqqBQChapWqqCqqqoKoqqqqqqqqoCqqoqqqqlWqqqqqqqoWqqqqqqqqqqqqqqqqqqlqqqlqqqqqqAAFWgAAAQVZWqqqqAAAFWqqqgUUVWqCqqqqqoKqqqqqlqqqqlqqqqqqqqqqVaqqqqqqqhaqqqqqqqqqqqqqqqpaqqqqqqqlWqqqVValQqqqgqqqqWqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqgqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqgqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqCqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqCqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqCqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqJVVVVVU');}catch(_){return;}
 if(bytes.length!==573)return;
 const table=new Map(),counts={10:0,15:0,20:0};
 for(let i=0;i<ids.length;i++){
   const code=(bytes.charCodeAt(i>>>2) >>> (6-2*(i&3))) & 3;
   const pattern=[10,15,20][code];
   if(!pattern)return;
   table.set(ids[i],pattern);counts[pattern]++;
 }
 if(counts[10]!==248||counts[15]!==245||counts[20]!==1798||
    table.get(10011)!==10||table.get(10021)!==15||
    table.get(10025)!==20||table.get(60015)!==10||
    table.get(87602603)!==15)return;
 const source=Object.freeze({
   archiveSha256:'69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9',
   master:'2022 F_UNIT_MST_1/2_Ver1084.json:unitExpPatternId',
   originalUnitRecords:2291,patterns:Object.freeze({...counts}),
   numericExpThresholdsVerifiedFor2022:false,liveExpChanged:false,
   savedExpChanged:false,saveFieldsAdded:0
 });
 window.BFGlobalOriginalExpPatternIdsV12100=Object.freeze({
   source,lookup:id=>Number.isSafeInteger(id)?table.get(id)??null:null
 });
})();
