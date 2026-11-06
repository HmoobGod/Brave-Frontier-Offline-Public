/* BF_GLOBAL_OPTIONAL_AUTO_SBB_DEMO */
(() => {
 'use strict';
 const prior=window.BF041SmartAuto,prototype=window.BF044SBBDemo;
 const host=document.getElementById('bf044-sbb-controls');
 if(window.BFGlobalAutoSBBDemo||!host||typeof prior?.kindFor!=='function'||
    typeof prototype?.enabled!=='function'||typeof prototype?.sourceFor!=='function'||
    typeof bfOriginalBB!=='function'||typeof P==='undefined'||P.version!==7||
    typeof S==='undefined')return;
 // The source preview sits in the action-button grid; give its controls a full row.
 host.closest('#bf043-sbb-preview')?.style.setProperty('grid-column','1 / -1');
 const label=document.createElement('label');
 const toggle=document.createElement('input');
 toggle.type='checkbox';toggle.id='bf-auto-sbb-enable';toggle.checked=false;
 label.append(toggle,document.createTextNode(' Allow experimental SBB in Auto Battle (DEMO)'));
 const note=document.createElement('small');
 note.textContent='Off by default; not saved. Also requires experimental SBB combat. '+
   'Applies to future Auto plans; preserves support and conserve choices. '+
   'Uses the existing 100% DEMO gauge and simulated damage, not native SBB charging or effects.';
 host.append(label,note);
 const enabled=()=>toggle.checked===true;
 function kindFor(unit){
  const previous=prior.kindFor.call(this,unit);
  if(previous!=='burst'||!enabled()||!prototype.enabled()||S.mode!=='archive'||
     S.auto!==true||S.over||!Number.isSafeInteger(unit?.id)||unit.id<0||unit.id>=6||
     S.party?.[unit.id]!==unit||unit.active!==true||!(unit.hp>0)||
     !Number.isSafeInteger(unit.unitId)||!Number.isFinite(unit.bb)||unit.bb<100||
     window.BFGlobalCurseBBLockV5900?.cursed(unit.id)||
     window.BFGlobalParalysisActionLockV6000?.paralyzed(unit.id))return previous;
  const bb=bfOriginalBB(unit.unitId),sbb=prototype.sourceFor(unit.unitId);
  // Upgrade offensive choices only; never replace a heal or party buff.
  if(!['single_enemy','all_enemies'].includes(bb?.target)||sbb?.target!=='all_enemies')return previous;
  return 'sbb_demo';
 }
 window.BF041SmartAuto=Object.freeze({...prior,kindFor});
 window.BFGlobalAutoSBBDemo=Object.freeze({enabled,kindFor});
})();
