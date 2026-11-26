#!/usr/bin/env python3
"""B5: preserve live legacy lookup branches and canonical duplicate markers."""
import hashlib,pathlib,sys
from a13 import readmanifest,one
HERE=pathlib.Path(__file__).resolve().parent
NAME='bf10200_qol_unit_flags.js'
OLD="const marked=(id,kind)=>copyId(id)?(typeof copyOrgRead==='function'&&copyOrgRead()[kind].includes(id)):flags[kind].includes(id);"
NEW="const marked=(id,kind)=>{\n   if(kind!=='favorites'&&kind!=='locked')return false;\n   if(copyId(id))return typeof copyOrgRead==='function'&&copyOrgRead()[kind].includes(id);\n   return kind==='favorites'?flags.favorites.includes(id):flags.locked.includes(id);\n };"
def transform(root):
 for n,h in readmanifest(HERE/'a14-hashes.txt').items():
  if hashlib.sha256((root/n).read_bytes()).hexdigest()!=h:raise ValueError('A14 input mismatch '+n)
 p=root/NAME;s=p.read_text('utf8');p.write_text(one(s,OLD,NEW),encoding='utf8')
 print('A15 live legacy favorite/lock branches; canonical copy marker dispatch retained')
if __name__=='__main__':transform(pathlib.Path(sys.argv[1]))
