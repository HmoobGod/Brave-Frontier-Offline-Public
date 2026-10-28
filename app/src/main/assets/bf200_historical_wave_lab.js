/* BF_GLOBAL_ARCHIVE_TRIALS_V200 */
(() => {
 'use strict';
 if(window.BFArchiveTrialsV200 || typeof QUESTS==='undefined' ||
    QUESTS.length!==106 || !window.BFGlobalQuestText ||
    !window.BFGlobalQuestJournalV110 || !window.BFGlobalUnitArchive ||
    !window.BFGlobalSourceCrosscheckV150)return;
 const DATA=/* BF200_DATA_PLACEHOLDER */null;
 if(DATA.schema!=='bf-global-2014-historical-wave-lab-v200' ||
    DATA.totals.missions!==21 || DATA.totals.waves!==112 ||
    DATA.totals.entries!==264 || DATA.totals.units!==42 ||
    BFGlobalUnitArchive.count!==2291)return;
 const archive=new Map();
 for(const entry of DATA.missions){
    const quest=QUESTS.find(q=>q.missionId===entry.id);
    const source=quest&&BFGlobalQuestText.sourceFor(quest);
    if(!source||source.mission.name!==entry.name||archive.has(entry.id)||
       entry.waves.some((w,i)=>w.wave!==i+1||!w.enemies.length||
         w.enemies.some(e=>!e.name||[e.unitId,e.hp,e.atk,e.def,e.aiId]
           .some(v=>!Number.isInteger(v)||v<0))))return;
    archive.set(entry.id,Object.freeze({...entry,quest}));
 }
 if(archive.size!==21)return;
 const host=document.getElementById('bf150-integrity');
 const list=document.getElementById('questlist');
 if(!host||!list)return;
 const style=document.createElement('style');
 style.id='bf200-trials-style';
 style.textContent=[
  '#bf200-trials{margin:10px 2px;padding:11px;border:1px solid #b69565;',
  'border-radius:8px;background:#1b2d42;color:#f3e7cd;',
  'font:12px/1.5 system-ui,sans-serif}',
  '#bf200-trials summary{cursor:pointer;font:bold 15px Georgia,serif;min-height:32px}',
  '#bf200-trials select{box-sizing:border-box;width:100%;min-height:42px;',
  'padding:7px;background:#132134;color:#fff;border:1px solid #c1a271;border-radius:5px}',
  '#bf200-trials button{min-height:40px;margin:4px 4px 4px 0;padding:8px 10px;',
  'border:1px solid #bfa374;border-radius:5px;background:#3b526e;color:#fff;font-weight:700}',
  '#bf200-trials button:disabled{opacity:.5}',
  '#bf200-status{font-weight:700}',
  '.bf200-wave{padding:6px 0;border-top:1px solid #5c6c7a}',
  '.bf200-foe{display:flex;align-items:center;gap:7px;margin:5px 0;',
  'padding:5px;border-radius:4px;background:#293c53}',
  '.bf200-foe img{width:40px;height:40px;object-fit:contain;flex:0 0 40px}',
  '.bf200-foe strong,.bf200-foe small{display:block}',
  '.bf200-foe small{color:#d0d6df}',
  '.bf200-alert{color:#f3cfa7}',
  '#bf200-log{max-height:120px;overflow:auto;border-top:1px solid #75859a;margin-top:6px}'
 ].join('');
 document.head.append(style);
 const panel=document.createElement('details');panel.id='bf200-trials';
 const title=document.createElement('summary');
 title.textContent='GLOBAL ARCHIVE TRIALS · 21 HISTORICAL MISSIONS';
 const context=document.createElement('p');context.className='bf200-alert';
 context.textContent='Optional 2014 historical encounter research and experimental practice. NOT native 2022 Brave Frontier combat. No quest clears, drops, summons, EXP, Zel or save changes.';
 const select=document.createElement('select');select.id='bf200-mission';
 for(const row of DATA.missions){
    const option=document.createElement('option');option.value=String(row.id);
    option.textContent='Mission '+row.id+' · '+row.name;select.append(option);
 }
 const origin=document.createElement('small');origin.id='bf200-source';
 const preview=document.createElement('div');preview.id='bf200-reference';
 const begin=document.createElement('button');begin.id='bf200-start';
 begin.type='button';begin.textContent='START SEPARATE PRACTICE';
 const exit=document.createElement('button');exit.id='bf200-reset';
 exit.type='button';exit.textContent='EXIT PRACTICE';
 const status=document.createElement('p');status.id='bf200-status';
 status.setAttribute('aria-live','polite');
 const arena=document.createElement('div');arena.id='bf200-battle';
 const target=document.createElement('select');target.id='bf200-target';
 target.setAttribute('aria-label','Select simulated target');
 const actions=document.createElement('div');actions.id='bf200-actions';
 const controls={};
 for(const [id,label] of [['attack','ATTACK'],['burst','TRAINING BURST'],
                          ['guard','GUARD'],['heal','HEAL KIT']]){
    const button=document.createElement('button');button.type='button';
    button.dataset.bf200Action=id;button.textContent=label;
    button.addEventListener('click',()=>perform(id));
    actions.append(button);controls[id]=button;
 }
 const log=document.createElement('div');log.id='bf200-log';
 log.setAttribute('aria-live','polite');
 const note=document.createElement('p');note.className='bf200-alert';
 note.textContent='All practice damage, turn rules, HP, Burst and healing are synthetic. Only historical 2014 enemy names/stats/waves derive from the archive. Never changes the main game or save.';
 arena.append(target,actions,log);
 panel.append(title,context,select,origin,preview,begin,exit,status,arena,note);
 host.after(panel);
 let current=null;
 const selection=()=>archive.get(Number(select.value))||null;
 const unlocked=()=>!!selection()&&questUnlocked(selection().quest);
 function showReference(){
    const row=selection();if(!row)return false;
    origin.textContent='Archived 2014 source: '+row.sourcePath+' · Git blob '+row.gitBlobSha;
    preview.replaceChildren();
    const caption=document.createElement('p');
    caption.textContent=row.waves.length+' archived 2014 waves · '+
       row.waves.reduce((n,w)=>n+w.enemies.length,0)+' enemy slots · '+
       (unlocked()?'Practice unlocked':'Original quest locked');
    preview.append(caption);
    for(const wave of row.waves){
      const section=document.createElement('section');section.className='bf200-wave';
      const heading=document.createElement('strong');
      heading.textContent='Historical wave '+wave.wave;section.append(heading);
      for(const enemy of wave.enemies){
        const entry=document.createElement('div');entry.className='bf200-foe';
        const unit=BFGlobalUnitArchive.find(enemy.unitId);
        if(unit?.thumbnail){
           const portrait=document.createElement('img');portrait.loading='lazy';
           portrait.src='content/unit_archive/unit_ills_thum_'+enemy.unitId+'.png';
           portrait.alt='2022 unit archive thumbnail; not a verified 2014 battle sprite';
           entry.append(portrait);
        }
        const copy=document.createElement('div');
        const name=document.createElement('strong');
        name.textContent=enemy.name+' · #'+enemy.unitId;
        const info=document.createElement('small');
        info.textContent='2014 HP '+enemy.hp+' · ATK '+enemy.atk+' · DEF '+enemy.def+
          (unit?' · 2022 unit ID exists':' · 2022 unit ID unverified');
        copy.append(name,info);entry.append(copy);section.append(entry);
      }
      preview.append(section);
    }
    begin.disabled=!unlocked()||!!S?.busy||current?.state==='running';
    return true;
 }
 function state(){
    if(!current)return null;
    const row=archive.get(current.missionId);
    return Object.freeze({missionId:current.missionId,state:current.state,
      wave:current.wave+1,totalWaves:row.waves.length,hp:current.hp,
      burst:current.burst,kits:current.kits,turns:current.turns,
      enemies:current.enemies.map(e=>Object.freeze({
        name:e.name,unitId:e.unitId,hp:e.hp,maxHp:e.maxHp})),
      recent:current.log.slice(-8)});
 }
 function putWave(row,index){
    current.wave=index;
    current.enemies=row.waves[index].enemies.map(e=>({...e,maxHp:e.hp}));
    current.log.push('Started archived 2014 wave '+(index+1)+'/'+row.waves.length+'.');
 }
 function startPractice(id=Number(select.value)){
    const row=archive.get(Number(id));
    if(!row||!questUnlocked(row.quest)||!!S?.busy)return false;
    select.value=String(row.id);
    current={missionId:row.id,state:'running',wave:0,hp:12000,
       burst:0,kits:2,turns:0,enemies:[],log:[]};
    putWave(row,0);render();return true;
 }
 // The 2014 original Basics-of-Battle archive specifies precisely one
 // normal attack per living foe per turn, action weight 100%, random targeting.
 // Here only the ACTION DECISION is source-backed: practice has a single
 // simulated aggregate HP bar, and damage/target RNG remain explicitly DEMO.
 // Fail closed to the legacy synthetic volley if the archive reference or
 // a wave/slot/source-stat join ever diverges.
 function sourceEnemyPlan2014(foes){
    // v141: for four mixed 2014 archives, return authenticated normal
    // attacks where proven and visibly mark complex actions as synthetic.
    const mixed=window.BFHistoricalMixedMissionSourceAIV14100;
    if(mixed?.source?.era===2014&&
       mixed.source.confirmed2022===false&&
       mixed.source.slots===46&&typeof mixed.plan==='function'){
      const plan=mixed.plan(current?.missionId,current?.wave+1,foes);
      if(plan)return plan;
    }
    // v140: use original archived 2014 source action decisions from the
    // five fully authenticated all-normal-attack historical missions.
    // Every row is checked against the exact loaded v2.00 source roster.
    const expanded=window.BFHistoricalFiveMissionSourceAIV14000;
    if(expanded?.source?.era===2014&&
       expanded.source.confirmed2022===false&&
       expanded.source.slots===41&&
       typeof expanded.plan==='function'){
      const planned=expanded.plan(current?.missionId,current?.wave+1,foes);
      if(planned)return planned;
    }
    if(current?.missionId!==1||!Array.isArray(foes))return null;
    const ref=window.BFHistoricalBasicsAIReferenceV8700;
    const src=ref?.source;
    if(src?.gitBlobSha!=='797a2945a40bcfffe7dfc500c8e3dfb6eb81b8fe'||
       src.confirmed2022!==false||src.enemySlots!==4||
       typeof ref.lookup!=='function')return null;
    const plan=[];
    for(let slot=0;slot<foes.length;slot++){
      const foe=foes[slot], original=ref.lookup(current.wave+1,slot);
      if(!original||foe.unitId!==original.unitId||foe.name!==original.name||
         foe.maxHp!==original.hp||foe.atk!==original.atk||
         foe.def!==original.def||foe.aiId!==original.aiId||
         original.actionsPerTurn?.min!==1||original.actionsPerTurn?.max!==1||
         original.action?.type!=='attack'||original.action?.percent!==100||
         original.action?.parameters!=='-1'||
         original.action?.targetCondition!=='random'||
         original.action?.targetType!==2||
         original.action?.conditionCount!==0)return null;
      if(foe.hp>0)plan.push(Object.freeze({
        wave:current.wave+1,slot,unitId:foe.unitId,name:foe.name,
        action:'attack',sourceWeight:100,
        nativeRandomTargetImplemented:false,
        syntheticHarm:Math.max(12,Math.ceil(foe.atk/12))
      }));
    }
    return Object.freeze(plan);
 }
 function perform(action){
    if(!current||current.state!=='running'||
       !['attack','burst','guard','heal'].includes(action))return false;
    if(action==='burst'&&current.burst<2)return false;
    if(action==='heal'&&(!current.kits||current.hp===12000))return false;
    const foes=current.enemies;
    if(action==='attack'){
       const focused=foes[Number(target.value)];
       const enemy=focused?.hp>0?focused:foes.find(e=>e.hp>0);
       if(!enemy)return false;
       // Experimental training arithmetic; NOT original Global damage.
       const hit=Math.max(450,Math.floor(1350-enemy.def*.55));
       enemy.hp=Math.max(0,enemy.hp-hit);
       current.burst=Math.min(3,current.burst+1);
       current.log.push('Synthetic strike on '+enemy.name+': '+hit+'.');
    }else if(action==='burst'){
       for(const enemy of foes.filter(e=>e.hp>0))
          enemy.hp=Math.max(0,enemy.hp-Math.max(350,Math.floor(enemy.maxHp*.45)));
       current.burst=0;current.log.push('Synthetic training Burst hit all enemies.');
    }else if(action==='guard')current.log.push('Synthetic Guard reduced next volley.');
    else{current.kits--;current.hp=Math.min(12000,current.hp+3000);
       current.log.push('Synthetic Heal Kit restored up to 3,000 HP.');}
    current.turns++;
    if(foes.every(e=>e.hp===0)){
       const row=archive.get(current.missionId);
       if(current.wave+1>=row.waves.length){
          current.state='won';
          current.log.push('PRACTICE COMPLETE. No game progress or rewards granted.');
       }else putWave(row,current.wave+1);
    }else{
       const sourceAttacks=sourceEnemyPlan2014(foes);
       const volley=sourceAttacks?
           sourceAttacks.reduce((n,a)=>n+a.syntheticHarm,0):
           foes.filter(e=>e.hp>0).reduce((n,e)=>
             n+Math.max(12,Math.ceil(e.atk/12)),0);
       const harm=action==='guard'?Math.ceil(volley*.3):volley;
       current.hp=Math.max(0,current.hp-harm);
       if(sourceAttacks){
          const anyComplex=sourceAttacks.some(a=>a.sourceBacked===false);
          current.log.push((anyComplex?'2014 source AI PARTIAL: ':'2014 source AI: ')+
            sourceAttacks.map(a=>a.sourceBacked===false?
              a.name+' #'+a.unitId+' UNMODELED COMPLEX AI (synthetic reply)':
              a.name+' #'+a.unitId+' ATTACK 100% (1 action)').join(' · ')+
            ' · random target NOT simulated.');
       }
       current.log.push('Synthetic enemy reply: '+harm+' HP.');
       if(!current.hp){
          current.state='lost';current.log.push('Practice lost. No game penalty.');
       }
    }
    current.log=current.log.slice(-25);
    render();return true;
 }
 function render(){
    showReference();
    const t=state();arena.hidden=!t;exit.disabled=!t;
    if(!t){status.textContent='Practice inactive. Choose an unlocked mission.';return;}
    status.textContent='EXPERIMENTAL · '+t.state.toUpperCase()+
       ' · Wave '+t.wave+'/'+t.totalWaves+' · HP '+t.hp+'/12000'+
       ' · Burst '+t.burst+'/2 · Heal Kits '+t.kits;
    target.replaceChildren();
    t.enemies.forEach((enemy,i)=>{
       const option=document.createElement('option');option.value=String(i);
       option.textContent=enemy.name+' · '+enemy.hp+'/'+enemy.maxHp+' HP';
       option.disabled=enemy.hp===0;target.append(option);
    });
    const alive=t.enemies.findIndex(e=>e.hp>0);
    target.value=String(alive<0?0:alive);
    for(const [key,button] of Object.entries(controls))
       button.disabled=t.state!=='running'||
          (key==='burst'&&t.burst<2)||
          (key==='heal'&&(!t.kits||t.hp===12000));
    log.replaceChildren();
    for(const line of t.recent){
       const p=document.createElement('p');p.textContent=line;log.append(p);
    }
 }
 function resetPractice(){current=null;render();return true;}
 select.addEventListener('change',()=>{current=null;render();});
 begin.addEventListener('click',()=>startPractice());
 exit.addEventListener('click',resetPractice);
 new MutationObserver(()=>{if(!current)showReference();})
    .observe(list,{childList:true});
 render();
 window.BFArchiveTrialsV200=Object.freeze({
    get missions(){return DATA.totals.missions},
    get historicalWaves(){return DATA.totals.waves},
    get historicalEntries(){return DATA.totals.entries},
    get distinctUnitIds(){return DATA.totals.units},
    sourceFor:id=>archive.get(Number(id))||null,
    get practice(){return state()},
    startPractice,perform,resetPractice,showReference
 });
})();
