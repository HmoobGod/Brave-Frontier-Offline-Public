/* BF_GLOBAL_STORY_BATTLE_HUD_V2000 */
(() => {
 'use strict';
 if (window.BFGlobalStoryBattleV2000 || !window.BFQuestAreas ||
     !window.BFGlobalQuestText || !window.BFGrandGaiaContinueV101 ||
     typeof QUESTS==='undefined' || QUESTS.length!==106 ||
     typeof P==='undefined' || P.version!==7 || typeof S==='undefined') return;
 const questDetail=document.getElementById('bf-quest-details');
 const battle=document.getElementById('battle');
 const tabs=document.querySelector('.bf080-region-tabs');
 if(!questDetail || !battle || !tabs || tabs.querySelectorAll('button').length!==3)return;
 const sheet=document.createElement('style');
 sheet.textContent=[
  '#bf2000-run{margin:9px 0;padding:12px;border:1px solid #a48c63;border-radius:8px;',
  'background:linear-gradient(150deg,#202f46,#142035);color:#f5ead5;',
  'font:12px/1.5 system-ui,sans-serif}',
  '#bf2000-run h3{margin:0;font:800 15px Georgia,serif;color:#ffe8b5}',
  '#bf2000-title{margin:5px 0;font-weight:800;font-size:13px}',
  '#bf2000-details{margin:3px 0;color:#d6e1ec}',
  '#bf2000-waves{display:grid;grid-template-columns:repeat(auto-fit,minmax(34px,1fr));gap:4px;margin:9px 0}',
  '#bf2000-waves span{padding:5px 1px;text-align:center;background:#2c4560;',
  'border:1px solid #607b91;border-radius:4px;color:#eaf4ff;font-weight:bold}',
  '#bf2000-waves span[data-completed=true]{background:#326a5c;border-color:#78bba8}',
  '#bf2000-waves span[aria-current=step]{border-color:#f8d584;outline:1px solid #f8d584}',
  '#bf2000-state{font-weight:700;margin:6px 0}',
  '#bf2000-actions{display:flex;gap:7px;flex-wrap:wrap;margin-top:8px}',
  '#bf2000-actions button{padding:8px 12px;min-height:42px;border:1px solid #d7b780;',
  'border-radius:5px;background:#76582c;color:white;font-weight:800}',
  '#bf2000-actions button:disabled{opacity:.45}',
  '#bf2000-foot{display:block;margin-top:8px;color:#c2cbd3;font-size:11px}'
 ].join('');
 document.head.append(sheet);
 const panel=document.createElement('section');panel.id='bf2000-run';
 panel.setAttribute('aria-label','Live offline story mission battle');
 const heading=document.createElement('h3');heading.textContent='STORY MISSION · LIVE BATTLE';
 const title=document.createElement('p');title.id='bf2000-title';
 const details=document.createElement('p');details.id='bf2000-details';
 const waves=document.createElement('div');waves.id='bf2000-waves';
 waves.setAttribute('aria-label','Demo battle wave progress');
 const status=document.createElement('p');status.id='bf2000-state';
 status.setAttribute('aria-live','polite');
 const actions=document.createElement('div');actions.id='bf2000-actions';
 const jump=document.createElement('button');jump.type='button';
 jump.id='bf2000-battle';jump.textContent='VIEW BATTLE ↓';
 const next=document.createElement('button');next.type='button';
 next.id='bf2000-next';next.textContent='NEXT STORY MISSION ›';
 const foot=document.createElement('small');foot.id='bf2000-foot';
 foot.textContent='2022 Global mission names and recorded stage counts; active enemy formations, AI, damage, loot and Energy spending remain DEMO. Training battles are separate.';
 actions.append(jump,next);
 panel.append(heading,title,details,waves,status,actions,foot);
 questDetail.after(panel);
 const region=q=>q.dungeonId>=300?2:q.dungeonId>=200?1:0;
 const cleared=q=>(P.questClears?.[q.missionId]||0)>0;
 function upcoming(q){
   const index=QUESTS.findIndex(row=>row.missionId===q?.missionId);
   return index<0?null:QUESTS.slice(index+1).find(row=>!cleared(row)&&questUnlocked(row))||null;
 }
 function snapshot(){
   const q=typeof QUEST==='undefined'?null:QUEST;
   if(!q)return null;
   const reference=BFGlobalQuestText.sourceFor(q);
   const archive=E?.mode?.value==='archive';
   const count=archive?q.battles:S.totalWaves;
   const total=Number.isInteger(count)&&count>0?count:0;
   const step=Number.isFinite(S.wave)?Math.floor(S.wave):0;
   const won=!!S.over&&S.phase==='Victory';
   const lost=!!S.over&&!won;
   const completed=won?total:Math.min(total,Math.max(0,step));
   const current=total?(won?total:Math.min(total,completed+1)):0;
   const party=Array.isArray(S.party)?S.party.filter(u=>u&&Number.isFinite(u.maxHp)&&u.maxHp>0):[];
   const foes=Array.isArray(S.enemies)?S.enemies.filter(u=>u&&Number.isFinite(u.maxHp)&&u.maxHp>0):[];
   const upcomingQuest=archive&&won&&cleared(q)?upcoming(q):null;
   return Object.freeze({
     missionId:q.missionId,region:['Mistral','Morgan','St. Lamia'][region(q)],
     name:reference?.mission?.name||'Mission '+q.missionId,
     dungeon:reference?.dungeon?.name||'Dungeon '+q.dungeonId,
     archive,total,current,completed,won,lost,busy:!!S.busy,
     phase:String(S.phase||''),clears:P.questClears?.[q.missionId]||0,
     allies:party.filter(u=>u.hp>0).length,party:party.length,
     enemies:foes.filter(u=>u.hp>0).length,foes:foes.length,
     nextId:upcomingQuest?.missionId||null,
     nextName:upcomingQuest?BFGlobalQuestText.sourceFor(upcomingQuest)?.mission?.name||'Mission '+upcomingQuest.missionId:null
   });
 }
 let previous='';
 function refresh(){
   const state=snapshot();
   if(!state)return null;
   const signature=JSON.stringify(state);
   if(signature===previous)return state;
   previous=signature;
   title.textContent=state.name+' · Mission '+state.missionId;
   details.textContent=state.dungeon+' · '+state.region+' · '+
     (state.archive?'Archived 2022 quest · demo battles':'Separate DEMO training mode')+
     ' · '+state.total+' waves';
   const fragment=document.createDocumentFragment();
   for(let i=1;i<=state.total;i++){
     const chip=document.createElement('span');
     chip.textContent=String(i);
     chip.setAttribute('aria-label','Wave '+i+' of '+state.total+
       (i<=state.completed?', cleared':''));
     chip.dataset.completed=String(i<=state.completed);
     if(!state.won && i===state.current)chip.setAttribute('aria-current','step');
     fragment.append(chip);
   }
   waves.replaceChildren(fragment);
   status.textContent=(state.won?'VICTORY':state.lost?'DEFEAT':state.busy?'TURN IN PROGRESS':'BATTLE READY')+
     ' · Wave '+state.current+'/'+state.total+
     ' · Allies '+state.allies+'/'+state.party+' · Enemies '+state.enemies+'/'+state.foes;
   next.disabled=!!state.busy||!state.nextId;
   next.textContent=state.nextId?'NEXT: '+state.nextName+' ›':'NEXT STORY MISSION ›';
   next.title=state.nextId?'Continue to archived mission '+state.nextId:
     'Clear the current DEMO story battle to unlock the next mission';
   return state;
 }
 function advance(){
   const state=snapshot();
   if(!state||state.busy||!state.won||!state.archive||!state.nextId)return false;
   const q=QUESTS.find(row=>row.missionId===state.nextId);
   if(!q||!questUnlocked(q)||cleared(q)||!BFQuestAreas.choose(q))return false;
   tabs.querySelectorAll('button')[region(q)]?.click();
   previous='';refresh();
   panel.scrollIntoView({block:'start',behavior:'smooth'});
   return true;
 }
 jump.addEventListener('click',()=>battle.scrollIntoView({block:'start',behavior:'smooth'}));
 next.addEventListener('click',advance);
 const observer=new MutationObserver(refresh);
 for(const id of ['questinfo','questlist','log']){
   const element=document.getElementById(id);
   if(element)observer.observe(element,{childList:true,characterData:true,subtree:true});
 }
 document.querySelector('.bf-navbar')?.addEventListener('click',refresh);
 // Core combat HP and turn state update in JS/canvas without guaranteed DOM changes.
 // Poll only this tiny read-only status snapshot; never step the core simulation.
 window.setInterval(()=>{if(!document.hidden)refresh();},850);
 refresh();
 window.BFGlobalStoryBattleV2000=Object.freeze({snapshot,refresh,advance});
})();
