#!/usr/bin/env python3
"""A15 exact baseline/prepared/legacy admission for all affected assets."""
import argparse,pathlib,hashlib,zipfile
from verify_stack_a12 import BASE,NAV,MODULE,MARKERS,EXPECTED as A12_EXPECTED
from a13 import CONSUMERS,readmanifest,BASELINE_LOOKUP
HERE=pathlib.Path(__file__).resolve().parent
EXTRA=readmanifest(HERE/'a13-extra-base-hashes.txt')
EXPECTED=readmanifest(HERE/'a15-hashes.txt')
assert set(EXTRA)==set(CONSUMERS)-{'bf_home_nav.js'}
assert set(EXPECTED)==set(A12_EXPECTED)|set(EXTRA)
BASELINE={**BASE,**EXTRA,'bf_home_nav.css':A12_EXPECTED['bf_home_nav.css'],'bf9800_qol_cleared_quest_repeat.js':A12_EXPECTED['bf9800_qol_cleared_quest_repeat.js']}
assert set(BASELINE)==set(EXPECTED)-{MODULE}
def check(read,exists,mode):
 for n in NAV:
  if not exists(n) or not 0<len(read(n))<=131072:raise ValueError('128 KiB navigation budget: '+n)
 for n in set(EXPECTED)-NAV-{'index.html'}:
  if n==MODULE and not exists(n) and mode!='prepared':continue
  if not exists(n) or not 0<len(read(n))<=65536:raise ValueError('64 KiB module budget: '+n)
 if mode=='prepared':
  expected=EXPECTED
  from a15 import NEW, OLD, NAME
  flags=read(NAME)
  if flags.count(NEW.encode())!=1 or OLD.encode() in flags:raise ValueError('Unit Box marker dispatch contract')
  html=read('index.html')
  if html.count(BASELINE_LOOKUP.encode())!=1 or b'stackInspectorUnit' in html:raise ValueError('Shared lookup contract')
  if html.count(b'const uid=P.squad[i],src=uid?effectiveUnit(uid):null;')!=1 or html.count(b'if(P.squad[i]>=OWNED_COPY_FIRST)return buildPlayerSlot(P.squad[i],stackOwnedUnit(P.squad[i]));')!=1:raise ValueError('Party constructor dispatch contract')
 elif mode=='baseline':
  expected=BASELINE
  if exists(MODULE):raise ValueError('Unexpected STACK module in baseline')
 elif mode=='legacy':
  expected={n:h for n,h in BASELINE.items() if n not in ('index.html','bf9800_qol_cleared_quest_repeat.js','bf_home_nav.css')}
  if exists(MODULE) or not read('index.html') or any(x in read('index.html') for x in (*MARKERS,b'stackOwnedUnit')):raise ValueError('Unflagged STACK residue')
 else:raise ValueError('Unknown admission mode')
 for n,h in expected.items():
  if not exists(n) or hashlib.sha256(read(n)).hexdigest()!=h:raise ValueError('Asset hash mismatch: '+n)
 print('PASS',mode,'25-asset STACK admission and unchanged resource budgets')
def main():
 p=argparse.ArgumentParser();src=p.add_mutually_exclusive_group(required=True);src.add_argument('--assets-dir',type=pathlib.Path);src.add_argument('--apk',type=pathlib.Path);p.add_argument('--mode',choices=['baseline','prepared','legacy'],required=True);a=p.parse_args()
 if a.assets_dir:check(lambda n:(a.assets_dir/n).read_bytes(),lambda n:(a.assets_dir/n).is_file(),a.mode)
 else:
  with zipfile.ZipFile(a.apk) as z:
   entries=z.namelist()
   def exists(n):
    count=entries.count('assets/'+n)
    if count>1:raise ValueError('Duplicate APK entry: '+n)
    return count==1
   check(lambda n:z.read('assets/'+n),exists,a.mode)
if __name__=='__main__':main()
