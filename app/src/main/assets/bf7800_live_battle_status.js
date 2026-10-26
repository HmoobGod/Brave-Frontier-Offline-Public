/* BF_GLOBAL_LIVE_BATTLE_STATUS_V7800 */
(() => {
 'use strict';
 // An accessible, read-only indicator for ACTUAL live battle status.
 // Source status identities are archived; timed effects/round boundaries
 // belong to the existing, explicitly labelled DEMO combat implementation.
 const ailments=window.BFGlobalOriginalAilmentStateV5700;
 const nullifier=window.BFGlobalStatusNegationV7600;
 const regeneration=window.BFGlobalOriginalPartyRegenV7700;
 if(window.BFGlobalLiveBattleStatusV7800||!ailments||!nullifier||!regeneration||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined')return;
 const battle=document.getElementById('battle');
 // #battle is a CANVAS, not a DOM container: children placed inside it
 // are fallback content and never render on supported Android/Chromium.
 // Use the existing visible quest/battle tracker for this tiny readout.
 const host=document.getElementById('bf2000-run')||
   battle?.closest('.arena')?.parentElement;
 const mode=document.getElementById('mode');
 if(!battle||!host||!mode)return;
 const descriptions=Object.freeze({
   1:'Poison · DEMO HP loss each tick',
   2:'Weakness · DEF -50%',
   3:'Sickness · REC -50%',
   4:'Injury · ATK -50%',
   5:'Curse · BB blocked',
   6:'Paralysis · cannot act'
 });
 const css=document.createElement('style');css.id='bf7800-style';
 css.textContent='#bf7800-status{margin:9px 11px;padding:8px;border:1px solid #978fba;border-radius:6px;background:#273347;color:#f5f4fc;font:12px/1.45 system-ui,sans-serif}'+
  '#bf7800-status[hidden]{display:none!important}#bf7800-status summary{cursor:pointer;min-height:34px;font-weight:800}'+
  '#bf7800-status .bf7800-row{border-top:1px solid #586178;padding:6px 0}'+
  '#bf7800-status .bf7800-unit{display:block;font-weight:750;margin:0 0 3px}'+
  '#bf7800-status .bf7800-chip{display:inline-block;margin:2px 5px 2px 0;padding:3px 6px;border:1px solid #929abb;border-radius:4px;background:#44465e;color:#fff}'+
  '#bf7800-status .bf7800-protection{border-color:#7cc2a5;background:#254f4c}'+
  '#bf7800-status small{display:block;color:#e5daec;font-size:11px;margin-top:6px}';
 document.head.append(css);
 const panel=document.createElement('details');panel.id='bf7800-status';
 panel.setAttribute('aria-label','Live ally battle statuses and supported protection');
 const heading=document.createElement('summary');heading.id='bf7800-heading';
 const rows=document.createElement('div');rows.id='bf7800-rows';
 const foot=document.createElement('small');
 foot.textContent='Archived 2022 ailments, plus source-described status immunity and recovery. Combat effects, stacking and remaining-round timing are DEMO until native rules are recovered.';
 panel.append(heading,rows,foot);
 host.prepend(panel);
 const freeze=a=>Object.freeze(a);
 function snapshot(){
   // Only current in-battle ally identities; KO or replacements cannot inherit
   // stale protections or statuses from a previous unit object.
   const immuneState=nullifier.snapshot();
   const regenState=regeneration.snapshot();
   const active=S.mode==='archive'&&!S.over;
   const immunityTurns=immuneState.expiresAfterRound===null?null:
     Math.max(0,immuneState.expiresAfterRound-S.round+1);
   const regenTurns=regenState.untilRound===null?null:
     Math.max(0,regenState.untilRound-S.round+1);
   const entries=[];
   if(active)for(let slot=0;slot<6;slot++){
     const unit=S.party?.[slot];
     if(!unit?.active||unit.hp<=0)continue;
     const codes=ailments.codesFor(slot);
     const immune=immuneState.protectedSlots.includes(slot);
     const regen=regenState.active&&regenState.targetSlots.includes(slot);
     if(!codes.length&&!immune&&!regen)continue;
     entries.push(freeze({
       slot,name:String(unit.name||'Ally '+(slot+1)),
       codes:freeze(Array.from(codes)),immune,regeneration:regen,
       immunityTurns:immune?immunityTurns:null,
       regenerationTurns:regen?regenTurns:null,
       actionBlocked:codes.includes(6),
       bbBlocked:codes.includes(5)||codes.includes(6)
     }));
   }
   return freeze({mode:S.mode,round:S.round,visible:active&&entries.length>0,
     units:freeze(entries),source:'2022 Global item master and already-loaded battle states',
     timing:'Current simulated battle rounds; not original native status lifetime'});
 }
 let last='';
 function refresh(){
   const st=snapshot();
   panel.hidden=!st.visible;
   const signature=JSON.stringify(st.units);
   if(signature===last)return st;
   last=signature;
   heading.textContent='BATTLE STATUS · '+st.units.length+
     (st.units.length===1?' AFFECTED ALLY':' AFFECTED ALLIES');
   const nodes=st.units.map(unit=>{
     const row=document.createElement('div');row.className='bf7800-row';
     row.dataset.slot=String(unit.slot);
     const title=document.createElement('strong');title.className='bf7800-unit';
     title.textContent=(unit.slot+1)+'. '+unit.name;
     row.append(title);
     function chip(label,protection=false){
       const span=document.createElement('span');
       span.className='bf7800-chip'+(protection?' bf7800-protection':'');
       span.textContent=label;row.append(span);
     }
     for(const code of unit.codes)
       chip(descriptions[code]||ailments.labels[code]||'Status '+code);
     if(unit.immune)chip('Nullifier · '+unit.immunityTurns+
       ' DEMO round'+(unit.immunityTurns===1?'':'s')+' left',true);
     if(unit.regeneration)chip('Regeneration · '+unit.regenerationTurns+
       ' DEMO round'+(unit.regenerationTurns===1?'':'s')+' left',true);
     return row;
   });
   rows.replaceChildren(...nodes);
   return st;
 }
 mode.addEventListener('change',refresh);
 document.getElementById('reset')?.addEventListener('click',refresh);
 window.setInterval(()=>{if(!document.hidden)refresh()},550);
 window.BFGlobalLiveBattleStatusV7800=freeze({snapshot,refresh});
 refresh();
})();