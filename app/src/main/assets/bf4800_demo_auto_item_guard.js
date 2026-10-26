/* BF_GLOBAL_DEMO_AUTO_ITEM_GUARD_V4800 */
(() => {
 'use strict';
 // DEMO turn safety only: do not let Auto overwrite a paid item action.
 const turns=window.BFGlobalItemTurnReservationsV4500;
 if(window.BFGlobalDemoAutoItemGuardV4800||!turns||
    !window.BFGlobalSourceFullReviveV4700||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined')return;
 const auto=document.getElementById('auto');
 if(!auto)return;
 function snapshot(){
   const state=turns.snapshot();
   return Object.freeze({
     mode:S.mode,round:S.round,
     reservations:state.reservations.length,
     pending:S.mode==='archive'&&state.reservations.length>0,
     auto:!!S.auto
   });
 }
 function protectToggle(event){
   if(!auto.checked)return;
   const info=snapshot();
   if(!info.pending)return;
   // Capture before the native Auto onchange queues/replaces commands.
   event.stopImmediatePropagation();
   event.preventDefault();
   auto.checked=false;
   S.auto=false;
   if(typeof msg==='function'){
     msg('DEMO battle item already reserved a unit action. Finish this round before enabling Auto Battle.');
   }
   if(typeof update==='function')update();
 }
 auto.addEventListener('change',protectToggle,true);
 window.BFGlobalDemoAutoItemGuardV4800=Object.freeze({snapshot,protectToggle});
})();
