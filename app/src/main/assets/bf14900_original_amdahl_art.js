/* BF_GLOBAL_AMDAHL_ORIGINAL_ART_VIEW_V14900 */
(() => {
 'use strict';
 // Original 2022 Global Amdahl map + seven original battle backgrounds.
 // Evidence only: 2022 enemy wave/AI data is not decoded; no quests unlocked.
 if(window.BFAmdahlOriginalArtV14900 || !window.BFGrandGaiaCampaignV100 ||
    typeof P==='undefined' || P.version!==7 ||
    typeof QUESTS==='undefined' || QUESTS.length!==106 ||
    typeof S==='undefined')return;
 const rows=[{"id":400,"name":"Julep Village","x":39,"y":779,"battleBackground":"dungeon_battle_50100.jpg","requires":365,"firstMissionId":400},{"id":410,"name":"Ghost Ship Legnia","x":430,"y":775,"battleBackground":"dungeon_battle_50200.jpg","requires":404,"firstMissionId":410},{"id":420,"name":"Elios Plains","x":197,"y":633,"battleBackground":"dungeon_battle_50300.jpg","requires":414,"firstMissionId":420},{"id":430,"name":"Saji Mines","x":74,"y":480,"battleBackground":"dungeon_battle_50400.jpg","requires":424,"firstMissionId":430},{"id":440,"name":"Lamellia Temple","x":121,"y":318,"battleBackground":"dungeon_battle_50500.jpg","requires":434,"firstMissionId":440},{"id":450,"name":"Ghost Town Edila","x":23,"y":201,"battleBackground":"dungeon_battle_50600.jpg","requires":444,"firstMissionId":450},{"id":460,"name":"Amdahl Castle","x":403,"y":192,"battleBackground":"dungeon_battle_50700.jpg","requires":454,"firstMissionId":460}];
 const original=Object.freeze({landId:3,areaId:400,sourceYear:2022,
   originalWorldArt:'content/area/area_0004.jpg',
   originalMapPlate:'content/area/area_plate_0004.png',
   originalImageSize:Object.freeze([640,960]),
   decodedEnemyWaves:false,originalGameplayEnabled:false,
   ownerSourceSha256:'65790b0c0e9099fedb347e4a0c53f76bde7ebe3ea0cb7b9089557cf51c759179'});
 if(rows.length!==7 || new Set(rows.map(d=>d.id)).size!==7 ||
    rows.some((d,i)=>d.id!==400+10*i || d.firstMissionId!==d.id ||
    d.x<0||d.x>640||d.y<0||d.y>960 ||
    d.battleBackground!=='dungeon_battle_'+(50100+100*i)+'.jpg'))return;
 const campaign=document.getElementById('bf100-campaign');
 if(!campaign)return;
 const section=document.createElement('details');section.id='bf14900-amdahl-art';
 section.style.cssText='padding:11px;margin:12px 0;border:1px solid #93764b;'+
   'border-radius:8px;background:#15273a;color:#f7e9d2;font:12px/1.45 system-ui';
 const summary=document.createElement('summary');
 summary.textContent='AMDAHL · ORIGINAL 2022 MAP & DUNGEONS (PREVIEW)';
 summary.style.cssText='cursor:pointer;font-weight:750;min-height:28px';
 const notice=document.createElement('p');notice.className='bf14900-notice';
 notice.textContent='Recovered original 2022 artwork and quest references. '+
    'Amdahl battles are NOT playable: enemy waves and native AI remain undecoded. '+
    'This preview never spends Energy, changes progress or unlocks quests.';
 const world=document.createElement('div');world.style.cssText=
    'position:relative;width:100%;max-width:400px;aspect-ratio:2/3;margin:6px auto;'+
    'border:1px solid #b39764;background:#111c2a;overflow:hidden';
 const image=document.createElement('img');
 image.src=original.originalWorldArt;
 image.alt='Original Brave Frontier Global Amdahl world map';
 image.style.cssText='width:100%;height:100%;display:block;object-fit:fill';
 world.append(image);
 const detail=document.createElement('section');detail.id='bf14900-selected';
 const title=document.createElement('strong');
 const info=document.createElement('p');
 const background=document.createElement('img');
 background.style.cssText='max-width:100%;max-height:180px;object-fit:contain;display:block';
 background.alt='Original Amdahl battle background';
 detail.append(title,info,background);
 const pins=new Map();
 for(const d of rows){
   const pin=document.createElement('button');pin.type='button';
   pin.textContent=String(d.id);pin.dataset.bf14900Dungeon=String(d.id);
   pin.title=d.name;pin.setAttribute('aria-label','Preview '+d.name+' original dungeon art');
   pin.style.cssText='position:absolute;transform:translate(-50%,-50%);'+
     'border:1px solid #f4e5bc;border-radius:50%;padding:3px 5px;'+
     'font:700 10px system-ui;color:#fff;background:#504766;min-width:33px;min-height:33px';
   pin.style.left=(d.x/640*100)+'%';pin.style.top=(d.y/960*100)+'%';
   pin.addEventListener('click',()=>preview(d.id));
   pins.set(d.id,pin);world.append(pin);
 }
 function lookup(id){return rows.find(r=>r.id===id)||null;}
 function preview(id){
   const d=lookup(id);if(!d)return false;
   title.textContent=d.name+' · Original dungeon #'+d.id;
   info.textContent='Original first mission '+d.firstMissionId+
     ' · original prerequisite mission '+d.requires+
     ' · preview only; quests 400–465 are not in the playable 106-quest catalog.';
   background.src='content/dungeon/'+d.battleBackground;
   background.alt='Original 2022 Global '+d.name+' battle background';
   for(const [key,button] of pins){
     button.setAttribute('aria-pressed',String(key===id));
     button.style.outline=key===id?'2px solid #a4e7fa':'none';
   }
   return true;
 }
 const footer=document.createElement('small');
 footer.textContent='Owner 2022 BF1 area/dungeon archive; original source images, '+
   'world coordinates, names. No combat, quest, loot, AI or save mutations.';
 section.append(summary,notice,world,detail,footer);
 campaign.after(section);preview(400);
 window.BFAmdahlOriginalArtV14900=Object.freeze({
   source:original,entries:Object.freeze(rows.map(r=>Object.freeze({...r}))),
   lookup,preview
 });
})();
