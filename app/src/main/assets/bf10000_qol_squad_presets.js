/* BF_GLOBAL_QOL_SQUAD_PRESETS_V10000 */
(() => {
 'use strict';
 // User-triggered loadouts for EXISTING owned base IDs. No new save schema,
 // extra unit slots, unit creation, auto-application or original balance edits.
 if(window.BFGlobalQoLSquadPresetsV10000||typeof P==='undefined'||P.version!==7||
   typeof S==='undefined'||typeof saveProgress!=='function'||
   typeof reset!=='function'||typeof renderProgress!=='function'||
   !Array.isArray(P.squad)||!Array.isArray(P.roster))return;
 const anchor=document.getElementById('squadpicker');
 if(!anchor)return;
 const key='bf_global_offline_qol_squad_presets_v100';
 const freeze=Object.freeze,max=5;
 function goodIds(ids,checkOwnership=true){
   return Array.isArray(ids)&&ids.length>=1&&ids.length<=6&&
     ids.every(id=>Number.isSafeInteger(id)&&id>0&&
       (!checkOwnership||P.roster.includes(id)))&&
     new Set(ids).size===ids.length;
 }
 function normalizeName(v,index){
   const s=String(v??'').trim().replace(/\s+/g,' ').slice(0,28);
   return s||'Squad '+(index+1);
 }
 function load(){
   try{
     const raw=localStorage.getItem(key);
     const data=JSON.parse(raw||'null');
     if(!data||data.version!==1||!Array.isArray(data.slots)||
       data.slots.length!==max)return Array(max).fill(null);
     return data.slots.map((slot,i)=>{
       if(!slot||!goodIds(slot.squad,false))return null;
       return {name:normalizeName(slot.name,i),squad:slot.squad.slice()};
     });
   }catch(_){return Array(max).fill(null);}
 }
 function store(slots){
   try{localStorage.setItem(key,JSON.stringify({version:1,slots}));return true}
   catch(_){return false}
 }
 let slots=load(),message='Preset changes are manual and local to this installation.';
 function info(){
   return freeze(slots.map((slot,index)=>freeze({
     slot:index+1,name:slot?.name||null,ids:freeze(slot?.squad.slice()||[]),
     available:!!slot&&goodIds(slot.squad,true)
   })));
 }
 function savePreset(index,name=''){
   if(!Number.isInteger(index)||index<0||index>=max||
      !goodIds(P.squad,true)||S.busy)return false;
   const next=slots.slice();
   next[index]={name:normalizeName(name,index),squad:P.squad.slice()};
   if(!store(next)){message='Could not store preset; current team unchanged.';refresh();return false;}
   slots=next;message='Saved current owned squad in preset '+(index+1)+'.';
   refresh();return true;
 }
 function deletePreset(index){
   if(!Number.isInteger(index)||index<0||index>=max||!slots[index]||S.busy)return false;
   const next=slots.slice();next[index]=null;
   if(!store(next))return false;
   slots=next;message='Deleted preset '+(index+1)+'; active squad unchanged.';
   refresh();return true;
 }
 function applyPreset(index){
   if(!Number.isInteger(index)||index<0||index>=max||S.busy||
      typeof saveRecoveryPending==='boolean'&&saveRecoveryPending)return false;
   const slot=slots[index];
   if(!slot||!goodIds(slot.squad,true)){
     message='Preset contains an unowned or invalid unit. Nothing changed.';
     refresh();return false;
   }
   const previous=P.squad.slice();
   if(previous.length===slot.squad.length&&
      previous.every((id,i)=>id===slot.squad[i])){
     message='This squad is already active.';refresh();return true;
   }
   P.squad=slot.squad.slice();
   // Apply through the existing save function; roll back if storage blocks it.
   if(!saveProgress()){
     P.squad=previous;
     message='Active save unavailable; squad was not changed.';
     refresh();return false;
   }
   reset();renderProgress();
   message='Applied preset '+(index+1)+'. Original battle restarted as usual.';
   refresh();return true;
 }
 const panel=document.createElement('details');panel.id='bf10000-squad-presets';
 panel.style.cssText='margin:10px 3px;padding:10px;border:1px solid #bd9f73;'+
   'border-radius:7px;background:#2e302d;color:#fff0d9;font:12px/1.5 system-ui,sans-serif';
 const heading=document.createElement('summary');heading.textContent='QoL · SAVED SQUAD PRESETS';
 heading.style.cssText='cursor:pointer;min-height:38px;font-weight:800';
 const explanation=document.createElement('p');
 explanation.textContent='Store up to five current squad loadouts. Applying a preset '+
   'only selects owned units, uses the original save system, and restarts '+
   'the current battle just like manual squad changes. Presets are local.';
 const selected=document.createElement('select');selected.id='bf10000-slot';
 selected.style.cssText='min-height:42px;padding:7px;color:white;background:#334253;'+
   'border:1px solid #bdaa87;border-radius:5px';
 for(let i=0;i<max;i++){
   const opt=document.createElement('option');opt.value=String(i);
   opt.textContent='Preset '+(i+1);selected.append(opt);
 }
 const name=document.createElement('input');name.id='bf10000-name';
 name.type='text';name.maxLength=28;name.placeholder='Preset name';
 name.setAttribute('aria-label','Squad preset name');
 name.style.cssText='min-height:42px;padding:7px;box-sizing:border-box;'+
   'color:#fff;background:#334253;border:1px solid #bdaa87;border-radius:5px';
 const buttons=document.createElement('div');buttons.style.cssText='margin:8px 0;display:flex;flex-wrap:wrap;gap:6px';
 const mk=(id,label,fn)=>{
   const b=document.createElement('button');b.type='button';b.id=id;
   b.textContent=label;b.style.cssText='min-height:42px;padding:8px;'+
     'border:1px solid #cfb88b;background:#574a37;color:#fff;border-radius:5px';
   b.addEventListener('click',fn);buttons.append(b);return b;
 };
 const saveButton=mk('bf10000-save','SAVE CURRENT',()=>savePreset(Number(selected.value),name.value));
 const equipButton=mk('bf10000-apply','APPLY PRESET',()=>applyPreset(Number(selected.value)));
 const removeButton=mk('bf10000-delete','DELETE PRESET',()=>deletePreset(Number(selected.value)));
 const status=document.createElement('p');status.id='bf10000-status';status.setAttribute('role','status');
 const help=document.createElement('small');
 help.textContent='Preset labels do not travel inside exported v7 saves. '+
   'No automatic selection or extra original unit slots.';
 panel.append(heading,explanation,selected,name,buttons,status,help);anchor.after(panel);
 function refresh(){
   const index=Number(selected.value)||0,slot=slots[index];
   const unavailable=!!S.busy;
   saveButton.disabled=unavailable||!goodIds(P.squad,true);
   equipButton.disabled=unavailable||!slot||!goodIds(slot.squad,true);
   removeButton.disabled=unavailable||!slot;
   selected.querySelectorAll('option').forEach((o,i)=>{
     o.textContent='Preset '+(i+1)+(slots[i]?' · '+slots[i].name:' · Empty');
   });
   status.textContent=message+(slot?' · '+slot.squad.length+' units saved.':' · Empty slot.');
   return info();
 }
 selected.addEventListener('change',()=>{
   name.value=slots[Number(selected.value)]?.name||'';
   refresh();
 });
 panel.addEventListener('toggle',()=>{if(panel.open)refresh()});
 setInterval(()=>{if(!document.hidden&&panel.open)refresh()},1400);
 refresh();
 window.BFGlobalQoLSquadPresetsV10000=freeze({
   key,info,savePreset,applyPreset,deletePreset,refresh
 });
})();
