/* BF_GLOBAL_ORIGINAL_STATUS_NULLIFIER_V7600 */
(() => {
 'use strict';
 // #20250 status-ailment immunity for three player turns (2022 source + 
 // historical item documentation). Item charge, Guard cost, expiration 
 // boundary and effect application UI are DEMO approximations.
 const registry=window.BFGlobalOriginalAilmentStateV5700;
 const turns=window.BFGlobalItemTurnReservationsV4500;
 if(window.BFGlobalStatusNegationV7600||!registry||!turns||
    !window.BFGlobalOriginalSaintLightV7500||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof enemyPhase!=='function'||typeof update!=='function'||typeof msg!=='function')return;
 const source=Object.freeze({
   archive:'mst-decoded.zip',table:'3-mst-translated/F_ITEM_MST_Ver1027.json',
   tableSha256:'0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474',
   itemId:20250,name:'抗疫薬',targetType:1,itemTargetArea:2,
   battleEffectGroupId:530,skillTypeId:17,
   passiveSkillInfo:'100,100,100,100,100,100,3,0',
   probabilities:Object.freeze([100,100,100,100,100,100]),
   affectedCodes:Object.freeze([1,2,3,4,5,6]),duration:3,
   itemMaxStack:99,itemMaxEquipped:3,
   historicalReference:'https://forum.gamer.com.tw/Co.php?bsn=24641&sn=125267',
   note:'Source and historical documentation support 3-turn party status negation. DEMO duration endpoint and action timing.'
 });
 const parent=document.getElementById('bf4200-items');
 const mode=document.getElementById('mode');
 if(!parent||!mode)return;
 const css=document.createElement('style');css.id='bf7600-style';
 css.textContent='#bf7600-nullifier{padding:9px;margin:9px 0;border:1px solid #93c5aa;border-radius:6px;background:#1c3839;color:#fff}'+
  '#bf7600-nullifier[hidden]{display:none!important}#bf7600-nullifier summary{cursor:pointer;min-height:36px;font-weight:750}'+
  '#bf7600-nullifier select,#bf7600-nullifier button{width:100%;min-height:44px;box-sizing:border-box;border-radius:5px;border:1px solid #a3d1b3;background:#234b46;color:white;padding:6px;margin:4px 0}'+
  '#bf7600-nullifier button:disabled{opacity:.5}';
 document.head.append(css);
 const panel=document.createElement('details');panel.id='bf7600-nullifier';
 const title=document.createElement('summary');title.textContent='ORIGINAL NULLIFIER · 3-TURN PARTY STATUS IMMUNITY';
 const state=document.createElement('strong');state.id='bf7600-status';
 const actor=document.createElement('select');actor.id='bf7600-actor';
 actor.setAttribute('aria-label','Choose acting unit for Nullifier');
 const use=document.createElement('button');use.type='button';use.id='bf7600-use';
 use.textContent='PREVENT ALL SIX STATUS AILMENTS · DEMO GUARD';
 const note=document.createElement('small');
 note.textContent='2022 source item #20250 covers all six ailments for three turns. This PREVENTS new statuses and DOES NOT cure existing ones. One temporary DEMO charge, Guard action, and phase expiration are not recovered native item timing.';
 panel.append(title,state,actor,use,note);parent.append(panel);
 const previousEnemy=window.enemyPhase;
 let battle=S,remaining=1,castRound=null,lastRound=null,last='';
 const protectedAllies=new Map();
 function sync(){
   if(S!==battle){battle=S;remaining=1;castRound=null;lastRound=null;
     protectedAllies.clear();last='';}
   for(const [slot,unit] of protectedAllies){
     const current=S.party?.[slot];
     if(current!==unit||!current?.active||current.hp<=0){
       protectedAllies.delete(slot);last='';
     }
   }
 }
 function actorEligible(i){
   const p=S.party?.[i];
   return Number.isInteger(i)&&i>=0&&i<6&&!!p&&p.active&&p.hp>0&&
     !p.action&&turns.free(i);
 }
 function protectedNow(){
   sync();
   return S.mode==='archive'&&!S.over&&castRound!==null&&
     Number.isInteger(S.round)&&S.round>=castRound&&S.round<castRound+source.duration;
 }
 function immune(slot,code){
   if(!Number.isInteger(code)||code<1||code>6||
      !Number.isInteger(slot)||slot<0||slot>=6||!protectedNow())return false;
   return protectedAllies.get(slot)===S.party?.[slot]&&
     S.party[slot]?.active&&S.party[slot]?.hp>0;
 }
 function snapshot(){
   sync();
   const actors=Object.freeze(Array.from({length:6},(_,i)=>i).filter(actorEligible));
   const blocked=Object.freeze(Array.from(protectedAllies.keys()).filter(i=>immune(i,1)).sort((a,b)=>a-b));
   return Object.freeze({source,mode:S.mode,round:S.round,remaining,castRound,
      protectedSlots:blocked,active:blocked.length>0,
      expiresAfterRound:castRound===null?null:castRound+source.duration-1,
      actors,available:S.mode==='archive'&&!S.busy&&!S.over&&!S.auto&&remaining>0&&actors.length>0});
 }
 function refresh(){
   const st=snapshot();
   panel.hidden=S.mode!=='archive';
   const key=JSON.stringify({mode:S.mode,round:S.round,busy:S.busy,over:S.over,auto:S.auto,
      remaining,protected:st.protectedSlots,castRound,
      party:S.party?.map(p=>p&&[p.active,p.hp,p.action?.kind||null]),
      locks:turns.snapshot().reservations});
   if(key===last)return st;last=key;
   const old=actor.value;
   actor.replaceChildren(...st.actors.map(i=>{
     const opt=document.createElement('option');opt.value=String(i);
     opt.textContent=(i+1)+'. '+S.party[i].name;return opt;
   }));
   if(st.actors.some(i=>String(i)===old))actor.value=old;
   state.textContent='Temporary Nullifier charges '+remaining+'/1 · '+
     (st.active?'Protected '+st.protectedSlots.length+' living allies through round '+st.expiresAfterRound:
     'No active protection');
   use.disabled=!st.available||!actorEligible(Number(actor.value));
   actor.disabled=use.disabled;
   return st;
 }
 function useNullifier(actorId){
   sync();
   if(S.mode!=='archive'||S.busy||S.over||S.auto||remaining!==1||
      !actorEligible(actorId))return false;
   if(!turns.reserve(actorId,'nullifier-demo'))return false;
   protectedAllies.clear();
   for(let slot=0;slot<6;slot++){
     const p=S.party?.[slot];
     if(p?.active&&p.hp>0)protectedAllies.set(slot,p);
   }
   castRound=S.round;lastRound=null;remaining=0;
   const caster=S.party[actorId];
   caster.action={kind:'guard',target:S.target};
   msg('2022 Nullifier #20250 prevents new ailments on '+
     protectedAllies.size+' living allies for 3 DEMO turns; '+caster.name+' Guards.');
   update();last='';refresh();return true;
 }
 function expireAfterTurn(round=S.round){
   sync();
   if(S.mode!=='archive'||S.over||castRound===null||
      round!==S.round||lastRound===round)return Object.freeze([]);
   lastRound=round;
   if(round<castRound+source.duration-1)return Object.freeze([]);
   const removed=Array.from(protectedAllies.keys()).sort((a,b)=>a-b);
   protectedAllies.clear();castRound=null;last='';refresh();
   return Object.freeze(removed);
 }
 window.enemyPhase=async function(...args){
   const activeBattle=S,round=S.round;
   const result=await previousEnemy.apply(this,args);
   if(S===activeBattle&&S.round===round&&!S.over)expireAfterTurn(round);
   return result;
 };
 use.addEventListener('click',()=>useNullifier(Number(actor.value)));
 mode.addEventListener('change',()=>{last='';refresh();});
 document.getElementById('reset')?.addEventListener('click',()=>{last='';refresh();});
 window.setInterval(()=>{if(!document.hidden)refresh()},850);
 window.BFGlobalStatusNegationV7600=Object.freeze({
   source,snapshot,immune,refresh,useNullifier,expireAfterTurn
 });
 refresh();
})();
