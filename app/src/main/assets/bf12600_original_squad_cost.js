/* BF_GLOBAL_ORIGINAL_PLAYABLE_SQUAD_COST_V12600 */
(() => {
  'use strict';
  // Source: owner's SHA256-verified 2022 F_UNIT_MST_1/2_Ver1084.json.
  // Source unitCost is NOT the unknown current summoner capacity formula.
  const leaders=window.BFGlobalPlayableLeadersV11200;
  if(window.BFGlobalOriginalSquadCostV12600||!leaders||
     leaders.source?.forms!==72||typeof leaders.lookup!=='function'||
     typeof P==='undefined'||P.version!==7||!Array.isArray(P.squad)||
     !Array.isArray(P.roster)||typeof effectiveUnit!=='function') return;
  const host=document.getElementById('bf11200-playable-leaders')||
    document.getElementById('squadpicker');
  if(!host) return;
  const offsets=Object.freeze([11,12,13,14,15,21,22,23,24,25,41,42]);
  // All six original element families share this 2022 source-verified cost vector.
  const costs=Object.freeze([2,4,8,10,20,3,5,9,14,25,4,6]);
  const freeze=Object.freeze,byId=new Map();
  for(let e=1;e<=6;e++)for(let i=0;i<offsets.length;i++){
    const unitId=e*10000+offsets[i],rarity=i<5?i+2:i<10?i-3:i-8;
    const leader=leaders.lookup(unitId);
    if(!leader||leader.unitId!==unitId||leader.rarity!==rarity||
       !Number.isSafeInteger(costs[i])||costs[i]<=0)return;
    byId.set(unitId,freeze({unitId,cost:costs[i],rarity,
      original2022:true,displayOnly:true}));
  }
  if(byId.size!==72||byId.get(10011)?.cost!==2||
     byId.get(10025)?.cost!==25||byId.get(60042)?.cost!==6) return;
  const provenance=freeze({
    source:'2022 Global F_UNIT_MST_1/2_Ver1084.json:unitCost/rarity',
    archiveSha256:'69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9',
    canonicalSHA256:'ad903ea6923fd71bfd14f50d6bfa566f2391e37a317a053c5236995118a12247',playableForms:72,
    capacityEnforced:false,battleStatsChanged:false,savedFieldsAdded:0
  });
  function lookup(unitId){return Number.isSafeInteger(unitId)?byId.get(unitId)||null:null;}
  function snapshot(){
    const rows=[],unsupported=[];
    let total=0;
    for(let i=0;i<Math.min(6,P.squad.length);i++){
      const baseId=P.squad[i];
      if(!Number.isSafeInteger(baseId)||!P.roster.includes(baseId))continue;
      const unit=effectiveUnit(baseId);
      const unitId=unit?.id;
      const original=lookup(unitId);
      if(!original){unsupported.push(freeze({slot:i+1,baseId,unitId:unitId??null}));continue;}
      total+=original.cost;
      rows.push(freeze({slot:i+1,baseId,unitId,
        rarity:original.rarity,cost:original.cost}));
    }
    return freeze({originalSquadCost:total,count:rows.length,
      complete:unsupported.length===0,rows:freeze(rows),
      unsupported:freeze(unsupported),capacityKnown:false,
      originalCapacityLimit:null,savedFieldsAdded:0});
  }
  const panel=document.createElement('details');
  panel.id='bf12600-original-squad-cost';
  panel.style.cssText='margin:8px 4px;padding:10px;border:1px solid #9fbaad;'+
    'border-radius:7px;background:#243c39;color:#edf8f2;font:12px/1.5 system-ui,sans-serif';
  const heading=document.createElement('summary');
  heading.style.cssText='cursor:pointer;min-height:36px;font-weight:800';
  const list=document.createElement('ol');list.id='bf12600-squad-cost-rows';
  const note=document.createElement('small');
  note.textContent='Exact original 2022 unit costs for playable forms. Read-only reference: '+
    'original summoner-level cost limit, roster restrictions and enforcement are '+
    'not reconstructed. No changes to battle, units, EXP, summons or saves.';
  panel.append(heading,list,note);host.after(panel);
  // Home-first original-source cost preview beside the existing six-unit
  // portrait grid. No new navigation, cap enforcement or persistent state.
  // This is loaded by the existing v126 native optional module injection.
  const homeParty=document.querySelector('#bf-home .bf-scene-squad #bf-scene-party');
  const homeCost=homeParty?document.createElement('p'):null;
  if(homeCost){
    homeCost.id='bf12600-home-squad-cost';
    homeCost.setAttribute('role','status');
    homeCost.setAttribute('aria-live','polite');
    homeCost.style.cssText='box-sizing:border-box;max-width:100%;min-width:0;'+
      'margin:7px 0;padding:8px 10px;background:#22374a;'+
      'border:1px solid #ab8e5c;color:#f4e6c6;'+
      'font:700 11px/1.5 system-ui,sans-serif;overflow-wrap:anywhere';
    homeParty.before(homeCost);
  }
  function refresh(){
    const state=snapshot();
    heading.textContent='ORIGINAL 2022 SQUAD COST · '+
      (state.complete?state.originalSquadCost+' ('+state.count+' units)':'INCOMPLETE SOURCE COVERAGE');
    list.replaceChildren();
    for(const row of state.rows){
      const entry=document.createElement('li');
      entry.textContent='Slot '+row.slot+' · #'+row.unitId+' · '+
        row.rarity+'★ · original cost '+row.cost;
      list.append(entry);
    }
    for(const row of state.unsupported){
      const entry=document.createElement('li');
      entry.textContent='Slot '+row.slot+' · #'+row.unitId+' · cost unknown (excluded)';
      list.append(entry);
    }
    if(homeCost){
      homeCost.textContent=!state.complete?
        'ORIGINAL 2022 SQUAD COST · SOURCE INCOMPLETE · '+
          state.unsupported.length+' unverified unit(s) · capacity unknown':
        state.count===0?
          'ORIGINAL 2022 SQUAD COST · NO OWNED UNITS SELECTED · capacity unknown':
          'ORIGINAL 2022 SQUAD COST · '+state.originalSquadCost+
          ' ('+state.count+' verified units) · capacity unknown';
    }
    return state;
  }
  // Read-only updates on squad/evolution interactions, no game render wrappers.
  document.addEventListener('change',refresh);
  document.addEventListener('click',event=>{
    if(event.target?.closest?.('[data-bf-goto="units"],#squadpicker,.squadsetup,.evo-panel'))
      setTimeout(refresh,0);
  });
  panel.addEventListener('toggle',refresh);
  window.addEventListener('bf-route-change',refresh);
  refresh();
  window.BFGlobalOriginalSquadCostV12600=freeze({provenance,lookup,snapshot,refresh});
})();
