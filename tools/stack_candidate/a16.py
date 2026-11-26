#!/usr/bin/env python3
"""B6: restore live legacy cap-preview lookup; preserve copy dispatch."""
import hashlib,pathlib,sys
from a13 import readmanifest,one
HERE=pathlib.Path(__file__).resolve().parent
NAME='bf11500_original_unit_level_caps.js'
OLD='const unit=stackUnit(baseId);'
NEW='const unit=baseId>=1e9?stackUnit(baseId):effectiveUnit(baseId);'
def transform(root):
 for n,h in readmanifest(HERE/'a15-hashes.txt').items():
  if hashlib.sha256((root/n).read_bytes()).hexdigest()!=h:raise ValueError('A15 input mismatch '+n)
 p=root/NAME;s=p.read_text('utf8');p.write_text(one(s,OLD,NEW),encoding='utf8')
 print('A16 live ordinary cap lookup; copy branch retains A15 resolver')
if __name__=='__main__':transform(pathlib.Path(sys.argv[1]))
