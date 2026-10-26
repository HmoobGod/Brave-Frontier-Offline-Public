/* BF_GLOBAL_HISTORICAL_BASICS_AI_REFERENCE_V8700 */
(() => {
  'use strict';
  if(window.BFHistoricalBasicsAIReferenceV8700) return;
  const archive=window.BFHistoricalEncountersV120;
  const trials=window.BFArchiveTrialsV200;
  if(!archive||!trials||typeof archive.lookup!=='function'||typeof trials.sourceFor!=='function')return;
  const old=archive.lookup(1), prior=trials.sourceFor(1);
  const path='missions_parsed/Basics of Battle_2014-03-10-20-43.json';
  const blob='797a2945a40bcfffe7dfc500c8e3dfb6eb81b8fe';
  if(!old||!prior||old.name!=='Basics of Battle'||prior.name!==old.name||
     old.sourcePath!==path||old.gitBlobSha!==blob||
     prior.sourcePath!==path||prior.gitBlobSha!==blob||old.waves.length!==3)return;
  // These exact values were independently checked against the 2014 archived JSON.
  // The 2022 Global mission link has NOT been demonstrated.
  const rows=[
    [1,0,'Mossy',30030,'earth',300,290,50,12,8,100,null],
    [2,0,'Sparky',40030,'thunder',300,320,0,12,8,100,null],
    [2,1,'Mossy',30030,'earth',300,290,50,12,8,null,[100,50,250,50,500]],
    [3,0,'King Mossy',30031,'earth',3000,320,30,120,75,null,null]
  ];
  const resists=Object.freeze({curse:0,injury:0,paralysis:0,poison:0,sick:0,weaken:0});
  const action=Object.freeze({type:'attack',parameters:'-1',percent:100,
                              targetCondition:'random',targetType:2,conditionCount:0});
  const indexed=new Map();
  for(const row of rows){
    const [wave,slot,name,unitId,element,hp,atk,def,zelMax,karmaMax,unitChance,chest]=row;
    const waveData=old.waves[wave-1], enemy=waveData&&waveData.enemies[slot];
    const other=prior.waves[wave-1]?.enemies[slot];
    if(!enemy||!other||enemy.name!==name||enemy.unitId!==unitId||
       enemy.hp!==hp||enemy.atk!==atk||enemy.def!==def||enemy.aiId!==1||
       other.unitId!==unitId||other.hp!==hp||other.atk!==atk||other.def!==def)return;
    indexed.set(wave+':'+slot,Object.freeze({
      wave,slot,name,unitId,element,hp,atk,def,aiId:1,
      actionsPerTurn:Object.freeze({min:1,max:1}),action,
      ailmentResistancePercent:resists,
      zel:Object.freeze({dropChecks:5,maxPerDrop:zelMax}),
      karma:Object.freeze({dropChecks:5,maxPerDrop:karmaMax}),
      unitDrop:unitChance===null?null:Object.freeze({level:1,percent:unitChance,type:'random'}),
      treasure:chest?Object.freeze({chestChancePercent:chest[0],
        karmaChancePercent:chest[1],karmaAmount:chest[2],
        zelChancePercent:chest[3],zelAmount:chest[4]}):null,
      itemDropEntries:0
    }));
  }
  if(indexed.size!==4)return;
  const host=document.getElementById('bf200-trials');
  const select=document.getElementById('bf200-mission');
  if(!host||!select)return;
  const panel=document.createElement('details');panel.id='bf8700-original-ai-evidence';
  panel.style.cssText='padding:9px;margin:8px 0;border:1px solid #9db0bf;border-radius:6px';
  const summary=document.createElement('summary');
  summary.textContent='2014 SOURCE AI / DROPS · BASICS OF BATTLE';
  summary.style.cssText='cursor:pointer;font-weight:700';
  const body=document.createElement('div');body.id='bf8700-source-rows';
  panel.append(summary,body);host.append(panel);
  function lookup(wave,slot){
    if(!Number.isInteger(wave)||!Number.isInteger(slot))return null;
    return indexed.get(wave+':'+slot)||null;
  }
  function refresh(){
    panel.hidden=select.value!=='1';
    if(panel.hidden)return false;
    body.replaceChildren();
    const note=document.createElement('p');
    note.textContent='Archived 2014 Global evidence only. NOT confirmed for 2022 Global. '+
      'Original native RNG, target picker and reward granting are unknown; this panel never executes AI or awards drops.';
    body.append(note);
    for(const [key,e] of indexed){
      const line=document.createElement('p');
      let text='Wave '+e.wave+' enemy '+(e.slot+1)+' '+e.name+' (#'+e.unitId+') · '+
        e.element+' · HP '+e.hp+' ATK '+e.atk+' DEF '+e.def+
        ' · 1 action/turn · attack 100%, random target (source type 2)'+
        ' · 2014 ailment-resistance fields all 0%'+
        ' · Zel 5 checks, max '+e.zel.maxPerDrop+
        ' · Karma 5 checks, max '+e.karma.maxPerDrop;
      if(e.unitDrop)text+=' · Unit drop '+e.unitDrop.percent+'% (Lv '+e.unitDrop.level+')';
      if(e.treasure)text+=' · Chest '+e.treasure.chestChancePercent+
        '%: Zel '+e.treasure.zelAmount+' at '+e.treasure.zelChancePercent+
        '% / Karma '+e.treasure.karmaAmount+' at '+e.treasure.karmaChancePercent+'%';
      line.textContent=text;line.dataset.sourceKey=key;body.append(line);
    }
    const cite=document.createElement('small');
    cite.textContent='Source: cheahjs/bravefrontier_data/'+path+' · Git blob '+blob+
      ' · 2022 formations/AI/rewards unverified.';
    body.append(cite);return true;
  }
  select.addEventListener('change',refresh);
  refresh();
  window.BFHistoricalBasicsAIReferenceV8700=Object.freeze({
    source:Object.freeze({archiveYear:2014,mission:'Basics of Battle',sourcePath:path,
      gitBlobSha:blob,confirmed2022:false,enemySlots:4}),
    lookup,refresh
  });
})();
