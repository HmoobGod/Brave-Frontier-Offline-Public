/* BF_GLOBAL_ITEM_TURN_RESERVATIONS_V4500 */
(() => {
 'use strict';
 // DEMO-only guard-cost consistency, not original native item turn semantics.
 if(window.BFGlobalItemTurnReservationsV4500 ||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined')return;
 const execute=document.getElementById('execute');
 if(!execute)return;
 let battle=S,round=S.round;
 const ledger=new Map();
 function sync(){
   if(S!==battle||S.round!==round){
     battle=S;round=S.round;ledger.clear();
   }
 }
 function free(slot){
   sync();
   const p=S.party?.[slot];
   return Number.isInteger(slot)&&slot>=0&&slot<6&&
     !!p&&p.active&&p.hp>0&&!ledger.has(slot)&&
     (!window.BFGlobalOriginalAilmentStateV5700||
      !window.BFGlobalOriginalAilmentStateV5700.codesFor(slot).includes(6));
 }
 function reserve(slot,kind){
   sync();
   if(!['demo-potion','party-heal-demo','atk-item-demo','bb-fill-demo','full-revive-demo','revived-recipient-demo','def-item-demo','party-atk-demo','double-atk-demo','double-def-demo','party-def-demo','hope-light-demo','strong-life-demo','life-potion-demo','status-remedy-demo','original-potion-demo','strong-potion-demo','saint-light-demo','nullifier-demo','party-regen-demo'].includes(kind)||
      S.mode!=='archive'||S.busy||S.over||S.auto||!free(slot))return false;
   ledger.set(slot,kind);
   return true;
 }
 function enforce(){
   sync();
   if(S.mode!=='archive'||S.over)return;
   for(const slot of ledger.keys()){
     const p=S.party?.[slot];
     if(p?.active&&p.hp>0)p.action={kind:'guard',target:S.target};
   }
 }
 function snapshot(){
   sync();
   return Object.freeze({mode:S.mode,round:S.round,
     reservations:Object.freeze(Array.from(ledger,([slot,kind])=>
       Object.freeze({slot,kind})))});
 }
 execute.addEventListener('click',enforce,true);
 window.BFGlobalItemTurnReservationsV4500=Object.freeze({
   free,reserve,enforce,snapshot
 });
})();
