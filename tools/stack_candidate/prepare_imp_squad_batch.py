"""Private prepared-source prototype, exact A17 Imp module guard; no new saves."""
import hashlib, pathlib, sys
EXPECTED='c1dec82a0ff73afd74acaa2cb27c79479b4a04457069d152c6920a03c3e56742'
def patch(s):
    if hashlib.sha256(s.encode()).hexdigest()!=EXPECTED: raise ValueError('unexpected prepared Imp module')
    def sub(a,b):
        nonlocal s
        if s.count(a)!=1: raise ValueError('unexpected anchor '+a[:80])
        s=s.replace(a,b,1)
    sub("function plan(baseId,preferred='smart',limit=500){", """function plan(baseId,preferred='smart',limit=500){
    synchronize();
    return state?planWithInventory(baseId,preferred,limit,state.inventory):null;
  }
  function planWithInventory(baseId,preferred,limit,inventory){""")
    sub('const remaining=cur.remaining.slice(),inv={...state.inventory};','const remaining=cur.remaining.slice(),inv={...inventory};')
    sub('  function claim(){', '''  // BF_IMP_SQUAD_BATCH_R1: explicit one-tap, leader-first, atomic v7 write.
  // Never treats a copy as its species ID. Uses existing ownership and cap checks.
  function planSquad(){
    synchronize();
    if(!state||invalidStorage||!Array.isArray(P.squad)||P.squad.length>6)return null;
    const inv={...state.inventory},seen=new Set(),rows=[];
    for(const baseId of P.squad){
      if(baseId===null||baseId===0)continue;
      if(!Number.isSafeInteger(baseId)||seen.has(baseId)||!P.roster.includes(baseId))return null;
      seen.add(baseId);
      const proposed=planWithInventory(baseId,'smart',500,inv);
      if(!proposed)continue; // existing cap lookup excludes unsupported forms
      if(!proposed.total)continue;
      for(const id of ids)inv[id]-=proposed.materials[id];
      rows.push(proposed);
    }
    return freeze({rows:freeze(rows),total:rows.reduce((n,r)=>n+r.total,0),remainingStock:freeze(inv)});
  }
  function feedSquad(){
    const proposed=planSquad();
    if(!proposed?.total)return false;
    const next=copy(state);
    next.inventory={...proposed.remainingStock};
    for(const row of proposed.rows){
      const old=bonus(row.baseId);
      next.amounts[String(row.baseId)]=old.map((n,i)=>n+row.gained[i]);
    }
    if(!persist(next))return false;
    refresh();return proposed;
  }
  function claim(){''')
    sub("  const backups=document.createElement('details');", """  const squadFeedButton=document.createElement('button');squadFeedButton.type='button';
  squadFeedButton.id='bf-imp-squad-feed-r1';
  squadFeedButton.textContent='SMART FEED SQUAD (leader first)';
  const backups=document.createElement('details');""")
    sub('claimButton,feedButton,exportButton,','claimButton,feedButton,squadFeedButton,exportButton,')
    sub('capLine,preview,claimButton,feedButton,backups,notice);','capLine,preview,claimButton,feedButton,squadFeedButton,backups,notice);')
    sub('claimButton.disabled=!state;feedButton.disabled=!prediction?.total;', '''claimButton.disabled=!state;feedButton.disabled=!prediction?.total;
    const squadPreview=planSquad();
    squadFeedButton.disabled=!squadPreview?.total;
    squadFeedButton.textContent='SMART FEED SQUAD (leader first · '+(squadPreview?.total||0)+' Imps)';''')
    sub("  exportButton.addEventListener('click',", """  squadFeedButton.addEventListener('click',()=>{
    const result=feedSquad();message=result?
      'Fed '+result.total+' Imps to '+result.rows.length+' owned squad units; next archive battle.':
      'No squad feed saved; no Imp materials spent.';refresh();
  });
  exportButton.addEventListener('click',""")
    sub('key,gains,names,original,maximum,bonus,view,stock,plan,feed,claim,','key,gains,names,original,maximum,bonus,view,stock,plan,feed,planSquad,feedSquad,claim,')
    return s
if __name__=='__main__':
    src,dst=map(pathlib.Path,sys.argv[1:]);dst.write_text(patch(src.read_text()),encoding='utf-8')
