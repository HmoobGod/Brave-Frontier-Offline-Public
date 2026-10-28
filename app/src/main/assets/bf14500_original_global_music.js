/* BF_ORIGINAL_2022_GLOBAL_OPTIN_MUSIC_V14500 */
(() => {
 'use strict';
 // 2022 source mission cue names; native map-vs-boss timing unknown.
 // No automatic playback, no saved setting, no archive-trial injection.
 if(window.BFOriginalGlobalMusicV14500||
    typeof P==='undefined'||P.version!==7||
    typeof QUESTS==='undefined'||QUESTS.length!==106)return;
 const canonical='b58c3a6af195fa1cce0ffa21025e813be44b589acdad6bf15c8c3230694ee6db';
 const records=[[1,"bf010_map_grass.mp3","bf006_btl_boss.mp3"],[2,"bf010_map_grass.mp3","bf006_btl_boss.mp3"],[10,"bf010_map_grass.mp3","bf006_btl_boss.mp3"],[11,"bf010_map_grass.mp3","bf006_btl_boss.mp3"],[12,"bf010_map_grass.mp3","bf006_btl_boss.mp3"],[20,"bf011_map_firecave.mp3","bf006_btl_boss.mp3"],[21,"bf011_map_firecave.mp3","bf006_btl_boss.mp3"],[22,"bf011_map_firecave.mp3","bf006_btl_boss.mp3"],[23,"bf011_map_firecave.mp3","bf006_btl_boss.mp3"],[30,"bf012_map_snow.mp3","bf006_btl_boss.mp3"],[31,"bf012_map_snow.mp3","bf006_btl_boss.mp3"],[32,"bf012_map_snow.mp3","bf006_btl_boss.mp3"],[33,"bf012_map_snow.mp3","bf006_btl_boss.mp3"],[40,"bf013_map_wood.mp3","bf006_btl_boss.mp3"],[41,"bf013_map_wood.mp3","bf006_btl_boss.mp3"],[42,"bf013_map_wood.mp3","bf006_btl_boss.mp3"],[43,"bf013_map_wood.mp3","bf006_btl_boss.mp3"],[50,"bf014_map_swamp.mp3","bf006_btl_boss.mp3"],[51,"bf014_map_swamp.mp3","bf006_btl_boss.mp3"],[52,"bf014_map_swamp.mp3","bf006_btl_boss.mp3"],[53,"bf014_map_swamp.mp3","bf006_btl_boss.mp3"],[60,"bf015_map_wilds.mp3","bf006_btl_boss.mp3"],[61,"bf015_map_wilds.mp3","bf006_btl_boss.mp3"],[62,"bf015_map_wilds.mp3","bf006_btl_boss.mp3"],[63,"bf015_map_wilds.mp3","bf006_btl_boss.mp3"],[70,"bf016_map_ghost.mp3","bf006_btl_boss.mp3"],[71,"bf016_map_ghost.mp3","bf006_btl_boss.mp3"],[72,"bf016_map_ghost.mp3","bf006_btl_boss.mp3"],[73,"bf016_map_ghost.mp3","bf006_btl_boss.mp3"],[81,"bf017_map_tower01.mp3","bf006_btl_boss.mp3"],[82,"bf017_map_tower01.mp3","bf006_btl_boss.mp3"],[83,"bf017_map_tower01.mp3","bf006_btl_boss.mp3"],[84,"bf017_map_tower01.mp3","bf006_btl_boss.mp3"],[85,"bf017_map_tower01.mp3","bf006_btl_boss.mp3"],[200,"bf018_map_sand.mp3","bf006_btl_boss.mp3"],[201,"bf018_map_sand.mp3","bf006_btl_boss.mp3"],[202,"bf018_map_sand.mp3","bf006_btl_boss.mp3"],[203,"bf018_map_sand.mp3","bf006_btl_boss.mp3"],[204,"bf018_map_sand.mp3","bf006_btl_boss.mp3"],[210,"bf019_map_shore.mp3","bf006_btl_boss.mp3"],[211,"bf019_map_shore.mp3","bf006_btl_boss.mp3"],[212,"bf019_map_shore.mp3","bf006_btl_boss.mp3"],[213,"bf019_map_shore.mp3","bf006_btl_boss.mp3"],[214,"bf019_map_shore.mp3","bf006_btl_boss.mp3"],[220,"bf020_map_nightwood.mp3","bf006_btl_boss.mp3"],[221,"bf020_map_nightwood.mp3","bf006_btl_boss.mp3"],[222,"bf020_map_nightwood.mp3","bf006_btl_boss.mp3"],[223,"bf020_map_nightwood.mp3","bf006_btl_boss.mp3"],[224,"bf020_map_nightwood.mp3","bf006_btl_boss.mp3"],[230,"bf021_map_wasteland.mp3","bf006_btl_boss.mp3"],[231,"bf021_map_wasteland.mp3","bf006_btl_boss.mp3"],[232,"bf021_map_wasteland.mp3","bf006_btl_boss.mp3"],[233,"bf021_map_wasteland.mp3","bf006_btl_boss.mp3"],[234,"bf021_map_wasteland.mp3","bf006_btl_boss.mp3"],[240,"bf022_map_temple.mp3","bf006_btl_boss.mp3"],[241,"bf022_map_temple.mp3","bf006_btl_boss.mp3"],[242,"bf022_map_temple.mp3","bf006_btl_boss.mp3"],[243,"bf022_map_temple.mp3","bf006_btl_boss.mp3"],[244,"bf022_map_temple.mp3","bf006_btl_boss.mp3"],[250,"bf023_map_ruins.mp3","bf006_btl_boss.mp3"],[251,"bf023_map_ruins.mp3","bf006_btl_boss.mp3"],[252,"bf023_map_ruins.mp3","bf006_btl_boss.mp3"],[253,"bf023_map_ruins.mp3","bf006_btl_boss.mp3"],[254,"bf023_map_ruins.mp3","bf006_btl_boss.mp3"],[260,"bf017_map_tower01.mp3","bf006_btl_boss.mp3"],[261,"bf017_map_tower01.mp3","bf006_btl_boss.mp3"],[262,"bf017_map_tower01.mp3","bf006_btl_boss.mp3"],[263,"bf017_map_tower01.mp3","bf006_btl_boss.mp3"],[264,"bf017_map_tower01.mp3","bf006_btl_boss.mp3"],[265,"bf017_map_tower01.mp3","bf028_map_space.mp3"],[300,"bf011_map_firecave.mp3","bf006_btl_boss.mp3"],[301,"bf011_map_firecave.mp3","bf006_btl_boss.mp3"],[302,"bf011_map_firecave.mp3","bf006_btl_boss.mp3"],[303,"bf011_map_firecave.mp3","bf006_btl_boss.mp3"],[304,"bf011_map_firecave.mp3","bf006_btl_boss.mp3"],[310,"bf012_map_snow.mp3","bf006_btl_boss.mp3"],[311,"bf012_map_snow.mp3","bf006_btl_boss.mp3"],[312,"bf012_map_snow.mp3","bf006_btl_boss.mp3"],[313,"bf012_map_snow.mp3","bf006_btl_boss.mp3"],[314,"bf012_map_snow.mp3","bf006_btl_boss.mp3"],[320,"bf016_map_ghost.mp3","bf006_btl_boss.mp3"],[321,"bf016_map_ghost.mp3","bf006_btl_boss.mp3"],[322,"bf016_map_ghost.mp3","bf006_btl_boss.mp3"],[323,"bf016_map_ghost.mp3","bf006_btl_boss.mp3"],[324,"bf016_map_ghost.mp3","bf006_btl_boss.mp3"],[330,"bf013_map_wood.mp3","bf006_btl_boss.mp3"],[331,"bf013_map_wood.mp3","bf006_btl_boss.mp3"],[332,"bf013_map_wood.mp3","bf006_btl_boss.mp3"],[333,"bf013_map_wood.mp3","bf006_btl_boss.mp3"],[334,"bf013_map_wood.mp3","bf006_btl_boss.mp3"],[340,"bf019_map_shore.mp3","bf006_btl_boss.mp3"],[341,"bf019_map_shore.mp3","bf006_btl_boss.mp3"],[342,"bf019_map_shore.mp3","bf006_btl_boss.mp3"],[343,"bf019_map_shore.mp3","bf006_btl_boss.mp3"],[344,"bf019_map_shore.mp3","bf006_btl_boss.mp3"],[350,"bf024_map_cave.mp3","bf006_btl_boss.mp3"],[351,"bf024_map_cave.mp3","bf006_btl_boss.mp3"],[352,"bf024_map_cave.mp3","bf006_btl_boss.mp3"],[353,"bf024_map_cave.mp3","bf006_btl_boss.mp3"],[354,"bf024_map_cave.mp3","bf006_btl_boss.mp3"],[360,"bf025_map_castle.mp3","bf006_btl_boss.mp3"],[361,"bf025_map_castle.mp3","bf006_btl_boss.mp3"],[362,"bf025_map_castle.mp3","bf006_btl_boss.mp3"],[363,"bf025_map_castle.mp3","bf006_btl_boss.mp3"],[364,"bf025_map_castle.mp3","bf006_btl_boss.mp3"],[365,"bf025_map_castle.mp3","bf028_map_space.mp3"]];
 const bundled=new Set(["bf006_btl_boss.mp3","bf010_map_grass.mp3","bf011_map_firecave.mp3"]);
 const map=new Map();
 if(records.length!==106||bundled.size!==3)return;
 for(const row of records){
   if(row.length!==3||!Number.isSafeInteger(row[0])||
      typeof row[1]!=='string'||typeof row[2]!=='string'||
      !/^bf[0-9]{3}_[a-z0-9_]+\.mp3$/.test(row[1])||
      !/^bf[0-9]{3}_[a-z0-9_]+\.mp3$/.test(row[2])||
      map.has(row[0]))return;
   map.set(row[0],Object.freeze({missionId:row[0],map:row[1],boss:row[2]}));
 }
 if(map.size!==106||QUESTS.some(q=>!map.has(q.missionId)))return;
 const host=document.getElementById('questinfo');
 if(!host||typeof Audio!=='function')return;
 const box=document.createElement('section');
 box.id='bf145-original-music';
 box.style.cssText='padding:8px 10px;margin:8px 0;border:1px solid #67869a;border-radius:7px;background:#1b2e42;color:#e0eaf1;font:12px/1.4 system-ui,sans-serif';
 const title=document.createElement('strong');
 title.textContent='2022 GLOBAL · ORIGINAL MUSIC (OPTIONAL)';
 const note=document.createElement('p');
 note.textContent='Only 3 exact archived tracks are bundled. Tap to play; other source cues remain silent. 2022 native playback timing is unverified. No saved setting.';
 const mapBtn=document.createElement('button');mapBtn.type='button';
 const bossBtn=document.createElement('button');bossBtn.type='button';
 const stopBtn=document.createElement('button');stopBtn.type='button';
 mapBtn.textContent='Play map';bossBtn.textContent='Play boss';stopBtn.textContent='Stop';
 for(const b of [mapBtn,bossBtn,stopBtn]){
  b.style.cssText='min-height:38px;margin:3px;padding:6px 9px;background:#2d4b62;border:1px solid #9cb4c5;border-radius:5px;color:white';
 }
 const status=document.createElement('p');status.id='bf145-original-music-status';
 status.setAttribute('aria-live','polite');
 box.append(title,note,mapBtn,bossBtn,stopBtn,status);
 host.after(box);
 const sound=new Audio();sound.loop=true;sound.preload='none';sound.volume=0.42;
 let active=null;let intent=null;let stopped=true;
 function current(){
   if(typeof QUEST==='undefined'||!QUEST||
      !map.has(QUEST.missionId))return null;
   return map.get(QUEST.missionId);
 }
 function stop(){
   sound.pause();sound.removeAttribute('src');sound.load();
   active=null;intent=null;stopped=true;
   refresh();return true;
 }
 function refresh(){
   const q=current(),mode=typeof E==='undefined'?null:E.mode?.value;
   const enabled=mode==='archive'&&!!q;
   const hasMap=enabled&&bundled.has(q.map),hasBoss=enabled&&bundled.has(q.boss);
   mapBtn.disabled=!hasMap;bossBtn.disabled=!hasBoss;
   stopBtn.disabled=stopped;
   if(!enabled){
     status.textContent='Select an archived story mission to view original cues.';
     if(!stopped)stop();return null;
   }
   const song=active==='map'?q.map:active==='boss'?q.boss:null;
   if(active&&song&&sound.getAttribute('src')!==('content/sound/'+song)){
     sound.pause();sound.removeAttribute('src');sound.load();
     stopped=true;active=null;intent=null;
   }
   status.textContent='Mission '+q.missionId+' · Map: '+q.map+
     (hasMap?' (bundled)':' (not bundled)')+' · Boss: '+q.boss+
     (hasBoss?' (bundled)':' (not bundled)')+
     ' · '+(stopped?'Music off':'Playing '+active+' (manual choice)');
   return Object.freeze({map:q.map,boss:q.boss,hasMap,hasBoss,playing:!stopped});
 }
 function play(kind){
   const q=current(),mode=typeof E==='undefined'?null:E.mode?.value;
   const file=kind==='map'?q?.map:kind==='boss'?q?.boss:null;
   if(mode!=='archive'||!file||!bundled.has(file))return false;
   sound.pause();sound.src='content/sound/'+file;
   active=kind;intent=file;stopped=false;
   const result=sound.play();
   if(result&&typeof result.catch==='function')result.catch(()=>{
     if(intent!==file)return;
     stopped=true;active=null;intent=null;
     sound.pause();status.textContent='Playback blocked or unavailable. Tap Play again.';
   });
   refresh();return true;
 }
 mapBtn.addEventListener('click',()=>play('map'));
 bossBtn.addEventListener('click',()=>play('boss'));
 stopBtn.addEventListener('click',stop);
 document.addEventListener('visibilitychange',()=>{
   if(document.hidden&&!stopped)stop();
 });
 const list=document.getElementById('questlist');
 if(list)new MutationObserver(()=>refresh()).observe(list,{childList:true});
 const mode=document.getElementById('mode');
 if(mode)mode.addEventListener('change',refresh);
 refresh();
 window.BFOriginalGlobalMusicV14500=Object.freeze({
   source:Object.freeze({year:2022,missions:106,sourceSha256:canonical,originalFiles:18,
     bundledTracks:3,nativePlaybackTimingKnown:false,
     autoplay:false,saveMutation:false}),
   lookup:id=>map.get(id)||null,refresh,
   get state(){return Object.freeze({active,stopped,src:sound.getAttribute('src')});}
 });
})();
