/* BF_HISTORICAL_GLOBAL_ENCOUNTERS_V120 */
(() => {
 'use strict';
 if(window.BFHistoricalEncountersV120 || typeof QUESTS==='undefined' ||
    QUESTS.length!==106 || !window.BFGlobalQuestJournalV110 ||
    !window.BFGlobalQuestText)return;
 const data={"schema":"bf-global-historical-encounters-2014-v120","provenance":"https://github.com/cheahjs/bravefrontier_data","caution":"2014 Global parsed files, NOT confirmed 2022 native spawns, sprites, AI or loot","missions":[{"id":1,"name":"Basics of Battle","sourcePath":"missions_parsed/Basics of Battle_2014-03-10-20-43.json","gitBlobSha":"797a2945a40bcfffe7dfc500c8e3dfb6eb81b8fe","waves":[{"wave":1,"enemies":[{"name":"Mossy","unitId":30030,"hp":300,"atk":290,"def":50,"aiId":1}]},{"wave":2,"enemies":[{"name":"Sparky","unitId":40030,"hp":300,"atk":320,"def":0,"aiId":1},{"name":"Mossy","unitId":30030,"hp":300,"atk":290,"def":50,"aiId":1}]},{"wave":3,"enemies":[{"name":"King Mossy","unitId":30031,"hp":3000,"atk":320,"def":30,"aiId":1}]}]},{"id":2,"name":"Element & Skill","sourcePath":"missions_parsed/Element & Skill_2014-03-10-20-47.json","gitBlobSha":"4b85fcbea4ee41c722b4d54a4140c5d84cd819b0","waves":[{"wave":1,"enemies":[{"name":"Squirty","unitId":20030,"hp":300,"atk":280,"def":10,"aiId":1},{"name":"Sparky","unitId":40030,"hp":300,"atk":320,"def":0,"aiId":1},{"name":"Mossy","unitId":30030,"hp":300,"atk":290,"def":50,"aiId":1}]},{"wave":2,"enemies":[{"name":"Burny","unitId":10030,"hp":300,"atk":300,"def":20,"aiId":1},{"name":"Mossy","unitId":30030,"hp":300,"atk":290,"def":50,"aiId":1},{"name":"Sparky","unitId":40030,"hp":300,"atk":320,"def":0,"aiId":1}]},{"wave":3,"enemies":[{"name":"Skeleton","unitId":60050,"hp":4000,"atk":340,"def":20,"aiId":1}]}]},{"id":10,"name":"Start of Adventure","sourcePath":"missions_parsed/Start of Adventure_2014-14-10-08-07.json","gitBlobSha":"556829bc0639e417ecd4dbc99ef28c44da25c621","waves":[{"wave":1,"enemies":[{"name":"Mossy","unitId":30030,"hp":830,"atk":340,"def":90,"aiId":1},{"name":"Sparky","unitId":40030,"hp":760,"atk":370,"def":0,"aiId":1}]},{"wave":2,"enemies":[{"name":"Squirty","unitId":20030,"hp":780,"atk":330,"def":20,"aiId":1},{"name":"Gloomy","unitId":60030,"hp":760,"atk":370,"def":0,"aiId":1},{"name":"Sparky","unitId":40030,"hp":760,"atk":370,"def":0,"aiId":1}]},{"wave":3,"enemies":[{"name":"Burny","unitId":10030,"hp":800,"atk":320,"def":50,"aiId":1},{"name":"Squirty","unitId":20030,"hp":780,"atk":330,"def":20,"aiId":1}]},{"wave":4,"enemies":[{"name":"Squirty","unitId":20030,"hp":780,"atk":330,"def":20,"aiId":1},{"name":"Gloomy","unitId":60030,"hp":760,"atk":370,"def":0,"aiId":1},{"name":"Sparky","unitId":40030,"hp":760,"atk":370,"def":0,"aiId":1}]},{"wave":5,"enemies":[{"name":"King Sparky","unitId":40031,"hp":2500,"atk":470,"def":30,"aiId":1}]}]},{"id":20,"name":"Cave of Dancing Flames","sourcePath":"missions_parsed/Cave of Dancing Flames_2014-14-10-08-22.json","gitBlobSha":"5049589d2ed64e08cbd6621fc332f27df945a83a","waves":[{"wave":1,"enemies":[{"name":"Burny","unitId":10030,"hp":1500,"atk":420,"def":60,"aiId":1},{"name":"Goblin","unitId":10050,"hp":1300,"atk":400,"def":90,"aiId":1}]},{"wave":2,"enemies":[{"name":"Goblin","unitId":10050,"hp":1700,"atk":450,"def":95,"aiId":1},{"name":"Fire Nymph","unitId":10130,"hp":4000,"atk":470,"def":10,"aiId":1},{"name":"Goblin","unitId":10050,"hp":1700,"atk":450,"def":95,"aiId":1}]},{"wave":3,"enemies":[{"name":"Goblin","unitId":10050,"hp":1300,"atk":400,"def":90,"aiId":1},{"name":"Goblin","unitId":10050,"hp":1300,"atk":400,"def":90,"aiId":1}]},{"wave":4,"enemies":[{"name":"Goblin","unitId":10050,"hp":1700,"atk":450,"def":95,"aiId":1},{"name":"Thief Leon","unitId":10061,"hp":2300,"atk":470,"def":20,"aiId":20}]},{"wave":5,"enemies":[{"name":"King Burny","unitId":10031,"hp":7000,"atk":470,"def":30,"aiId":1},{"name":"King Burny","unitId":10031,"hp":7000,"atk":470,"def":30,"aiId":1}]}]}]};
 const archive=new Map();
 for(const entry of data.missions){
   const q=QUESTS.find(x=>x.missionId===entry.id);
   const source=q&&BFGlobalQuestText.sourceFor(q);
   if(!source || source.mission.name!==entry.name ||
      archive.has(entry.id) || entry.waves.some((w,i)=>w.wave!==i+1 ||
      !w.enemies.length || w.enemies.some(e=>!e.name ||
      [e.unitId,e.hp,e.atk,e.def,e.aiId].some(x=>!Number.isInteger(x)))))return;
   archive.set(entry.id,Object.freeze(entry));
 }
 if(archive.size!==4)return;
 const host=document.getElementById('bf-quest-details');
 const list=document.getElementById('questlist');
 if(!host||!list)return;
 const box=document.createElement('details');box.id='bf120-historical-battles';
 box.setAttribute('aria-label','Historical 2014 Global battle records (read only)');
 box.style.cssText='padding:9px;margin:10px 2px;border:1px solid #aa9370;border-radius:6px;background:#202a39;color:#eaddc6;font:12px/1.45 system-ui,sans-serif';
 const head=document.createElement('summary');
 head.textContent='2014 GLOBAL ENCOUNTER ARCHIVE · READ ONLY';
 head.style.cssText='cursor:pointer;font:700 13px Georgia,serif';
 const notice=document.createElement('p');notice.id='bf120-historical-note';
 notice.textContent='2014 historical parser only: NOT confirmed as 2022 native enemy spawns, AI, sprite identities or drops. Demo combat unchanged.';
 const waves=document.createElement('div');waves.id='bf120-historical-waves';
 box.append(head,notice,waves);host.after(box);
 function lookup(id){return archive.get(Number(id))||null;}
 function refresh(){
   const entry=typeof QUEST==='undefined'?null:lookup(QUEST?.missionId);
   box.hidden=!entry;waves.replaceChildren();if(!entry)return false;
   const intro=document.createElement('p');
   intro.textContent=entry.name+' · '+entry.waves.length+' historical 2014 wave groups';
   waves.append(intro);
   for(const w of entry.waves){
     const group=document.createElement('section');
     group.style.cssText='padding:6px 0;border-top:1px solid #526075';
     const title=document.createElement('strong');title.textContent='WAVE '+w.wave;
     group.append(title);
     for(const e of w.enemies){
       const item=document.createElement('div');
       item.textContent=e.name+' · unit '+e.unitId+' · HP '+e.hp+
         ' · ATK '+e.atk+' · DEF '+e.def+' · AI ref '+e.aiId;
       group.append(item);
     }
     waves.append(group);
   }
   const cite=document.createElement('small');
   cite.textContent='Archived file: '+entry.sourcePath+
     ' · Git blob '+entry.gitBlobSha.slice(0,12)+
     ' · 2022 correspondence unverified.';
   waves.append(cite);
   return true;
 }
 new MutationObserver(refresh).observe(list,{childList:true});
 document.querySelector('.bf-navbar')?.addEventListener('click',refresh);
 refresh();
 window.BFHistoricalEncountersV120=Object.freeze({
   lookup,refresh,
   get ids(){return [...archive.keys()];},
   get waves(){return data.missions.reduce((n,q)=>n+q.waves.length,0);},
   get enemySlots(){return data.missions.reduce((n,q)=>n+
       q.waves.reduce((s,w)=>s+w.enemies.length,0),0);}
 });
})();
