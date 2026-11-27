#!/usr/bin/env python3
"""Exact prepared Combined R1 HTML patch. No unit consumption or new save fields."""
from pathlib import Path
import hashlib,sys
BASE='268b08b9ab91f6c4ecd24c18ba15e4b2e6b60c6670ee82201314d9d12528f70b'
def transform(raw):
 if hashlib.sha256(raw).hexdigest()!=BASE:raise ValueError('Unexpected Combined R1 index')
 s=raw.decode('utf8')
 def one(old,new):
  nonlocal s
  if s.count(old)!=1:raise ValueError('Unexpected source anchor '+old[:80])
  s=s.replace(old,new,1)
 one('function renderTrainingPanel(){','''// Optional smart selection uses only existing demo Training Shards, not owned units.
function smartTrainingPlan(id){
 if(!P||P.version!==7||!saveEnabled||saveRecoveryPending||!copyPlayerSummonIdle()||!Number.isSafeInteger(id)||!P.roster.includes(id)||!stackOwnedUnit(id))return null;
 const exp=P.unitExp[id],shards=P.trainingShards,zel=P.zel,spent=P.trainingSpent;
 if(![exp,shards,zel,spent].every(n=>Number.isSafeInteger(n)&&n>=0)||exp>1000000000||shards>100000||zel>1000000000||spent>100000)return null;
 const level=demoLevel(exp),remaining=nextDemoUnitExp(exp);
 if(level>=99||remaining<=0)return null;
 const count=Math.ceil(remaining/10),cost=count*150,gain=count*10;
 if(count<1||count>49||shards<count||zel<cost||spent>100000-count||exp>1000000000-gain)return null;
 return Object.freeze({id,exp,level,count,cost,gain,shards,zel,spent});
}
function smartTrainNext(id,rendered){
 if(P!==rendered)return false;
 const plan=smartTrainingPlan(id);if(!plan)return false;
 if(typeof confirm!=='function'||!confirm('Train to next level using '+plan.count+' Training Shards and '+plan.cost+' Zel? No owned units are consumed.'))return false;
 if(P!==rendered||JSON.stringify(smartTrainingPlan(id))!==JSON.stringify(plan))return false;
 const ok=copyCommitProgress(next=>{
  if(!next.roster.includes(id)||next.unitExp[id]!==plan.exp||next.trainingShards!==plan.shards||next.zel!==plan.zel||next.trainingSpent!==plan.spent)return false;
  next.trainingShards-=plan.count;next.trainingSpent+=plan.count;next.zel-=plan.cost;next.unitExp[id]+=plan.gain;return true;
 });
 if(!ok){renderTrainingPanel();return false;}
 reset();renderProgress();E.trainingmessage.textContent='Smart Training: used '+plan.count+' demo Shards and '+plan.cost+' Zel. Level '+plan.level+' → '+demoLevel(P.unitExp[id])+'. No owned units consumed.';return true;
}
function renderTrainingPanel(){''')
 one('  item.append(art,info,actions);E.traininglist.append(item);','''  const smart=document.createElement('button');smart.type='button';smart.className='bf-smart-train-next';smart.dataset.ownedId=String(base.id);
  const smartPlan=smartTrainingPlan(base.id);smart.textContent=smartPlan?'NEXT LEVEL · '+smartPlan.count+' shards':'NEXT LEVEL · unavailable';
  smart.title=smartPlan?'Use '+smartPlan.count+' demo Training Shards and '+smartPlan.cost+' Zel; no owned units consumed':'Not enough resources, save unavailable, max level or active battle/repeat';
  smart.disabled=!smartPlan;const smartProgress=P;smart.onclick=()=>smartTrainNext(base.id,smartProgress);actions.append(smart);
  item.append(art,info,actions);E.traininglist.append(item);''')
 return s.encode('utf8')
if __name__=='__main__':
 p=Path(sys.argv[1]);out=Path(sys.argv[2]);out.write_bytes(transform(p.read_bytes()));print(hashlib.sha256(out.read_bytes()).hexdigest())
