/* BF_GLOBAL_ARCHIVE_DRAFT_V800 */
(() => {
 'use strict';
 if(window.BFArchiveDraftV800 || !window.BFTacticalRoundsV300 ||
    !window.BFGlobalUnitArchive || !window.BFArchiveTrialsV200 ||
    typeof P==='undefined'||P?.version!==7 ||
    typeof QUESTS==='undefined'||QUESTS.length!==106 ||
    typeof questUnlocked!=='function')return;
 const anchor=document.getElementById('bf400-dossier'),
    data=document.getElementById('bf-global-unit-catalog-data');
 if(!anchor||!data||BFGlobalUnitArchive.count!==2291)return;
 let parsed;
 try{parsed=JSON.parse(data.textContent);}catch(_){return;}
 if(parsed.schema!=='bf-global-unit-archive-2022-v1'||
    !Array.isArray(parsed.units)||parsed.units.length!==2291)return;
 const isCandidate=u=>u?.unitKind===0&&Number.isSafeInteger(u.id)&&u.id>0&&
   typeof u.name==='string'&&u.name.trim()&&
   [u.unitBaseHp,u.unitBaseAtk,u.unitBaseDef,u.unitBaseRec].every(
     v=>Number.isSafeInteger(v)&&v>0);
 const forms=parsed.units.filter(isCandidate),byId=new Map(forms.map(u=>[u.id,u]));
 if(!forms.length||!byId.has(10011)||!byId.has(10012))return;
 const history=window.BFArchiveTrialsV200,trial=window.BFTacticalRoundsV300;
 const ids=[1,2,10,11,20,21,30,31,40,41,42,50,51,52,60,61,70,71,200,202,240];
 const style=document.createElement('style');
 style.id='bf800-draft-styles';
 style.textContent=[
  '#bf800-draft{padding:11px;margin:12px 2px;background:#233046;',
  'border:1px solid #bd9b6d;border-radius:7px;color:#f3e8d2;',
  'font:12px/1.5 system-ui,sans-serif}',
  '#bf800-draft summary{min-height:32px;cursor:pointer;font:bold 15px Georgia,serif}',
  '#bf800-draft input,#bf800-draft select,#bf800-draft button{',
  'box-sizing:border-box;min-height:40px;padding:7px;color:#fff;',
  'background:#2d4b65;border:1px solid #ad9873;border-radius:5px}',
  '#bf800-draft input,#bf800-draft select{width:100%}',
  '.bf800-results{max-height:240px;overflow:auto}',
  '.bf800-entry{display:flex;justify-content:space-between;align-items:center;',
  'gap:8px;padding:6px;border-bottom:1px solid #49637c}',
  '.bf800-entry small,.bf800-entry strong{display:block;overflow-wrap:anywhere}',
  '.bf800-note{color:#ffe0b1}',
  '.bf1100-order{display:flex;align-items:center;gap:4px;margin-left:auto}',
  '.bf1100-order button{min-width:42px;font-size:18px;padding:6px}',
  '.bf1100-slot{font-weight:bold;color:#ecd39c}',
  '#bf800-selected{padding:6px 0}',
  '#bf800-start{width:100%;font-weight:bold}',
  '#bf800-start:disabled{opacity:.45}'
 ].join('');
 document.head.append(style);
 const root=document.createElement('details');root.id='bf800-draft';
 const h=document.createElement('summary');h.textContent='GLOBAL ARCHIVE DRAFT LAB · v8.00';
 const note=document.createElement('p');note.className='bf800-note';
 note.textContent='OPTIONAL OFFLINE EXPERIMENT. Try up to six source-backed 2022 Global standard forms in a temporary simulated trial; archived characters are NOT recruited, summoned, equipped or added to the owned roster. Historical enemies are 2014 references, not verified 2022 battles.';
 const filter=document.createElement('input');filter.type='search';filter.id='bf800-search';
 filter.placeholder='Search archived unit name or ID';
 filter.setAttribute('aria-label','Find source-backed archived units for trial');
 const found=document.createElement('p');found.id='bf800-found';
 const results=document.createElement('div');results.id='bf800-results';results.className='bf800-results';
 const title=document.createElement('strong');title.textContent='TEMPORARY DRAFT · maximum six';
 const selectedView=document.createElement('div');selectedView.id='bf800-selected';
 const sortControls=document.createElement('div');sortControls.id='bf1200-presets';
 sortControls.setAttribute('aria-label','Temporary draft source stat sorting');
 for(const [sort,title] of [['atk','ATK FIRST'],['def','DEF FIRST'],
   ['rec','REC FIRST'],['original','RESTORE ADDED ORDER']]){
   const button=document.createElement('button');button.type='button';
   button.textContent=title;button.dataset.bf1200Sort=sort;
   button.addEventListener('click',()=>sortBy(sort));sortControls.append(button);
 }
 const mission=document.createElement('select');mission.id='bf800-mission';
 mission.setAttribute('aria-label','Choose an unlocked historical trial mission');
 for(const id of ids){
   const row=history.sourceFor(id),opt=document.createElement('option');
   opt.value=String(id);opt.textContent='2014 Mission '+id+' · '+row.name;
   mission.append(opt);
 }
 const start=document.createElement('button');start.id='bf800-start';
 start.type='button';start.textContent='START ARCHIVE-ONLY PRACTICE';
 const info=document.createElement('p');info.id='bf800-status';info.setAttribute('aria-live','polite');
 const foot=document.createElement('p');foot.className='bf800-note';
 foot.textContent='2022 unit base stats, names and optional thumbnails are original source references. ALL action, Burst, HP scaling, opponent and reward rules remain synthetic. Draft resets on exit/reload and never changes actual v7 save.';
 root.append(h,note,filter,found,results,title,selectedView,mission,start,info,foot);
 anchor.after(root);
 let chosen=[];
 let addedOrder=[];
 const value=id=>byId.get(Number(id))||null;
 const selected=()=>chosen.slice();
 const missionId=()=>Number(mission.value);
 const canStart=()=>chosen.length>0&&trial.canStartDraft(chosen,missionId());
 const row=(u,allowRemove)=>{
   const outer=document.createElement('div');outer.className='bf800-entry';
   const txt=document.createElement('div'),name=document.createElement('strong');
   name.textContent=u.name+' · #'+u.id;
   const stats=document.createElement('small');
   stats.textContent=u.rarity+'★ · Base HP '+u.unitBaseHp+' / ATK '+
     u.unitBaseAtk+' / DEF '+u.unitBaseDef+' / REC '+u.unitBaseRec;
   txt.append(name,stats);outer.append(txt);
   if(allowRemove){
     const controls=document.createElement('div');controls.className='bf1100-order';
     const pos=chosen.indexOf(u.id);
     const slot=document.createElement('span');slot.className='bf1100-slot';
     slot.textContent='SLOT '+(pos+1);controls.append(slot);
     const up=document.createElement('button');up.type='button';up.textContent='↑';
     up.setAttribute('aria-label','Move '+u.name+' one slot forward');
     up.disabled=pos===0;
     up.addEventListener('click',()=>move(u.id,-1));
     const down=document.createElement('button');down.type='button';down.textContent='↓';
     down.setAttribute('aria-label','Move '+u.name+' one slot back');
     down.disabled=pos===chosen.length-1;
     down.addEventListener('click',()=>move(u.id,1));
     controls.append(up,down);outer.append(controls);
   }
   const action=document.createElement('button');action.type='button';
   action.textContent=allowRemove?'REMOVE':'ADD';
   action.disabled=!allowRemove&&(chosen.includes(u.id)||chosen.length>=6);
   action.addEventListener('click',()=>allowRemove?remove(u.id):add(u.id));
   outer.append(action);return outer;
 };
 function render(){
   const q=filter.value.trim().toLocaleLowerCase();
   const matches=forms.filter(u=>!q||String(u.id).includes(q)||
     u.name.toLocaleLowerCase().includes(q));
   found.textContent=forms.length+' source-backed standard forms with positive base stats · '+
     matches.length+' matches · showing '+Math.min(12,matches.length);
   results.replaceChildren();
   for(const u of matches.slice(0,12))results.append(row(u,false));
   selectedView.replaceChildren();
   if(chosen.length>1)selectedView.append(sortControls);
   for(const id of chosen){const u=value(id);if(u)selectedView.append(row(u,true));}
   if(!chosen.length)selectedView.textContent='No archived forms selected.';
   start.disabled=!canStart();
   info.textContent=trial.snapshot?.phase==='running'?
     'A separate synthetic trial is already active. Exit it before starting a new draft.':
     chosen.length+' / 6 temporary source forms · ORDER LEFT TO RIGHT = SIMULATED ACTION ORDER · Mission '+missionId()+
     (canStart()?' is available for draft practice.':
       ' must be unlocked and no other training can be active.');
   return matches.length;
 }
 function add(id){
   const u=value(id);if(!u||chosen.includes(u.id)||chosen.length>=6)return false;
   chosen.push(u.id);addedOrder.push(u.id);render();return true;
 }
 function move(id,direction){
   if(!Number.isInteger(id)||![-1,1].includes(direction))return false;
   const index=chosen.indexOf(id),destination=index+direction;
   if(index<0||destination<0||destination>=chosen.length)return false;
   const previous=chosen[index];
   chosen[index]=chosen[destination];chosen[destination]=previous;
   render();return true;
 }
 function moveTo(id,slot){
   if(!Number.isInteger(id)||!Number.isInteger(slot)||
      slot<1||slot>chosen.length)return false;
   const index=chosen.indexOf(id);
   if(index<0)return false;
   if(index===slot-1)return true;
   chosen.splice(index,1);chosen.splice(slot-1,0,id);
   render();return true;
 }
 // v16: atomic, temporary form swap preserving synthetic party slot and
 // original selection order. Only 2022 archive-eligible positive-stat forms.
 function replaceDraft(from,to){
   if(!Number.isInteger(from)||!Number.isInteger(to)||
     from===to||!value(to)||chosen.includes(to)||!chosen.includes(from)||
     trial.snapshot||S?.busy)return false;
   const index=chosen.indexOf(from);
   chosen[index]=to;
   const original=addedOrder.indexOf(from);
   if(original>=0)addedOrder[original]=to;
   else addedOrder.push(to);
   render();return true;
 }
 function remove(id){
   const pos=chosen.indexOf(Number(id));if(pos<0)return false;
   chosen.splice(pos,1);
   addedOrder=addedOrder.filter(x=>x!==Number(id));
   render();return true;
 }
 function sortBy(stat){
   if(!['atk','def','rec','original'].includes(stat)||chosen.length<2)return false;
   if(stat==='original'){
     chosen=addedOrder.filter(id=>chosen.includes(id));
   }else{
     const field={atk:'unitBaseAtk',def:'unitBaseDef',rec:'unitBaseRec'}[stat];
     const before=new Map(chosen.map((id,i)=>[id,i]));
     chosen.sort((a,b)=>(value(b)[field]-value(a)[field])||
       before.get(a)-before.get(b));
   }
   render();return true;
 }
 function clear(){chosen=[];addedOrder=[];render();return true;}
 function startDraft(){
   if(!canStart())return false;
   const ok=trial.startDraft(chosen,missionId());
   if(ok){
     const area=document.getElementById('bf300-tactics');
     area.open=true;area.scrollIntoView?.({behavior:'smooth',block:'start'});
   }
   render();return ok;
 }
 filter.addEventListener('input',render);
 mission.addEventListener('change',render);
 start.addEventListener('click',startDraft);
 document.querySelector('.bf-navbar')?.addEventListener('click',()=>{
   if(root.open)render();
 });
 render();
 window.BFArchiveDraftV800=Object.freeze({
   get eligibleCount(){return forms.length;},
   get archiveCount(){return parsed.units.length;},
   get selected(){return selected();},
   get mission(){return missionId();},
   add,remove,replace:replaceDraft,eligible:id=>!!value(id),
   move,moveTo,sortBy,clear,canStart,start:startDraft,refresh:render
 });
})();
