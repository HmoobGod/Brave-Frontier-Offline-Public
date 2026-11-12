/* BF_GLOBAL_PLAYABLE_FOCUS_ACTIONS_V3100 */
(() => {
 'use strict';
 const commands=window.BFGlobalBattleCommandsV2100;
 if(window.BFGlobalBattleFocusV3100||!commands||!window.BFGlobalBattleResultsV3000||
    typeof S==='undefined'||typeof P==='undefined'||P.version!==7)return;
 const host=document.getElementById('bf2100-tray');
 if(!host)return;
 const css=document.createElement('style');css.id='bf3100-style';
 css.textContent='#bf3100-focus{margin-top:12px;padding:10px 0;border-top:1px solid #a48d6b;color:#fff;font:12px/1.5 system-ui,sans-serif}'+
 '#bf3100-options{display:grid;grid-template-columns:repeat(auto-fit,minmax(105px,1fr));gap:7px}'+
 '#bf3100-focus button{background:#35516b;color:white;border:1px solid #a9916b;border-radius:5px;min-height:42px;padding:7px;font-weight:bold}'+
 '#bf3100-focus button:disabled{opacity:.4}#bf3100-status{margin:9px 0;color:#d9e3eb}';
 document.head.append(css);
 const panel=document.createElement('section');panel.id='bf3100-focus';
 const title=document.createElement('h3');title.textContent='TACTICAL FOCUS · DEMO';
 const options=document.createElement('div');options.id='bf3100-options';
 const state=document.createElement('p');state.id='bf3100-status';
 const foot=document.createElement('small');
 foot.textContent='Targets use visible DEMO enemy stats. Wounded Threat prioritizes the highest ATK foe at or below 50% HP, Wounded Low DEF the least-armored one; both reject unknown foe stats. Element Weakness requires a known advantage; Fewest Resists uses source-listed elemental disadvantages for identified DEMO foes only when every live ally/foe element is known. Queuing uses native player controls; Execute remains manual, except the explicitly clicked one-turn native Focus + Execute shortcut. Not recovered original AI or 2022 wave formations.';
 panel.append(title,options,state,foot);host.append(panel);
 const strategies=[
  ['lowest-hp','LOWEST HP'],['lowest-hp-percent','LOWEST HP %'],
  ['highest-hp','HIGHEST HP'],['highest-hp-percent','HIGHEST HP %'],
  ['highest-atk','HIGHEST ATK'],['lowest-def','LOWEST DEF'],
  // User-only tactics: a visible DEMO foe below half HP can be singled
  // out either by its live attack threat or low defense. These are current
  // simulated combat stats, NEVER authenticated 2022 enemy formations.
  ['wounded-threat','FINISH WOUNDED THREAT'],
  ['wounded-armor','FINISH WOUNDED LOW DEF'],
  ['elemental','ELEMENT WEAKNESS'],
  ['element-safe','FEWEST RESISTS']
 ];
 let selected='lowest-hp',signature='';
 const legal=()=>!S.busy&&!S.over&&!S.auto&&!!commands.snapshot()?.canQueue;
 function lookup(kind){
   if(!strategies.some(x=>x[0]===kind)||!Array.isArray(S.enemies))return null;
   const key=kind==='highest-atk'||kind==='wounded-threat'?'atk':
     kind==='lowest-def'||kind==='wounded-armor'?'def':'hp';
   // Validate EVERY living native foe before any optional ranking.
   // Silently skipping a corrupt foe can mis-map the real target buttons,
   // even if the candidate itself has valid HP and a legal slot.
   if(S.enemies.some(e=>e&&e.hp>0&&!Number.isFinite(e.hp)))return null;
   const living=S.enemies.filter(e=>e&&Number.isFinite(e.hp)&&e.hp>0);
   if(living.some(e=>!Number.isFinite(e.maxHp)||e.maxHp<=0||
      !Number.isSafeInteger(e.slot)||e.slot<0)||
      new Set(living.map(e=>e.slot)).size!==living.length)return null;
   // Only source-known six-element advantages count; never infer types
   // from names, artwork, or missing enemy metadata. Favor the foe weak to
   // the most living typed allies, then lowest HP%, then native slot.
   // No verified advantage means no manual focus; do not silently fall back.
   if(kind==='elemental'){
     const element=window.BFGlobalElementalCombatV6900;
     if(S.mode!=='archive'||!element||
        typeof element.normalize!=='function'||
        typeof element.multiplier!=='function'||
        typeof UNIT_BY_ID==='undefined'||typeof UNIT_BY_ID.get!=='function'||
        !Array.isArray(S.party))return null;
     // Both ally-type normalization and foe ranking read optional source
     // helpers. Any provider exception must fail closed before touching
     // a native target, queued order, or the canonical v7 save.
     let ranked;
     try{
       const types=S.party.filter(u=>u&&u.active&&Number.isFinite(u.hp)&&u.hp>0)
         .map(u=>element.normalize(UNIT_BY_ID.get(u.unitId)?.element)).filter(Boolean);
       if(!types.length)return null;
       ranked=living.map(foe=>{
         const targetType=element.normalize(foe.element);
         const count=targetType?types.filter(type=>
           element.multiplier(type,targetType)===1.5).length:0;
         return {foe,count};
       }).filter(row=>row.count>0);
     }catch(_){return null;}
     ranked.sort((a,b)=>b.count-a.count||
       a.foe.hp/a.foe.maxHp-b.foe.hp/b.foe.maxHp||
       a.foe.slot-b.foe.slot);
     const f=ranked[0]?.foe;
     return f?Object.freeze({slot:f.slot,name:f.name,hp:f.hp,atk:f.atk,def:f.def}):null;
   }
   // Distinct manual command: minimize the number of current squad members
   // facing a source-listed 0.5x ELEMENTAL disadvantage in this DEMO battle.
   // Unlike Element Weakness, this also works if no ally has an advantage.
   // Enemy rosters remain DEMO, not authenticated 2022 formations. If any
   // living combatant has an unknown element, reject without moving the target.
   if(kind==='element-safe'){
     const element=window.BFGlobalElementalCombatV6900;
     if(S.mode!=='archive'||!element||
       typeof element.normalize!=='function'||
       typeof element.multiplier!=='function'||
       typeof UNIT_BY_ID==='undefined'||typeof UNIT_BY_ID.get!=='function'||
       !Array.isArray(S.party))return null;
     let ranked;
     try{
       const allies=S.party.filter(u=>u&&u.active&&
         Number.isFinite(u.hp)&&u.hp>0);
       if(!allies.length||allies.some(u=>!Number.isSafeInteger(u.id)||
          u.id<0||S.party[u.id]!==u)||
          new Set(allies.map(u=>u.id)).size!==allies.length)return null;
       const types=allies.map(u=>
         element.normalize(UNIT_BY_ID.get(u.unitId)?.element));
       if(types.some(type=>!type))return null;
       ranked=living.map(foe=>{
         const targetType=element.normalize(foe.element);
         if(!targetType)return null;
         let resisted=0,advantaged=0;
         for(const type of types){
           const factor=element.multiplier(type,targetType);
           if(factor===0.5)resisted++;
           else if(factor===1.5)advantaged++;
           else if(factor!==1)throw Error('unverified-element-matchup');
         }
         return {foe,resisted,advantaged};
       });
       if(ranked.some(row=>!row))return null;
     }catch(_){return null;}
     ranked.sort((a,b)=>a.resisted-b.resisted||
       b.advantaged-a.advantaged||
       a.foe.hp/a.foe.maxHp-b.foe.hp/b.foe.maxHp||
       a.foe.hp-b.foe.hp||a.foe.slot-b.foe.slot);
     const f=ranked[0]?.foe;
     return f?Object.freeze({slot:f.slot,name:f.name,hp:f.hp,
       atk:f.atk,def:f.def}):null;
   }
   // Missing ATK/DEF on ANY living foe makes its rank unknowable.
   // Silently dropping that foe can change the target of a player command.
   // Fail closed for that stat strategy; independent valid-HP priorities
   // and native slot ordering remain unchanged.
   if(living.some(e=>!Number.isFinite(e[key])))return null;
   // A wounded finisher uses a REAL current DEMO combat HP ratio. Check
   // every living foe's HP range before choosing; zero valid wounded foes
   // means no player command, not an arbitrary fallback target.
   if(kind==='wounded-threat'||kind==='wounded-armor'){
     if(S.mode!=='archive'||living.some(e=>e.hp>e.maxHp))return null;
     // Unknown/NaN or negative HP cannot establish that a foe is dead.
     // Do not silently drop a malformed native foe and pick a false finisher.
     if(S.enemies.some(e=>e&&(!Number.isFinite(e.hp)||e.hp<0)))return null;
     const wounded=living.filter(e=>e.hp/e.maxHp<=0.5);
     if(!wounded.length)return null;
     wounded.sort((a,b)=>kind==='wounded-threat'?
       b.atk-a.atk||a.hp/a.maxHp-b.hp/b.maxHp||a.slot-b.slot:
       a.def-b.def||a.hp/a.maxHp-b.hp/b.maxHp||a.slot-b.slot);
     const f=wounded[0];
     return Object.freeze({slot:f.slot,name:f.name,hp:f.hp,
       atk:f.atk,def:f.def});
   }
   const foes=living.slice();
   foes.sort((a,b)=>{
     const diff=kind==='highest-atk'?b[key]-a[key]:
       kind==='highest-hp'?b.hp-a.hp:
       kind==='highest-hp-percent'?b.hp/b.maxHp-a.hp/a.maxHp:
       kind==='lowest-hp-percent'?a.hp/a.maxHp-b.hp/b.maxHp:
       a[key]-b[key];
     return diff||a.slot-b.slot;
   });
   const f=foes[0];return f?Object.freeze({slot:f.slot,name:f.name,hp:f.hp,atk:f.atk,def:f.def}):null;
 }
 function snapshot(){return Object.freeze({strategy:selected,target:lookup(selected),canQueue:legal()});}
 function refresh(){
   const s=snapshot();
   // Every focus control has its own eligibility. An enemy's ATK/DEF can
   // disappear while the selected focus and elemental availability remain
   // unchanged. Include ALL strategies in the refresh signature so disabled
   // buttons update immediately rather than retaining stale enabled state.
   const eligible=new Map(strategies.map(([kind])=>[kind,!!lookup(kind)]));
   const key=JSON.stringify([s,[...eligible]]);
   if(key===signature)return s;signature=key;
   for(const b of options.querySelectorAll('button')){
     if(b.id==='bf3100-run-turn'){
       // An explicit player click may execute one native round only when
       // no manually queued order would be overwritten.
       b.disabled=!s.canQueue||!s.target||S.mode!=='archive'||
         document.hidden||!Array.isArray(S.party)||
         S.party.some(p=>p?.action!=null);
       continue;
     }
     const strategy=b.dataset.strategy;
     // An uncertain or missing native target never appears runnable.
     b.disabled=!s.canQueue||(strategy?!eligible.get(strategy):!s.target);
   }
   state.textContent=s.target?'Focus '+s.target.name+' · '+s.strategy.replaceAll('-',' ')+' · '+s.target.hp+' HP':'No eligible target';
   return s;
 }
 function focus(kind){
   if(!legal())return false;const target=lookup(kind);
   if(!target||!commands.setTarget(target.slot))return false;
   selected=kind;signature='';refresh();return true;
 }
 function queueFocus(kind,action='attack'){
   if(action!=='attack'&&action!=='burst'||!legal()||!Array.isArray(S.party))return false;
   // Focus changes the selected native target BEFORE queueAll checks actors.
   // Refuse a shuffled/cloned player squad without touching target or orders.
   const actors=S.party.filter(p=>p&&p.active&&p.hp>0);
   const nativeSlots=document.getElementById('slots')?.children;
   if(!actors.length||actors.some(p=>!Number.isSafeInteger(p.id)||p.id<0||
      S.party[p.id]!==p||!Number.isFinite(p.hp)||
      !Number.isFinite(p.maxHp)||p.maxHp<=0||
      !nativeSlots?.[p.id]||nativeSlots[p.id].disabled)||
      new Set(actors.map(p=>p.id)).size!==actors.length)return false;
   if(!focus(kind)||!commands.queueAll(action))return false;
   const target=lookup(kind),live=S.party.filter(p=>p.active&&p.hp>0);
   signature='';refresh();
   return !!target&&live.length>0&&live.every(p=>p.action?.target===target.slot);
 }
 // One explicitly clicked player turn, not a new AI or repeat loop.
 // Refuse to replace a manually queued action. The shared native command
 // adapter owns final target legality and the actual Execute control.
 function runFocusedTurn(kind=selected,action='attack'){
   if(action!=='attack'&&action!=='burst'||!legal()||
      S.mode!=='archive'||document.hidden||!Array.isArray(S.party)||
      S.party.some(p=>p?.action!=null)||
      typeof commands.queuedAttacksSafe!=='function'||
      typeof commands.executeTurn!=='function')return false;
   try{
     if(!queueFocus(kind,action)||!commands.queuedAttacksSafe())return false;
     return commands.executeTurn()===true;
   }catch(_){return false;}
 }
 for(const [kind,label] of strategies){
   const b=document.createElement('button');b.type='button';
   b.dataset.strategy=kind;b.textContent=label+' + ATTACK';
   b.addEventListener('click',()=>queueFocus(kind));options.append(b);
 }
 const bursts=document.createElement('button');bursts.type='button';
 bursts.textContent='FOCUS + BB IF READY';bursts.id='bf3100-burst';
 bursts.addEventListener('click',()=>queueFocus(selected,'burst'));options.append(bursts);
 const oneTurn=document.createElement('button');oneTurn.type='button';
 oneTurn.id='bf3100-run-turn';oneTurn.textContent='FOCUS + EXECUTE ONE TURN';
 oneTurn.setAttribute('aria-label','Execute one manually chosen player squad turn');
 oneTurn.addEventListener('click',()=>runFocusedTurn());options.append(oneTurn);
 new MutationObserver(refresh).observe(document.getElementById('meta')||host,{childList:true,characterData:true,subtree:true});
 window.setInterval(()=>{if(!document.hidden)refresh()},900);
 refresh();
 window.BFGlobalBattleFocusV3100=Object.freeze({lookup,snapshot,refresh,focus,queueFocus,runFocusedTurn});
})();
