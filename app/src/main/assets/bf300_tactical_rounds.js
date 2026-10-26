/* BF_GLOBAL_TACTICAL_ROUNDS_V300 */
(() => {
 'use strict';
 if(window.BFTacticalRoundsV300 || typeof P==='undefined' || P?.version!==7 ||
   typeof QUESTS==='undefined' || QUESTS.length!==106 ||
   typeof questUnlocked!=='function' || !window.BFSquadTrainingV250 ||
   !window.BFArchiveTrialsV200 || !window.BFGlobalUnitArchive)return;
 const old=window.BFSquadTrainingV250, history=window.BFArchiveTrialsV200;
 const sourceBB=window.BFOriginalBBV500||null;
 const hitSources=window.BFOriginalHitSequenceV700||null;
 const ids=[1,2,10,11,20,21,30,31,40,41,42,50,51,52,60,61,70,71,200,202,240];
 if(old.sourceQuests!==21||history.missions!==21||
   history.historicalWaves!==112||history.historicalEntries!==264||
   BFGlobalUnitArchive.count!==2291)return;
 const parent=document.getElementById('bf250-squad');
 if(!parent||ids.some(id=>!history.sourceFor(id)?.waves?.length))return;
 const css=document.createElement('style');css.id='bf300-style';
 css.textContent=[
  '#bf300-tactics{padding:11px;margin:12px 2px;background:#162b40;',
  'border:1px solid #b99d69;border-radius:8px;color:#f2e5cc;',
  'font:12px/1.5 system-ui,sans-serif}',
  '#bf300-tactics summary{min-height:32px;cursor:pointer;font:bold 15px Georgia,serif}',
  '#bf300-tactics button,#bf300-tactics select{min-height:40px;',
  'color:#f9f5eb;border:1px solid #b4a078;border-radius:5px;',
  'background:#334e68;padding:7px;margin:3px 2px}',
  '#bf300-tactics button:disabled{opacity:.45}',
  '#bf300-mission{width:100%;background:#192b3c}',
  '#bf300-roster,#bf300-enemies{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:5px}',
  '.bf300-card{border:1px solid #506881;border-radius:5px;',
  'background:#283e54;padding:7px;overflow-wrap:anywhere}',
  '.bf300-card strong,.bf300-card small{display:block}',
  '.bf300-card small{color:#d0d8e3}',
  '.bf300-planner{border-top:1px solid #70849a;margin-top:5px;padding:7px 0}',
  '.bf300-planner strong{display:block}',
  '.bf300-planner label{display:block;font-size:11px}',
  '.bf300-planner select{width:100%;min-height:38px}',
  '.bf300-actions{display:flex;flex-wrap:wrap;gap:4px;margin:7px 0}',
  '#bf300-status{font-weight:bold}',
  '#bf300-report{max-height:170px;overflow:auto;border-top:1px solid #8793a4}',
  '#bf300-report p{margin:4px 0}',
  '.bf300-caution{color:#ffdbac}',
  '.bf350-unit{display:flex;align-items:center;gap:6px}',
  '.bf350-unit img{width:40px;height:40px;object-fit:contain;flex:0 0 40px}',
  '.bf350-meter{height:7px;border:1px solid #879bb0;background:#102234;',
  'border-radius:4px;overflow:hidden;margin:5px 0}',
  '.bf350-fill{height:100%;background:#a4c58b;max-width:100%}',
  '.bf350-fainted{opacity:.6}',
  '.bf700-hit{margin:7px 0;padding:7px;background:#213b53;border:1px solid #607894;border-radius:5px}',
  '.bf700-hits{display:flex;flex-wrap:wrap;gap:5px}',
  '.bf700-hit-cell{padding:5px;border:1px solid #a4906b;border-radius:3px;min-width:55px}',
  '#bf350-undo,#bf350-autorun{min-width:120px}'
 ].join('');
 document.head.append(css);
 const panel=document.createElement('details');panel.id='bf300-tactics';
 const heading=document.createElement('summary');
 heading.textContent='TACTICAL SIX-UNIT ROUNDS · v3.50';
 const disclosure=document.createElement('p');disclosure.className='bf300-caution';
 disclosure.textContent='OFFLINE EXPERIMENT. Plan one action per owned squad member, then resolve a coordinated team round against 2014 historical wave data. All damage, guard, healing, Burst and enemy actions are synthetic, NOT recovered 2022 battle rules.';
 const mission=document.createElement('select');mission.id='bf300-mission';
 for(const id of ids){
   const row=history.sourceFor(id),opt=document.createElement('option');
   opt.value=String(id);opt.textContent='Mission '+id+' · '+row.name;
   mission.append(opt);
 }
 const source=document.createElement('p');source.id='bf300-source';
 const start=document.createElement('button');start.type='button';start.id='bf300-start';
 start.textContent='START FULL-SQUAD TRIAL';
 const stop=document.createElement('button');stop.type='button';stop.id='bf300-stop';
 stop.textContent='EXIT / DISCARD TRIAL';
 const status=document.createElement('p');status.id='bf300-status';
 status.setAttribute('aria-live','polite');
 const arena=document.createElement('div');arena.id='bf300-arena';
 const roster=document.createElement('div');roster.id='bf300-roster';
 const enemies=document.createElement('div');enemies.id='bf300-enemies';
 const planner=document.createElement('div');planner.id='bf300-planner';
 const actions=document.createElement('div');actions.className='bf300-actions';
 const autoplan=document.createElement('button');autoplan.type='button';autoplan.id='bf300-autoplan';
 autoplan.textContent='AUTO-PLAN ALL';
 const resolve=document.createElement('button');resolve.type='button';resolve.id='bf300-resolve';
 resolve.textContent='EXECUTE FULL ROUND';
 const undo=document.createElement('button');undo.type='button';undo.id='bf350-undo';
 undo.textContent='UNDO LAST ROUND';
 const autorun=document.createElement('button');autorun.type='button';autorun.id='bf350-autorun';
 autorun.textContent='AUTO-PLAY UP TO 5 ROUNDS';
 const hitPanel=document.createElement('div');hitPanel.id='bf700-hit-report';
 hitPanel.setAttribute('aria-live','polite');
 const report=document.createElement('div');report.id='bf300-report';
 report.setAttribute('aria-live','polite');
 const footer=document.createElement('p');footer.className='bf300-caution';
 footer.textContent='Trial starts from temporary copies of your equipped squad. No Energy, drops, EXP, Zel, Karma, quest clears, actual unit HP, roster, summons or saved progress are changed.';
 actions.append(autoplan,resolve,undo,autorun);
 arena.append(roster,enemies,planner,actions,hitPanel,report);
 panel.append(heading,disclosure,mission,source,start,stop,status,arena,footer);
 parent.after(panel);
 let fight=null;
 // Bounded RAM-only snapshots: allows rewinding the last 20 synthetic rounds.
 // No persistent storage writes or changes to the original player's v7 save.
 let undoStack=[];
 function cloneFight(src){
   return {...src,party:src.party.map(u=>({...u})),
     foes:src.foes.map(e=>({...e})),
     plans:new Map([...src.plans].map(([id,p])=>[id,{...p}])),
     hitEvents:src.hitEvents.map(h=>({...h,events:h.events.map(e=>({...e}))})),
     log:src.log.slice()};
 }
 const getRow=id=>history.sourceFor(Number(id));
 const validId=id=>Number.isInteger(Number(id))&&ids.includes(Number(id));
 const safe=v=>Number.isFinite(v)&&v>=0?Math.floor(v):0;
 const elementNames={1:'Fire',2:'Water',3:'Earth',4:'Thunder',5:'Light',6:'Dark'};
 const actionsList=['attack','burst','guard','heal',...(sourceBB?['sourcebb']:[])];
 const sourceSkill=u=>sourceBB?.getAtLevel?.(u?.unitId,u?.bbLevel||1)||
   sourceBB?.get(u?.unitId)||null;
 function squad(){
   const seen=new Set(),units=[];
   const original=old.squadSnapshot;
   if(!Array.isArray(original))return units;
   for(const x of original.slice(0,6)){
     if(!x||!Number.isInteger(x.sourceId)||seen.has(x.sourceId)||
        !P.roster?.includes(x.sourceId)||!P.squad?.includes(x.sourceId)||
        !x.name||!x.atk||!x.baseHp||!x.def||!x.rec)continue;
     seen.add(x.sourceId);
     units.push({sourceId:x.sourceId,name:String(x.name),
       unitId:x.unitId,element:String(x.element||'Unknown'),
       portrait:String(x.portrait||''),atk:safe(x.atk),
       def:safe(x.def),rec:safe(x.rec),baseHp:safe(x.baseHp),
       hp:safe(x.maxHp),maxHp:safe(x.maxHp),burst:0,guard:false,
       bbLevel:1});
   }
   return units;
 }
 function canStart(id=Number(mission.value)){
   if(!validId(id)||S?.busy || old.training?.phase==='running'||
      history.practice?.state==='running')return false;
   const quest=QUESTS.find(q=>q.missionId===Number(id));
   return !!quest&&questUnlocked(quest)&&squad().length>0;
 }
 function addWave(){
   const wave=getRow(fight.missionId)?.waves[fight.wave];
   if(!wave)return false;
   fight.foes=wave.enemies.map(e=>({
     name:String(e.name),unitId:e.unitId,hp:safe(e.hp),maxHp:safe(e.hp),
     atk:safe(e.atk),def:safe(e.def)}));
   fight.plans=new Map();
   for(const u of fight.party)if(u.hp>0)
     fight.plans.set(u.sourceId,{kind:'attack',target:0,ally:u.sourceId});
   fight.log.push('2014 historical wave '+(fight.wave+1)+' loaded ('+
      fight.foes.length+' enemy slots).');
   return true;
 }
 function draftSquad(ids){
   if(!Array.isArray(ids)||ids.length<1||ids.length>6||
      new Set(ids).size!==ids.length)return null;
   const units=[];
   for(const id of ids){
     if(!Number.isSafeInteger(id)||id<=0)return null;
     const x=BFGlobalUnitArchive.find(id);
     if(!x||x.unitKind!==0||!x.name||
       ![x.unitBaseHp,x.unitBaseAtk,x.unitBaseDef,x.unitBaseRec].every(
          v=>Number.isSafeInteger(v)&&v>0))return null;
     const hp=x.unitBaseHp*2;
     if(!Number.isSafeInteger(hp))return null;
     units.push({sourceId:-id,unitId:id,name:x.name,
       element:elementNames[x.element]||'Unknown',
       portrait:x.thumbnail?'content/unit_archive/unit_ills_thum_'+id+'.png':'',
       atk:x.unitBaseAtk,def:x.unitBaseDef,rec:x.unitBaseRec,
       baseHp:x.unitBaseHp,hp,maxHp:hp,
       burst:0,guard:false,bbLevel:1});
   }
   return units;
 }
 function canStartDraft(ids,id=1){
   if(fight||S?.busy||old.training?.phase==='running'||
     history.practice?.state==='running'||!validId(id))return false;
   const quest=QUESTS.find(q=>q.missionId===Number(id));
   return !!quest&&questUnlocked(quest)&&!!draftSquad(ids);
 }
 function startDraft(ids,id=1){
   if(!canStartDraft(ids,id))return false;
   const party=draftSquad(ids);
   if(!party)return false;
   mission.value=String(id);
   fight={missionId:Number(id),mode:'archive-draft',draftUnitIds:ids.slice(),
     phase:'running',wave:0,turns:0,kits:3,party,foes:[],
     plans:new Map(),log:[],damageDealt:0,damageTaken:0,kills:0,heals:0,
     hitEvents:[]};
   undoStack=[];
   addWave();render();return true;
 }
 function startTrial(id=Number(mission.value)){
   if(fight || !canStart(id))return false;
   const party=squad();if(!party.length)return false;
   mission.value=String(id);
   fight={missionId:Number(id),mode:'owned',draftUnitIds:[],
     phase:'running',wave:0,turns:0,kits:3,
     party,foes:[],plans:new Map(),log:[],damageDealt:0,damageTaken:0,
     kills:0,heals:0,hitEvents:[]};
   undoStack=[];
   addWave();render();return true;
 }
 function state(){
   if(!fight)return null;
   const row=getRow(fight.missionId);
   return {missionId:fight.missionId,phase:fight.phase,
     mode:fight.mode||'owned',draftUnitIds:fight.draftUnitIds.slice(),
     undoDepth:undoStack.length,
     wave:fight.wave+1,totalWaves:row.waves.length,
     rounds:fight.turns,kits:fight.kits,
     sourceBBCount:sourceBB?.count||0,
     sourceBBLevels:sourceBB?.levelCount||1,
     sourceHitCoverage:hitSources?.eligible||0,
     hitEvents:fight.hitEvents.map(h=>({...h,events:h.events.map(e=>({...e}))})),
     damageDealt:fight.damageDealt,damageTaken:fight.damageTaken,
     kills:fight.kills,heals:fight.heals,
     party:fight.party.map(u=>({sourceId:u.sourceId,name:u.name,hp:u.hp,
       maxHp:u.maxHp,burst:u.burst,guard:u.guard,
       boostPct:u.boostPct||0,boostRounds:u.boostRounds||0,
       sourceSkill:sourceSkill(u)?.name||null,
       bbLevel:u.bbLevel||1,
       portrait:u.portrait,element:u.element,unitId:u.unitId})),
     enemies:fight.foes.map((e,slot)=>({slot,name:e.name,unitId:e.unitId,
       hp:e.hp,maxHp:e.maxHp,
       thumbnail:!!BFGlobalUnitArchive.find(e.unitId)?.thumbnail})),
     plans:fight.party.filter(u=>u.hp>0).map(u=>({
       sourceId:u.sourceId,...fight.plans.get(u.sourceId)})),
     recent:fight.log.slice(-18)};
 }
 function plan(id,kind,target,ally){
   if(!fight||fight.phase!=='running'||S?.busy ||
      !actionsList.includes(kind)||!Number.isInteger(Number(id)))return false;
   const u=fight.party.find(x=>x.sourceId===Number(id)&&x.hp>0);
   const slot=Number(target),allyId=Number(ally);
   if(!u||!Number.isInteger(slot)||slot<0||slot>=fight.foes.length||
      !Number.isInteger(allyId)||!fight.party.some(x=>x.sourceId===allyId&&x.hp>0))return false;
   if(kind==='burst'&&u.burst<2)return false;
   if(kind==='sourcebb'&&(!sourceSkill(u)||u.burst<2))return false;
   if(kind==='heal'&&fight.kits===0)return false;
   fight.plans.set(u.sourceId,{kind,target:slot,ally:allyId});
   render();return true;
 }
 function setSkillLevel(id,level){
   if(!fight||fight.phase!=='running'||S?.busy||
     !Number.isInteger(level)||level<1||level>10)return false;
   const unit=fight.party.find(u=>u.sourceId===Number(id)&&u.hp>0);
   if(!unit||!sourceBB?.getAtLevel?.(unit.unitId,level))return false;
   unit.bbLevel=level;render();return true;
 }
 function autoPlan(){
   if(!fight||fight.phase!=='running'||S?.busy)return false;
   let plannedHeals=0;
   for(const u of fight.party.filter(u=>u.hp>0)){
     const enemies=fight.foes.map((e,slot)=>({e,slot})).filter(x=>x.e.hp>0);
     if(!enemies.length)break;
     enemies.sort((a,b)=>a.e.hp-b.e.hp||a.slot-b.slot);
     const wounded=fight.party.filter(x=>x.hp>0&&x.hp<x.maxHp*.45)
       .sort((a,b)=>a.hp/a.maxHp-b.hp/b.maxHp);
     let kind='attack',ally=u.sourceId;
     if(wounded.length&&fight.kits>plannedHeals){kind='heal';ally=wounded[0].sourceId;plannedHeals++;}
     else if(u.burst>=2&&sourceSkill(u))kind='sourcebb';
     else if(u.burst>=2)kind='burst';
     else if(u.hp<u.maxHp*.22)kind='guard';
     fight.plans.set(u.sourceId,{kind,target:enemies[0].slot,ally});
   }
   render();return true;
 }
 function stepRound(){
   if(!fight||fight.phase!=='running'||S?.busy)return false;
   if(!fight.party.some(u=>u.hp>0)||!fight.foes.some(e=>e.hp>0))return false;
   // Check every queued action before mutating trial state. Each *living*
   // party member acts at most once; dead or invalid targets fall back safely.
   const actors=fight.party.filter(u=>u.hp>0);
   if(!actors.every(u=>fight.plans.has(u.sourceId)))return false;
   let remainingKits=fight.kits;
   for(const u of actors){
     const plan=fight.plans.get(u.sourceId);
     if(plan.kind==='heal'&&remainingKits>0)remainingKits--;
     else if(plan.kind==='burst'&&u.burst<2)return false;
     else if(plan.kind==='sourcebb'&&(!sourceSkill(u)||u.burst<2))return false;
   }
   // Take the pre-round snapshot after validations, before any mutation.
   const previousRound=cloneFight(fight);
   fight.hitEvents=[];
   fight.turns++;
   const say=v=>fight.log.push(v);
   say('SIMULATED team round '+fight.turns+' — '+actors.length+' unit actions.');
   // All six queued actions happen before *one* synthetic enemy volley.
   for(const u of actors){
     const p=fight.plans.get(u.sourceId);
     if(!p || u.hp<=0)continue;
     if(p.kind==='guard'){u.guard=true;say(u.name+' defended.');continue;}
     if(p.kind==='sourcebb'){
       const skill=sourceSkill(u);
       if(!skill||u.burst<2)return false;
       u.burst=0;
       if(skill.kind==='heal_all'){
         // Source level range recovered; midpoint, lacking REC, is synthetic.
         const amount=Math.floor((skill.low+skill.high)/2);
         let healed=0;
         for(const ally of fight.party.filter(x=>x.hp>0)){
           const n=Math.min(ally.maxHp-ally.hp,amount);
           ally.hp+=n;healed+=n;
         }
         fight.heals+=healed;
         say(u.name+' · '+skill.name+' (2022 source Lv'+(u.bbLevel||1)+'): '+healed+
           ' total simulated party healing.');
         continue;
       }
       if(skill.kind==='atk_buff_all'){
         for(const ally of fight.party.filter(x=>x.hp>0)){
           ally.boostPct=skill.pct;ally.boostRounds=skill.rounds+1;
         }
         say(u.name+' · '+skill.name+' (2022 source Lv'+(u.bbLevel||1)+'): simulated ATK +'+
           skill.pct+'% party buff.');
         continue;
       }
       if(skill.kind==='attack'){
         const target=fight.foes[p.target]?.hp>0?fight.foes[p.target]:
           fight.foes.find(e=>e.hp>0);
         const chosen=skill.target==='all_enemies'?
           fight.foes.filter(e=>e.hp>0):target?[target]:[];
         let dealt=0;
         for(const enemy of chosen){
           const boostedAtk=Math.floor(u.atk*(100+(u.boostPct||0))/100);
           const base=Math.max(120,Math.floor(boostedAtk*1.7-enemy.def*.4));
           const raw=Math.max(1,Math.floor(base*(100+skill.pct)/100));
           const applied=Math.min(enemy.hp,raw);
           enemy.hp-=applied;dealt+=applied;fight.damageDealt+=applied;
           if(enemy.hp===0)fight.kills++;
         }
         say(u.name+' · '+skill.name+' (2022 Lv'+(u.bbLevel||1)+' modifier '+skill.pct+
           '% / '+skill.target+'): '+dealt+' simulated damage.'+
           (skill.secondary?' Secondary effects not simulated.':''));
         continue;
       }
       return false;
     }
     if(p.kind==='heal'){
       if(!fight.kits){say(u.name+' had no heal kit left.');continue;}
       const ally=fight.party.find(x=>x.sourceId===p.ally&&x.hp>0) ||u;
       const amount=Math.max(350,Math.floor(u.rec*1.6+300));
       const actual=Math.min(ally.maxHp-ally.hp,amount);
       if(actual>0){fight.kits--;ally.hp+=actual;fight.heals+=actual;
         say(u.name+' healed '+ally.name+' for '+actual+' (synthetic).');
       }else say(u.name+' skipped healing a full-HP ally.');
       continue;
     }
     const foe=fight.foes[p.target]?.hp>0?fight.foes[p.target]:
       fight.foes.find(e=>e.hp>0);
     if(!foe){say(u.name+' had no remaining foe to attack.');continue;}
     // No recovered original 2022 damage formula is claimed.
     const boostedAtk=Math.floor(u.atk*(100+(u.boostPct||0))/100);
     const raw=Math.max(120,Math.floor(boostedAtk*1.7-foe.def*.4));
     function hit(enemy,dmg){
       const actual=Math.min(enemy.hp,dmg);
       enemy.hp-=actual;fight.damageDealt+=actual;
       if(enemy.hp===0)fight.kills++;
       return actual;
     }
     if(p.kind==='burst'){
       const n=hit(foe,Math.floor(raw*2.1));
       let splash=0;
       for(const other of fight.foes.filter(e=>e!==foe&&e.hp>0))
         splash+=hit(other,Math.max(90,Math.floor(raw*.30)));
       u.burst=0;say(u.name+' simulated Burst '+n+
         ' primary / '+splash+' splash damage.');
     }else{
       const n=hit(foe,raw);u.burst=Math.min(3,u.burst+1);
       const frames=hitSources?.get(u.unitId);
       if(frames&&frames.length){
         // Exact original F_UNIT frame/weight pairs; distribute only the
         // already-computed synthetic total using cumulative integer weights.
         let prev=0,percent=0;
         const events=frames.map(([frame,weight])=>{
           percent+=weight;
           const next=Math.floor(n*percent/100);
           const amount=next-prev;prev=next;
           return {frame,weight,damage:amount};
         });
         fight.hitEvents.push({sourceId:u.sourceId,unitId:u.unitId,
           name:u.name,target:foe.name,total:n,events});
         say(u.name+' hit timeline: '+events.length+
           ' original frame references / '+n+' synthetic total.');
       }
       say(u.name+' attacked '+foe.name+' for '+n+' synthetic damage.');
     }
   }
   if(fight.foes.every(e=>e.hp===0)){
     if(fight.wave+1===getRow(fight.missionId).waves.length){
       fight.phase='won';say('TRIAL VICTORY. No actual quest clear or rewards.');
     }else{fight.wave++;addWave();}
   }else{
     const living=()=>fight.party.filter(u=>u.hp>0);
     fight.foes.forEach((e,slot)=>{
       const targets=living();
       if(e.hp<=0||!targets.length)return;
       const defender=targets[(fight.turns+slot-1)%targets.length];
       const raw=Math.max(10,Math.floor(e.atk*.14-defender.def*.02));
       const dmg=Math.min(defender.hp,defender.guard?Math.ceil(raw*.3):raw);
       defender.hp-=dmg;fight.damageTaken+=dmg;
       say(e.name+' replied to '+defender.name+' for '+dmg+' synthetic damage.');
     });
     fight.party.forEach(u=>{u.guard=false;});
     if(!living().length){fight.phase='lost';say('TRIAL DEFEAT. No permanent penalty.');}
   }
   // Source duration is retained; exact original stacking/timing is unknown.
   for(const u of fight.party){
     if(u.boostRounds>0){u.boostRounds--;
       if(!u.boostRounds)u.boostPct=0;}
   }
   fight.log=fight.log.slice(-70);
   if(fight.phase==='running') {
     const previous=new Map(fight.plans);
     fight.plans=new Map();
     for(const u of fight.party.filter(u=>u.hp>0)){
       const p=previous.get(u.sourceId);
       fight.plans.set(u.sourceId,{
         kind:p?.kind==='guard'?'guard':'attack',
         target:fight.foes.findIndex(e=>e.hp>0),
         ally:u.sourceId});
     }
   }
   undoStack.push(previousRound);
   if(undoStack.length>20)undoStack.shift();
   render();return true;
 }
 function undoLastRound(){
   if(!fight||!undoStack.length||S?.busy)return false;
   fight=undoStack.pop();
   render();return true;
 }
 function autoAdvance(count=5){
   if(!fight||fight.phase!=='running'||S?.busy||
      !Number.isInteger(count)||count<1||count>15)return false;
   let actual=0;
   for(let i=0;i<count&&fight.phase==='running';i++){
     if(!autoPlan()||!stepRound())break;
     actual++;
   }
   return actual;
 }
 function exit(){fight=null;undoStack=[];render();return true;}
 function option(sel,value,label){
   const el=document.createElement('option');
   el.value=String(value);el.textContent=label;sel.append(el);
 }
 function cards(dst,items){
   dst.replaceChildren();
   for(const u of items){
     const node=document.createElement('div');
     node.className='bf300-card'+(u.hp<=0?' bf350-fainted':'');
     const top=document.createElement('div');top.className='bf350-unit';
     const isParty=Number.isInteger(u.sourceId);
     const thumb=isParty?u.portrait:
       (u.thumbnail?'content/unit_archive/unit_ills_thum_'+u.unitId+'.png':'');
     if(thumb){
       const img=document.createElement('img');img.src=thumb;
       img.alt=isParty?'Equipped unit portrait':
         '2022 unit archive portrait, not a verified 2014 enemy sprite';
       img.loading='lazy';top.append(img);
     }
     const names=document.createElement('div'),title=document.createElement('strong');
     title.textContent=u.name+(isParty?' · #'+u.sourceId:' · slot '+(u.slot+1));
     const detail=document.createElement('small');
     detail.textContent=u.hp+'/'+u.maxHp+' training HP'+
       (u.burst!==undefined?' · Burst '+u.burst:'')+
       (u.boostRounds>0?' · ATK +'+u.boostPct+'% ('+u.boostRounds+' rounds)':'');
     const kind=document.createElement('small');
     kind.textContent=isParty?u.element+' · 2022 owned source form':
       '2014 historical foe · #'+u.unitId;
     names.append(title,detail,kind);top.append(names);node.append(top);
     const bar=document.createElement('div');bar.className='bf350-meter';
     bar.setAttribute('role','progressbar');bar.setAttribute('aria-label',u.name+' HP');
     bar.setAttribute('aria-valuemin','0');
     bar.setAttribute('aria-valuemax',String(u.maxHp));
     bar.setAttribute('aria-valuenow',String(u.hp));
     const fill=document.createElement('div');fill.className='bf350-fill';
     fill.style.width=(Math.max(0,Math.min(100,100*u.hp/Math.max(1,u.maxHp))))+'%';
     bar.append(fill);node.append(bar);dst.append(node);
   }
 }
 function render(){
   const row=getRow(Number(mission.value));
   source.textContent=row?'2014 archived waves: '+row.waves.length+
     ' · '+row.sourcePath+' · read-only name join to 2022 Global quest':'';
   start.disabled=!!fight||!canStart();stop.disabled=!fight;
   arena.hidden=!fight;
   if(!fight){status.textContent='Inactive — select an unlocked quest to train.';return;}
   const s=state();
   status.textContent='EXPERIMENTAL '+(s.mode==='archive-draft'?
     'ARCHIVE DRAFT (NOT OWNED)':'OWNED SQUAD')+' · '+s.phase.toUpperCase()+' · Wave '+
     s.wave+'/'+s.totalWaves+' · Team rounds '+s.rounds+
     ' · Kits '+s.kits+' · Undo '+s.undoDepth+'/20';
   cards(roster,s.party);cards(enemies,s.enemies);
   planner.replaceChildren();
   if(s.phase==='running'){
     for(const u of s.party.filter(x=>x.hp>0)){
       const p=fight.plans.get(u.sourceId);
       const section=document.createElement('div');section.className='bf300-planner';
       const caption=document.createElement('strong');caption.textContent=u.name;
       section.append(caption);
       const addSelect=(captionText,values,current,handler)=>{
         const label=document.createElement('label');label.textContent=captionText;
         const select=document.createElement('select');
         for(const [v,name] of values)option(select,v,name);
         select.value=String(current);
         select.addEventListener('change',()=>{
           const next=handler(select.value);
           if(!next)render();
         });
         label.append(select);section.append(label);
       };
       const skill=sourceSkill(fight.party.find(x=>x.sourceId===u.sourceId));
       if(skill && sourceBB?.levelCount===10){
         addSelect('2022 BB SOURCE LEVEL · practice only',
           Array.from({length:10},(_,i)=>[i+1,'Level '+(i+1)]),
           u.bbLevel||1,v=>setSkillLevel(u.sourceId,Number(v)));
         const preview=document.createElement('p');
         preview.textContent='2022 source: '+skill.name+' Lv'+(u.bbLevel||1)+
           ' · '+(skill.kind==='attack'?
             skill.pct+'% first damage modifier · '+skill.target:
             skill.kind==='heal_all'?
               skill.low+'–'+skill.high+' base heal range (REC formula unknown)':
               'ATK +'+skill.pct+'% · '+skill.rounds+' source rounds')+
           ' · applied through synthetic training calculations only.';
         section.append(preview);
       }
       addSelect('ACTION',actionsList.filter(a=>a!=='sourcebb'||
           (skill&&u.burst>=2))
         .map(a=>[a,a==='sourcebb'?'ORIGINAL BB · '+skill.name+
           ' (2022 Lv'+(u.bbLevel||1)+' practice)':a.toUpperCase()]),
         p.kind,v=>plan(u.sourceId,v,p.target,p.ally));
       addSelect('ENEMY SLOT',s.enemies.filter(e=>e.hp>0).map(e=>[
         e.slot,e.name+' · #'+(e.slot+1)+' · '+e.hp+' HP']),
         s.enemies[p.target]?.hp>0?p.target:s.enemies.find(e=>e.hp>0)?.slot,
         v=>plan(u.sourceId,p.kind,Number(v),p.ally));
       addSelect('ALLY HEAL TARGET',s.party.filter(x=>x.hp>0).map(x=>[
         x.sourceId,x.name+' · '+x.hp+'/'+x.maxHp+' HP']),
         p.ally,v=>plan(u.sourceId,p.kind,p.target,Number(v)));
       planner.append(section);
     }
   }
   autoplan.disabled=resolve.disabled=autorun.disabled=s.phase!=='running'||!!S?.busy;
   undo.disabled=!undoStack.length||!!S?.busy;
   hitPanel.replaceChildren();
   if(s.hitEvents.length){
     const heading=document.createElement('strong');
     heading.textContent='2022 ORIGINAL HIT REFERENCES · latest synthetic round';
     hitPanel.append(heading);
     const note=document.createElement('p');
     note.textContent='Original frame indices and percent weights; divided damage is synthetic. 60-tick timing unverified.';
     hitPanel.append(note);
     for(const h of s.hitEvents){
       const wrap=document.createElement('div');wrap.className='bf700-hit';
       const headline=document.createElement('strong');
       headline.textContent=h.name+' → '+h.target+' · '+h.events.length+
         ' source hits · '+h.total+' training damage';wrap.append(headline);
       const cells=document.createElement('div');cells.className='bf700-hits';
       h.events.forEach(e=>{
         const chip=document.createElement('div');chip.className='bf700-hit-cell';
         chip.textContent='Frame '+e.frame+' · '+e.weight+'% · '+
           e.damage+' training damage';cells.append(chip);
       });
       wrap.append(cells);hitPanel.append(wrap);
     }
   }
   report.replaceChildren();
   const totals=document.createElement('p');
   totals.textContent='Synthetic telemetry: '+s.damageDealt+' dealt · '+
     s.damageTaken+' taken · '+s.kills+' enemies defeated · '+
     s.heals+' healed.';
   report.append(totals);
   for(const line of s.recent){
     const p=document.createElement('p');p.textContent=line;report.append(p);
   }
 }
 mission.addEventListener('change',()=>{if(!fight)render();});
 start.addEventListener('click',()=>startTrial());
 stop.addEventListener('click',exit);
 autoplan.addEventListener('click',autoPlan);
 resolve.addEventListener('click',stepRound);
 undo.addEventListener('click',undoLastRound);
 autorun.addEventListener('click',()=>autoAdvance(5));
 document.querySelector('.bf-navbar')?.addEventListener('click',()=>{
   if(!fight)render();
 });
 render();
 window.BFTacticalRoundsV300=Object.freeze({
   get sourceMissions(){return ids.length;},
   get snapshot(){return state();},
   get clonedSquad(){return squad();},
   get undoDepth(){return undoStack.length;},
   canStart,startTrial,canStartDraft,startDraft,plan,setSkillLevel,autoPlan,stepRound,undoLastRound,autoAdvance,
   exit,refresh:render
 });
})();
