"""Reproducibly patch v0.13.1's bundled HTML at build time.

The GitHub connector's text payload limit prevents replacing the ~4.5 MB
HTML blob directly. This very small, assertive build step keeps the original
HTML source unchanged until the compiled Android assets are prepared.
"""
from pathlib import Path

html = Path(__file__).parent / 'app/src/main/assets/index.html'
s = html.read_text(encoding='utf-8')
OLD = """   const qkey=BF_QUARANTINE_PREFIX+Date.now()+'_'+i;
   const issue={key,raw,message:String(err.message||err),quarantineKey:qkey,stored:false};
   try{localStorage.setItem(qkey,raw);issue.stored=true;}catch(qerr){console.warn('Could not persist quarantine backup',qerr);}
"""
NEW = """   // Stable content-addressed quarantine key avoids multiplying identical
   // backups on every load. Never delete unreadable originals automatically.
   let hash=2166136261;
   for(const c of key+'\\u0000'+raw){hash=Math.imul(hash^c.charCodeAt(0),16777619)>>>0;}
   const qkey=BF_QUARANTINE_PREFIX+hash.toString(16)+'_'+raw.length;
   const issue={key,raw,message:String(err.message||err),quarantineKey:qkey,stored:false};
   try{
    const stored=localStorage.getItem(qkey);
    const slots=typeof localStorage.key==='function'&&Number.isInteger(localStorage.length)
     ?Array.from({length:localStorage.length},(_,n)=>localStorage.key(n)).filter(k=>k&&k.startsWith(BF_QUARANTINE_PREFIX)).length:0;
    if(stored===raw){issue.stored=true;}
    else if(stored===null&&slots<12){localStorage.setItem(qkey,raw);issue.stored=true;}
    else console.warn('Quarantine slot already used or full; original save was not altered',qkey);
   }catch(qerr){console.warn('Could not persist quarantine backup',qerr);}
"""
if s.count(OLD) == 1:
    html.write_text(s.replace(OLD, NEW, 1), encoding='utf-8')
    print('Patched bundled HTML quarantine deduplication.')
elif s.count(NEW) == 1:
    print('Bundled HTML already patched; no change.')
else:
    raise SystemExit('Refusing to patch unexpected HTML; original source not modified.')
