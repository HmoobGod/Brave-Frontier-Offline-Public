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
   // Never normalize corrupt live DEMO health into invented 1-HP units.
   if(!u||!Number.isFinite(u.hp)||!Number.isFinite(u.maxHp)||
      u.maxHp<=0||u.hp<0||u.hp>u.maxHp)return null;
   const max=u.maxHp,hp=u.hp;
   return freeze({name:String(u.name||('Unit #'+(u.unitId||'?'))).slice(0,90),
     kind,unitId:Number.isSafeInteger(u.unitId)?u.unitId:null,
     hp,maxHp:max,hpPercent:Math.round(100*hp/max),
     bb:kind==='ally'?Math.min(100,safe(u.bb)):null,
     active:kind==='ally'?!!u.active&&hp>0:hp>0,
     defending:kind==='ally'?!!u.guard:null});
 }
 // The 2022 mission's recorded wave count is read-only provenance.
 // It does not recover enemy formations, native AI, or drop probabilities.
 // A corrupt catalog must never be described as source verified.
 function recordedWaves(){
   const api=window.BFGrandGaiaCampaignV100;
   const q=typeof QUEST==='undefined'?null:QUEST;
   if(S.mode!=='archive'||!Number.isSafeInteger(q?.missionId)||
      typeof api?.waveReadiness!=='function')return null;
   try{
     const row=api.waveReadiness(q.missionId);
     return row?.missionId===q.missionId&&
       Number.isSafeInteger(row.verifiedWaveCount)&&
       row.verifiedWaveCount>=1&&row.verifiedWaveCount<=100&&
       row.enemyFormationsVerified===false&&row.dropsVerified===false&&
       row.nativeMultiWaveEnabled===false?row.verifiedWaveCount:null;
   }catch(_){return null;}
 }
 // Optional critical evidence providers are outside the battle engine.
 // An unavailable or malformed provider must never break the read-only HUD
 // or be displayed as an apparently verified zero criticals.
 function criticalCount(){
   try{
     const one=window.BFGlobalSingleHitCriticalV9300?.snapshot?.();
     const multi=window.BFGlobalMultiHitCriticalV9500?.snapshot?.();
     if(!Number.isSafeInteger(one?.criticals)||one.criticals<0||
       !Number.isSafeInteger(multi?.criticalHits)||multi.criticalHits<0)return null;
     const total=one.criticals+multi.criticalHits;
     return Number.isSafeInteger(total)?total:null;
   }catch(_){return null;}
 }
 function snapshot(){
   const allySource=Array.isArray(S.party)?S.party.filter(u=>u&&u.active):[];
   const enemySource=Array.isArray(S.enemies)?S.enemies:[];
   const allies=allySource.map(u=>readUnit(u,'ally')).filter(Boolean);
   const foes=enemySource.map(u=>readUnit(u,'enemy')).filter(Boolean);
   const invalidAllies=allySource.length-allies.length;
   const invalidFoes=enemySource.length-foes.length;
   const recorded=recordedWaves(),criticals=criticalCount();
   const quest=typeof QUEST==='undefined'?null:QUEST;
   // A fractional, negative, or out-of-range DEMO total must not be
   // normalized into an apparent match with immutable source metadata.
   const liveValid=Number.isSafeInteger(S.totalWaves)&&
     S.totalWaves>=1&&S.totalWaves<=100;
   const liveWaveValid=liveValid&&Number.isSafeInteger(S.wave)&&
     S.wave>=0&&S.wave<S.totalWaves;
   const provenance=recorded===null?'UNAVAILABLE':
     liveWaveValid&&recorded===S.totalWaves&&
     quest?.battles===recorded?'MATCH':'MISMATCH';
   return freeze({
     mode:String(S.mode||''),wave:liveWaveValid?S.wave+1:null,
     totalWaves:liveValid?S.totalWaves:null,waveVerified:liveWaveValid,
     sourceRecordedWaveCount:recorded,sourceWaveStatus:provenance,
     round:safe(S.round),busy:!!S.busy,over:!!S.over,
     phase:String(S.phase||''),allies:freeze(allies),foes:freeze(foes),
     invalidAllies,invalidFoes,
     sourceScopedCriticalHits:criticals,criticalCountsVerified:criticals!==null,
     nativeFullDamageFormula:false,progressUnchanged:true
   });
 }
 const panel=document.createElement('details');panel.id='bf10300-details';
 panel.style.cssText='margin:10px 2px;padding:10px;border:1px solid #a6b4cc;'+
   'border-radius:7px;background:#18293c;color:#e7effa;font:12px/1.5 system-ui,sans-serif';
 const title=document.createElement('summary');title.textContent='QoL · LIVE BATTLE DETAILS';
 title.style.cssText='cursor:pointer;min-height:44px;font-weight:800';
 const header=document.createElement('p');header.id='bf10300-header';
 const ally=document.createElement('div');ally.id='bf10300-allies';
 const enemy=document.createElement('div');enemy.id='bf10300-enemies';
 const note=document.createElement('small');
 note.textContent='Read-only DEMO state. HP, BB and source-qualified critical counters '+
   'are displayed without changing combat, original units, rewards or saves. '+
   'Source wave count checks use pinned repository 2022 fixtures only; '+
   'original enemy formations, native AI and drops are not verified.';
 panel.append(title,header,ally,enemy,note);battle.after(panel);
 function group(host,label,units,invalid){
   host.replaceChildren();
   const h=document.createElement('strong');h.textContent=label+
     (invalid?' · '+invalid+' UNVERIFIED DEMO HP RECORD'+(invalid===1?'':'S')+' HIDDEN':'');
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
     ' · '+(s.waveVerified?'DEMO Wave '+s.wave+'/'+s.totalWaves:
       'DEMO wave unavailable')+
     (s.mode==='archive'?' · 2022 recorded wave count: '+
       (s.sourceWaveStatus==='MATCH'?String(s.sourceRecordedWaveCount)+' (MATCH)':
        s.sourceWaveStatus==='MISMATCH'?'MISMATCH — DEMO data differs':
        'UNAVAILABLE'):'')+
     ' · Turn '+s.round+
     ' · '+(s.over?'RESULT':s.busy?'ACTION':'READY')+
     ' · '+(s.criticalCountsVerified?
       s.sourceScopedCriticalHits+' source-eligible critical hits':
       'source-eligible critical count unavailable');
   group(ally,'ALLIES · HP / BB',s.allies,s.invalidAllies);
   group(enemy,'ENEMIES · HP',s.foes,s.invalidFoes);
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
