#!/usr/bin/env python3
"""Restore the live legacy party constructor contract; dispatch copies first.
Both paths share the exact same stat construction. Never change existing tests.
"""
import hashlib,pathlib,sys
from a13 import readmanifest,one
HERE=pathlib.Path(__file__).resolve().parent
OLD='''function playerUnit(i){
 const uid=P.squad[i],src=uid?stackOwnedUnit(uid):null;'''
NEW='''function playerUnit(i){
 if(P.squad[i]>=OWNED_COPY_FIRST)return buildPlayerSlot(P.squad[i],stackOwnedUnit(P.squad[i]));
 const uid=P.squad[i],src=uid?effectiveUnit(uid):null;
 return buildPlayerSlot(uid,src);
 function buildPlayerSlot(uid,src){'''
END='''  def:src.stats.def+grow*8,rec:src.stats.rec+grow*6,bb:0,action:null,guard:false,anim:'idle',animSince:clock()};
}
function makeWave(idx)'''
NEW_END=END.replace('\n}\nfunction makeWave','\n }\n}\nfunction makeWave')
def transform(root):
 for n,h in readmanifest(HERE/'a13-hashes.txt').items():
  if hashlib.sha256((root/n).read_bytes()).hexdigest()!=h:raise ValueError('A13 input mismatch '+n)
 p=root/'index.html';s=p.read_text('utf8');s=one(s,OLD,NEW);s=one(s,END,NEW_END)
 p.write_text(s,encoding='utf8');print('A14 explicit copy branch, original live constructor line, shared unchanged slot builder')
if __name__=='__main__':transform(pathlib.Path(sys.argv[1]))
