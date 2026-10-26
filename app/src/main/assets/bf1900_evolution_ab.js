/* BF_GLOBAL_EVOLUTION_AB_TRIALS_V1900 */
(() => {
 'use strict';
 if(window.BFGlobalEvolutionABV1900 || !window.BFGlobalMultistageDraftV1800 ||
   !window.BFGlobalBatchDraftEvolutionV1700 ||
   !window.BFArchiveDraftV800 || !window.BFTacticalRoundsV300 ||
   !window.BFGlobalUnitArchive || typeof P==='undefined'||P?.version!==7)return;
 const multi=window.BFGlobalMultistageDraftV1800;
 const draft=window.BFArchiveDraftV800;
 const battle=window.BFTacticalRoundsV300;
 const archive=window.BFGlobalUnitArchive;
 const anchor=document.getElementById('bf1800-multistage');
 if(!anchor||archive.count!==2291)return;
 const copy=x=>JSON.parse(JSON.stringify(x));
 const idle=()=>battle.snapshot===null&&!(typeof S!=='undefined'&&S?.busy);
 let latest=null;
 const sourceStats=id=>{
   const rec=archive.find(id);
   const raw=rec?.stats||{};
   return {formId:id,name:rec?.name||'#'+id,
     hp:raw.hp??null,atk:raw.atk??null,
     def:raw.def??null,rec:raw.rec??null};
 };
 function ready(){
   const plan=multi.preview;
   if(!idle()||!plan.ready||!plan.entries.length)return false;
   const start=draft.selected;
   const changes=new Map(plan.entries.map(r=>[r.from,r.to]));
   const evolved=start.map(x=>changes.get(x)||x);
   return evolved.length>0&&evolved.length<=6&&
     new Set(evolved).size===evolved.length&&
     battle.canStartDraft(start,draft.mission)&&
     battle.canStartDraft(evolved,draft.mission);
 }
 function simulate(ids,mission,rounds){
   if(!battle.startDraft(ids,mission))return null;
   try{
     const initial=battle.snapshot;
     if(!initial||initial.mode!=='archive-draft'||
       JSON.stringify(initial.draftUnitIds)!==JSON.stringify(ids))
       return null;
     const attempted=battle.autoAdvance(rounds);
     if(attempted===false)return null;
     const final=battle.snapshot;
     if(!final)return null;
     return {sourceFormIds:ids.slice(),sourceStats:ids.map(sourceStats),
       initialParty:initial.party.map(x=>({id:x.unitId,name:x.name,
         hp:x.hp,maxHp:x.maxHp})),
       results:{
         rounds:final.rounds,phase:final.phase,wave:final.wave,
         totalWaves:final.totalWaves,
         damageDealt:final.damageDealt,damageTaken:final.damageTaken,
         kills:final.kills,heals:final.heals,
         surviving:final.party.filter(u=>u.hp>0).length,
         remainingHP:final.party.reduce((a,u)=>a+u.hp,0)
       }};
   }finally{
     // The synthetic battle must never become an ongoing real quest or save.
     battle.exit();
   }
 }
 function run(rounds=5){
   if(!Number.isInteger(rounds)||rounds<1||rounds>5||!ready())return null;
   const plan=multi.preview;
   const beforeIds=draft.selected;
   const substitutions=new Map(plan.entries.map(x=>[x.from,x.to]));
   const afterIds=beforeIds.map(id=>substitutions.get(id)||id);
   const mission=draft.mission;
   const sourceBefore=copy(draft.selected),oldEvolutionDepth=
     window.BFGlobalDraftEvolutionV1600?.history.length??0;
   let before=null,after=null;
   try{
     before=simulate(beforeIds,mission,rounds);
     if(!before)return null;
     after=simulate(afterIds,mission,rounds);
     if(!after)return null;
   }finally{
     // Keep trials strictly volatile; never leave even an interrupted fight.
     if(battle.snapshot)battle.exit();
   }
   if(JSON.stringify(draft.selected)!==JSON.stringify(sourceBefore)||
     (window.BFGlobalDraftEvolutionV1600?.history.length??0)!==oldEvolutionDepth)
     throw new Error('Simulated matchup unexpectedly changed temporary evolution choices');
   const difference={
     damageDealt:after.results.damageDealt-before.results.damageDealt,
     damageTaken:after.results.damageTaken-before.results.damageTaken,
     kills:after.results.kills-before.results.kills,
     remainingHP:after.results.remainingHP-before.results.remainingHP
   };
   latest={originalYear:2022,historicalEnemyYear:2014,
     synthetic:true,missionId:mission,roundLimit:rounds,
     changedForms:plan.entries.map(x=>({from:x.from,to:x.to,
       sourceStages:x.steps,path:x.path.slice()})),
     before,after,difference};
   render();return copy(latest);
 }
 const style=document.createElement('style');style.id='bf1900-ab-style';
 style.textContent=[
   '#bf1900-ab{margin:8px 0;padding:11px;background:#203449;',
   'color:#f3e6d2;border:1px solid #bfaa81;border-radius:7px;',
   'font:12px/1.55 system-ui,sans-serif}',
   '#bf1900-ab>summary{font:bold 14px Georgia,serif;cursor:pointer;',
   'min-height:38px}',
   '#bf1900-ab button,#bf1900-ab select{width:100%;',
   'min-height:40px;box-sizing:border-box;margin:4px 0;',
   'padding:7px;border:1px solid #bca17b;border-radius:5px;',
   'background:#31516d;color:#fff}',
   '#bf1900-ab button:disabled{opacity:.45}',
   '.bf1900-result{background:#294259;padding:8px;margin:6px 0;',
   'border-radius:5px}',
   '.bf1900-result strong,.bf1900-result small{display:block}',
   '.bf1900-warning{color:#ffe1b3}'
 ].join('');
 document.head.append(style);
 const panel=document.createElement('details');panel.id='bf1900-ab';
 const summary=document.createElement('summary');
 summary.textContent='COMPARE EVOLUTION BATTLES · v19.00';
 const note=document.createElement('p');note.className='bf1900-warning';
 note.textContent='Run the SAME 2014 historical enemy mission for both 2022 source squads using identical bounded synthetic auto-battle rules. This is an experimental A/B simulation, NOT an original 2022 Global battle formula, original combat balance or guaranteed evolution power ranking. Does not actually evolve or save a squad.';
 const roundLabel=document.createElement('label');
 roundLabel.textContent='Simulated team-round limit (both squads)';
 const selector=document.createElement('select');selector.id='bf1900-rounds';
 for(const count of [1,3,5]){
   const opt=document.createElement('option');opt.value=String(count);
   opt.textContent='Up to '+count+' synthetic round(s)';
   selector.append(opt);
 }
 selector.value='5';roundLabel.append(selector);
 const button=document.createElement('button');button.id='bf1900-run';
 button.type='button';button.textContent='RUN SOURCE SQUAD A/B BATTLE';
 const status=document.createElement('p');status.id='bf1900-status';
 const results=document.createElement('div');results.id='bf1900-results';
 panel.append(summary,note,roundLabel,button,status,results);
 anchor.after(panel);
 const el=(tag,text)=>{const e=document.createElement(tag);e.textContent=text;return e;};
 function render(){
   const can=ready();
   button.disabled=!can;
   status.textContent=can?
     'Ready: preview compares original draft with fully documented planned 2022 evolution destinations for mission '+draft.mission+'.':
     'Select at least one fully documented multi-stage evolution route and exit any active training battle before comparing.';
   results.replaceChildren();
   if(!latest)return can;
   const title=el('div','Last comparison: 2014 historical mission '+latest.missionId+
     ' · up to '+latest.roundLimit+' simulated team rounds per squad');
   title.className='bf1900-result';results.append(title);
   for(const [caption,record] of [['BASE 2022 DRAFT',latest.before],
     ['EVOLVED 2022 DRAFT',latest.after]]){
     const card=document.createElement('div');card.className='bf1900-result';
     card.append(el('strong',caption),
       el('small',record.sourceStats.map(x=>x.name+' (#'+x.formId+')').join(' · ')),
       el('small','Rounds '+record.results.rounds+' · Wave '+
         record.results.wave+'/'+record.results.totalWaves+' · '+
         record.results.phase),
       el('small','Synthetic damage dealt '+record.results.damageDealt+
         ' · taken '+record.results.damageTaken+
         ' · defeated foes '+record.results.kills),
       el('small','Surviving '+record.results.surviving+
         ' · remaining HP '+record.results.remainingHP));
     results.append(card);
   }
   const delta=document.createElement('div');delta.className='bf1900-result';
   delta.append(el('strong','EXPERIMENTAL DIFFERENCES (EVOLVED MINUS BASE)'),
     el('small','Simulated damage dealt '+latest.difference.damageDealt+
       ' · taken '+latest.difference.damageTaken+
       ' · defeated foes '+latest.difference.kills+
       ' · remaining HP '+latest.difference.remainingHP));
   results.append(delta);
   return can;
 }
 button.addEventListener('click',()=>run(Number(selector.value)));
 panel.addEventListener('toggle',()=>{if(panel.open)render();});
 document.querySelector('.bf-navbar')?.addEventListener('click',()=>{
   if(panel.open)render();
 });
 render();
 window.BFGlobalEvolutionABV1900=Object.freeze({
   get result(){return latest?copy(latest):null;},
   get ready(){return ready();},
   run,refresh:render
 });
})();
