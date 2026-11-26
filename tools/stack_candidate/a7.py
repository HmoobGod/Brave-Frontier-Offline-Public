"""Apply only to staged A6 candidate. Never runs Gradle or modifies accepted APK."""
from pathlib import Path
import sys,hashlib
root=Path(sys.argv[1]);p=root/'index.html';s=p.read_text()
assert hashlib.sha256(p.read_bytes()).hexdigest()=='82023b14a7ae35644e9e4b31fb50277550b4f3c78683a5fa853752894cfee07f'
def edit(a,b):
 global s
 assert s.count(a)==1,(a[:100],s.count(a));s=s.replace(a,b,1)
edit("const OWNED_COPY_FIRST=1000000001, OWNED_COPY_LAST=9999999999;","const OWNED_COPY_FIRST=1000000001, OWNED_COPY_LAST=9999999999;\nlet copySaveEpoch=0;")
edit('   btn.onclick=()=>performTraining(base.id,count);', '''   const renderedProgress=P;
   btn.onclick=()=>{if(P!==renderedProgress&&(P[OWNED_COPY_META]||renderedProgress[OWNED_COPY_META]))return;performTraining(base.id,count);};''')
edit('P[OWNED_COPY_META]&&(P!==renderedProgress||saveRecoveryPending||S?.auto&&!S.over)', '(P[OWNED_COPY_META]||renderedProgress[OWNED_COPY_META])&&(P!==renderedProgress||saveRecoveryPending||S?.auto&&!S.over)') if False else None
# Two deliberately separate guarded stale-handler edits.
a='P[OWNED_COPY_META]&&(P!==renderedProgress||saveRecoveryPending||S?.auto&&!S.over)';assert s.count(a)==2;s=s.replace(a,'(P[OWNED_COPY_META]||renderedProgress[OWNED_COPY_META])&&(P!==renderedProgress||saveRecoveryPending||S?.auto&&!S.over)')
edit('function bfImportSaveText(input,sourceLabel){','''// Strict replacement for copy-bearing transfers. Never reset battle on unconfirmed persistence.
function copyTransferCommit(incoming){
 if(saveRecoveryPending||S?.busy||S?.auto&&!S.over)return false;
 const before=P;let rawBefore,undoBefore,expected,backupWritten=false,observed;
 try{
  rawBefore=localStorage.getItem(SAVE_KEY);undoBefore=localStorage.getItem(BF_IMPORT_UNDO_KEY);
  if(rawBefore!==JSON.stringify(before))return false;
  expected=JSON.stringify(incoming);
  if(new TextEncoder().encode(JSON.stringify(incoming,null,2)).length>MAX_SAVE_FILE_BYTES)return false;
  localStorage.setItem(BF_IMPORT_UNDO_KEY,rawBefore);backupWritten=localStorage.getItem(BF_IMPORT_UNDO_KEY)===rawBefore;
  if(!backupWritten)throw Error('Undo backup not verified');
  P=incoming;
  if(saveProgress()===true&&JSON.stringify(P)===expected&&localStorage.getItem(SAVE_KEY)===expected){copySaveEpoch++;return true;}
 }catch(_){}
 P=before;saveEnabled=false;
 try{
  observed=localStorage.getItem(SAVE_KEY);
  if(typeof expected==='string'&&observed===expected&&typeof rawBefore==='string'){localStorage.setItem(SAVE_KEY,rawBefore);observed=localStorage.getItem(SAVE_KEY);}
  const backupNow=localStorage.getItem(BF_IMPORT_UNDO_KEY);
  if(backupNow===rawBefore&&undoBefore!==undefined){if(undoBefore===null)localStorage.removeItem(BF_IMPORT_UNDO_KEY);else localStorage.setItem(BF_IMPORT_UNDO_KEY,undoBefore);}
  if(typeof rawBefore==='string'&&observed===rawBefore&&localStorage.getItem(BF_IMPORT_UNDO_KEY)===undoBefore)return false;
 }catch(_){}
 saveRecoveryPending=true;return false;
}
function copyTransferRefresh(){
 try{window.BFUnitBox?.refresh?.();window.BFGlobalQoLUnitFlagsV10200?.refresh?.();window.BFGlobalQoLSquadPresetsV10000?.refresh?.();}catch(_){}
}
function bfImportSaveText(input,sourceLabel){''')
edit("  if(!confirm(warning))return false;\n  try{localStorage.setItem(BF_IMPORT_UNDO_KEY,JSON.stringify(P));}",'''  if(!confirm(warning))return false;
  if(P[OWNED_COPY_META]||incoming[OWNED_COPY_META]){
   if(!copyTransferCommit(incoming)){bfTransferNotice('Copy save not imported: stop Auto, verify storage and retry only after recovery.');return false;}
   reset();renderProgress();copyTransferRefresh();bfTransferNotice('Copy save imported and verified. Undo backup retained.');return true;
  }
  try{localStorage.setItem(BF_IMPORT_UNDO_KEY,JSON.stringify(P));}''')
edit("if(typeof input!=='string'||input.length>MAX_SAVE_FILE_BYTES)","if(typeof input!=='string'||new TextEncoder().encode(input).length>MAX_SAVE_FILE_BYTES)")
edit(" const raw=JSON.stringify(P,null,2),filename=bfSaveFileName();"," const raw=JSON.stringify(P,null,2),filename=bfSaveFileName();\n if(new TextEncoder().encode(raw).length>MAX_SAVE_FILE_BYTES){bfTransferNotice('Save exceeds the 1 MB transfer limit.');return;}")
edit("$('exportsave').onclick=()=>{$('savetc').value=JSON.stringify(P,null,2);", "$('exportsave').onclick=()=>{const raw=JSON.stringify(P,null,2);if(new TextEncoder().encode(raw).length>MAX_SAVE_FILE_BYTES){bfTransferNotice('Save exceeds the 1 MB transfer limit.');return;}$('savetc').value=raw;")
edit(" P=defaultProgress();saveProgress();reset();renderProgress();msg('Created a new demo save.');"," if(P[OWNED_COPY_META]){alert('Reset is unavailable for this experimental copy save. Export a backup first.');return;}\n P=defaultProgress();saveProgress();reset();renderProgress();msg('Created a new demo save.');")
# Explicit disposable-only UI, default off, no change to original summon controls.
edit(' const personal=P._bfGemV170Custom;\n gemButton.textContent=', ''' if(window.BF_STACK_DISPOSABLE_UI===true){
  let duplicateButton=document.getElementById('bf-copy-token-summon');
  if(!duplicateButton){duplicateButton=document.createElement('button');duplicateButton.type='button';duplicateButton.id='bf-copy-token-summon';duplicateButton.style.cssText='min-height:44px;width:100%';E.summonbutton.insertAdjacentElement('afterend',duplicateButton);duplicateButton.addEventListener('click',()=>{
   if(window.BF_STACK_DISPOSABLE_UI!==true||!confirm('Experimental custom demo summon: spend 1 token for a random recruit, duplicates possible?'))return;
   const receipt=customDuplicateSummon();E.summonresult.textContent=receipt.ok?'Recruited '+UNIT_BY_ID.get(receipt.sourceId).name+' · owned #'+receipt.id:'Duplicate summon not saved; no token spent.';renderProgress();copyTransferRefresh();
  });}
  duplicateButton.textContent='EXPERIMENTAL · Summon with duplicates (1 demo token)';duplicateButton.disabled=!!S?.busy||saveRecoveryPending||S?.auto&&!S.over||P.summonTokens<1||P.summonHistory.length>=100;
 }
 const personal=P._bfGemV170Custom;
 gemButton.textContent=''')
p.write_text(s)
p=root/'bf10000_qol_squad_presets.js';s=p.read_text()
edit('   P.squad=slot.squad.slice();\n   // Apply', '''   if(copyMode()){
     if(typeof copyCommitProgress!=='function'||!copyCommitProgress(next=>{next.squad=slot.squad.slice();return true;})){message='Copy preset not saved; active squad unchanged.';refresh();return false;}
     reset();renderProgress();message='Applied saved copy preset '+(index+1)+'.';refresh();return true;
   }
   P.squad=slot.squad.slice();
   // Apply''')
edit('   if(copyMode())return typeof copyOrgCommit===\'function\'&&copyOrgCommit(org=>{org.presets=slots;return true;});',"   if(copyMode()){const ok=typeof copyOrgCommit==='function'&&copyOrgCommit(org=>{org.presets=slots;return true;});if(ok)renderProgress();return ok;}")
p.write_text(s)
p=root/'bf10200_qol_unit_flags.js';s=p.read_text()
edit('     refresh();return true;\n   }\n   const fav=', '     if(typeof renderProgress===\'function\')renderProgress();refresh();return true;\n   }\n   const fav=')
edit('get favorites(){return freeze(flags.favorites.slice())}',"get favorites(){return freeze(P.roster.filter(id=>marked(id,'favorites')))}")
edit('get locked(){return freeze(flags.locked.slice())}',"get locked(){return freeze(P.roster.filter(id=>marked(id,'locked')))}")
p.write_text(s)
p=root/'bf_home_nav.js';s=p.read_text()
edit('  let activeId = null;\n  const stackToggle', "  let activeId = null, observedCopyEpoch=typeof copySaveEpoch==='number'?copySaveEpoch:0;\n  const stackToggle")
edit('    const {owned, filtered, unresolved}=ownedUnits();',"    if(typeof copySaveEpoch==='number'&&copySaveEpoch!==observedCopyEpoch){activeId=null;observedCopyEpoch=copySaveEpoch;stackToggle.checked=false;}\n    const {owned, filtered, unresolved}=ownedUnits();")
p.write_text(s)
print('A7 staged')
