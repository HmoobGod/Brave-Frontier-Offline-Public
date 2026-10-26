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
 const configDefaults=()=>({on:false,heal:60,target:'percent',burst:'normal'});
 function readPrefs(){
   try{
     const raw=JSON.parse(localStorage.getItem(pref)||'null');
     return {on:false,
       heal:[35,50,60,75].includes(raw?.heal)?raw.heal:60,
       target:['percent','absolute'].includes(raw?.target)?raw.target:'percent',
       burst:['normal','conserve'].includes(raw?.burst)?raw.burst:'normal'};
   }catch(_){return configDefaults();}
 }
 let config=readPrefs();
 function get(){return freeze({...config})}
 function valid(options){
   return options&&typeof options==='object'&&typeof options.on==='boolean'&&
     [35,50,60,75].includes(options.heal)&&
     ['percent','absolute'].includes(options.target)&&
     ['normal','conserve'].includes(options.burst);
 }
 function set(next){
   if(!valid(next))return false;
   const requested={on:next.on,heal:next.heal,
     target:next.target,burst:next.burst};
   try{localStorage.setItem(pref,JSON.stringify({
     heal:requested.heal,target:requested.target,burst:requested.burst
   }));}catch(_){return false}
   config=requested;refresh();return true;
 }
 function active(){return config.on&&smart.enabled()===true}
 function kindFor(unit){
   const previous=baseKind(unit);
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
   return previous;
 }
 function chooseTarget(enemies){
   if(!active()||config.target==='percent')return baseTarget(enemies);
   if(!Array.isArray(enemies))return baseTarget(enemies);
   const eligible=enemies.filter(e=>e&&Number.isFinite(e.hp)&&e.hp>0&&
     Number.isSafeInteger(e.slot));
   eligible.sort((a,b)=>a.hp-b.hp||a.slot-b.slot);
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
 const target=option('Enemy target','bf10500-target',[['percent','Lowest HP percentage (existing)'],['absolute','Lowest remaining HP']]);
 const burst=option('Offensive BB','bf10500-burst',[['normal','Use as normal'],['conserve','Conserve offensive BB gauge']]);
 const status=document.createElement('p');status.id='bf10500-status';
 const caution=document.createElement('small');
 caution.textContent='Only applies when both optional Smart Auto and Advanced Auto are on. '+
   'No changes to saved squad, attack formulas, source buffs, quest rewards or game save.';
 panel.append(title,intro,settings,status,caution);host.after(panel);
 function refresh(){
   toggle.checked=config.on;heal.value=String(config.heal);
   target.value=config.target;burst.value=config.burst;
   status.textContent='Advanced rules '+(config.on?'ON':'OFF')+
     (smart.enabled()?' · Smart Auto ready':' · Existing Smart Auto is disabled');
   return get();
 }
 toggle.addEventListener('change',()=>set({...config,on:toggle.checked}));
 heal.addEventListener('change',()=>set({...config,heal:Number(heal.value)}));
 target.addEventListener('change',()=>set({...config,target:target.value}));
 burst.addEventListener('change',()=>set({...config,burst:burst.value}));
 host.addEventListener('change',refresh);
 refresh();
 window.BFGlobalQoLAdvancedAutoV10500=freeze({
   get,active,kindFor,chooseTarget,set,refresh
 });
})();
