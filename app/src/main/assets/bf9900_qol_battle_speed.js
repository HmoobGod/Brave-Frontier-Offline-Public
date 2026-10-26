/* BF_GLOBAL_QOL_BATTLE_SPEED_V9900 */
(() => {
 'use strict';
 // Existing battle code reads Number(E.speed.value), snapshots roundSpeed
 // before Execute, and uses window.wait for presentation timing.
 // Only optional presentation controls are changed here; no game arithmetic.
 const speed=document.getElementById('speed');
 const host=document.getElementById('bf2000-run');
 const nativeWait=window.wait;
 if(window.BFGlobalQoLBattleSpeedV9900||!speed||!host||
   typeof nativeWait!=='function'||typeof P==='undefined'||P.version!==7||
   typeof S==='undefined'||typeof E==='undefined'||E.speed!==speed)return;
 const freeze=Object.freeze;
 const prefSpeed='bf_global_offline_qol_speed_v99';
 const prefSkip='bf_global_offline_qol_skip_animations_v99';
 function get(k){try{return localStorage.getItem(k)}catch(_){return null}}
 function put(k,v){try{localStorage.setItem(k,v);return true}catch(_){return false}}
 const nativeOptions=[...speed.options].map(x=>x.value);
 if(!['1','2','3','5'].every(x=>nativeOptions.includes(x)))return;
 for(const value of [8,12]){
   if(![...speed.options].some(x=>x.value===String(value))){
     const opt=document.createElement('option');
     opt.value=String(value);opt.textContent=value+'× · QoL fast';
     speed.append(opt);
   }
 }
 const allowed=new Set(['1','2','3','5','8','12']);
 const stored=get(prefSpeed);
 if(allowed.has(stored)&&!S.busy)speed.value=stored;
 let skip=get(prefSkip)==='on';
 const nativeSpeed=()=>Number(speed.value)||2;
 function setSpeed(value){
   const s=String(value);
   if(!allowed.has(s))return false;
   speed.value=s;
   if(speed.value!==s)return false;
   put(prefSpeed,s);
   speed.dispatchEvent(new Event('change',{bubbles:true}));
   refresh();return true;
 }
 function setSkip(on){
   if(typeof on!=='boolean'||S.busy)return false;
   if(!put(prefSkip,on?'on':'off'))return false;
   skip=on;refresh();return true;
 }
 window.wait=function(ms){
   if(!skip||S.mode!=='archive'||!Number.isFinite(ms)||ms<=40)
     return nativeWait.apply(this,arguments);
   // Retain an asynchronous wait so existing animation / epoch checks run.
   // This is not a turn-skip, battle-skip or damage simulation shortcut.
   return nativeWait.call(this,40);
 };
 const panel=document.createElement('details');
 panel.id='bf9900-speed';
 panel.style.cssText='margin:10px 2px;padding:10px;border:1px solid #92abc8;'+
   'border-radius:7px;background:#172b44;color:#e7f0ff;font:12px/1.5 system-ui,sans-serif';
 const heading=document.createElement('summary');
 heading.textContent='QoL · BATTLE SPEED & ANIMATION SKIP';
 heading.style.cssText='min-height:36px;cursor:pointer;font-weight:800';
 const caption=document.createElement('p');
 caption.textContent='Extra 8×/12× speeds extend the existing round-speed control. '+
   'Optional animation skip shortens long presentation waits only. '+
   'Combat formulas, player commands and rewards are unchanged.';
 const group=document.createElement('label');
 group.textContent='BATTLE SPEED ';
 const control=document.createElement('select');control.id='bf9900-speed-select';
 control.style.cssText='margin:6px;min-height:42px;color:white;background:#2d4762;'+
   'border:1px solid #9db5d0;border-radius:5px;padding:7px';
 for(const value of [1,2,3,5,8,12]){
   const opt=document.createElement('option');opt.value=String(value);
   opt.textContent=value+'×'+(value>=8?' fast':'');
   control.append(opt);
 }
 group.append(control);
 const label=document.createElement('label');
 label.style.cssText='display:block;margin:9px 0';
 const checkbox=document.createElement('input');checkbox.type='checkbox';
 checkbox.id='bf9900-anim-skip';
 label.append(checkbox,document.createTextNode(' Skip long battle animations (optional)'));
 const note=document.createElement('small');
 note.textContent='Animation skip is OFF until enabled; applies to original-style '+
   'story battles only, and cannot be toggled during a running turn. '+
   'Turn-speed changes take effect on the next turn.';
 const info=document.createElement('p');info.id='bf9900-speed-info';
 panel.append(heading,caption,group,label,note,info);host.after(panel);
 function snapshot(){return freeze({speed:nativeSpeed(),skip,
   originalOptions:freeze(nativeOptions.slice()),extra:freeze([8,12]),
   unchangedSaveSchema:P.version===7});}
 function refresh(){
   control.value=speed.value;
   checkbox.checked=skip;
   checkbox.disabled=!!S.busy;
   info.textContent='Speed '+nativeSpeed()+'× · Long animation skip '+
     (skip?'ON':'OFF')+(S.busy?' · finish this turn to change skip':'');
   return snapshot();
 }
 control.addEventListener('change',()=>setSpeed(control.value));
 checkbox.addEventListener('change',()=>{
   if(!setSkip(checkbox.checked))refresh();
 });
 speed.addEventListener('change',()=>{
   if(allowed.has(speed.value))put(prefSpeed,speed.value);
   refresh();
 });
 setInterval(()=>{if(!document.hidden&&panel.open)refresh();},1100);
 refresh();
 window.BFGlobalQoLBattleSpeedV9900=freeze({snapshot,setSpeed,setSkip,refresh});
})();
