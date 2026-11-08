/* BF_GLOBAL_QOL_ADVANCED_SMART_AUTO_V10500 */
(() => {
 'use strict';
 // v0.41+v0.42 source-aware DEMO heuristics remain the default. Only an
 // explicit player toggle can activate modified threshold/targeting behavior.
 const smart=window.BF041SmartAuto;
 const coordinated=window.BF042AutoCoordination;
 const host=document.getElementById('bf041-smart-auto-label');
 if(window.BFGlobalQoLAdvancedAutoV10500||!smart||!coordinated||!host||
   typeof smart.kindFor!=='function'||typeof smart.enabled!=='function'||
   typeof coordinated.chooseTarget!=='function'||
   typeof P==='undefined'||P.version!==7||
   typeof liveParty!=='function'||typeof bfOriginalBB!=='function'||
   typeof originalSupport!=='function')return;
 const freeze=Object.freeze;
 const pref='bf_global_offline_qol_advanced_auto_v105';
 const baseKind=smart.kindFor.bind(smart);
 const baseTarget=coordinated.chooseTarget.bind(coordinated);
 const configDefaults=()=>({on:false,heal:60,target:'percent',burst:'normal',guard:0});
 function readPrefs(){
   try{
     const raw=JSON.parse(localStorage.getItem(pref)||'null');
     return {on:false,
       heal:[35,50,60,75].includes(raw?.heal)?raw.heal:60,
       target:['percent','absolute','highest-atk','lowest-def','elemental'].includes(raw?.target)?raw.target:'percent',
       burst:['normal','conserve','final-wave'].includes(raw?.burst)?raw.burst:'normal',
       guard:[0,20,35,50].includes(raw?.guard)?raw.guard:0};
   }catch(_){return configDefaults();}
 }
 let config=readPrefs();
 function get(){return freeze({...config})}
 function valid(options){
   return options&&typeof options==='object'&&typeof options.on==='boolean'&&
     [35,50,60,75].includes(options.heal)&&
     ['percent','absolute','highest-atk','lowest-def','elemental'].includes(options.target)&&
     ['normal','conserve','final-wave'].includes(options.burst)&&
     (options.guard===undefined||[0,20,35,50].includes(options.guard));
 }
 function set(next){
   if(!valid(next))return false;
   const requested={on:next.on,heal:next.heal,
     target:next.target,burst:next.burst,
     guard:next.guard===undefined?config.guard:next.guard};
   try{localStorage.setItem(pref,JSON.stringify({
     heal:requested.heal,target:requested.target,burst:requested.burst,
     guard:requested.guard
   }));}catch(_){return false}
   config=requested;refresh();return true;
 }
 function active(){return config.on&&smart.enabled()===true}
 function kindFor(unit){
   const previous=baseKind(unit);
   // Optional low-HP survival Guard on the live PLAYER-controlled Auto turn.
   // Check original battler identity and current health; clones and noncombat
   // planning calls cannot trigger the rule. No enemy/NPC AI is modified.
   if(active()&&config.guard>0&&typeof S!=='undefined'&&
      S.mode==='archive'&&S.auto===true&&!S.over&&
      Number.isSafeInteger(unit?.id)&&unit.id>=0&&unit.id<6&&
      S.party?.[unit.id]===unit&&unit.active===true&&
      Number.isFinite(unit.hp)&&unit.hp>0&&
      Number.isFinite(unit.maxHp)&&unit.maxHp>0&&
      unit.hp/unit.maxHp<=config.guard/100&&
      !window.BFGlobalParalysisActionLockV6000?.paralyzed(unit.id))return 'guard';
   if(window.BFGlobalCurseBBLockV5900?.cursed(unit?.id))return 'attack';
   if(!active()||!unit||!unit.active||!(unit.hp>0)||
     !(Number(unit.bb)>=100))return previous;
   const source=Number.isSafeInteger(unit.unitId)?
     bfOriginalBB(unit.unitId):null;
   if(!source)return previous;
   const support=source.target==='support'?originalSupport(unit.unitId):null;
   if(support?.kind==='heal_all'){
     return liveParty().some(a=>a&&a.active&&a.hp>0&&a.maxHp>0&&
       a.hp<a.maxHp&&a.hp/a.maxHp<=config.heal/100)?'burst':'attack';
   }
   if(config.burst==='conserve'&&source.target!=='support'&&
      previous==='burst')return 'attack';
   // Player opt-in: keep offensive BB for the *last recorded quest wave*.
   // Only compare against the source-backed 2022 quest wave COUNT; actual
   // enemy identities/AI and the boss's identity remain demo/unknown.
   // Heal and support BBs stay available throughout the mission.
   if(config.burst==='final-wave'&&previous==='burst'&&
      ['single_enemy','all_enemies'].includes(source.target)&&
      typeof S!=='undefined'&&S.mode==='archive'&&S.auto===true&&!S.over&&
      Number.isSafeInteger(unit.id)&&unit.id>=0&&unit.id<6&&
      S.party?.[unit.id]===unit&&Number.isSafeInteger(S.wave)&&S.wave>=0&&
      typeof QUEST!=='undefined'&&typeof QUESTS!=='undefined'&&
      Array.isArray(QUESTS)){
     const archived=QUESTS.find(q=>q.missionId===QUEST?.missionId);
     if(archived&&Number.isSafeInteger(archived.battles)&&archived.battles>1&&
        archived.battles===QUEST.battles&&S.wave<archived.battles-1)
       return 'attack';
   }
   return previous;
 }
 // Source-backed elemental targeting for the player's optional Smart Auto.
 // Favor the foe weak to the largest number of living source-typed allies.
 // Unknown foe/ally elements are not inferred; default behavior survives.
 function elementalTarget(enemies){
   const element=window.BFGlobalElementalCombatV6900;
   if(typeof S==='undefined'||S.mode!=='archive'||S.over||
      !element||typeof element.normalize!=='function'||
      typeof element.multiplier!=='function'||
      typeof UNIT_BY_ID==='undefined'||typeof UNIT_BY_ID.get!=='function')
     return undefined;
   const live=enemies.filter(e=>e&&Number.isFinite(e.hp)&&e.hp>0);
   if(live.some(e=>!Number.isFinite(e.maxHp)||e.maxHp<=0||
       !Number.isSafeInteger(e.slot)||e.slot<0)||
       new Set(live.map(e=>e.slot)).size!==live.length)
     return null; // Ambiguous target roster: fail closed, never guess slots.
   const types=liveParty().filter(u=>u&&u.active&&Number.isFinite(u.hp)&&u.hp>0)
     .map(u=>element.normalize(UNIT_BY_ID.get(u.unitId)?.element)).filter(Boolean);
   if(!types.length)return undefined;
   const ranked=live.map(foe=>{
     const kind=element.normalize(foe.element);
     const count=kind?types.filter(a=>element.multiplier(a,kind)===1.5).length:0;
     return {foe,count};
   }).filter(row=>row.count>0);
   ranked.sort((a,b)=>b.count-a.count||
     a.foe.hp/a.foe.maxHp-b.foe.hp/b.foe.maxHp||
     a.foe.slot-b.foe.slot);
   return ranked[0]?.foe||undefined;
 }
 function chooseTarget(enemies){
   if(!active()||config.target==='percent')return baseTarget(enemies);
   if(!Array.isArray(enemies))return baseTarget(enemies);
   if(config.target==='elemental'){
     const chosen=elementalTarget(enemies);
     return chosen===undefined?baseTarget(enemies):chosen;
   }
   // Player-selected DEMO priorities, not recovered enemy or original AI.
   // Keep the native planner's positive HP/max HP and legal slot gate before
   // ranking by an optional visible enemy statistic. Unknown stats fail closed.
   const key=config.target==='highest-atk'?'atk':
     config.target==='lowest-def'?'def':'hp';
   const eligible=enemies.filter(e=>e&&Number.isFinite(e.hp)&&e.hp>0&&
     Number.isFinite(e.maxHp)&&e.maxHp>0&&
     Number.isSafeInteger(e.slot)&&e.slot>=0&&Number.isFinite(e[key]));
   eligible.sort((a,b)=>{
     const delta=config.target==='highest-atk'?b.atk-a.atk:a[key]-b[key];
     return delta||a.slot-b.slot;
   });
   return eligible[0]||null;
 }
 // Old coordinated plan dynamically calls window.BF041SmartAuto.kindFor(p).
 // Do not change the existing strongest-buff coordination or plan function.
 window.BF041SmartAuto=freeze({...smart,kindFor});
 window.BF042AutoCoordination=freeze({...coordinated,chooseTarget});
 const panel=document.createElement('details');panel.id='bf10500-auto-settings';
 panel.style.cssText='padding:10px;margin:8px 2px;border:1px solid #87a68c;'+
   'border-radius:7px;background:#1d332b;color:#e8f6e9;font:12px/1.5 system-ui,sans-serif';
 const title=document.createElement('summary');title.textContent='QoL · ADVANCED SMART AUTO';
 title.style.cssText='cursor:pointer;font-weight:800;min-height:36px';
 const intro=document.createElement('p');
 intro.textContent='Optional DEMO heuristics only. Native Global AI rules are not reconstructed. '+
   'Existing source-aware Smart Auto and coordinated ATK buffs stay the baseline.';
 const settings=document.createElement('div');
 const option=(text,id,entries)=>{
   const label=document.createElement('label');label.textContent=text;
   label.style.cssText='display:block;margin:7px 0';
   const select=document.createElement('select');select.id=id;
   select.style.cssText='margin-left:7px;min-height:40px;padding:7px;'+
     'background:#324f43;border:1px solid #92b9a4;color:#fff';
   for(const [value,name] of entries){
     const opt=document.createElement('option');opt.value=String(value);
     opt.textContent=name;select.append(opt);
   }
   label.append(select);settings.append(label);return select;
 };
 const onLabel=document.createElement('label');
 const toggle=document.createElement('input');toggle.type='checkbox';toggle.id='bf10500-enable';
 onLabel.append(toggle,document.createTextNode(' Enable advanced rules (Smart Auto must also be enabled)'));
 settings.append(onLabel);
 const heal=option('Heal-all BB threshold','bf10500-heal',[[35,'35%'],[50,'50%'],[60,'60% (existing)'],[75,'75%']]);
 const target=option('Enemy target','bf10500-target',[['percent','Lowest HP percentage (existing)'],['absolute','Lowest remaining HP'],['highest-atk','Highest enemy ATK'],['lowest-def','Lowest enemy DEF'],['elemental','Most allied elemental advantages (known types)']]);
 const burst=option('Offensive BB','bf10500-burst',[['normal','Use as normal'],['conserve','Conserve offensive BB gauge'],['final-wave','Save offensive BB until final recorded quest wave']]);
 const guard=option('Low HP Auto defense','bf10500-guard',[[0,'Off (original default)'],[20,'Guard at or below 20% HP'],[35,'Guard at or below 35% HP'],[50,'Guard at or below 50% HP']]);
 const status=document.createElement('p');status.id='bf10500-status';
 const caution=document.createElement('small');
 caution.textContent='Only applies when both optional Smart Auto and Advanced Auto are on. '+
   'Element targeting uses known original unit types and visible, identified enemy types; '+
   'unknown weaknesses revert to the existing HP% strategy. Optional Guard applies '+
   'only to active player Auto turns. Final-wave BB strategy uses only archived quest wave counts, not restored enemy formations; no enemy AI, damage, rewards or v7 save changes.';
 panel.append(title,intro,settings,status,caution);host.after(panel);
 function refresh(){
   toggle.checked=config.on;heal.value=String(config.heal);
   target.value=config.target;burst.value=config.burst;guard.value=String(config.guard);
   status.textContent='Advanced rules '+(config.on?'ON':'OFF')+
     (smart.enabled()?' · Smart Auto ready':' · Existing Smart Auto is disabled');
   return get();
 }
 toggle.addEventListener('change',()=>set({...config,on:toggle.checked}));
 heal.addEventListener('change',()=>set({...config,heal:Number(heal.value)}));
 target.addEventListener('change',()=>set({...config,target:target.value}));
 burst.addEventListener('change',()=>set({...config,burst:burst.value}));
 guard.addEventListener('change',()=>set({...config,guard:Number(guard.value)}));
 host.addEventListener('change',refresh);
 refresh();
 window.BFGlobalQoLAdvancedAutoV10500=freeze({
   get,active,kindFor,chooseTarget,set,refresh
 });
})();
