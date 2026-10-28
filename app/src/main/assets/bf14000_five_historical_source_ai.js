/* BF_GLOBAL_2014_FIVE_MISSION_SOURCE_AI_V14000 */
(() => {
 'use strict';
 if(window.BFHistoricalFiveMissionSourceAIV14000 ||
    !window.BFArchiveTrialsV200 || !window.BFHistoricalBasicsAIReferenceV8700)return;
 const archive=window.BFArchiveTrialsV200;
 // Source-verified 2014 cheahjs mission JSON, NOT an authenticated
 // original 2022 Global enemy AI or target/damage implementation.
 const M={"schema":"bf-global-historical-2014-five-mission-attack-ai-source-v140","archiveEra":2014,"confirmed2022":false,"enemyAction":{"type":"attack","actCount":1,"percent":100,"parameters":"-1","targetCondition":"random","targetType":2,"conditions":0},"totals":{"missions":5,"waves":21,"slots":41},"missions":[{"id":1,"name":"Basics of Battle","sourcePath":"missions_parsed/Basics of Battle_2014-03-10-20-43.json","gitBlobSha":"797a2945a40bcfffe7dfc500c8e3dfb6eb81b8fe","waves":[[[30030,"Mossy",300,290,50,1]],[[40030,"Sparky",300,320,0,1],[30030,"Mossy",300,290,50,1]],[[30031,"King Mossy",3000,320,30,1]]]},{"id":2,"name":"Element & Skill","sourcePath":"missions_parsed/Element & Skill_2014-03-10-20-47.json","gitBlobSha":"4b85fcbea4ee41c722b4d54a4140c5d84cd819b0","waves":[[[20030,"Squirty",300,280,10,1],[40030,"Sparky",300,320,0,1],[30030,"Mossy",300,290,50,1]],[[10030,"Burny",300,300,20,1],[30030,"Mossy",300,290,50,1],[40030,"Sparky",300,320,0,1]],[[60050,"Skeleton",4000,340,20,1]]]},{"id":10,"name":"Start of Adventure","sourcePath":"missions_parsed/Start of Adventure_2014-14-10-08-07.json","gitBlobSha":"556829bc0639e417ecd4dbc99ef28c44da25c621","waves":[[[30030,"Mossy",830,340,90,1],[40030,"Sparky",760,370,0,1]],[[20030,"Squirty",780,330,20,1],[60030,"Gloomy",760,370,0,1],[40030,"Sparky",760,370,0,1]],[[10030,"Burny",800,320,50,1],[20030,"Squirty",780,330,20,1]],[[20030,"Squirty",780,330,20,1],[60030,"Gloomy",760,370,0,1],[40030,"Sparky",760,370,0,1]],[[40031,"King Sparky",2500,470,30,1]]]},{"id":11,"name":"Monsters of the Prairie","sourcePath":"missions_parsed/Monsters of the Prairie_2014-14-10-08-08.json","gitBlobSha":"cd089b9640c049b033ef16a6c52e5f3c1d9a3f36","waves":[[[20030,"Squirty",780,330,20,1],[10050,"Goblin",1000,370,90,1]],[[50030,"Glowy",850,340,60,1],[10050,"Goblin",1000,370,90,1]],[[20050,"Merman",950,360,90,1],[10030,"Burny",800,320,50,1]],[[50030,"Glowy",850,340,60,1],[10050,"Goblin",1000,370,90,1]],[[50031,"King Glowy",3300,450,80,1]]]},{"id":40,"name":"Shadowy Forests","sourcePath":"missions_parsed/Shadowy Forests_2014-14-10-08-25.json","gitBlobSha":"24da1148c7e8fd2293e504d0fd1b8f0594a6df51","waves":[[[30030,"Mossy",1600,440,130,1],[30050,"Mandragora",1650,460,180,1]],[[30050,"Mandragora",1650,460,180,1],[30050,"Mandragora",1650,460,180,1]],[[30030,"Mossy",1600,440,130,1],[30050,"Mandragora",1650,460,180,1]],[[30050,"Mandragora",1650,460,180,1],[30050,"Mandragora",1650,460,180,1]],[[30031,"King Mossy",7500,500,150,1],[30031,"King Mossy",7500,500,150,1]]]}]};
 if(M.schema!=='bf-global-historical-2014-five-mission-attack-ai-source-v140'||
    M.archiveEra!==2014||M.confirmed2022!==false||
    M.totals.missions!==5||M.totals.waves!==21||M.totals.slots!==41||
    M.enemyAction.type!=='attack'||M.enemyAction.actCount!==1||
    M.enemyAction.percent!==100||M.enemyAction.targetCondition!=='random'||
    M.enemyAction.parameters!=='-1'||M.enemyAction.targetType!==2||
    M.enemyAction.conditions!==0)return;
 const rows=new Map();
 let waves=0,slots=0;
 for(const record of M.missions){
    const original=archive.sourceFor(record.id);
    if(!original||original.sourcePath!==record.sourcePath||
       original.gitBlobSha!==record.gitBlobSha||
       original.name!==record.name||
       record.waves.length!==original.waves.length||
       rows.has(record.id))return;
    for(let wi=0;wi<record.waves.length;wi++){
      const roster=record.waves[wi];
      const prev=original.waves[wi].enemies;
      if(!Array.isArray(roster)||roster.length!==prev.length)return;
      for(let i=0;i<roster.length;i++){
        const tuple=roster[i],enemy=prev[i];
        if(tuple.length!==6||enemy.unitId!==tuple[0]||
           enemy.name!==tuple[1]||enemy.hp!==tuple[2]||
           enemy.atk!==tuple[3]||enemy.def!==tuple[4]||
           enemy.aiId!==tuple[5]||enemy.aiId!==1)return;
        slots++;
      }
      waves++;
    }
    rows.set(record.id,record);
 }
 if(rows.size!==5||waves!==21||slots!==41)return;
 function plan(missionId,wave,foes){
    if(!Number.isSafeInteger(missionId)||!Number.isSafeInteger(wave)||
       !Array.isArray(foes))return null;
    const mission=rows.get(missionId),list=mission?.waves?.[wave-1];
    if(!list||foes.length!==list.length)return null;
    const attacks=[];
    for(let slot=0;slot<list.length;slot++){
       const [id,name,hp,atk,def,ai]=list[slot],foe=foes[slot];
       if(!foe||foe.unitId!==id||foe.name!==name||
          foe.maxHp!==hp||foe.atk!==atk||foe.def!==def||
          foe.aiId!==ai||!Number.isFinite(foe.hp)||
          foe.hp<0||foe.hp>hp)return null;
       if(foe.hp>0)attacks.push(Object.freeze({
         wave,slot,unitId:id,name,action:'attack',sourceWeight:100,
         nativeRandomTargetImplemented:false,
         syntheticHarm:Math.max(12,Math.ceil(atk/12))
       }));
    }
    return Object.freeze(attacks);
 }
 window.BFHistoricalFiveMissionSourceAIV14000=Object.freeze({
    source:Object.freeze({
      era:2014,confirmed2022:false,missions:5,waves:21,slots:41,
      file:'source_data/bf_global_historical_five_mission_ai_v140.json'
    }),
    lookup:id=>rows.get(id)||null,plan
 });
})();
