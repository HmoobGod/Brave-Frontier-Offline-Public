/* BF_GLOBAL_OPTIONAL_IMP_FUSION_V16900 */
(() => {
  'use strict';
  // 2022 source caps; opt-in strict <=125% enhancements now persist alongside
  // the canonical v7 quest/summon save. v169 sidecar is legacy import only.
  const archive=window.BFGlobalUnitArchive;
  if(window.BFGlobalOptionalImpsV16900||!archive||archive.count!==2291||
     typeof archive.originalImpCaps!=='function'||
     typeof P==='undefined'||P.version!==7||!Array.isArray(P.roster)||
     !Array.isArray(P.squad)||typeof effectiveUnit!=='function'||
     typeof S==='undefined')return;
  const host=document.getElementById('squadpicker');
  if(!host)return;
  const key='bf_global_offline_optional_imps_v169'; // legacy v169 read-only migration source
  const canonicalField='_bfImpsV171';
  const ids=Object.freeze(['molin','pakpak','ganju','fwahl','arton']);
  const names=Object.freeze({molin:'Vigor Imp Molin',pakpak:'Power Imp Pakpak',
    ganju:'Guard Imp Ganju',fwahl:'Healing Imp Fwahl',
    arton:'Almighty Imp Arton'});
  const gains=Object.freeze({molin:Object.freeze([50,0,0,0]),
    pakpak:Object.freeze([0,20,0,0]),ganju:Object.freeze([0,0,20,0]),
    fwahl:Object.freeze([0,0,0,20]),arton:Object.freeze([150,60,60,60])});
  const steps=Object.freeze([50,20,20,20]);
  const freeze=Object.freeze;
  const copy=x=>JSON.parse(JSON.stringify(x));
  function validState(raw){
    if(!raw||raw.version!==1||raw.started!==true||
       !['original','custom'].includes(raw.mode)||
       !raw.amounts||Array.isArray(raw.amounts)||
       !raw.inventory||Array.isArray(raw.inventory)||
       !raw.cursors||Array.isArray(raw.cursors))return null;
    const amounts={},inventory={},cursors={};
    if(Object.keys(raw.amounts).length>5000||
       Object.keys(raw.cursors).length>3000)return null;
    for(const [k,v] of Object.entries(raw.amounts)){
      if(!/^[1-9]\d{0,9}$/.test(k)||!Array.isArray(v)||v.length!==4||
         v.some(n=>!Number.isSafeInteger(n)||n<0||n>65535))return null;
      amounts[k]=v.slice();
    }
    for(const id of ids){
      const n=raw.inventory[id];
      if(!Number.isSafeInteger(n)||n<0||n>10000)return null;
      inventory[id]=n;
    }
    for(const [k,n] of Object.entries(raw.cursors)){
      if(!/^[1-9]\d{0,7}$/.test(k)||!Number.isSafeInteger(n)||
         n<0||n>10000000)return null;
      cursors[k]=n;
    }
    return {version:1,started:true,mode:raw.mode,amounts,inventory,cursors};
  }
  let state=null,invalidStorage=false,observedP=null,observedState=undefined;
  function synchronize(){
    const raw=P?.[canonicalField];
    if(observedP===P&&observedState===raw)return;
    observedP=P;observedState=raw;
    state=raw===null||raw===undefined?null:validState(raw);
    invalidStorage=raw!==null&&raw!==undefined&&!state;
  }
  synchronize();
  function persist(next){
    synchronize();
    if(invalidStorage||typeof saveProgress!=='function')return false;
    const checked=validState(next);
    if(!checked)return false;
    const before=P[canonicalField];
    P[canonicalField]=checked;
    try{
      if(!saveProgress()){P[canonicalField]=before;synchronize();return false;}
      synchronize();return true;
    }catch(_){P[canonicalField]=before;synchronize();return false;}
  }
  function cursorsNow(){
    const seen={};
    for(const [id,count] of Object.entries(P.questClears||{})){
      if(/^[1-9]\d{0,7}$/.test(id)&&Number.isSafeInteger(count)&&
         count>=0&&count<=10000000)seen[id]=count;
    }
    return seen;
  }
  function activate(){
    synchronize();
    if(state||invalidStorage)return false;
    const starter={version:1,started:true,mode:'custom',amounts:{},
      inventory:{molin:0,pakpak:0,ganju:0,fwahl:0,arton:5},
      cursors:cursorsNow()};
    const done=persist(starter);
    if(done)refresh();
    return done;
  }
  function formOf(baseId){
    if(!Number.isSafeInteger(baseId)||!P.roster.includes(baseId))return null;
    const source=effectiveUnit(baseId);
    return Number.isSafeInteger(source?.id)?source.id:null;
  }
  function original(formId){
    const caps=archive.originalImpCaps(formId);
    return Array.isArray(caps)&&caps.length===4&&
      caps.every(n=>Number.isSafeInteger(n)&&n>=0&&n<=65535)?
      caps.slice():null;
  }
  function maximum(baseId,mode=undefined){
    synchronize();
    mode=mode??state?.mode??'original';
    const formId=formOf(baseId),caps=original(formId);
    if(!caps)return null;
    const max=caps.map((n,i)=>mode==='custom'&&n>0?
      Math.max(n,Math.floor((n*5/4)/steps[i])*steps[i]):n);
    return freeze({baseId,formId,mode,original:freeze(caps),
      maximum:freeze(max)});
  }
  function bonus(baseId){
    synchronize();
    if(!state)return freeze([0,0,0,0]);
    const saved=state.amounts[String(baseId)];
    return freeze(saved?saved.slice():[0,0,0,0]);
  }
  function view(baseId){
    const cap=maximum(baseId);
    if(!cap)return null;
    const stored=bonus(baseId),live=stored.map((n,i)=>Math.min(n,cap.maximum[i]));
    return freeze({...cap,stored,applied:freeze(live),
      remaining:freeze(cap.maximum.map((n,i)=>Math.max(0,n-live[i])))});
  }
  function stock(){synchronize();return freeze(state?{...state.inventory}:
    {molin:0,pakpak:0,ganju:0,fwahl:0,arton:0});}
  function plan(baseId,preferred='smart',limit=500){
    synchronize();
    if(!state||!ids.includes(preferred)&&preferred!=='smart')return null;
    const cur=view(baseId);
    if(!cur||!Number.isSafeInteger(limit)||limit<1||limit>500)return null;
    const remaining=cur.remaining.slice(),inv={...state.inventory};
    const counts={molin:0,pakpak:0,ganju:0,fwahl:0,arton:0};
    const add=[0,0,0,0];
    let total=0;
    while(total<limit){
      let chosen=null,score=-1;
      for(const id of ids){
        if(!inv[id]||(preferred!=='smart'&&preferred!==id))continue;
        const gain=gains[id];
        const improvements=gain.map((n,i)=>Math.min(remaining[i],n));
        if(improvements.every(n=>n===0))continue;
        const value=improvements.reduce((sum,n,i)=>
          sum+(gain[i]?n/gain[i]:0),0);
        // Prefer a targeted Imp over wasting a multi-stat Imp for one stat.
        if(value>score){score=value;chosen=id;}
      }
      if(!chosen)break;
      inv[chosen]--;counts[chosen]++;total++;
      gains[chosen].forEach((n,i)=>{
        const v=Math.min(remaining[i],n);
        remaining[i]-=v;add[i]+=v;
      });
    }
    return freeze({baseId,formId:cur.formId,mode:cur.mode,
      materials:freeze({...counts}),total,
      gained:freeze(add),remaining:freeze(remaining)});
  }
  function feed(baseId,preferred='smart',limit=500){
    synchronize();
    if(!state||invalidStorage)return false;
    const proposed=plan(baseId,preferred,limit);
    if(!proposed||proposed.total===0)return false;
    const next=copy(state),old=bonus(baseId);
    for(const id of ids)next.inventory[id]-=proposed.materials[id];
    next.amounts[String(baseId)]=old.map((n,i)=>n+proposed.gained[i]);
    if(!persist(next))return false;
    refresh();
    return proposed;
  }
  function claim(){
    synchronize();
    if(!state||invalidStorage)return 0;
    const current=cursorsNow(),next=copy(state);
    let clears=0;
    for(const [id,n] of Object.entries(current)){
      const old=next.cursors[id]??0;
      if(n>old){
        const delta=Math.min(n-old,Math.max(0,20-clears));
        clears+=delta;next.cursors[id]=old+delta;
      }
      if(clears>=20)break;
    }
    const granted=Math.min(clears*2,10000-next.inventory.arton);
    if(granted<=0)return 0;
    // Never advance the paid cursor beyond the material actually granted.
    if(granted<clears*2){
      let pending=granted/2;
      next.cursors={...state.cursors};
      for(const [id,n] of Object.entries(current)){
        if(pending<=0)break;
        const old=next.cursors[id]??0;
        const delta=Math.min(n-old,Math.floor(pending));
        if(delta>0){next.cursors[id]=old+delta;pending-=delta;}
      }
    }
    next.inventory.arton+=granted;
    if(!persist(next))return 0;
    refresh();
    return granted;
  }
  const audits=new WeakMap();
  function apply(unit,slot){
    synchronize();
    if(!state||!unit||typeof unit!=='object'||audits.has(unit)||
       document.getElementById('mode')?.value!=='archive'||
       !unit.active||!Number.isSafeInteger(slot)||slot<0||slot>=6||
       !Number.isSafeInteger(unit.baseId)||!Number.isSafeInteger(unit.unitId)||
       P.squad[slot]!==unit.baseId||formOf(unit.baseId)!==unit.unitId||
       unit.hp!==unit.maxHp)return unit;
    const row=view(unit.baseId);
    if(!row||row.formId!==unit.unitId)return unit;
    if(['maxHp','atk','def','rec'].some(k=>!Number.isSafeInteger(unit[k])||
        unit[k]<1||unit[k]>100000000))return unit;
    const actual=row.applied;
    const next=[unit.maxHp+actual[0],unit.atk+actual[1],
      unit.def+actual[2],unit.rec+actual[3]];
    if(next.some(n=>!Number.isSafeInteger(n)||n<1||n>100000000))return unit;
    unit.maxHp=unit.hp=next[0];
    unit.atk=next[1];unit.def=next[2];unit.rec=next[3];
    audits.set(unit,freeze({baseId:unit.baseId,formId:unit.unitId,
      applied:actual,customCap:row.mode==='custom',saveFieldsAdded:1}));
    return unit;
  }
  function snapshot(){
    synchronize();
    const rows=Array.isArray(S.party)?S.party.map(unit=>audits.get(unit)).
      filter(Boolean):[];
    return freeze({enabled:!!state,mode:state?.mode||'off',
      ownedForms:P.roster.length,inventory:stock(),rows:freeze(rows),
      noCanonicalSaveMutation:false,original2022Caps:true,
      impFeedValuesOriginal:true,customCeilingMultiplier:1.25,
      sidecarKey:null,legacySidecarKey:key,canonicalField,saveFieldsAdded:1});
  }
  function modeChange(value){
    synchronize();
    if(!state||!['original','custom'].includes(value))return false;
    const next=copy(state);next.mode=value;
    const done=persist(next);if(done)refresh();return done;
  }
  function exportState(){synchronize();return state?JSON.stringify(state):null;}
  function importState(raw){
    synchronize();
    if(typeof raw!=='string'||raw.length>250000)return false;
    let data;try{data=validState(JSON.parse(raw));}catch(_){return false;}
    if(!data)return false;
    const previousInvalid=invalidStorage;
    invalidStorage=false;
    const done=persist(data);
    if(!done)invalidStorage=previousInvalid;
    if(done)refresh();return done;
  }
  // User-triggered control; no auto-granted legacy quest rewards or Gem changes.
  const panel=document.createElement('details');
  panel.id='bf16900-imp-fusion';
  panel.style.cssText='margin:9px 3px;padding:10px;border:1px solid #a5c7b0;'+
    'border-radius:8px;background:#243637;color:#eff9ed;font:12px/1.5 system-ui';
  const heading=document.createElement('summary');heading.textContent=
    'IMPS · ORIGINAL GAINS / OPTIONAL +25% CAPS';
  heading.style.cssText='cursor:pointer;min-height:40px;font-weight:800';
  const status=document.createElement('p');
  const selector=document.createElement('select');selector.id='bf16900-owned';
  selector.setAttribute('aria-label','Choose owned unit for Imp fusion');
  selector.style.cssText='width:100%;min-height:40px;margin:5px 0';
  const selectMode=document.createElement('select');selectMode.id='bf16900-mode';
  for(const [v,title] of [['custom','Custom caps (+25%)'],
                           ['original','Original Brave Frontier caps']]){
    const opt=document.createElement('option');opt.value=v;opt.textContent=title;
    selectMode.append(opt);
  }
  selectMode.setAttribute('aria-label','Imp cap mode');
  const stockLine=document.createElement('p');
  const capLine=document.createElement('p');
  const preview=document.createElement('p');
  const enable=document.createElement('button');enable.type='button';
  enable.textContent='ENABLE OPTIONAL IMP FUSION (includes 5 starter Artons)';
  const claimButton=document.createElement('button');claimButton.type='button';
  claimButton.textContent='CLAIM EARNED IMP SUPPLY (2 Artons per new quest clear)';
  const feedButton=document.createElement('button');feedButton.type='button';
  feedButton.textContent='SMART BATCH FEED (no zero-gain materials)';
  const backups=document.createElement('details');
  const backupHeading=document.createElement('summary');
  backupHeading.textContent='Imp progress in main v7 save · separate legacy import';
  const backupText=document.createElement('textarea');
  backupText.id='bf16900-backup';backupText.rows=4;
  backupText.style.cssText='width:100%;min-height:80px;color:#182322';
  backupText.setAttribute('aria-label','Optional Imp progress JSON');
  const exportButton=document.createElement('button');exportButton.type='button';
  exportButton.textContent='SHOW IMP BACKUP';
  const importButton=document.createElement('button');importButton.type='button';
  importButton.textContent='RESTORE IMP BACKUP TO CURRENT SAVE';
  const migrateButton=document.createElement('button');migrateButton.type='button';
  migrateButton.textContent='IMPORT LEGACY v169 IMPS INTO THIS SAVE';
  const notice=document.createElement('small');
  notice.textContent='Imp enhancement is optional, applied to newly built archive DEMO squads only. '+
    'Original per-form caps and Imp feeding gains are preserved. The +25% cap mode, '+
    'starter Artons and two-Arton-per-new-clear supply are OFFLINE QoL, NOT original Global drops. '+
    'No Gems awarded. Training and saved EXP remain unchanged. '+
    'Imp progress is now included in full v7 exports and rotating backups. '+
    'Legacy v169 Imp sidecars are NOT auto-linked to another save; import only '+
    'if you know those Imps belong to this exact save.';
  for(const button of [enable,claimButton,feedButton,exportButton,importButton,migrateButton]){
    button.style.cssText='padding:8px;margin:5px 4px 4px 0;min-height:38px';
  }
  backups.append(backupHeading,backupText,exportButton,importButton,migrateButton);
  panel.append(heading,status,enable,selector,selectMode,stockLine,
    capLine,preview,claimButton,feedButton,backups,notice);
  host.after(panel);
  let message='';
  function refresh(){
    synchronize();
    const selected=Number(selector.value);
    const old=selected;
    selector.replaceChildren();
    for(const baseId of P.roster){
      const formId=formOf(baseId);
      if(!original(formId))continue;
      const opt=document.createElement('option');opt.value=String(baseId);
      opt.textContent='Unit #'+formId+' (owned base #'+baseId+')';
      selector.append(opt);
    }
    if([...selector.options].some(o=>Number(o.value)===old))selector.value=String(old);
    const baseId=Number(selector.value),current=view(baseId),prediction=plan(baseId);
    status.textContent=invalidStorage?
      'Saved Imp state is invalid; no enhancements or rewards applied. Restore valid backup.' :
      !state?'Imp fusion inactive. Activate explicitly to create optional Imp progress.' :
      'Imp fusion ACTIVE · next-battle stats only · '+(message||'No changes to core v7 saves');
    enable.hidden=!!state||invalidStorage;
    selector.disabled=!state;selectMode.disabled=!state;
    selectMode.value=state?.mode||'custom';
    const inv=stock();
    stockLine.textContent='Owned Imps: '+ids.map(id=>names[id]+' ×'+inv[id]).join(' · ');
    capLine.textContent=current?
      'Imp caps HP/ATK/DEF/REC: '+current.maximum.join(' / ')+
      ' · fed '+current.stored.join(' / '):
      'Select an eligible owned form (unknown or unowned forms cannot receive Imps)';
    preview.textContent=prediction?
      'Smart batch preview: '+prediction.total+' materials; '+
      ids.filter(id=>prediction.materials[id]>0).map(id=>names[id]+
        ' ×'+prediction.materials[id]).join(', ')+
      '; expected stat gains '+prediction.gained.join(' / '):
      'No available smart feed preview';
    claimButton.disabled=!state;feedButton.disabled=!prediction?.total;
    let legacyAvailable=false;
    if(!state){try{legacyAvailable=!!validState(JSON.parse(localStorage.getItem(key)||'null'));}catch(_){}}
    migrateButton.disabled=!legacyAvailable||invalidStorage;
    return current;
  }
  selector.addEventListener('change',refresh);
  enable.addEventListener('click',()=>{
    message=activate()?'Enabled; starter Artons received.':'Could not safely enable Imp fusion.';
    refresh();
  });
  selectMode.addEventListener('change',()=>{message=modeChange(selectMode.value)?
    'Mode saved; new battle constructions use this cap.':'Mode change not saved.';refresh();});
  claimButton.addEventListener('click',()=>{const n=claim();message=n?
    'Claimed '+n+' optional Artons from new DEMO quest clears.':
    'No new eligible quest clears or no inventory room.';refresh();});
  feedButton.addEventListener('click',()=>{
    const result=feed(Number(selector.value));message=result?
      'Fed '+result.total+' Imps; bonuses take effect next archive battle.':
      'No beneficial Imp materials available; no inventory spent.';refresh();
  });
  exportButton.addEventListener('click',()=>{backupText.value=exportState()||'';});
  importButton.addEventListener('click',()=>{message=importState(backupText.value)?
    'Imp progress stored with the current v7 save.':
    'Invalid Imp backup; current save was not changed.';refresh();});
  function legacyImport(){
    synchronize();
    if(state||invalidStorage)return false;
    let raw;
    try{raw=localStorage.getItem(key);}catch(_){return false;}
    if(!raw||raw.length>250000)return false;
    let data;try{data=validState(JSON.parse(raw));}catch(_){return false;}
    if(!data)return false;
    // Imported saves with higher quest counters must never earn unplayed
    // Arton supply merely because the v169 cursor belonged to another save.
    const current=cursorsNow();
    for(const [id,n] of Object.entries(current))
      data.cursors[id]=Math.max(data.cursors[id]??0,n);
    return importState(JSON.stringify(data));
  }
  migrateButton.addEventListener('click',()=>{
    const yes=typeof confirm==='function'?
      confirm('Only migrate v169 Imp progress if it belongs to THIS game save. Continue?'):true;
    message=yes&&legacyImport()?'Legacy Imps safely moved into the current v7 save.':
      'No legacy import performed. No save changed.';
    refresh();
  });
  window.BFGlobalOptionalImpsV16900=freeze({
    key,gains,names,original,maximum,bonus,view,stock,plan,feed,claim,
    activate,modeChange,exportState,importState,legacyImport,apply,snapshot,refresh
  });
  refresh();
})();