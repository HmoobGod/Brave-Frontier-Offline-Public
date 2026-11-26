/* BF_STACK_COPY_UI_A12: bounded read-only Unit Box extension. Load before Home.
 * The native Unit Box retains selection, filtering, rendering and ownership.
 * Only groups the already-rendered cards; never writes player state. */
(()=>{
 'use strict';
 if(window.BFStackCopies)return;
 function mount(results,refresh){
  const toggle=document.createElement('input');toggle.type='checkbox';toggle.id='bf-copy-stack-toggle';
  const label=document.createElement('label');label.append(toggle,document.createTextNode(' Stack matching forms (preview)'));label.hidden=true;label.style.cssText='display:none;min-height:44px';results.before(label);
  let epoch=typeof copySaveEpoch==='number'?copySaveEpoch:0;
  const mode=()=>typeof OWNED_COPY_META!=='undefined'&&!!P[OWNED_COPY_META];
  const base=id=>typeof ownedCopyBase==='function'?ownedCopyBase(id,P[OWNED_COPY_META]):id;
  toggle.addEventListener('change',refresh);
  function before(id){
   if(typeof copySaveEpoch==='number'&&copySaveEpoch!==epoch){epoch=copySaveEpoch;toggle.checked=false;return null;}
   return id;
  }
  function group(filtered,activeId){
   const enabled=mode();label.hidden=!enabled;label.style.display=enabled?'block':'none';
   const cards=new Map([...results.querySelectorAll('button[data-bf-unit-id]')].map(card=>[Number(card.dataset.bfUnitId),card]));
   const groups=new Map();
   for(const row of filtered){
    const card=cards.get(row.id);if(!card)continue;
    if(row.id>=1000000001){card.setAttribute('aria-label',card.getAttribute('aria-label')+', copy '+row.id);card.querySelector('small').textContent+=' · #'+row.id;}
    if(enabled&&toggle.checked){const key=JSON.stringify([base(row.id),row.unit.id]);if(!groups.has(key))groups.set(key,[]);groups.get(key).push(row);}
   }
   for(const rows of groups.values())if(rows.length>1){
    const item=document.createElement('details');item.className='bf-copy-stack';item.style.cssText='grid-column:1/-1;min-width:0';
    const heading=document.createElement('summary');heading.style.cssText='min-height:44px;cursor:pointer';heading.textContent=rows[0].unit.name+' ×'+rows.length+' · type unavailable';
    const body=document.createElement('div');body.className='bf-box-results';item.append(heading,body);item.open=rows.some(row=>row.id===activeId);
    results.insertBefore(item,cards.get(rows[0].id));
    for(const row of rows)body.append(cards.get(row.id));
    item.addEventListener('toggle',()=>window.BFGlobalQoLUnitFlagsV10200?.refresh());
   }
  }
  function select(id){const card=[...results.querySelectorAll('button[data-bf-unit-id]')].find(x=>Number(x.dataset.bfUnitId)===id);const item=card?.closest('details.bf-copy-stack');if(item)item.open=true;}
  return {before,group,select,base};
 }
 window.BFStackCopies=Object.freeze({mount});
})();
