/* BF_GLOBAL_QOL_ROTATING_BACKUPS_V9700 */
(() => {
 'use strict';
 // Optional recovery snapshots ONLY. Never change the active v7 save, P,
 // combat, signing, or the existing save/import recovery code.
 if(window.BFGlobalQoLBackupsV9700||typeof P==='undefined'||P.version!==7)return;
 const liveKey='bf_global_offline_demo_v7';
 const backupKey='bf_global_offline_qol_rotating_backups_v97';
 const enabledKey='bf_global_offline_qol_backups_enabled_v97';
 const limit=3,maxBytes=512*1024;
 const host=document.getElementById('bf101-story-continue')||
   document.getElementById('bf3000-result')||document.getElementById('questlist');
 if(!host)return;
 const freeze=Object.freeze;
 function safeGet(k){try{return localStorage.getItem(k);}catch(_){return null;}}
 function valid(raw){
   if(typeof raw!=='string'||raw.length<2||
      new TextEncoder().encode(raw).length>maxBytes)return false;
   try{
     const v=JSON.parse(raw);
     return !!v&&v.version===7&&Array.isArray(v.roster)&&
       Array.isArray(v.squad)&&v.questClears!==null&&
       typeof v.questClears==='object'&&!Array.isArray(v.questClears);
   }catch(_){return false;}
 }
 function existing(){
   try{
     const value=JSON.parse(safeGet(backupKey)||'null');
     if(!value||value.version!==1||!Array.isArray(value.slots))return [];
     return value.slots.slice(0,limit).filter(x=>
       x&&Number.isSafeInteger(x.time)&&x.time>0&&valid(x.raw));
   }catch(_){return [];}
 }
 let enabled=safeGet(enabledKey)!=='off';
 function listing(){
   return freeze(existing().map((x,i)=>freeze({
     slot:i+1,time:x.time,bytes:new TextEncoder().encode(x.raw).length
   })));
 }
 function capture(){
   if(!enabled)return false;
   const raw=safeGet(liveKey);
   if(!valid(raw))return false;
   const slots=existing();
   if(slots[0]?.raw===raw)return false;
   const next=[{time:Date.now(),raw},...slots].slice(0,limit);
   try{localStorage.setItem(backupKey,JSON.stringify({version:1,slots:next}));}
   catch(_){return false;}
   refresh();return true;
 }
 function download(index=0){
   const x=existing()[index];
   if(!x||!valid(x.raw))return false;
   const filename='BraveFrontier-v7-backup-'+
     new Date(x.time).toISOString().replace(/[:.]/g,'-')+'.json';
   try{
     // Android SAF is deliberately invoked only from an explicit tap.
     if(window.BFAndroid?.exportSaveFile){
       window.BFAndroid.exportSaveFile(x.raw,filename);
     }else{
       const blob=new Blob([x.raw],{type:'application/json'});
       const url=URL.createObjectURL(blob);
       const a=document.createElement('a');
       a.href=url;a.download=filename;document.body.append(a);a.click();a.remove();
       setTimeout(()=>URL.revokeObjectURL(url),2000);
     }
     return true;
   }catch(_){return false;}
 }
 function enable(value){
   const newValue=value===true;
   try{localStorage.setItem(enabledKey,newValue?'on':'off');}
   catch(_){return false;}
   enabled=newValue;
   if(enabled)capture();
   refresh();return true;
 }
 const panel=document.createElement('details');panel.id='bf9700-backups';
 panel.style.cssText='margin:10px 2px;padding:10px;border:1px solid #96ad9c;'+
   'border-radius:7px;background:#172f35;color:#e8f6e9;'+
   'font:12px/1.5 system-ui,sans-serif';
 const heading=document.createElement('summary');
 heading.textContent='QoL · LOCAL SAVE BACKUPS';
 heading.style.cssText='font-weight:800;min-height:34px;cursor:pointer';
 const status=document.createElement('p');status.id='bf9700-status';
 const caution=document.createElement('small');
 caution.textContent='Keeps up to three different valid v7 snapshots on this device. '+
   'Never restores or overwrites progress automatically. '+
   'Download a copy for protection against uninstall or app-data loss.';
 const toggle=document.createElement('label');
 toggle.style.cssText='display:block;margin:9px 0';
 const checkbox=document.createElement('input');
 checkbox.type='checkbox';checkbox.id='bf9700-auto';checkbox.checked=enabled;
 toggle.append(checkbox,document.createTextNode(' Enable automatic local backups'));
 const actions=document.createElement('div');
 actions.style.cssText='display:flex;flex-wrap:wrap;gap:7px;margin:9px 0';
 function button(id,name){
   const b=document.createElement('button');b.type='button';b.id=id;
   b.textContent=name;
   b.style.cssText='min-height:42px;padding:7px 10px;border-radius:5px;'+
     'background:#335768;color:white;border:1px solid #b0cfbf';
   actions.append(b);return b;
 }
 const now=button('bf9700-capture','BACK UP NOW');
 const exportButton=button('bf9700-export','EXPORT A BACKUP');
 const selector=document.createElement('select');selector.id='bf9700-select';
 selector.setAttribute('aria-label','Choose local backup');
 selector.style.cssText='min-height:42px;max-width:100%;background:#193943;'+
   'border:1px solid #b0cfbf;color:#fff;padding:7px;border-radius:5px';
 panel.append(heading,status,caution,toggle,actions,selector);host.after(panel);
 function refresh(){
   const slots=listing();
   checkbox.checked=enabled;
   status.textContent=(enabled?'Automatic backup enabled':'Automatic backup paused')+
     ' · '+slots.length+'/'+limit+' distinct saved snapshots';
   const previous=selector.value;selector.replaceChildren();
   for(const x of slots){
     const option=document.createElement('option');option.value=String(x.slot-1);
     option.textContent=new Date(x.time).toLocaleString()+
       ' · '+Math.ceil(x.bytes/1024)+' KB';
     selector.append(option);
   }
   selector.value=slots.some(x=>String(x.slot-1)===previous)?previous:'0';
   selector.disabled=!slots.length;exportButton.disabled=!slots.length;
   return slots;
 }
 checkbox.addEventListener('change',()=>{if(!enable(checkbox.checked))refresh();});
 now.addEventListener('click',()=>{capture();refresh();});
 exportButton.addEventListener('click',()=>download(Number(selector.value)));
 document.addEventListener('visibilitychange',()=>{
   if(document.hidden)capture();
 });
 const timer=setInterval(()=>{if(!document.hidden)capture();},12000);
 window.addEventListener('pagehide',()=>capture());
 window.addEventListener('beforeunload',()=>clearInterval(timer),{once:true});
 capture();refresh();
 window.BFGlobalQoLBackupsV9700=freeze({
   key:backupKey,liveKey,limit,maxBytes,valid,
   capture,listing,download,enable,refresh,
   get enabled(){return enabled;}
 });
})();
