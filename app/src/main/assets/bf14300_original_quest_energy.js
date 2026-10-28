/* BF_ORIGINAL_2022_QUEST_ENERGY_VISIBILITY_V14300 */
(() => {
 'use strict';
 // Exact original 2022 Global mission economy, not a stamina-system claim.
 if(window.BFOriginalGlobalQuestEnergyV14300||
    typeof P==='undefined'||P.version!==7||
    typeof QUESTS==='undefined'||!Array.isArray(QUESTS)||
    QUESTS.length!==106)return;
 const canonical='a1b36659dfc80bc6e1e0e244ba52b3c6d423b239cf684439a5488bf679764a66';
 const records=[[1,1,0,3,0,5,500,100],[2,1,1,3,0,8,1000,200],[10,10,2,5,3,20,300,0],[11,10,10,5,3,25,350,0],[12,10,11,6,5,29,400,0],[20,20,12,5,3,32,400,0],[21,20,20,5,3,35,450,0],[22,20,21,5,4,50,500,0],[23,20,22,6,5,80,600,0],[30,30,23,5,3,35,400,0],[31,30,30,5,3,40,450,0],[32,30,31,5,4,53,500,0],[33,30,32,6,5,83,600,0],[40,40,33,5,3,36,400,0],[41,40,40,5,3,42,450,0],[42,40,41,5,4,57,500,0],[43,40,42,6,5,84,600,0],[50,50,43,5,3,41,400,0],[51,50,50,5,3,47,450,0],[52,50,51,5,4,59,500,0],[53,50,52,6,5,87,600,0],[60,60,53,6,4,44,400,0],[61,60,60,6,4,51,450,0],[62,60,61,6,5,62,500,0],[63,60,62,7,7,89,600,0],[70,70,63,6,4,46,400,0],[71,70,70,6,4,53,450,0],[72,70,71,6,5,65,500,0],[73,70,72,7,7,91,600,0],[81,80,73,7,5,70,500,0],[82,80,81,7,5,90,550,0],[83,80,82,7,6,110,600,0],[84,80,83,7,6,130,650,0],[85,80,84,8,8,180,800,0],[200,200,85,7,5,180,500,0],[201,200,200,7,5,230,550,0],[202,200,201,8,7,280,600,0],[203,200,202,8,7,300,650,0],[204,200,203,9,9,600,700,0],[210,210,204,7,5,220,500,0],[211,210,210,7,5,260,550,0],[212,210,211,8,7,310,600,0],[213,210,212,8,7,380,650,0],[214,210,213,9,9,650,700,0],[220,220,214,7,5,240,500,0],[221,220,220,7,5,280,550,0],[222,220,221,8,7,330,600,0],[223,220,222,8,7,410,650,0],[224,220,223,9,9,700,700,0],[230,230,224,7,5,280,500,0],[231,230,230,7,5,350,550,0],[232,230,231,8,7,390,600,0],[233,230,232,8,7,450,650,0],[234,230,233,9,9,760,700,0],[240,240,234,7,6,350,500,0],[241,240,240,7,6,460,550,0],[242,240,241,8,8,540,600,0],[243,240,242,8,8,560,650,0],[244,240,243,9,10,800,700,0],[250,250,244,7,6,380,500,0],[251,250,250,7,6,490,550,0],[252,250,251,8,8,580,600,0],[253,250,252,8,8,600,650,0],[254,250,253,9,10,860,700,0],[260,260,254,9,7,450,700,0],[261,260,260,9,7,520,800,0],[262,260,261,9,8,600,850,0],[263,260,262,9,8,700,900,0],[264,260,263,9,9,800,950,0],[265,260,264,10,10,1000,1000,0],[300,300,265,8,8,800,500,0],[301,300,300,8,8,930,600,0],[302,300,301,9,9,1300,700,0],[303,300,302,9,9,1500,800,0],[304,300,303,11,12,2000,900,0],[310,310,304,8,8,930,500,0],[311,310,310,8,8,1260,600,0],[312,310,311,9,9,1440,700,0],[313,310,312,9,9,1860,800,0],[314,310,313,11,12,2230,900,0],[320,320,314,8,8,1050,500,0],[321,320,320,8,8,1360,600,0],[322,320,321,9,8,1750,700,0],[323,320,322,9,8,1930,800,0],[324,320,323,11,10,2220,900,0],[330,330,324,8,8,1080,500,0],[331,330,330,8,8,1388,600,0],[332,330,331,9,8,1780,700,0],[333,330,332,9,8,2010,800,0],[334,330,333,11,10,2350,900,0],[340,340,334,8,9,1250,500,0],[341,340,340,8,9,1430,600,0],[342,340,341,9,9,1820,700,0],[343,340,342,9,9,2050,800,0],[344,340,343,11,12,2400,900,0],[350,350,344,8,9,1280,500,0],[351,350,350,8,9,1460,600,0],[352,350,351,9,9,1850,700,0],[353,350,352,9,9,2100,800,0],[354,350,353,11,12,2440,900,0],[360,360,354,10,9,1600,600,0],[361,360,360,10,9,2000,700,0],[362,360,361,11,9,2300,800,0],[363,360,362,11,10,2500,900,0],[364,360,363,11,10,2600,1000,0],[365,360,364,12,14,3000,1500,0]];
 if(records.length!==106)return;
 const indexed=new Map();
 for(const r of records){
   if(!Array.isArray(r)||r.length!==8||r.some(v=>!Number.isSafeInteger(v)||v<0)||
      indexed.has(r[0]))return;
   indexed.set(r[0],r);
 }
 const known=new Map();
 for(const q of QUESTS){
   const r=indexed.get(q.missionId);
   if(!r||known.has(q.missionId)||
      r[1]!==q.dungeonId||r[2]!==q.requires||
      r[3]!==q.battles||r[4]!==q.energy||
      r[5]!==q.exp||r[6]!==q.zel||r[7]!==q.karma)return;
   known.set(q.missionId,r);
 }
 if(indexed.size!==106||known.size!==106)return;
 const questList=document.getElementById('questlist');
 if(!questList)return;
 const style=document.createElement('style');
 style.id='bf143-original-quest-cost-style';
 style.textContent='.bf143-original-cost{color:#b9dbb7;display:block;'+
   'font-size:11px;line-height:1.4;padding-top:3px}';
 document.head.append(style);
 function decorate(){
   let shown=0;
   for(const button of questList.querySelectorAll('button.questcard')){
     const title=button.querySelector('strong')?.textContent||'';
     const match=title.match(/Mission (\d+)/);
     const r=match?known.get(Number(match[1])):null;
     if(!r)continue;
     let label=button.querySelector('.bf143-original-cost');
     if(!label){
       label=document.createElement('small');
       label.className='bf143-original-cost';
       button.append(label);
     }
     label.textContent='2022 original · Energy '+r[4]+' · Karma '+r[7]+
       ' (reference; stamina not enforced)';
     shown++;
   }
   return shown;
 }
 const watcher=new MutationObserver(()=>decorate());
 // The native demo reconstructs all quest buttons on renderQuestList().
 // Observe only direct quest-list children, avoiding an observer loop.
 watcher.observe(questList,{childList:true});
 decorate();
 window.BFOriginalGlobalQuestEnergyV14300=Object.freeze({
   source:Object.freeze({year:2022,recordCount:106,
      sourceSha256:canonical,staminaEnforced:false,saveMutation:false}),
   lookup:id=>indexed.has(id)?Object.freeze([...indexed.get(id)]):null,
   refresh:decorate
 });
})();
