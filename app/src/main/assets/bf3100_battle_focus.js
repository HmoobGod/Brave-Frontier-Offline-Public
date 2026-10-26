/* BF_GLOBAL_PLAYABLE_FOCUS_ACTIONS_V3100 */
(() => {
 'use strict';
 const commands=window.BFGlobalBattleCommandsV2100;
 if(window.BFGlobalBattleFocusV3100||!commands||!window.BFGlobalBattleResultsV3000||
    typeof S==='undefined'||typeof P==='undefined'||P.version!==7)return;
 const host=document.getElementById('bf2100-tray');
 if(!host)return;
 const css=document.createElement('style');css.id='bf3100-style';
 css.textContent='#bf3100-focus{margin-top:12px;padding:10px 0;border-top:1px solid #a48d6b;color:#fff;font:12px/1.5 system-ui,sans-serif}'+
 '#bf3100-options{display:grid;grid-template-columns:repeat(auto-fit,minmax(105px,1fr));gap:7px}'+
 '#bf3100-focus button{background:#35516b;color:white;border:1px solid #a9916b;border-radius:5px;min-height:42px;padding:7px;font-weight:bold}'+
 '#bf3100-focus button:disabled{opacity:.4}#bf3100-status{margin:9px 0;color:#d9e3eb}';
 document.head.append(css);
 const panel=document.createElement('section');panel.id='bf3100-focus';
 const title=document.createElement('h3');title.textContent='TACTICAL FOCUS · DEMO';
 const options=document.createElement('div');options.id='bf3100-options';
 const state=document.createElement('p');state.id='bf3100-status';
 const foot=document.createElement('small');
 foot.textContent='Targets use visible DEMO enemy stats. Queuing replaces earlier squad orders; Execute is manual. This is optional and not recovered original AI.';
 panel.append(title,options,state,foot);host.append(panel);
 const strategies=[
  ['lowest-hp','LOWEST HP'],['highest-atk','HIGHEST ATK'],['lowest-def','LOWEST DEF']
 ];
 let selected='lowest-hp',signature='';
 const legal=()=>!S.busy&&!S.over&&!S.auto&&!!commands.snapshot()?.canQueue;
 function lookup(kind){
   if(!strategies.some(x=>x[0]===kind)||!Array.isArray(S.enemies))return null;
   const key=kind==='highest-atk'?'atk':kind==='lowest-def'?'def':'hp';
   const foes=S.enemies.filter(e=>e&&e.hp>0&&Number.isInteger(e.slot)&&Number.isFinite(e[key]));
   foes.sort((a,b)=>{
     const diff=kind==='highest-atk'?b[key]-a[key]:a[key]-b[key];
     return diff||a.slot-b.slot;
   });
   const f=foes[0];return f?Object.freeze({slot:f.slot,name:f.name,hp:f.hp,atk:f.atk,def:f.def}):null;
 }
 function snapshot(){return Object.freeze({strategy:selected,target:lookup(selected),canQueue:legal()});}
 function refresh(){
   const s=snapshot(),key=JSON.stringify(s);
   if(key===signature)return s;signature=key;
   for(const b of options.querySelectorAll('button'))b.disabled=!s.canQueue;
   state.textContent=s.target?'Focus '+s.target.name+' · '+s.strategy.replaceAll('-',' ')+' · '+s.target.hp+' HP':'No eligible target';
   return s;
 }
 function focus(kind){
   if(!legal())return false;const target=lookup(kind);
   if(!target||!commands.setTarget(target.slot))return false;
   selected=kind;signature='';refresh();return true;
 }
 function queueFocus(kind,action='attack'){
   if(action!=='attack'&&action!=='burst')return false;
   if(!focus(kind)||!commands.queueAll(action))return false;
   const target=lookup(kind),live=S.party.filter(p=>p.active&&p.hp>0);
   signature='';refresh();
   return !!target&&live.length>0&&live.every(p=>p.action?.target===target.slot);
 }
 for(const [kind,label] of strategies){
   const b=document.createElement('button');b.type='button';b.textContent=label+' + ATTACK';
   b.addEventListener('click',()=>queueFocus(kind));options.append(b);
 }
 const bursts=document.createElement('button');bursts.type='button';
 bursts.textContent='FOCUS + BB IF READY';bursts.id='bf3100-burst';
 bursts.addEventListener('click',()=>queueFocus(selected,'burst'));options.append(bursts);
 new MutationObserver(refresh).observe(document.getElementById('meta')||host,{childList:true,characterData:true,subtree:true});
 window.setInterval(()=>{if(!document.hidden)refresh()},900);
 refresh();
 window.BFGlobalBattleFocusV3100=Object.freeze({lookup,snapshot,refresh,focus,queueFocus});
})();
