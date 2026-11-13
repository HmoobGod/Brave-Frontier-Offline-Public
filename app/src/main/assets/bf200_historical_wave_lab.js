/* BF_GLOBAL_ARCHIVE_TRIALS_V200 */
(() => {
 'use strict';
 if(window.BFArchiveTrialsV200 || typeof QUESTS==='undefined' ||
    QUESTS.length!==106 || !window.BFGlobalQuestText ||
    !window.BFGlobalQuestJournalV110 || !window.BFGlobalUnitArchive ||
    !window.BFGlobalSourceCrosscheckV150)return;
 const DATA=/* BF200_DATA_PLACEHOLDER */null;
 const M10_ALT=/* BF200_M10_ALT_PLACEHOLDER */null;
 const M10_AI=/* BF200_M10_AI_PLACEHOLDER */null;
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
 // v411: Alternate original 2014 capture is NOT a 2022 formation.
 // Require the exact original five-wave roster before allowing a wave-4 swap.
 const m10Base=archive.get(10);
 const m10AltValid=M10_ALT?.schema==='bf-global-mission10-dual-2014-capture-v411'&&
   M10_ALT.sourceEra===2014&&M10_ALT.historicalPracticeOnly===true&&
   M10_ALT.native2022FormationsVerified===false&&
   M10_ALT.originalGameRewardsEnabled===false&&
   M10_ALT.missionId===10&&m10Base?.name==='Start of Adventure'&&
   m10Base.gitBlobSha==='556829bc0639e417ecd4dbc99ef28c44da25c621'&&
   M10_ALT.primary.gitBlobSha===m10Base.gitBlobSha&&
   M10_ALT.alternate.gitBlobSha==='c6a9d86b7e72a079ebdaa48b84864d078e5568e3'&&
   M10_ALT.waves===5&&M10_ALT.enemySlots===11&&
   m10Base.waves.length===5&&m10Base.waves[3].wave===4&&
   JSON.stringify(m10Base.waves[3].enemies)===JSON.stringify(M10_ALT.wave4Original)&&
   JSON.stringify(M10_ALT.wave4Alternate.map(e=>e.unitId))==='[10030,50030,30030]'&&
   M10_ALT.wave4Alternate.every(e=>Number.isInteger(e.hp)&&e.hp>0&&
     Number.isInteger(e.atk)&&e.atk>=0&&Number.isInteger(e.def)&&e.def>=0&&e.aiId===1);
 const m10Alternate=m10AltValid?Object.freeze({...m10Base,
   sourcePath:M10_ALT.alternate.sourcePath,
   gitBlobSha:M10_ALT.alternate.gitBlobSha,
   captureVariant:'alternate',
   waves:m10Base.waves.map((w,i)=>i===3?Object.freeze({
      wave:4,enemies:M10_ALT.wave4Alternate.map(e=>Object.freeze({...e}))
   }):w)
 }):null;
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
  '#bf200-capture-variant{min-height:44px;margin:8px 0}',
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
 const capture=document.createElement('select');capture.id='bf200-capture-variant';
 capture.setAttribute('aria-label','Mission 10 original 2014 capture version');
 for(const [key,label] of [
   ['primary','2014 capture 08:07 · original practice'],
   ['alternate','2014 capture 08:34 · alternate wave 4']]){
   const option=document.createElement('option');option.value=key;
   option.textContent=label;capture.append(option);
 }
 const captureGuide=document.createElement('p');captureGuide.className='bf200-alert';
 captureGuide.textContent='Two observed 2014 versions; wave 4 differs. Neither is authenticated 2022. All damage and reward behavior is simulated.';
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
 panel.append(title,context,select,capture,captureGuide,origin,preview,begin,exit,status,arena,note);
 host.after(panel);
 let current=null;
 const selection=()=>{
    const row=archive.get(Number(select.value))||null;
    return row?.id===10&&m10Alternate&&capture.value==='alternate'?
      m10Alternate:row;
 };
 const unlocked=()=>!!selection()&&questUnlocked(selection().quest);
 function showReference(){
    const row=selection();if(!row)return false;
    capture.hidden=row.id!==10||!m10Alternate;
    capture.disabled=current?.state==='running';
    captureGuide.hidden=capture.hidden;
    origin.textContent='Archived 2014 source: '+row.sourcePath+' · Git blob '+row.gitBlobSha+
      (row===m10Alternate?' · alternate capture; wave 4 changes only':'');
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
    const row=current.captureVariant==='alternate'&&current.missionId===10?
      m10Alternate:archive.get(current.missionId);
    return Object.freeze({missionId:current.missionId,state:current.state,
      captureVariant:current.captureVariant,
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
    const row=Number(id)===10&&Number(select.value)===10?
      selection():archive.get(Number(id));
    if(!row||!questUnlocked(row.quest)||!!S?.busy)return false;
    select.value=String(row.id);
    current={missionId:row.id,captureVariant:row===m10Alternate?
       'alternate':'primary',state:'running',wave:0,hp:12000,
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
    // v413: Never apply the original 08:07 planner to the 08:34 wave 4.
    // Use a separate FULLY MATCHED original 2014 source-action record.
    // Only source attack CHOICE is recovered: damage and targeting remain
    // synthetic. No story encounter/AI, capture, items or rewards are touched.
    if(current?.captureVariant==='alternate'&&current?.wave===3){
      const witness=M10_AI, action=witness?.normalAttack;
      if(!m10Alternate||current.missionId!==10||!Array.isArray(foes)||
         witness?.schema!=='bf-global-2014-m10-alternate-normal-attack-evidence-v413'||
         witness.sourceEra!==2014||witness.original2022Confirmed!==false||
         witness.changesCanonicalBattle!==false||
         witness.changesRewardsOrSave!==false||
         witness.missionId!==10||witness.wave!==4||
         witness.source?.gitBlobSha!==m10Alternate.gitBlobSha||
         witness.source?.sourcePath!==m10Alternate.sourcePath||
         action?.type!=='attack'||action.parameters!=='-1'||
         action.percent!==100||action.targetCondition!=='random'||
         action.targetType!==2||action.conditions!==0||
         action.actionsPerTurn!=='1~1'||action.skills!==0||
         !Array.isArray(witness.enemies)||witness.enemies.length!==3||
         foes.length!==3)return null;
      const planned=[];
      for(let slot=0;slot<foes.length;slot++){
        const foe=foes[slot],source=witness.enemies[slot];
        if(source?.slot!==slot||!foe||foe.name!==source.name||
           foe.unitId!==source.unitId||foe.maxHp!==source.hp||
           foe.atk!==source.atk||foe.def!==source.def||
           foe.aiId!==source.aiId||!Number.isFinite(foe.hp)||
           foe.hp<0||foe.hp>source.hp)return null;
        if(foe.hp>0)planned.push(Object.freeze({
          wave:4,slot,unitId:source.unitId,name:source.name,
          action:'attack',sourceWeight:100,sourceBacked:true,
          nativeRandomTargetImplemented:false,
          syntheticHarm:Math.max(12,Math.ceil(source.atk/12))
        }));
      }
      return Object.freeze(planned);
    }
    // v144: remaining twelve archived 2014 Global missions.
    // Source-backed one-action normals only; complex source AI stays
    // explicitly labeled synthetic and never contaminates 2022 combat.
    const remaining=window.BFHistoricalRemainingMissionSourceAIV14400;
    if(remaining?.source?.era===2014&&
       remaining.source.confirmed2022===false&&
       remaining.source.slots===177&&
       typeof remaining.plan==='function'){
       const original=remaining.plan(current?.missionId,current?.wave+1,foes);
       if(original)return original;
    }
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
       const row=current.captureVariant==='alternate'&&current.missionId===10?
          m10Alternate:archive.get(current.missionId);
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
 capture.addEventListener('change',()=>{current=null;render();});
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
    get mission10AlternateAvailable(){return !!m10Alternate},
    get practice(){return state()},
    startPractice,perform,resetPractice,showReference
 });
})();
