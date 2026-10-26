/* BF_GLOBAL_SOURCE_SPEAKER_CUES_V2800 */
(() => {
 'use strict';
 const archive=window.BFGlobalOriginalEventsV2200;
 const portraits=window.BFGlobalOriginalEventPortraitsV2600;
 if(window.BFGlobalDialogueSpeakerV2800||!archive||!portraits||
    !window.BFOriginalEventStageV2700 || typeof QUESTS==='undefined'||QUESTS.length!==106)return;
 const text=document.getElementById('bf2200-text');
 const portraitName=document.getElementById('bf2600-character');
 if(!text||!portraitName)return;
 // Each digit is the chrN_* image family preceding the corresponding MSGDRAW.
 // Exact line-by-line scan of source content/event/map[1-3]-dungeon[1-7].txt.
 // 0 would represent a frame without a declared character source (none here).
 const rows=Object.freeze({
  'map1-dungeon1.txt':'111111111111111111111111111111111111',
  'map1-dungeon2.txt':'111111111111111111111111',
  'map1-dungeon3.txt':'111111111111',
  'map1-dungeon4.txt':'11111111111',
  'map1-dungeon5.txt':'11111111111111111',
  'map1-dungeon6.txt':'1111111111111',
  'map1-dungeon7.txt':'1111111111',
  'map2-dungeon1.txt':'2222222222222222',
  'map2-dungeon2.txt':'1111111111111',
  'map2-dungeon3.txt':'22222222222222',
  'map2-dungeon4.txt':'2222222222222222',
  'map2-dungeon5.txt':'2222222233322323332333332233332',
  'map2-dungeon6.txt':'22223322333222233222232222',
  'map2-dungeon7.txt':'2322222232223232322333223323223223233323333322222',
  'map3-dungeon1.txt':'111111111111111',
  'map3-dungeon2.txt':'1111111111111111',
  'map3-dungeon3.txt':'111111111111',
  'map3-dungeon4.txt':'11111111111111111',
  'map3-dungeon5.txt':'11111111111111113333333333333333333333333333',
  'map3-dungeon7.txt':'2222222222222'
 });
 const people=Object.freeze({'1':'Tilith','2':'Karl','3':'Seria'});
 if(Object.keys(rows).length!==20)return;
 for(const [name,sequence] of Object.entries(rows)){
   const found=/^map([123])-dungeon([1-7])\.txt$/.exec(name);
   if(!found || !/^[123]+$/.test(sequence))return;
   const region=Number(found[1]),part=Number(found[2]);
   const id=region===1?part*10+10:region===2?part*10+190:part*10+290;
   const s=archive.lookup('dungeon',id);
   if(!s||s.source!=='content/event/'+name||s.lines.length!==sequence.length)return;
 }
 const marker=document.createElement('small');marker.id='bf2800-speaker';
 marker.style.cssText='display:block;margin:5px 0;color:#f4d69d;font:700 11px system-ui,sans-serif';
 portraitName.after(marker);
 function lookup(source,step){
   const sequence=rows[source];
   if(!sequence||!Number.isInteger(step)||step<1||step>sequence.length)return null;
   return people[sequence[step-1]]||null;
 }
 function snapshot(){
   const current=archive.snapshot();
   const name=lookup(current?.source,current?.step);
   return Object.freeze({source:current?.source||null,step:current?.step||0,
     character:name,supportedScenes:Object.keys(rows).length});
 }
 function refresh(){
   const current=snapshot(),character=current.character;
   marker.hidden=!character;
   if(!character)return current;
   marker.textContent='2022 SOURCE SPEAKER · '+character;
   if(portraitName.textContent!==character){
     const buttons=document.querySelectorAll('#bf2600-portrait-controls button');
     const candidate=[...buttons].find(button=>button.textContent===character);
     if(candidate && !candidate.disabled)candidate.click();
   }
   return current;
 }
 new MutationObserver(refresh).observe(text,{childList:true,characterData:true,subtree:true});
 document.getElementById('bf2200-scenes')?.addEventListener('change',()=>queueMicrotask(refresh));
 refresh();
 window.BFGlobalDialogueSpeakerV2800=Object.freeze({lookup,snapshot,refresh});
})();
