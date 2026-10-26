/* BF_GLOBAL_SQUAD_TRAINING_V250 */
(() => {
 'use strict';
 if (window.BFSquadTrainingV250 || typeof P==='undefined' || P?.version!==7 ||
    typeof QUESTS==='undefined' || QUESTS.length!==106 ||
    !window.BFArchiveTrialsV200 || !window.BFGlobalUnitArchive ||
    typeof effectiveUnit!=='function' || typeof questUnlocked!=='function') return;
 const history=window.BFArchiveTrialsV200;
 if(history.missions!==21||history.historicalWaves!==112||
    history.historicalEntries!==264||history.distinctUnitIds!==42)return;
 const allIds=[1,2,10,11,20,21,30,31,40,41,42,50,51,52,60,61,70,71,200,202,240];
 if(allIds.some(id=>!history.sourceFor(id)?.waves?.length))return;
 const base=document.getElementById('bf200-trials');
 if(!base)return;
 const styles=document.createElement('style');styles.id='bf250-squad-styles';
 styles.textContent=[
  '#bf250-squad{padding:11px;margin:12px 2px;background:#192d40;',
  'border:1px solid #af9a71;border-radius:8px;color:#f1e6d1;font:12px/1.5 system-ui,sans-serif}',
  '#bf250-squad summary{font:bold 15px Georgia,serif;min-height:32px;cursor:pointer}',
  '#bf250-squad button,#bf250-squad select{box-sizing:border-box;min-height:40px;',
  'background:#314f69;border:1px solid #b6a070;border-radius:5px;color:white;',
  'padding:7px 9px;margin:3px}',
  '#bf250-squad button:disabled{opacity:.45}',
  '#bf250-squad select{width:100%;background:#17293e}',
  '.bf250-roster{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;margin:7px 0}',
  '.bf250-member{display:flex;gap:7px;align-items:center;padding:6px;',
  'border:1px solid #758a9d;border-radius:5px;background:#283f55}',
  '.bf250-member img{width:40px;height:40px;object-fit:contain;flex:0 0 40px}',
  '.bf250-member strong,.bf250-member small{display:block;overflow-wrap:anywhere}',
  '.bf250-member small{color:#d4dfeb}',
  '#bf250-fight p{margin:4px 0}',
  '#bf250-fight strong{color:#e4c78c}',
  '#bf250-log{max-height:150px;overflow:auto;border-top:1px solid #8292a8;margin-top:7px}',
  '.bf250-warning{color:#f0cba6}',
  '#bf250-status{font-weight:700}',
  '.bf250-target-grid{display:grid;grid-template-columns:1fr 1fr;gap:5px}',
  '.bf250-target-grid label{font-size:11px;display:block}',
  '.bf250-action-row{display:flex;flex-wrap:wrap;gap:3px}'
 ].join('');
 document.head.append(styles);
 const panel=document.createElement('details');panel.id='bf250-squad';
 panel.setAttribute('aria-label','Experimental isolated six-unit squad training against 2014 historical waves');
 const heading=document.createElement('summary');
 heading.textContent='SQUAD TRAINING LAB · v2.50';
 const caution=document.createElement('p');caution.className='bf250-warning';
 caution.textContent='Opt-in DEMO: clone your currently owned squad (2022 source unit BASE stats) for a separate tactical exercise against historical 2014 enemy wave records. All damage, targeting, healing and Burst mechanics are synthetic—not native Brave Frontier.';
 const mission=document.createElement('select');mission.id='bf250-mission';
 for(const id of allIds){
   const row=history.sourceFor(id);
   const option=document.createElement('option');option.value=String(id);
   option.textContent='Mission '+id+' · '+row.name;mission.append(option);
 }
 const copied=document.createElement('div');copied.id='bf250-copied';
 copied.className='bf250-roster';copied.setAttribute('aria-label','Read-only snapshot of current squad');
 const begin=document.createElement('button');begin.id='bf250-start';
 begin.type='button';begin.textContent='CLONE SQUAD & START';
 const exit=document.createElement('button');exit.id='bf250-exit';
 exit.type='button';exit.textContent='EXIT · DISCARD PRACTICE';
 const status=document.createElement('p');status.id='bf250-status';
 status.setAttribute('aria-live','polite');
 const fight=document.createElement('div');fight.id='bf250-fight';
 const controls=document.createElement('div');controls.className='bf250-target-grid';
 const picker=(id,label)=>{
   const el=document.createElement('label');el.textContent=label;
   const select=document.createElement('select');select.id=id;
   el.append(select);controls.append(el);return select;
 };
 const actor=picker('bf250-actor','ACTING UNIT');
 const enemy=picker('bf250-enemy','ENEMY TARGET');
 const healTarget=picker('bf250-heal-target','ALLY HEAL TARGET');
 const actions=document.createElement('div');actions.className='bf250-action-row';
 const keys=['attack','burst','guard','heal','auto'];
 const buttons={};
 for(const kind of keys){
   const button=document.createElement('button');button.type='button';
   button.dataset.bf250Action=kind;
   button.textContent={attack:'ATTACK',burst:'TRAINING BURST',
     guard:'GUARD',heal:'HEAL KIT',auto:'AUTO TURN'}[kind];
   button.addEventListener('click',()=>kind==='auto'?autoTurn():action(kind));
   buttons[kind]=button;actions.append(button);
 }
 const log=document.createElement('div');log.id='bf250-log';
 log.setAttribute('aria-live','polite');
 const disclaimer=document.createElement('p');disclaimer.className='bf250-warning';
 disclaimer.textContent='SQUAD LAB IS TEMPORARY. It cannot earn rewards, spend Energy, change original combat or update any save, roster or squad. It resets whenever you exit or reload.';
 fight.append(controls,actions,log);panel.append(heading,caution,mission,copied,
   begin,exit,status,fight,disclaimer);
 base.after(panel);
 let session=null;
 const selected=()=>history.sourceFor(Number(mission.value));
 const numeric=v=>Number.isFinite(v)&&v>=0?Math.floor(v):0;
 function snapshotSquad(){
   if(!Array.isArray(P.squad)||!Array.isArray(P.roster))return [];
   const chosen=new Set(),out=[];
   for(const id of P.squad.slice(0,6)){
     if(!Number.isInteger(id)||chosen.has(id)||!P.roster.includes(id))continue;
     const unit=effectiveUnit(id);
     if(!unit||!unit.name||!unit.stats)continue;
     const {hp,atk,def,rec}=unit.stats;
     if([hp,atk,def,rec].some(v=>!Number.isFinite(v)||v<=0))continue;
     chosen.add(id);
     out.push({sourceId:id,unitId:unit.id,name:String(unit.name),
       portrait:String(unit.portrait||''),element:String(unit.element||'Unknown'),
       baseHp:numeric(hp),atk:numeric(atk),def:numeric(def),rec:numeric(rec),
       hp:numeric(hp)*2,maxHp:numeric(hp)*2,burst:0,guard:false});
   }
   return out;
 }
 function rosterCards(team,where){
   where.replaceChildren();
   for(const unit of team){
     const card=document.createElement('div');card.className='bf250-member';
     if(unit.portrait){
       const img=document.createElement('img');img.src=unit.portrait;
       img.alt='';img.loading='lazy';card.append(img);
     }
     const info=document.createElement('div'),name=document.createElement('strong'),
           stats=document.createElement('small');
     name.textContent=unit.name;
     stats.textContent='2022 source base '+unit.baseHp+' HP / '+
       unit.atk+' ATK / '+unit.def+' DEF / '+unit.rec+' REC'+
       (session?' · Training HP '+unit.hp+'/'+unit.maxHp+' · Burst '+unit.burst:'/ source-only');
     info.append(name,stats);card.append(info);where.append(card);
   }
 }
 function progress(){
   if(!session)return null;
   return {missionId:session.missionId,phase:session.phase,
     wave:session.wave+1,totalWaves:selectedById(session.missionId).waves.length,
     turns:session.turns,kits:session.kits,
     party:session.party.map(u=>({name:u.name,sourceId:u.sourceId,
       unitId:u.unitId,hp:u.hp,maxHp:u.maxHp,burst:u.burst,guard:u.guard})),
     enemies:session.enemies.map(e=>({name:e.name,unitId:e.unitId,hp:e.hp,maxHp:e.maxHp})),
     recent:session.log.slice(-10)};
 }
 function selectedById(id){return history.sourceFor(Number(id));}
 function loadWave(){
   const row=selectedById(session.missionId);
   session.enemies=row.waves[session.wave].enemies.map(e=>({
     name:e.name,unitId:e.unitId,maxHp:e.hp,hp:e.hp,
     atk:e.atk,def:e.def}));
   session.log.push('Entered 2014 historical wave '+(session.wave+1)+
       '/'+row.waves.length+' for EXPERIMENTAL practice.');
 }
 function canStart(id=Number(mission.value)){
   const row=selectedById(id);
   const quest=QUESTS.find(q=>q.missionId===Number(id));
   return !!row&&!!quest&&questUnlocked(quest)&&!S?.busy&&snapshotSquad().length>0;
 }
 function start(id=Number(mission.value)){
   if(!canStart(id))return false;
   const team=snapshotSquad();
   if(!team.length)return false;
   mission.value=String(id);
   session={missionId:id,phase:'running',wave:0,turns:0,kits:3,
     party:team.map(u=>({...u})),enemies:[],log:[]};
   loadWave();render();return true;
 }
 function aliveParty(){return session.party.filter(u=>u.hp>0);}
 function actFor(kind,actorId,targetId,healedId){
   if(!session||session.phase!=='running'||S?.busy||
     !['attack','burst','guard','heal'].includes(kind))return false;
   const unit=session.party.find(u=>u.sourceId===actorId);
   if(!unit||unit.hp<=0)return false;
   if(kind==='burst'&&unit.burst<2)return false;
   if(kind==='heal'&&session.kits<=0)return false;
   const enemies=session.enemies;
   if(kind==='attack'||kind==='burst'){
     const focus=enemies[Number(targetId)]?.hp>0?
       enemies[Number(targetId)]:enemies.find(e=>e.hp>0);
     if(!focus)return false;
     // EXPLICITLY SYNTHETIC; source data only provides base unit stats.
     const damage=Math.max(150,Math.floor(unit.atk*1.65-focus.def*.5));
     if(kind==='attack'){
       focus.hp=Math.max(0,focus.hp-damage);
       unit.burst=Math.min(3,unit.burst+1);
       session.log.push(unit.name+' strike: '+damage+' training damage.');
     }else{
       focus.hp=Math.max(0,focus.hp-Math.floor(damage*2.2));
       for(const e of enemies.filter(e=>e!==focus&&e.hp>0))
         e.hp=Math.max(0,e.hp-Math.max(80,Math.floor(damage*.33)));
       unit.burst=0;
       session.log.push(unit.name+' synthetic Burst: practice splash damage.');
     }
   }else if(kind==='guard'){
     unit.guard=true;
     session.log.push(unit.name+' guards during the enemy training volley.');
   }else{
     const ally=session.party.find(u=>u.sourceId===healedId&&u.hp>0)||unit;
     const heal=Math.max(450,Math.floor(unit.rec*1.9+300));
     if(ally.hp===ally.maxHp)return false;
     session.kits--;
     ally.hp=Math.min(ally.maxHp,ally.hp+heal);
     session.log.push(unit.name+' practices healing '+ally.name+' for '+heal+'.');
   }
   session.turns++;
   if(enemies.every(e=>e.hp===0)){
     const missionRow=selectedById(session.missionId);
     if(session.wave===missionRow.waves.length-1){
       session.phase='won';
       session.log.push('TRAINING COMPLETE. No original quest clear or rewards.');
     }else {session.wave++;loadWave();}
   }else{
     const alive=aliveParty();
     for(let i=0;i<enemies.length;i++){
       const foe=enemies[i];if(foe.hp<=0||!alive.length)continue;
       const target=alive[(session.turns+i-1)%alive.length];
       const damage=Math.max(9,Math.floor(foe.atk*.16-target.def*.018));
       const applied=target.guard?Math.ceil(damage*.28):damage;
       target.hp=Math.max(0,target.hp-applied);
       session.log.push(foe.name+' simulated hit on '+target.name+': '+applied+'.');
     }
     for(const ally of session.party)ally.guard=false;
     if(!aliveParty().length){
       session.phase='lost';session.log.push('TRAINING FAILED. No permanent penalty.');
     }
   }
   session.log=session.log.slice(-35);
   render();return true;
 }
 function action(kind){
   return actFor(kind,Number(actor.value),Number(enemy.value),Number(healTarget.value));
 }
 function autoTurn(){
   if(!session||session.phase!=='running'||S?.busy)return false;
   const alive=aliveParty();if(!alive.length)return false;
   const chosen=alive.slice().sort((a,b)=>b.atk-a.atk)[0];
   const candidates=session.enemies.map((e,index)=>({e,index}))
     .filter(r=>r.e.hp>0).sort((a,b)=>a.e.hp-b.e.hp||a.index-b.index);
   if(!candidates.length)return false;
   return actFor(chosen.burst>=2?'burst':'attack',
     chosen.sourceId,candidates[0].index,chosen.sourceId);
 }
 function reset(){session=null;render();return true;}
 function refresh(){
   // Preserve selections through DOM refreshes and each simulated action.
   const previousActor=actor.value,previousEnemy=enemy.value,
         previousHeal=healTarget.value;
   rosterCards(session?.party||snapshotSquad(),copied);
   begin.disabled=!!session||!canStart();
   exit.disabled=!session;
   if(!session){fight.hidden=true;
     status.textContent='No training in progress. Select an unlocked mission.';
     return;}
   fight.hidden=false;
   const p=progress();
   status.textContent='EXPERIMENTAL '+p.phase.toUpperCase()+
     ' · Wave '+p.wave+'/'+p.totalWaves+' · Round '+p.turns+
     ' · Heal kits '+p.kits;
   actor.replaceChildren();healTarget.replaceChildren();enemy.replaceChildren();
   const squad=p.party.filter(u=>u.hp>0);
   const foes=p.enemies.filter(u=>u.hp>0);
   for(const u of squad){
     const option=document.createElement('option');
     option.value=String(u.sourceId);option.textContent=u.name+
       ' · '+u.hp+'/'+u.maxHp+' HP · Burst '+u.burst;
     actor.append(option);
     healTarget.append(option.cloneNode(true));
   }
   // Target by absolute wave slot, not unit ID: duplicate enemy IDs
   // must remain individually selectable in a historical formation.
   p.enemies.forEach((foe,index)=>{
     if(foe.hp<=0)return;
     const option=document.createElement('option');
     option.value=String(index);
     option.textContent=foe.name+' (#'+(index+1)+') · '+
       foe.hp+'/'+foe.maxHp+' HP';
     enemy.append(option);
   });
   if(squad.some(u=>String(u.sourceId)===previousActor))
     actor.value=previousActor;
   if([...enemy.options].some(o=>o.value===previousEnemy))
     enemy.value=previousEnemy;
   // Prefer wounded ally for single-target simulated healing but retain a
   // manually selected, still-living target.
   const wounded=squad.find(u=>u.hp<u.maxHp);
   if(squad.some(u=>String(u.sourceId)===previousHeal))
     healTarget.value=previousHeal;
   else if(wounded)healTarget.value=String(wounded.sourceId);
   const active=squad.find(u=>u.sourceId===Number(actor.value))||squad[0];
   for(const [kind,button] of Object.entries(buttons))
     button.disabled=p.phase!=='running'||!!S?.busy||
       (kind==='burst'&&(!active||active.burst<2))||
       (kind==='heal'&&(!p.kits||!wounded));
   log.replaceChildren();
   for(const line of p.recent){const item=document.createElement('p');
     item.textContent=line;log.append(item);}
 }
 function render(){refresh();}
 mission.addEventListener('change',()=>{if(!session)render();});
 actor.addEventListener('change',refresh);
 begin.addEventListener('click',()=>start());
 exit.addEventListener('click',reset);
 document.querySelector('.bf-navbar')?.addEventListener('click',()=>{
   if(!session)refresh();
 });
 render();
 window.BFSquadTrainingV250=Object.freeze({
   get sourceQuests(){return allIds.length},
   get squadSnapshot(){return snapshotSquad().map(u=>({...u}));},
   get training(){return progress()},
   canStart,start,action,autoTurn,reset,refresh
 });
})();
