/* BF_GLOBAL_ORIGINAL_PARTY_REGEN_V7700 */
(() => {
 'use strict';
 // 2022 source item #20102: party gradual healing, 800..1000 base,
 // source duration 3. Tick RNG, rounding and phase boundary are DEMO.
 const turns=window.BFGlobalItemTurnReservationsV4500;
 if(window.BFGlobalOriginalPartyRegenV7700||!turns||
    !window.BFGlobalStatusNegationV7600||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined'||
    typeof enemyPhase!=='function'||typeof update!=='function'||typeof msg!=='function')return;
 const source=Object.freeze({
   archive:'mst-decoded.zip',
   table:'3-mst-translated/F_ITEM_MST_Ver1027.json',
   sha256:'0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474',
   itemId:20102,name:'継復光',battleEffectGroupId:520,
   targetType:1,itemTargetArea:2,skillTypeId:3,
   passiveSkillInfo:'800,1000,0,3,0',baseLow:800,baseHigh:1000,duration:3,
   itemMaxStack:99,itemMaxEquipped:3,
   historicalReference:'https://forum.gamer.com.tw/Co.php?bsn=24641&sn=125267',
   interpretation:'Party gradual HP restoration for three turns is original; sampling and per-turn application boundary are DEMO.'
 });
 const parent=document.getElementById('bf4200-items');
 const mode=document.getElementById('mode');
 if(!parent||!mode)return;
 const css=document.createElement('style');css.id='bf7700-style';
 css.textContent='#bf7700-party-regen{margin:9px 0;padding:9px;border:1px solid #89bcb1;border-radius:6px;background:#213a40;color:#f6fffa}'+
  '#bf7700-party-regen[hidden]{display:none!important}#bf7700-party-regen summary{cursor:pointer;font-weight:750;min-height:34px}'+
  '#bf7700-party-regen select,#bf7700-party-regen button{width:100%;min-height:44px;padding:7px;box-sizing:border-box;border:1px solid #9ec5b9;border-radius:5px;background:#244f51;color:white;margin:5px 0}'+
  '#bf7700-party-regen button:disabled{opacity:.5}';
 document.head.append(css);
 const panel=document.createElement('details');panel.id='bf7700-party-regen';
 const title=document.createElement('summary');title.textContent='ORIGINAL REGENERATION LIGHT · 3 TURNS';
 const state=document.createElement('strong');state.id='bf7700-stock';
 const actor=document.createElement('select');actor.id='bf7700-actor';
 actor.setAttribute('aria-label','Choose actor for original party regeneration item');
 const use=document.createElement('button');use.id='bf7700-use';use.type='button';
 use.textContent='APPLY ALL-ALLY REGENERATION · DEMO GUARD';
 const note=document.createElement('small');
 note.textContent='2022 item #20102: all-ally gradual recovery, source 800–1000 for 3 turns. A uniform per-turn DEMO roll and Guard turn are placeholders; native RNG, REC scaling, timings, and item inventory are not recovered.';
 panel.append(title,state,actor,use,note);parent.append(panel);
 const originalEnemy=window.enemyPhase;
 let battle=S,remaining=1,effect=null,last='';
 function sync(){
   if(S!==battle){battle=S;remaining=1;effect=null;last='';}
   // Core battles may skip the enemy phase on a cleared wave yet advance
   // S.round; never retain an expired status across those wave boundaries.
   if(effect&&(!Number.isInteger(S.round)||S.round>effect.untilRound)){
     effect=null;last='';
   }
   if(effect){
     for(const [slot,unit] of effect.targets){
       const p=S.party?.[slot];
       if(p!==unit||!p?.active||p.hp<=0)effect.targets.delete(slot);
     }
   }
 }
 function canAct(i){
   const p=S.party?.[i];
   return Number.isInteger(i)&&i>=0&&i<6&&!!p&&p.active&&p.hp>0&&
     !p.action&&turns.free(i);
 }
 function allowed(){return S.mode==='archive'&&!S.busy&&!S.over&&!S.auto&&remaining===1;}
 function snapshot(){
   sync();
   return Object.freeze({source,mode:S.mode,round:S.round,remaining,
     active:!!effect&&S.mode==='archive'&&!S.over,
     startRound:effect?.startRound??null,
     untilRound:effect?.untilRound??null,
     targetSlots:Object.freeze(effect?Array.from(effect.targets.keys()).sort((a,b)=>a-b):[]),
     eligibleActors:Object.freeze(Array.from({length:6},(_,i)=>i).filter(canAct)),
     available:allowed()&&Array.from({length:6},(_,i)=>i).some(canAct)});
 }
 function refresh(){
   const st=snapshot();panel.hidden=S.mode!=='archive';
   const key=JSON.stringify({mode:S.mode,round:S.round,busy:S.busy,over:S.over,auto:S.auto,
     remaining,active:st.active,targets:st.targetSlots,until:st.untilRound,
     party:S.party?.map(p=>p&&[p.hp,p.active,p.action?.kind||null]),
     locks:turns.snapshot().reservations});
   if(last===key)return st;last=key;
   const keep=actor.value;
   actor.replaceChildren(...st.eligibleActors.map(i=>{
     const opt=document.createElement('option');opt.value=String(i);
     opt.textContent=(i+1)+'. '+S.party[i].name;return opt;
   }));
   if(st.eligibleActors.some(i=>String(i)===keep))actor.value=keep;
   state.textContent='Temporary regeneration charges '+remaining+'/1 · '+
     (st.active?'Active for '+st.targetSlots.length+' living allies through round '+st.untilRound:
      'Inactive');
   use.disabled=!st.available||!canAct(Number(actor.value));
   actor.disabled=use.disabled;
   return st;
 }
 function useRegeneration(actorId){
   sync();
   if(!allowed()||!canAct(actorId))return false;
   if(!turns.reserve(actorId,'party-regen-demo'))return false;
   const targets=new Map();
   for(let slot=0;slot<6;slot++){
     const p=S.party?.[slot];
     if(p?.active&&p.hp>0)targets.set(slot,p);
   }
   effect={startRound:S.round,untilRound:S.round+source.duration-1,
     lastTick:null,targets};
   remaining=0;
   const caster=S.party[actorId];
   caster.action={kind:'guard',target:S.target};
   msg('2022 Regeneration Light #20102 applies 3-round DEMO gradual HP restoration to '+
      targets.size+' allies. '+caster.name+' Guards.');
   update();last='';refresh();return true;
 }
 function processTurn(round=S.round){
   sync();
   if(!effect||S.mode!=='archive'||S.over||
      round!==S.round||effect.lastTick===round||round<effect.startRound||
      round>effect.untilRound)return Object.freeze([]);
   effect.lastTick=round;
   const events=[];
   for(const [slot,p] of effect.targets){
     if(S.party?.[slot]!==p||!p.active||p.hp<=0||
        !Number.isFinite(p.maxHp)||!Number.isFinite(p.hp))continue;
     const base=source.baseLow+
       Math.floor(Math.random()*(source.baseHigh-source.baseLow+1));
     const healed=Math.max(0,Math.min(base,p.maxHp-p.hp));
     if(healed>0){p.hp+=healed;events.push(Object.freeze({slot,round,healed,base}));}
   }
   if(events.length){
     const total=events.reduce((n,e)=>n+e.healed,0);
     msg('REGENERATION · '+events.length+' allies restore '+total+
       ' DEMO HP (2022 base range 800–1000).');
     update();
   }
   if(round>=effect.untilRound){effect=null;last='';}
   refresh();
   return Object.freeze(events);
 }
 window.enemyPhase=async function(...args){
   const battleAtStart=S,round=S.round;
   const result=await originalEnemy.apply(this,args);
   if(S===battleAtStart&&S.round===round&&!S.over)processTurn(round);
   return result;
 };
 use.addEventListener('click',()=>useRegeneration(Number(actor.value)));
 mode.addEventListener('change',()=>{last='';refresh();});
 document.getElementById('reset')?.addEventListener('click',()=>{last='';refresh();});
 window.setInterval(()=>{if(!document.hidden)refresh()},850);
 window.BFGlobalOriginalPartyRegenV7700=Object.freeze({
   source,snapshot,refresh,useRegeneration,processTurn
 });
 refresh();
})();
