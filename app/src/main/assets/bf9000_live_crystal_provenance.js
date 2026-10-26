/* BF_GLOBAL_LIVE_CRYSTAL_PROVENANCE_V9000 */
(() => {
 'use strict';
 const normal=window.BFGlobalLiveNormalCrystalEventsV8800;
 const burst=window.BFGlobalLiveSimpleBBCrystalsV8900;
 const source=window.BFGlobalAllNormalCrystalChecksV8400;
 const bbSource=window.BFGlobalAllBBDropChecksV8500;
 if(window.BFGlobalLiveCrystalProvenanceV9000||!normal||!burst||!source||!bbSource||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined')return;
 const host=document.getElementById('bf8900-bb-crystals')?.parentElement;
 if(!host)return;
 const freeze=Object.freeze;
 const panel=document.createElement('details');
 panel.id='bf9000-crystal-provenance';
 panel.style.cssText='margin:9px 4px;padding:9px;border:1px solid #8cb7a7;border-radius:6px;background:#183b41;color:#eafaf6;font:12px/1.5 system-ui,sans-serif';
 const title=document.createElement('summary');
 title.textContent='SOURCE CRYSTAL LEDGER · NORMAL / BB';
 title.style.cssText='cursor:pointer;min-height:35px;font-weight:800';
 const text=document.createElement('p');text.id='bf9000-ledger-totals';
 const detail=document.createElement('ol');detail.id='bf9000-ledger-lines';
 const caution=document.createElement('small');caution.id='bf9000-ledger-caution';
 caution.textContent='Only observed DEMO combat events with 2022 original source-valid profiles. These are generated reference rolls, NOT collected BC/HC. No BB gauge charging, HP healing, native enemy resistance, recipient selection or overkill assumed.';
 panel.append(title,text,detail,caution);host.append(panel);
 function validEvent(e,kind){
   if(!e||e.referenceOnly!==true||e.overkill!==false||
      !Number.isSafeInteger(e.unitId)||!Number.isSafeInteger(e.wave)||e.wave<1||
      !Number.isSafeInteger(e.battleCrystals)||e.battleCrystals<0||
      !Number.isSafeInteger(e.heartCrystals)||e.heartCrystals<0)return false;
   if(kind==='normal'){
     const p=source.lookup(e.unitId);
     return !!p&&e.normalHits===p.normalHits&&e.checksPerHit===p.checksPerHit&&
       e.totalDropChecks===p.totalDropChecks&&
       e.battleCrystals<=p.totalDropChecks&&e.heartCrystals<=p.normalHits;
   }
   const p=bbSource.lookup(e.unitId);
   return !!p&&!!p.simpleDamageEvents&&p.skillId===e.skillId&&
     e.simpleDamageEvents===p.simpleDamageEvents&&e.checksPerTarget===p.checksPerTarget&&
     e.battleCrystals<=p.checksPerTarget&&e.heartCrystals<=p.simpleDamageEvents;
 }
 function snapshot(){
   const n=normal.snapshot(),b=burst.snapshot();
   const eligible=S.mode==='archive'&&!S.over;
   // v88 and v89 each maintain at most 64 in-memory records; totals are the
   // authoritative complete-session counters, whereas recent is a bounded UI.
   const nValid=(n.recent||[]).filter(e=>validEvent(e,'normal'));
   const bValid=(b.recent||[]).filter(e=>validEvent(e,'bb'));
   const all=nValid.map(e=>freeze({kind:'normal',wave:e.wave,unitId:e.unitId,
          battleCrystals:e.battleCrystals,heartCrystals:e.heartCrystals}))
     .concat(bValid.map(e=>freeze({kind:'bb',wave:e.wave,unitId:e.unitId,
          battleCrystals:e.battleCrystals,heartCrystals:e.heartCrystals})));
   const totals=freeze({normalBC:n.battleCrystals,normalHC:n.heartCrystals,
     burstBC:b.battleCrystals,burstHC:b.heartCrystals,
     uncollectedBC:n.battleCrystals+b.battleCrystals,
     uncollectedHC:n.heartCrystals+b.heartCrystals});
   return freeze({mode:S.mode,round:S.round,active:eligible,totals,
     normalEvents:n.observed,burstTargetEvents:b.observed,
     recent:freeze(all),saved:false,collected:false,
     source:'2022 source-valid normal attack checks and simple offensive BB events',
     interpretation:'Uncollected reference rolls only; no HP/BB changes or rewards'});
 }
 function render(){
   const s=snapshot(),t=s.totals;
   panel.hidden=S.mode!=='archive';
   text.textContent='Normal '+s.normalEvents+' events: '+t.normalBC+' BC / '+t.normalHC+
     ' HC · BB '+s.burstTargetEvents+' target events: '+t.burstBC+' BC / '+t.burstHC+
     ' HC · Total uncollected '+t.uncollectedBC+' BC / '+t.uncollectedHC+' HC';
   detail.replaceChildren();
   for(const event of s.recent.slice(-8)){
     const li=document.createElement('li');
     li.textContent='Wave '+event.wave+' · '+event.kind.toUpperCase()+' unit #'+
       event.unitId+': '+event.battleCrystals+' BC / '+event.heartCrystals+' HC';
     detail.append(li);
   }
   return s;
 }
 document.getElementById('reset')?.addEventListener('click',render);
 document.getElementById('mode')?.addEventListener('change',render);
 window.setInterval(()=>{if(!document.hidden)render()},700);
 window.BFGlobalLiveCrystalProvenanceV9000=freeze({snapshot,refresh:render,validEvent});
 render();
})();
