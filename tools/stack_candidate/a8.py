"""A8 guarded changes to disposable A7 generated HTML, no build or activation."""
from pathlib import Path
import sys,hashlib
p=Path(sys.argv[1])/'index.html';s=p.read_text()
assert hashlib.sha256(p.read_bytes()).hexdigest()=='b8ea1a4d9a207dfa6d553b94e6c0a79d2796c7944d498bfb31df0926e240c347'
def edit(old,new):
 global s
 assert s.count(old)==1,(old[:90],s.count(old));s=s.replace(old,new,1)
edit('  const u=effectiveUnit(base.id),op=document.createElement(\'option\');',"  // Archive-only forms are source IDs, not owned instance IDs.\n  const u=effectiveUnit(base.id)||UNIT_BY_ID.get(base.id);if(!u)continue;const op=document.createElement('option');")
edit(" if(P[OWNED_COPY_META]){alert('Reset is unavailable for this experimental copy save. Export a backup first.');return;}",''' if(P[OWNED_COPY_META]){
  let fresh;try{fresh=parseProgress(defaultProgress());}catch(_){bfTransferNotice('New save validation failed; nothing changed.');return;}
  if(!copyTransferCommit(fresh)){bfTransferNotice('Reset not saved; prior copy save retained. Stop Auto and verify storage.');return;}
  reset();renderProgress();copyTransferRefresh();bfTransferNotice('New save verified. Previous copy save retained as Undo backup.');msg('Created a new demo save.');return;
 }''')
p.write_text(s);print('A8 applied',hashlib.sha256(p.read_bytes()).hexdigest())
