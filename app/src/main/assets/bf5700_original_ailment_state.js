/* BF_GLOBAL_ORIGINAL_AILMENT_STATE_V5700 */
(() => {
 'use strict';
 // Source-aligned ailment identity and cures. Does not invent infliction,
 // damage-over-time, action denial, duration, or persistent item ownership.
 if(window.BFGlobalOriginalAilmentStateV5700||
    typeof P==='undefined'||P.version!==7||typeof S==='undefined')return;
 const meta=document.getElementById('meta');
 const mode=document.getElementById('mode');
 if(!meta||!mode)return;
 const cureItems=Object.freeze([
  Object.freeze({itemId:20200,name:'Poison remedy',codes:Object.freeze([1])}),
  Object.freeze({itemId:20210,name:'Weakness/disease/injury remedy',codes:Object.freeze([2,3,4])}),
  Object.freeze({itemId:20220,name:'Curse remedy',codes:Object.freeze([5])}),
  Object.freeze({itemId:20230,name:'Paralysis remedy',codes:Object.freeze([6])}),
  Object.freeze({itemId:50200,name:'All-ailment remedy',codes:Object.freeze([1,2,3,4,5,6])})
 ]);
 const source=Object.freeze({
  archive:'mst-decoded.zip',
  archiveSha256:'69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9',
  table:'3-mst-translated/F_ITEM_MST_Ver1027.json',
  tableSha256:'0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474',
  itemEffectRowsInCatalog:99, cureItems
 });
 const labels=Object.freeze({
  1:'Poison',2:'Weakness',3:'Sickness',4:'Injury',5:'Curse',6:'Paralysis'
 });
 const css=document.createElement('style');css.id='bf5700-style';
 css.textContent='#bf5700-ailments{font:11px/1.5 system-ui,sans-serif;padding:6px 8px;margin:5px 0;border:1px solid #bfa57a;border-radius:4px;background:#342d2c;color:#f4e4ce}' +
 '#bf5700-ailments[hidden]{display:none!important}';
 document.head.append(css);
 const panel=document.createElement('aside');panel.id='bf5700-ailments';
 panel.setAttribute('aria-label','Tracked battle status ailments');
 meta.after(panel);
 let battle=S,last='',issuance=0;
 const entries=new Map();
 function sync(){
  if(S!==battle){battle=S;entries.clear();last='';}
  for(const [slot,record] of entries){
   const p=S.party?.[slot];
   if(p!==record.unit||!p.active||p.hp<=0){entries.delete(slot);last='';}
  }
 }
 function legalUnit(slot){
  const p=S.party?.[slot];
  return S.mode==='archive'&&!S.over&&Number.isInteger(slot)&&
   slot>=0&&slot<6&&!!p&&p.active&&p.hp>0;
 }
 function codesFor(slot){
  sync();
  const record=entries.get(slot);
  return Object.freeze(record?Array.from(record.codes).sort((a,b)=>a-b):[]);
 }
 function snapshot(){
  sync();
  const units=Object.freeze(Array.from(entries,([slot,r])=>Object.freeze({
   slot,unitName:r.unit.name,codes:codesFor(slot)
  })).sort((a,b)=>a.slot-b.slot));
  return Object.freeze({source,mode:S.mode,round:S.round,units});
 }
 function refresh(){
  const st=snapshot();
  const key=JSON.stringify(st.units);
  panel.hidden=S.mode!=='archive'||st.units.length===0;
  if(last===key)return st;
  last=key;
  panel.textContent='SOURCE STATUS IDENTITIES · DEMO STATE ONLY: '+
   st.units.map(u=>u.unitName+' ['+u.codes.map(c=>labels[c]).join(', ')+']').join(' · ')+
   ' (native damage/turn rules not yet decoded)';
  return st;
 }
 // Integration point for future verified enemy attacks and Brave Burst effects.
 // It tracks state only; it DOES NOT inflict game-system damage or action denial.
 function inflict(slot,code){
  sync();
  if(!legalUnit(slot)||!Number.isInteger(code)||code<1||code>6)return false;
  // v91: 2022 original innate 100% resistance blocks NEW ailments.
  // Fail open when optional original resistance module is absent.
  if(window.BFGlobalInnateStatusResistV9100?.immune(slot,code))return false;
  // v76: optional source-backed Nullifier prevents NEW ailments only.
  // Absence of the optional module preserves the previous ailment engine.
  if(window.BFGlobalStatusNegationV7600?.immune(slot,code))return false;
  const p=S.party[slot];
  let record=entries.get(slot);
  if(!record){record={unit:p,codes:new Set(),tokens:new Map()};entries.set(slot,record);}
  if(record.codes.has(code))return false;
  record.codes.add(code);record.tokens.set(code,++issuance);
  last='';refresh();return true;
 }
 function cure(slot,itemId){
  sync();
  const item=cureItems.find(x=>x.itemId===itemId);
  if(!item||!legalUnit(slot))return null;
  const record=entries.get(slot);
  const removed=record?item.codes.filter(code=>record.codes.delete(code)):[];
  if(record)for(const code of removed)record.tokens.delete(code);
  if(record&&record.codes.size===0)entries.delete(slot);
  if(removed.length){last='';refresh();}
  return Object.freeze({itemId,slot,
   removed:Object.freeze(removed),remaining:codesFor(slot)});
 }
 // Expiring code 2 must not erase independent codes 3 and 4 merely
 // because the original item #20210 cures all three at once.
 function removeCode(slot,code){
  sync();
  if(!legalUnit(slot)||!Number.isInteger(code)||code<1||code>6)return false;
  const record=entries.get(slot);
  if(!record||!record.codes.delete(code))return false;
  record.tokens.delete(code);
  if(record.codes.size===0)entries.delete(slot);
  last='';refresh();return true;
 }
 function tokenFor(slot,code){
  sync();
  const record=entries.get(slot);
  if(!Number.isInteger(code)||code<1||code>6||!record?.codes.has(code))return null;
  return record.tokens.get(code)??null;
 }
 function clear(slot){
  sync();
  if(!Number.isInteger(slot)||slot<0||slot>=6)return false;
  const changed=entries.delete(slot);if(changed){last='';refresh();}
  return changed;
 }
 mode.addEventListener('change',refresh);
 window.setInterval(()=>{if(!document.hidden)refresh()},900);
 window.BFGlobalOriginalAilmentStateV5700=Object.freeze({
  source,labels,snapshot,codesFor,inflict,cure,removeCode,tokenFor,clear,refresh
 });
 refresh();
})();