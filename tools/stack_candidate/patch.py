from pathlib import Path
import hashlib
root=Path('/tmp/bf-a5/assets')
# Disposable candidate only: no acquisition, no source/build integration.
def change(s,a,b):
 assert s.count(a)==1,(a[:100],s.count(a));return s.replace(a,b,1)
p=root/'index.html';s=p.read_text();print('base index',hashlib.sha256(p.read_bytes()).hexdigest())
codec='''const OWNED_COPY_FIRST=1000000001, OWNED_COPY_LAST=9999999999;
const OWNED_COPY_META='_bfUnitInstancesV1', COPY_ORGANIZATION='_bfCopyOrganizationV1';
function ownedCopyBase(id,meta){
 if(!Number.isSafeInteger(id))return null;
 if(ALL_IDS.includes(id))return id;
 return meta&&Object.hasOwn(meta.baseById,String(id))?meta.baseById[id]:null;
}
function decodeOwnedCopies(data){
 if(!Object.hasOwn(data,OWNED_COPY_META))return null;
 const bad=()=>{throw new Error('Invalid owned unit instances');};
 const record=x=>!!x&&typeof x==='object'&&!Array.isArray(x)&&(Object.getPrototypeOf(x)===Object.prototype||Object.getPrototypeOf(x)===null);
 const raw=data[OWNED_COPY_META];
 if(data.version!==7||!record(raw)||Object.keys(raw).sort().join(',')!=='baseById,nextId'||!Number.isSafeInteger(raw.nextId)||raw.nextId<OWNED_COPY_FIRST||raw.nextId>OWNED_COPY_LAST+1||!record(raw.baseById)||!Array.isArray(data.roster)||!record(data.unitExp)||new TextEncoder().encode(JSON.stringify(data,null,2)).length>1048576)bad();
 const owned=new Set(data.roster),baseById={};
 for(const [key,base] of Object.entries(raw.baseById)){
  const id=Number(key);
  if(!Number.isSafeInteger(id)||String(id)!==key||id<OWNED_COPY_FIRST||id>OWNED_COPY_LAST||id>=raw.nextId||ALL_IDS.includes(id)||!ALL_IDS.includes(base)||!owned.has(id)||!Object.hasOwn(data.unitExp,key))bad();
  baseById[key]=base;
 }
 return {nextId:raw.nextId,baseById};
}
function effectiveUnit(baseId){const sourceId=ownedCopyBase(baseId,P[OWNED_COPY_META]);return sourceId===null?undefined:UNIT_BY_ID.get(P.evolutions[baseId]||sourceId);}
function decodeCopyOrganization(data,roster,copies){
 if(!Object.hasOwn(data,COPY_ORGANIZATION))return null;
 const raw=data[COPY_ORGANIZATION],owned=new Set(roster),bad=()=>{throw new Error('Invalid copy organization');};
 const isCopy=id=>Number.isSafeInteger(id)&&owned.has(id)&&!!copies&&Object.hasOwn(copies.baseById,String(id));
 if(data.version!==7||!copies||!raw||typeof raw!=='object'||Array.isArray(raw)||Object.keys(raw).sort().join(',')!=='favorites,locked,presets'||!Array.isArray(raw.presets)||raw.presets.length!==5)bad();
 const list=ids=>{if(!Array.isArray(ids)||ids.length>5000||ids.some(id=>!isCopy(id))||new Set(ids).size!==ids.length)bad();return ids.slice().sort((a,b)=>a-b);};
 const presets=raw.presets.map(slot=>{if(slot===null)return null;if(!slot||typeof slot!=='object'||Array.isArray(slot)||Object.keys(slot).sort().join(',')!=='name,squad'||typeof slot.name!=='string'||!slot.name.trim()||slot.name.length>28||!Array.isArray(slot.squad)||slot.squad.length<1||slot.squad.length>6||new Set(slot.squad).size!==slot.squad.length||slot.squad.some(id=>!Number.isSafeInteger(id)||!owned.has(id))||!slot.squad.some(isCopy))bad();return {name:slot.name,squad:slot.squad.slice()};});
 return {favorites:list(raw.favorites),locked:list(raw.locked),presets};
}
function copyOrgRead(){return P[COPY_ORGANIZATION]||{favorites:[],locked:[],presets:Array(5).fill(null)};}
function copyOrgCommit(mutator){
 if(saveRecoveryPending||S?.busy||S?.auto&&!S.over||!P[OWNED_COPY_META])return false;
 const before=P;let rawBefore,next,expected;
 try{rawBefore=localStorage.getItem(SAVE_KEY);if(rawBefore!==JSON.stringify(before))return false;
  next=JSON.parse(rawBefore);const org=next[COPY_ORGANIZATION]||{favorites:[],locked:[],presets:Array(5).fill(null)};
  if(!mutator(org))return false;next[COPY_ORGANIZATION]=decodeCopyOrganization({...next,[COPY_ORGANIZATION]:org},next.roster,next[OWNED_COPY_META]);
  parseProgress(next);if(new TextEncoder().encode(JSON.stringify(next,null,2)).length>1048576)return false;expected=JSON.stringify(next);
 }catch(_){return false;}
 P=next;let ok=false,observed;try{ok=saveProgress()===true;observed=localStorage.getItem(SAVE_KEY);}catch(_){}
 if(ok&&P===next&&JSON.stringify(P)===expected&&observed===expected)return true;
 P=before;saveEnabled=false;
 try{if(observed===expected){localStorage.setItem(SAVE_KEY,rawBefore);observed=localStorage.getItem(SAVE_KEY);}if(observed===rawBefore)return false;}catch(_){}
 saveRecoveryPending=true;return false;
}
'''
s=change(s,'function effectiveUnit(baseId){return UNIT_BY_ID.get(P.evolutions[baseId]||baseId);}',codec)
s=change(s," const out=defaultProgress();for(const key of ['exp','zel','karma','clears'])out[key]=limitNumber(data[key]);", " const out=defaultProgress(),copies=decodeOwnedCopies(data);const known=id=>ownedCopyBase(id,copies)!==null;const copyIds=copies?Object.keys(copies.baseById).map(Number):[];const copyIdSet=new Set(copyIds);if(copies)out[OWNED_COPY_META]=copies;for(const key of ['exp','zel','karma','clears'])out[key]=limitNumber(data[key]);")
s=change(s,'data.squad.some(id=>!ALL_IDS.includes(id))','data.squad.some(id=>!known(id))')
s=change(s,'for(const id of ALL_IDS)out.unitExp[id]=limitNumber(data.unitExp?.[id]??0);','for(const id of [...ALL_IDS,...copyIds])out.unitExp[id]=limitNumber(copyIdSet.has(id)?data.unitExp[id]:data.unitExp?.[id]??0);')
s=change(s,'data.roster.length>ALL_IDS.length||data.roster.some(id=>!ALL_IDS.includes(id))','data.roster.length>ALL_IDS.length+copyIds.length||data.roster.some(id=>!known(id))')
s=change(s,'const recipe=EVO_RECIPES.find(r=>r.baseId===Number(bid) && r.evolvedId===value);',"const recipe=EVO_RECIPES.find(r=>r.baseId===ownedCopyBase(Number(bid),copies) && r.evolvedId===value);if(copies&&String(Number(bid))!==bid)throw new Error('Invalid evolution identity');")
s=change(s,'out._bfImpsV171=bf171ValidateCanonicalImps(data._bfImpsV171);',"out._bfImpsV171=bf171ValidateCanonicalImps(data._bfImpsV171);const organization=decodeCopyOrganization(data,out.roster,copies);if(organization)out[COPY_ORGANIZATION]=organization;if(copies&&out._bfImpsV171&&Object.keys(out._bfImpsV171.amounts).some(k=>Number(k)>=OWNED_COPY_FIRST&&!Object.hasOwn(copies.baseById,k)))throw new Error('Unowned copy Imp amount');")
s=change(s,'P._bfImpsV171=bf171ValidateCanonicalImps(P._bfImpsV171);',"P._bfImpsV171=bf171ValidateCanonicalImps(P._bfImpsV171);if(Object.hasOwn(P,OWNED_COPY_META)||Object.hasOwn(P,COPY_ORGANIZATION)){const checked=parseProgress(P);if(checked[COPY_ORGANIZATION])P[COPY_ORGANIZATION]=checked[COPY_ORGANIZATION];if(new TextEncoder().encode(JSON.stringify(P,null,2)).length>1048576)throw new Error('Copy save exceeds transfer limit');}")
p.write_text(s)
p=root/'bf_home_nav.js';s=p.read_text()
s=change(s,'  let activeId = null;\n  function ownedUnits()', '''  let activeId = null;
  const stackToggle=document.createElement('input');stackToggle.type='checkbox';stackToggle.id='bf-copy-stack-toggle';
  const stackLabel=document.createElement('label');stackLabel.append(stackToggle,document.createTextNode(' Stack matching forms (preview)'));stackLabel.hidden=true;stackLabel.style.cssText='display:block;min-height:44px';stackLabel.style.display='none';results.before(stackLabel);
  stackToggle.addEventListener('change',refresh);
  function ownedUnits()''')
s=change(s,'const recipe=EVO_RECIPES.find(row=>row.baseId===id);','const recipe=EVO_RECIPES.find(row=>row.baseId===(typeof ownedCopyBase===\'function\'?ownedCopyBase(id,P[OWNED_COPY_META]):id));')
s=change(s,"form.textContent='Base roster ID '+id+' · Current form '+unit.id", "form.textContent='Owned ID '+id+' · Current form '+unit.id")
s=change(s,'    for(const {id,unit} of filtered){','''    const copyMode=typeof OWNED_COPY_META!=='undefined'&&!!P[OWNED_COPY_META];stackLabel.hidden=!copyMode;stackLabel.style.display=copyMode?'block':'none';
    const groups=new Map(),targets=new Map();
    if(copyMode&&stackToggle.checked){
      for(const row of filtered){const source=ownedCopyBase(row.id,P[OWNED_COPY_META]);const key=JSON.stringify([source,row.unit.id]);if(!groups.has(key))groups.set(key,[]);groups.get(key).push(row);}
    }
    for(const rows of groups.values())if(rows.length>1){
      const group=document.createElement('details');group.className='bf-copy-stack';group.style.cssText='grid-column:1/-1;min-width:0';
      const heading=document.createElement('summary');heading.style.cssText='min-height:44px;cursor:pointer';heading.textContent=rows[0].unit.name+' ×'+rows.length+' · type unavailable';
      const body=document.createElement('div');body.className='bf-box-results';group.append(heading,body);group.open=rows.some(row=>row.id===activeId);results.append(group);
      for(const row of rows)targets.set(row.id,body);
      group.addEventListener('toggle',()=>window.BFGlobalQoLUnitFlagsV10200?.refresh());
    }
    for(const {id,unit} of filtered){''')
s=change(s,"card.setAttribute('aria-label',unit.name+', level '+demoLevel(P.unitExp[id]||0));","card.setAttribute('aria-label',unit.name+', level '+demoLevel(P.unitExp[id]||0)+(id>=1000000001?', copy '+id:''));")
s=change(s,"state.textContent=P.squad.includes(id)?'ACTIVE':'RESERVE';","state.textContent=(P.squad.includes(id)?'ACTIVE':'RESERVE')+(id>=1000000001?' · #'+id:'');")
s=change(s,'      results.append(card);\n    }\n    if (activeId', '      (targets.get(id)||results).append(card);\n    }\n    if (activeId')
s=change(s,"    for (const card of results.querySelectorAll('button[data-bf-unit-id]')) card.setAttribute('aria-pressed', String(Number(card.dataset.bfUnitId) === id));", "    for (const card of results.querySelectorAll('button[data-bf-unit-id]')) {const selected=Number(card.dataset.bfUnitId)===id;card.setAttribute('aria-pressed',String(selected));if(selected&&card.closest('details.bf-copy-stack'))card.closest('details.bf-copy-stack').open=true;}")
p.write_text(s)
p=root/'bf10200_qol_unit_flags.js';s=p.read_text()
s=change(s,"node.hidden || node.style.display==='none'","node.hidden || node.style.display==='none' || node.closest('details.bf-copy-stack:not([open])')")
s=change(s,'filter(x=>x>0)','filter(x=>x>0&&x<1000000001)')
s=change(s,' let flags=load();',''' let flags=load();
 const copyId=id=>id>=1000000001;
 const marked=(id,kind)=>copyId(id)?(typeof copyOrgRead==='function'&&copyOrgRead()[kind].includes(id)):flags[kind].includes(id);
 const markedCount=kind=>P.roster.filter(id=>marked(id,kind)).length;''')
s=change(s,'   const fav=new Set(flags.favorites),lock=new Set(flags.locked);', '''   if(copyId(id)){
     if(typeof copyOrgCommit!=='function'||!copyOrgCommit(org=>{const ids=new Set(org[kind]);if(on)ids.add(id);else ids.delete(id);org[kind]=[...ids];return true;}))return false;
     refresh();return true;
   }
   const fav=new Set(flags.favorites),lock=new Set(flags.locked);''')
s=s.replace('flags.favorites.includes(id)',"marked(id,'favorites')").replace('flags.locked.includes(id)',"marked(id,'locked')").replace('flags.favorites.filter(validId).length',"markedCount('favorites')").replace('flags.locked.filter(validId).length',"markedCount('locked')")
s=change(s,"   const s=state();\n   favorite.disabled", "   for(const group of results.querySelectorAll('details.bf-copy-stack')){const cards=[...group.querySelectorAll('.bf-box-card')].filter(c=>!c.hidden);group.hidden=!cards.length;const summary=group.querySelector('summary');if(summary){const label=summary.textContent.replace(/×\\d+/, '×'+cards.length);if(summary.textContent!==label)summary.textContent=label;}}\n   const s=state();\n   favorite.disabled")
s=change(s,"'Markers are stored locally and do not modify the game save. '+", "'Legacy markers stay local; duplicate markers travel with the canonical save. '+")
p.write_text(s)
p=root/'bf10000_qol_squad_presets.js';s=p.read_text()
s=change(s,'if(!slot||!goodIds(slot.squad,false))return null;', 'if(!slot||!goodIds(slot.squad,false)||slot.squad.some(id=>id>=1000000001))return null;')
s=change(s,' function store(slots){', """ const copyMode=()=>typeof OWNED_COPY_META!=='undefined'&&!!P[OWNED_COPY_META];
 function currentSlots(){return copyMode()?copyOrgRead().presets.map(slot=>slot?{name:slot.name,squad:slot.squad.slice()}:null):load();}
 function store(slots){
   if(copyMode())return typeof copyOrgCommit==='function'&&copyOrgCommit(org=>{org.presets=slots;return true;});
   if(slots.some(slot=>slot?.squad.some(id=>id>=1000000001)))return false;""")
s=change(s,'let slots=load(),message=', 'let slots=currentSlots(),message=')
for name in ['info()','savePreset(index,name=\'\')','deletePreset(index)','renamePreset(index,name)','duplicatePreset(index)','applyPreset(index)','refresh()']:
 a=' function '+name+'{';s=change(s,a,a+'\n   slots=currentSlots();')
s=change(s,'   const next=slots.slice();\n   next[index]={name:normalizeName(name,index),squad:P.squad.slice()};', "   if(copyMode()&&!P.squad.some(id=>id>=1000000001)){message='Copy-save presets require at least one duplicate; legacy slots are unchanged.';refresh();return false;}\n   const next=slots.slice();\n   next[index]={name:normalizeName(name,index),squad:P.squad.slice()};")
s=change(s,"'Preset labels do not travel inside exported v7 saves. '+", "'Legacy presets stay local. Copy-save presets travel with the save, use separate slots, and require a duplicate. '+")
s=change(s," name.value=slots[Number(selected.value)]?.name||'';", " slots=currentSlots();name.value=slots[Number(selected.value)]?.name||'';")
p.write_text(s)
print('candidate patched')
