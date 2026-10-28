/* BF_GLOBAL_HISTORICAL_2014_COMPLETE_SOURCE_AI_V14400 */
(() => {
 'use strict';
 if(window.BFHistoricalRemainingMissionSourceAIV14400||
    !window.BFArchiveTrialsV200)return;
 // 2014 original parsed Global enemy actions, NOT 2022 Global native AI.
 // Only simple 1x normal attacks are executed as original source choices;
 // conditional, turn_end, skill or variable-count actions stay DEMO.
 const original=[{"id":41,"name":"Puppeteer of the Trees","sourcePath":"missions_parsed/Puppeteer of the Trees_2014-14-10-08-26.json","gitBlobSha":"d89860fe5a45a7d3cce3a6a9c0d60e6c643b99d8","waves":[[[30050,"Mandragora",1650,460,180,1,1],[30050,"Mandragora",1650,460,180,1,1]],[[30030,"Mossy",1600,440,130,1,1],[30030,"Mossy",1600,440,130,1,1],[30030,"Mossy",1600,440,130,1,1]],[[30030,"Mossy",1600,440,130,1,1],[30050,"Mandragora",1650,460,180,1,1]],[[30030,"Mossy",1600,440,130,1,1],[30050,"Mandragora",2000,520,250,1,1],[30030,"Mossy",1600,440,130,1,1]],[[30050,"Mandragora",2000,520,250,1,1],[30041,"Time Mage Claris",11000,610,200,5000,0],[30050,"Mandragora",2000,520,250,1,1]]]},{"id":42,"name":"Bandit of the Forest","sourcePath":"missions_parsed/Bandit of the Forest_2014-14-10-08-27.json","gitBlobSha":"0924501d0ee0592c52038aa3b22cd7950e5ffc7d","waves":[[[30030,"Mossy",1600,440,130,1,1],[30050,"Mandragora",1650,460,180,1,1]],[[30050,"Mandragora",1650,460,180,1,1],[30050,"Mandragora",1650,460,180,1,1],[30050,"Mandragora",1650,460,180,1,1],[30050,"Mandragora",1650,460,180,1,1]],[[30030,"Mossy",1600,440,130,1,1],[30050,"Mandragora",1650,460,180,1,1]],[[30030,"Mossy",1600,440,130,1,1],[30050,"Mandragora",2000,520,250,1,1],[30030,"Mossy",1600,440,130,1,1]],[[30050,"Mandragora",2000,520,250,1,1],[30050,"Mandragora",2000,520,250,1,1],[30062,"Head Bandit Zaza",12000,660,20,5004,0]]]},{"id":50,"name":"Thunder Blasting Wetlands","sourcePath":"missions_parsed/Thunder Blasting Wetlands_2014-24-9-18-02.json","gitBlobSha":"96342e58a56be659740a1e7c0968680a3e4c9522","waves":[[[40050,"Harpy",1600,460,60,1,1],[40050,"Harpy",1600,460,60,1,1]],[[40050,"Harpy",1900,510,60,1,1],[40061,"Sky Pirate Grafl",3500,570,130,20,0]],[[40030,"Sparky",1500,470,50,1,1],[40050,"Harpy",1600,460,60,1,1]],[[40050,"Harpy",1600,460,60,1,1],[40050,"Harpy",1600,460,60,1,1],[40050,"Harpy",1600,460,60,1,1],[40050,"Harpy",1600,460,60,1,1]],[[40031,"King Sparky",9000,520,30,1,1],[40031,"King Sparky",9000,520,30,1,1]]]},{"id":51,"name":"Commander of the Thunder","sourcePath":"missions_parsed/Commander of the Thunder_2014-14-10-08-28.json","gitBlobSha":"77eb5b825a4549b6a670b678216aac11d6be42c8","waves":[[[40050,"Harpy",1900,510,60,1,1],[40130,"Thunder Nymph",4800,520,100,1,0],[40050,"Harpy",1900,510,60,1,1]],[[40050,"Harpy",1600,460,60,1,1],[40050,"Harpy",1600,460,60,1,1],[40050,"Harpy",1600,460,60,1,1],[40050,"Harpy",1600,460,60,1,1]],[[40030,"Sparky",1500,470,50,1,1],[40050,"Harpy",1600,460,60,1,1]],[[40050,"Harpy",1600,460,60,1,1],[40050,"Harpy",1600,460,60,1,1],[40050,"Harpy",1600,460,60,1,1],[40050,"Harpy",1600,460,60,1,1]],[[40050,"Harpy",1900,510,60,1,1],[40041,"High Dancer May",13000,620,100,5000,0],[40050,"Harpy",1900,510,60,1,1]]]},{"id":52,"name":"Pirate of the Wetlands","sourcePath":"missions_parsed/Pirate of the Wetlands_2014-14-10-08-29.json","gitBlobSha":"ffcb59327583e8dd504d5767a072bb3b5b30c297","waves":[[[40130,"Thunder Nymph",4800,520,100,1,0]],[[40050,"Harpy",1600,460,60,1,1],[40050,"Harpy",1600,460,60,1,1],[40050,"Harpy",1600,460,60,1,1],[40050,"Harpy",1600,460,60,1,1]],[[40050,"Harpy",1600,460,60,1,1],[40050,"Harpy",1600,460,60,1,1]],[[40030,"Sparky",1500,470,50,1,1],[40050,"Harpy",1900,510,60,1,1],[40030,"Sparky",1500,470,50,1,1]],[[40050,"Harpy",1900,510,60,1,1],[40050,"Harpy",1900,510,60,1,1],[40062,"Sky Boss Grafl",13500,650,130,5004,0]]]},{"id":60,"name":"Sacred Ruins","sourcePath":"missions_parsed/Sacred Ruins_2014-14-10-08-30.json","gitBlobSha":"3c0b2a0d2b10fe890370c2aa3105949ab9ea8511","waves":[[[50030,"Glowy",2000,500,180,1,1],[50050,"Angel",2200,510,120,1,1]],[[50030,"Glowy",2000,500,180,1,1],[50050,"Angel",2200,510,120,1,1]],[[50030,"Glowy",2000,500,180,1,1],[50050,"Angel",2200,510,120,1,1]],[[50050,"Angel",2600,550,150,1,1],[50060,"Unicorn",3900,560,150,20,0],[50050,"Angel",2600,550,150,1,1]],[[50050,"Angel",2600,550,150,1,1],[50060,"Unicorn",3900,560,150,20,0],[50050,"Angel",2600,550,150,1,1]],[[50031,"King Glowy",12000,620,200,1,1],[50031,"King Glowy",12000,620,200,1,1]]]},{"id":61,"name":"Wielder of the Light","sourcePath":"missions_parsed/Wielder of the Light_2014-14-10-08-31.json","gitBlobSha":"460515a59b6f8cdb81cccfb2b0501f077570c1ce","waves":[[[50050,"Angel",2200,510,120,1,1],[50050,"Angel",2200,510,120,1,1]],[[50050,"Angel",2600,550,150,1,1],[50050,"Angel",2600,550,150,1,1]],[[50050,"Angel",2200,510,120,1,1],[50050,"Angel",2200,510,120,1,1]],[[50030,"Glowy",2000,500,180,1,1],[50050,"Angel",2600,550,150,1,1],[50030,"Glowy",2000,500,180,1,1]],[[50050,"Angel",2600,550,150,1,1],[50120,"Light Nymph",5000,540,100,1,0],[50050,"Angel",2600,550,150,1,1]],[[50050,"Angel",2600,550,150,1,1],[50041,"Light Lord Mimir",16000,700,200,5000,0],[50050,"Angel",2600,550,150,1,1]]]},{"id":70,"name":"The Heinous Chamber","sourcePath":"missions_parsed/The Heinous Chamber_2014-14-10-08-33.json","gitBlobSha":"fde7fc3378d9c0382b1a20c362cfc179eab81880","waves":[[[60030,"Gloomy",1950,520,20,1,1],[60050,"Skeleton",2100,530,50,1,1]],[[60030,"Gloomy",1950,520,20,1,1],[60050,"Skeleton",2100,530,50,1,1]],[[60030,"Gloomy",1950,520,20,1,1],[60050,"Skeleton",2100,530,50,1,1]],[[60050,"Skeleton",2100,530,50,1,1],[60050,"Skeleton",2100,530,50,1,1]],[[60050,"Skeleton",2500,570,50,1,1],[60061,"Medusa",4000,570,60,20,0],[60050,"Skeleton",2500,570,50,1,1]],[[60031,"King Gloomy",13000,620,100,1,1],[60031,"King Gloomy",13000,620,100,1,1]]]},{"id":71,"name":"Manipulator of the Dark","sourcePath":"missions_parsed/Manipulator of the Dark_2014-14-10-08-03.json","gitBlobSha":"6d0e0d2aa5ac98521cf04e36160b6e26d72e91d5","waves":[[[60050,"Skeleton",2500,570,50,1,1],[60050,"Skeleton",2500,570,50,1,1]],[[60030,"Gloomy",1950,520,20,1,1],[60030,"Gloomy",1950,520,20,1,1],[60030,"Gloomy",1950,520,20,1,1]],[[60050,"Skeleton",2100,530,50,1,1],[60050,"Skeleton",2100,530,50,1,1]],[[60030,"Gloomy",1950,520,20,1,1],[60030,"Gloomy",1950,520,20,1,1],[60030,"Gloomy",1950,520,20,1,1]],[[60030,"Gloomy",1950,520,20,1,1],[60050,"Skeleton",2500,570,50,1,1],[60030,"Gloomy",1950,520,20,1,1]],[[60050,"Skeleton",2500,570,50,1,1],[60041,"Magician Lily",16000,690,100,5000,0],[60050,"Skeleton",2500,570,50,1,1]]]},{"id":200,"name":"The Burning Desert","sourcePath":"missions_parsed/The Burning Desert_2014-06-10-08-17.json","gitBlobSha":"5b7abb59542983348d0b32e6028b8d02781598c9","waves":[[[10071,"Orthos",2800,640,130,1,1],[10071,"Orthos",2800,640,130,1,1]],[[10071,"Orthos",2800,640,130,1,1],[10071,"Orthos",2800,640,130,1,1]],[[10071,"Orthos",2800,640,130,1,1],[10071,"Orthos",2800,640,130,1,1]],[[10071,"Orthos",2800,640,130,1,1],[10040,"Witch Liza",3800,590,200,10,0]],[[10071,"Orthos",2800,640,130,1,1],[10040,"Witch Liza",3800,590,200,10,0]],[[10071,"Orthos",2800,640,130,1,1],[10040,"Witch Liza",3800,590,200,10,0]],[[10102,"Knight Agni",30000,770,350,5030,0]]]},{"id":202,"name":"The Precarious Beast Master","sourcePath":"missions_parsed/The Precarious Beast Master_2014-05-10-08-41.json","gitBlobSha":"1f859c9ddd1534a146a8f402cd97fd51d341a7c9","waves":[[[10061,"Thief Leon",4000,660,150,20,0],[10050,"Goblin",2400,580,90,1,1],[10050,"Goblin",2400,580,90,1,1],[10050,"Goblin",2400,580,90,1,1]],[[10061,"Thief Leon",4000,660,150,20,0],[10040,"Witch Liza",3800,590,200,10,0],[10071,"Orthos",2800,640,130,1,1]],[[10071,"Orthos",2800,640,130,1,1],[10071,"Orthos",2800,640,130,1,1],[10071,"Orthos",2800,640,130,1,1]],[[10061,"Thief Leon",4000,660,150,20,0],[10050,"Goblin",2400,580,90,1,1],[10050,"Goblin",2400,580,90,1,1],[10050,"Goblin",2400,580,90,1,1]],[[10061,"Thief Leon",4000,660,150,20,0],[10040,"Witch Liza",3800,590,200,10,0],[10071,"Orthos",2800,640,130,1,1]],[[10071,"Orthos",2800,640,130,1,1],[10040,"Witch Liza",3800,590,200,10,0],[10071,"Orthos",2800,640,130,1,1]],[[10050,"Goblin",2400,580,90,1,1],[10071,"Orthos",2800,640,130,1,1],[10050,"Goblin",2400,580,90,1,1]],[[10041,"Warlock Liza",14000,620,200,5000,0],[10022,"Rage Beast Zegar",23000,750,10,5001,0]]]},{"id":240,"name":"Land of the Light","sourcePath":"missions_parsed/Land of the Light_2014-08-10-09-49.json","gitBlobSha":"1cdf8e966110f18ed3c0fe6b86a7d49848a08673","waves":[[[10071,"Orthos",3600,700,130,1,1],[50040,"Sage Mimir",4500,620,240,10,0]],[[20071,"Ramia",3500,690,150,1,1],[20071,"Ramia",3500,690,150,1,1]],[[10071,"Orthos",3600,700,130,1,1],[50050,"Angel",3000,590,200,1,1]],[[10071,"Orthos",3600,700,130,1,1],[50040,"Sage Mimir",4500,620,240,10,0]],[[20071,"Ramia",3500,690,150,1,1],[20071,"Ramia",3500,690,150,1,1]],[[20071,"Ramia",3500,690,150,1,1],[20071,"Ramia",3500,690,150,1,1]],[[50092,"Cowboy Heidt",38000,840,350,5030,0]]]}];
 if(original.length!==12)return;
 const source=window.BFArchiveTrialsV200;
 const byId=new Map();let waves=0,slots=0,simple=0,complex=0;
 for(const mission of original){
   const historical=source.sourceFor(mission.id);
   if(!historical||historical.name!==mission.name||
      historical.sourcePath!==mission.sourcePath||
      historical.gitBlobSha!==mission.gitBlobSha||
      historical.waves.length!==mission.waves.length||
      byId.has(mission.id))return;
   for(let i=0;i<mission.waves.length;i++){
     const a=mission.waves[i],b=historical.waves[i].enemies;
     if(a.length!==b.length)return;
     for(let j=0;j<a.length;j++){
       const e=a[j],v=b[j];
       if(e.length!==7||v.unitId!==e[0]||v.name!==e[1]||
          v.hp!==e[2]||v.atk!==e[3]||
          v.def!==e[4]||v.aiId!==e[5]||
          (e[6]!==0&&e[6]!==1))return;
       e[6]?simple++:complex++;
       slots++;
     }
     waves++;
   }
   byId.set(mission.id,mission);
 }
 if(waves!==71||slots!==177||simple!==148||complex!==29||
    byId.size!==12)return;
 function plan(id,wave,enemies){
   if(!Number.isSafeInteger(id)||!Number.isSafeInteger(wave)||
      !Array.isArray(enemies))return null;
   const original=byId.get(id)?.waves?.[wave-1];
   if(!original||original.length!==enemies.length)return null;
   const actions=[];
   for(let slot=0;slot<original.length;slot++){
     const [unitId,name,hp,atk,def,aiId,safe]=original[slot];
     const enemy=enemies[slot];
     if(!enemy||enemy.unitId!==unitId||enemy.name!==name||
        enemy.maxHp!==hp||enemy.atk!==atk||
        enemy.def!==def||enemy.aiId!==aiId||
        !Number.isFinite(enemy.hp)||enemy.hp<0||
        enemy.hp>hp)return null;
     if(enemy.hp===0)continue;
     actions.push(Object.freeze({
       wave,slot,unitId,name,sourceBacked:safe===1,
       action:safe?'attack':'unmodeled-source-fallback',
       sourceWeight:safe?100:null,
       nativeRandomTargetImplemented:false,
       syntheticHarm:Math.max(12,Math.ceil(atk/12))
     }));
   }
   return Object.freeze(actions);
 }
 window.BFHistoricalRemainingMissionSourceAIV14400=Object.freeze({
   source:Object.freeze({
     era:2014,confirmed2022:false,missions:12,
     waves:71,slots:177,simple:148,complex:29}),
   lookup:id=>byId.get(id)||null,plan
 });
})();
