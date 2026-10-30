/* BF_AMDAHL_ORIGINAL_2022_STORY_GUIDE_V20600 */
(() => {
 'use strict';
 // Read-only source-backed 36-mission Amdahl journal; absolutely no battles, wallet, save or unlock.
 const MASTER_SHA256='d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83';
 const QUEST_SHA256='f35a7b06bc9e6fae6facc1fd77422f74c04798da4fb87f64a2737a0483a572c3';
 const art=window.BFAmdahlOriginalArtV14900, refs=window.BFGlobalEncounterReferencesV15100;
 if(window.BFAmdahlSourceQuestGuideV20600 || typeof P==='undefined' || P.version!==7 ||
   typeof QUESTS==='undefined' || !Array.isArray(QUESTS) || QUESTS.length!==106 ||
   !art || art.entries?.length!==7 || art.source?.sourceYear!==2022 ||
   art.source?.originalGameplayEnabled!==false ||
   art.source?.decodedEnemyWaves!==false || !refs ||
   refs.summary?.sourceYear!==2022 ||
   refs.summary?.sha256!==MASTER_SHA256 ||
   refs.summary?.amdahlQuestCanonicalSha256!==QUEST_SHA256 ||
   refs.summary?.amdahlSourceOnlyMissions!==36 || refs.summary?.playableMissions!==106 ||
   refs.summary?.meaningDecoded!==false || refs.summary?.gameplayMutation!==false ||
   refs.summary?.saveMutation!==false) return;
 const rows=[[400,400,365,8,10,1800,1000,0,"The Scars of War","Amdahl, one of the islands in the Palmyna Archipelago which is ruled over by Cardes the Malevolent. A town can be seen near the entrance, having been devastated by war. "],[401,400,400,8,10,1950,1000,0,"Abandoned Ruins","Past the damaged houses lies nothing but fiery ruins. Could these flames be the work of monsters?"],[402,400,401,9,12,2100,1500,0,"Presence of Flames","You can feel the flames growing stronger. This might be a sign that something dangerous is waiting ahead."],[403,400,402,10,12,2200,1500,0,"Of Thunder and Flames","When lightning strikes it sometimes ignites the earth where it hits. The force that controls the lightning and flames has set their aim on you."],[404,400,403,11,14,2350,2000,0,"In Comes a Fire God","A figure watches you from the shadows as you attempt to leave the village. It seems all the intense fighting has attracted the attention of a fire god."],[410,410,404,8,10,1830,1000,0,"Party On Board","Monsters snarl in unison as they scheme to make you their main dish at this ghost ship party."],[411,410,410,8,10,1980,1000,0,"Venture Inside","What could be waiting unbeknownst to history in this ship that appeared so long ago? You can't deny your curiosity."],[412,410,411,9,12,2140,1500,0,"Dragon's Roar","You can hear a water dragon's roar even from inside the ship. Is this howl meant to get rid of those who disturb the souls of the dead crew members?"],[413,410,412,10,12,2240,1500,0,"Frozen Blades","As you try to escape the ghost ship to investigate, a frigid swordsman appears before you, along with his sword techniques which can turn anything to ice."],[414,410,413,11,14,2380,2000,0,"A Water God Appears","It seems you must leave Amdahl if you are to defeat Cardes, but before that you need to escape the ghost ship."],[420,420,414,8,10,1890,1000,0,"Windswept Prairie","You stop in a field, surprised by a mysterious man who now blocks your path. There's no time to loiter, you need to shake your fear and push ahead."],[421,420,420,8,10,2030,1000,0,"The Graceful Figure","On your way toward Amdahl Castle, an incredibly graceful figure appears before you. Vanquish it and move ahead."],[422,420,421,9,12,2220,1500,0,"From Forest's Shadow","You've come to a prairie covered in trees and shrubs, but what is that lurking in the shadows, seemingly ready to strike..."],[423,420,422,10,12,2300,1500,0,"Princess of the Pond","Nearing a pond at the edge of the prairie, some Water Nymphs stand in your way as if they're protecting something. What could it be?"],[424,420,423,11,14,2440,2000,0,"The Gallant Earth God","On your way from the prairie, someone has been sent to block your path. Carefully proceed forward."],[430,430,424,8,10,1920,1000,0,"The Rotting Bridge","After parting with Karl and Seria you proceed through the mines. Making your way through the monster infested tunnels, you come across a decaying bridge."],[431,430,430,8,10,2050,1000,0,"Enlightenment of the Ages","It seems the demon Graham who escaped from Mistral has shown up around here. Could this strong presence coming from ahead be him? Or maybe..."],[432,430,431,9,12,2260,1500,0,"Where Thunder Pulses","Continuing through the mines, you occasionally hear the sound of thunder. Whether it's natural or the roar of some thunder beast, surely you'll find out soon."],[433,430,432,10,12,2340,1500,0,"Lightning Quick Attack","The center of the mine is full of traps. Blades are also quickly flashing about. Eliminate those who stand in your way and advance!"],[434,430,433,11,14,2450,2000,0,"A Thunder God Strikes","A sanctuary can be seen shining just beyond the mine. The exit seems to be within reach. All you have to do is defeat the enemies before you."],[440,440,434,9,12,2300,2000,0,"Forest Sanctuary","According to a mysterious old man, this sanctuary holds information on the Four Heroes of Old. Take a quick detour and check it out. "],[441,440,440,9,12,2380,2000,0,"Descending Force","A warrior carrying a massive sword appears before you as you're searching for information on the Four Heroes. He swings at you as he approaches."],[442,440,441,10,14,2500,2500,0,"Radiant Helix","The sunlight shining on the sanctuary is as pleasant as Tilith said it would be, but who is this coming in to bathe in the light the same as she would have..."],[443,440,442,11,14,2550,2500,0,"Hades Blast","A gunshot suddenly echoes through the solemn sanctuary interior. As startled as you are, you see a shining marksman before you. "],[444,440,443,12,15,2700,3000,0,"Light God's Progression","There doesn't seem to be any particularly important information in the sanctuary. It's time to end your detour and set your sites back on Amdahl Castle."],[450,450,444,9,12,2350,2000,0,"Never Ending Rain","According to Karl and Seria, Graham has already left this place. However, you should still be cautious as you proceed."],[451,450,450,9,12,2430,2000,0,"Dark Night Requiem","The remains of a city thought to have at one time prided itself on its extravagance. It seems someone is controlling the spirits who would otherwise be at rest here."],[452,450,451,10,14,2550,2500,0,"A Thirst for Blood","Your senses suddenly heighten. Could it be this intense blood-thirsty presence you feel up ahead? It's already too late to turn back."],[453,450,452,11,14,2600,2500,0,"Pure Magic Barrier","You pick up an item while advancing through the destroyed city. It's a powerful magic barrier, the likes of which have never been seen."],[454,450,453,12,15,2780,3000,0,"A Dark God Emerges","As you exit Edila you're able to see the entrance to Amdahl Castle, but suddenly, a figure consumed by darkness blocks your way forward."],[460,460,454,9,12,2400,2000,0,"The Commander's Power","Amdahl Castle, where vengeful ghosts of the past are said to reside. Through here is the only way to get to Palmyna, the land sealed away by Cardes the Malevolent."],[461,460,460,9,12,2480,2000,0,"The Commander's Skill","According to Elder Grah, a vengeful ghost that resents humans lives here. Still, you mustn't lose your way, even if only to prevent yourself from becoming a ghost as well."],[462,460,461,10,14,2650,2000,0,"The Princess' Ball","The beautifully decorated interior of the castle suggests that at one time many an extravagant banquet was held here. But all relics aside, it's time to head further inside."],[463,460,462,11,15,2700,2000,0,"Dark Surge","There is light and darkness wherever you go. But still, where did the darkness in the Amdahl Empire come from? There's probably no longer anyone around that knows."],[464,460,463,12,15,2800,2000,0,"Light Pulse","The end of Amdahl, the first island in the Palmyna Archipelago, is within sight. However, there are still some rather troublesome enemies about..."],[465,460,464,12,17,3000,3000,0,"Malevolent Ceremony","You sense a strikingly ominous presence coming from the path ahead. What awaits you isn't a god like before, but some being with a strong resentment toward humans."]];
 const ids=[400,410,420,430,440,450,460], seen=new Set();
 if(rows.length!==36 || rows.some((r,i)=>{
   if(!Array.isArray(r)||r.length!==10 || seen.has(r[0]))return true;
   const id=i<30?400+10*Math.floor(i/5)+(i%5):460+i-30;
   const dungeon=i<30?400+10*Math.floor(i/5):460;
   const valid=r[0]===id && r[1]===dungeon && r[2]===(i?rows[i-1][0]:365) &&
     Number.isSafeInteger(r[3]) && r[3]>=1 && r[3]<=30 &&
     [r[4],r[5],r[6],r[7]].every(n=>Number.isSafeInteger(n)&&n>=0) &&
     typeof r[8]==='string' && r[8].length>0 && typeof r[9]==='string' && r[9].length>0;
   const prior=refs.lookup(r[0]);
   if(!valid || !prior || prior.dungeonId!==r[1] || prior.requires!==r[2] ||
     prior.originalSourceWaveCount!==r[3] || prior.name!==r[8] || prior.playable!==false)return true;
   seen.add(r[0]); return false;
 }))return;
 const root=document.getElementById('bf14900-amdahl-art');
 if(!root || document.getElementById('bf20600-amdahl-guide') ||
    ids.some(id=>!art.lookup(id)))return;
 const block=document.createElement('details');block.id='bf20600-amdahl-guide';
 block.style.cssText='margin:12px 0 4px;padding:10px;border:1px solid #95886e;border-radius:6px;background:#1b3047';
 const heading=document.createElement('summary');
 heading.textContent='ORIGINAL 2022 AMDAHL STORY · 36 QUESTS (READ-ONLY)';
 heading.style.cssText='font-weight:750;cursor:pointer;min-height:28px';
 const disclaimer=document.createElement('p');
 disclaimer.textContent='Original English story text, prerequisites, wave counts, Energy, EXP, Zel and Karma. Amdahl battles are not playable; original enemies, AI and loot remain unverified. No Energy or Gems are spent here.';
 const label=document.createElement('label');label.textContent='Source dungeon: ';
 const select=document.createElement('select');select.id='bf20600-dungeon';
 select.style.cssText='max-width:100%;padding:7px;color:#fff;background:#253950;border:1px solid #91806b';
 for(const id of ids){
   const d=art.lookup(id),option=document.createElement('option');
   option.value=String(id);option.textContent=d.name+' ('+id+')';select.append(option);
 }
 label.append(select);
 const list=document.createElement('ol');list.id='bf20600-quest-list';
 list.style.cssText='padding-left:23px;margin:10px 0';
 function preview(id){
   if(!ids.includes(id))return 0;
   select.value=String(id);list.replaceChildren();
   for(const r of rows.filter(x=>x[1]===id)){
     const li=document.createElement('li');li.dataset.missionId=String(r[0]);
     li.style.cssText='margin-bottom:12px;line-height:1.45';
     const name=document.createElement('strong');name.textContent=r[0]+' · '+r[8];
     const desc=document.createElement('p');desc.textContent=r[9];desc.style.margin='4px 0';
     const meta=document.createElement('small');
     meta.textContent='Requires mission '+r[2]+' · '+r[3]+' source waves (rosters unknown) · Energy '+r[4]+
       ' · '+r[5]+' EXP · '+r[6]+' Zel · '+r[7]+' Karma · NOT PLAYABLE';
     li.append(name,desc,meta);list.append(li);
   }
   return list.children.length;
 }
 select.addEventListener('change',()=>{
   const id=Number(select.value);preview(id);art.preview(id);
 });
 for(const pin of root.querySelectorAll('[data-bf14900-dungeon]')){
   const id=Number(pin.dataset.bf14900Dungeon);
   if(ids.includes(id))pin.addEventListener('click',()=>preview(id));
 }
 block.append(heading,disclaimer,label,list);root.append(block);preview(400);
 window.BFAmdahlSourceQuestGuideV20600=Object.freeze({
   source:Object.freeze({year:2022,masterSha256:MASTER_SHA256,
     canonicalQuestSha256:QUEST_SHA256,
     missions:36,originalEnemyWavesVerified:false,playable:false,saveMutation:false}),
   lookup:id=>Number.isSafeInteger(id)?rows.find(r=>r[0]===id)?.slice()||null:null,preview
 });
})();
