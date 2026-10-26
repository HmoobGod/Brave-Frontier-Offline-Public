/* BF_GLOBAL_QOL_BATTLE_DETAILS_V10300 */
(() => {
 'use strict';
 // Strictly observer-only. The original DEMO battle state S remains authoritative.
 if(window.BFGlobalQoLBattleDetailsV10300||
    typeof P==='undefined'||P.version!==7||
    typeof S==='undefined')return;
 const battle=document.getElementById('bf2000-run');
 if(!battle)return;
 const freeze=Object.freeze;
 function safe(n){return Number.isFinite(n)?Math.max(0,Math.floor(n)):0}
 function readUnit(u,kind){
   if(!u||!Number.isFinite(u.hp))return null;
   const max=Math.max(1,safe(u.maxHp));
   const hp=Math.min(max,safe(u.hp));
   return freeze({name:String(u.name||('Unit #'+(u.unitId||'?'))).slice(0,90),
     kind,unitId:Number.isSafeInteger(u.unitId)?u.unitId:null,
     hp,maxHp:max,hpPercent:Math.round(100*hp/max),
     bb:kind==='ally'?Math.min(100,safe(u.bb)):null,
     active:kind==='ally'?!!u.active&&hp>0:hp>0,
     defending:kind==='ally'?!!u.guard:null});
 }
 function snapshot(){
   const allies=Array.isArray(S.party)?
     S.party.filter(u=>u&&u.active).map(u=>readUnit(u,'ally')).filter(Boolean):[];
   const foes=Array.isArray(S.enemies)?
     S.enemies.map(u=>readUnit(u,'enemy')).filter(Boolean):[];
   const one=window.BFGlobalSingleHitCriticalV9300?.snapshot();
   const multi=window.BFGlobalMultiHitCriticalV9500?.snapshot();
   return freeze({
     mode:String(S.mode||''),wave:safe(S.wave)+1,totalWaves:safe(S.totalWaves),
     round:safe(S.round),busy:!!S.busy,over:!!S.over,
     phase:String(S.phase||''),allies:freeze(allies),foes:freeze(foes),
     sourceScopedCriticalHits:safe(one?.criticals)+safe(multi?.criticalHits),
     nativeFullDamageFormula:false,progressUnchanged:true
   });
 }
 const panel=document.createElement('details');panel.id='bf10300-details';
 panel.style.cssText='margin:10px 2px;padding:10px;border:1px solid #a6b4cc;'+
   'border-radius:7px;background:#18293c;color:#e7effa;font:12px/1.5 system-ui,sans-serif';
 const title=document.createElement('summary');title.textContent='QoL · LIVE BATTLE DETAILS';
 title.style.cssText='cursor:pointer;min-height:36px;font-weight:800';
 const header=document.createElement('p');header.id='bf10300-header';
 const ally=document.createElement('div');ally.id='bf10300-allies';
 const enemy=document.createElement('div');enemy.id='bf10300-enemies';
 const note=document.createElement('small');
 note.textContent='Read-only DEMO state. HP, BB and source-qualified critical counters '+
   'are displayed without changing combat, original units, rewards or saves.';
 panel.append(title,header,ally,enemy,note);battle.after(panel);
 function group(host,label,units){
   host.replaceChildren();
   const h=document.createElement('strong');h.textContent=label;
   host.append(h);
   for(const unit of units){
     const item=document.createElement('div');
     item.style.cssText='display:flex;justify-content:space-between;'+
       'align-items:center;flex-wrap:wrap;gap:6px;border-bottom:1px solid #4d627b;'+
       'padding:5px 0';
     const name=document.createElement('span');name.textContent=unit.name+
       (unit.active?'':' · KO');
     const numbers=document.createElement('span');
     numbers.textContent=unit.hp.toLocaleString()+'/'+unit.maxHp.toLocaleString()+
       ' HP · '+unit.hpPercent+'%'+
       (unit.kind==='ally'?' · BB '+unit.bb+'%'+
         (unit.defending?' · Guard':''):'');
     item.append(name,numbers);host.append(item);
   }
 }
 let last='';
 function refresh(){
   const s=snapshot();
   const signature=JSON.stringify(s);
   if(signature===last)return s;
   last=signature;
   header.textContent=(s.mode==='archive'?'STORY':'TRAINING')+
     ' · Wave '+s.wave+'/'+s.totalWaves+' · Turn '+s.round+
     ' · '+(s.over?'RESULT':s.busy?'ACTION':'READY')+
     ' · '+s.sourceScopedCriticalHits+' source-eligible critical hits';
   group(ally,'ALLIES · HP / BB',s.allies);
   group(enemy,'ENEMIES · HP',s.foes);
   return s;
 }
 panel.addEventListener('toggle',()=>{if(panel.open)refresh();});
 const timer=setInterval(()=>{
   if(!document.hidden&&panel.open)refresh();
 },800);
 window.addEventListener('pagehide',()=>clearInterval(timer),{once:true});
 refresh();
 window.BFGlobalQoLBattleDetailsV10300=freeze({snapshot,refresh});
})();
