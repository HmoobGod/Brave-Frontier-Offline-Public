#!/usr/bin/env python3
"""Reuse ordinary summon save bookkeeping; no player-facing history addition."""
from pathlib import Path
import hashlib,sys
BASE='6c7fe770a4674b9154b702be557bd1061dbee7021c3d747e39651a3ef366ce09'
def transform(raw):
 if hashlib.sha256(raw).hexdigest()!=BASE:raise ValueError('Unexpected Smart Training R1 index')
 s=raw.decode('utf8')
 def one(old,new):
  nonlocal s
  if s.count(old)!=1:raise ValueError('Unexpected source anchor '+old[:80])
  s=s.replace(old,new,1)
 one('P.summonTokens>0&&P.summonHistory.length<100;', 'P.summonTokens>0&&validRollingSummonHistory(P.summonHistory);')
 one('function customDuplicateSummon(){','''// Match ordinary summon save bookkeeping, not a lifetime ownership limit.
function validRollingSummonHistory(history){return Array.isArray(history)&&history.length<=100&&history.every(id=>RECRUIT_IDS.includes(id));}
function customDuplicateSummon(){''')
 one('P.summonTokens<1||P.summonHistory.length>=100)return {ok:false};','P.summonTokens<1||!validRollingSummonHistory(P.summonHistory))return {ok:false};')
 one('next.summonTokens--;next.summonHistory.push(sourceId);return true;', 'next.summonTokens--;next.summonHistory.push(sourceId);if(next.summonHistory.length>100)next.summonHistory=next.summonHistory.slice(-100);return true;')
 one('Limit: 100 summon history entries.','Save size limits still apply.')
 one('P.summonTokens<1||P.summonHistory.length>=100:!copyPlayerSummonAvailable();','P.summonTokens<1||!validRollingSummonHistory(P.summonHistory):!copyPlayerSummonAvailable();')
 return s.encode('utf8')
if __name__=='__main__':
 p=Path(sys.argv[1]);out=Path(sys.argv[2]);out.write_bytes(transform(p.read_bytes()));print(hashlib.sha256(out.read_bytes()).hexdigest())
