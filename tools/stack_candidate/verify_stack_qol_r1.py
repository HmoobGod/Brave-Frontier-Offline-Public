#!/usr/bin/env python3
"""Combined QoL R1 exact admission: A17 contract, two reviewed asset digests changed."""
import argparse,pathlib,hashlib,zipfile
from verify_stack_a12 import BASE,NAV,MODULE,MARKERS,EXPECTED as A12_EXPECTED
from a13 import CONSUMERS,readmanifest,BASELINE_LOOKUP
HERE=pathlib.Path(__file__).resolve().parent
EXTRA=readmanifest(HERE/'a13-extra-base-hashes.txt')
EXPECTED=readmanifest(HERE/'a17-hashes.txt')
assert EXPECTED['bf16900_optional_imp_fusion.js']=='c1dec82a0ff73afd74acaa2cb27c79479b4a04457069d152c6920a03c3e56742'
EXPECTED['bf16900_optional_imp_fusion.js']='dea4657d13a08b141ac647ff57e1b9950dbb18d83bbf9e9805f106a3ae433490'
assert EXPECTED['index.html']=='bb45645fc06e370f02f10e819401422ac7079eba97f6618904cbb066bff74bd5'
EXPECTED['index.html']='268b08b9ab91f6c4ecd24c18ba15e4b2e6b60c6670ee82201314d9d12528f70b'
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
  from a16 import NEW as CAP_NEW, OLD as CAP_OLD, NAME as CAP_NAME
  caps=read(CAP_NAME)
  if caps.count(CAP_NEW.encode())!=1 or CAP_OLD.encode() in caps:raise ValueError('Level cap preview dispatch contract')
  html=read('index.html')
  if html.count(b'BF_COPY_PLAYER_OPTIN_R1')!=1:raise ValueError('Player duplicate opt-in marker')
  from a17 import NEW as EVO_NEW, OLD as EVO_OLD
  if html.count(EVO_NEW.encode())!=1 or EVO_OLD.encode() in html:raise ValueError('Evolution import dispatch contract')
  if html.count(BASELINE_LOOKUP.encode())!=1 or b'stackInspectorUnit' in html:raise ValueError('Shared lookup contract')
  if html.count(b'const uid=P.squad[i],src=uid?effectiveUnit(uid):null;')!=1 or html.count(b'if(P.squad[i]>=OWNED_COPY_FIRST)return buildPlayerSlot(P.squad[i],stackOwnedUnit(P.squad[i]));')!=1:raise ValueError('Party constructor dispatch contract')
 elif mode=='baseline':
  expected=BASELINE
  if exists(MODULE):raise ValueError('Unexpected STACK module in baseline')
 elif mode=='legacy':
  expected={n:h for n,h in BASELINE.items() if n not in ('index.html','bf9800_qol_cleared_quest_repeat.js','bf_home_nav.css')}
  if exists(MODULE) or not read('index.html') or any(x in read('index.html') for x in (*MARKERS,b'stackOwnedUnit',b'BF_COPY_PLAYER_OPTIN_R1')):raise ValueError('Unflagged STACK residue')
 else:raise ValueError('Unknown admission mode')
 for n,h in expected.items():
  if not exists(n) or hashlib.sha256(read(n)).hexdigest()!=h:raise ValueError('Asset hash mismatch: '+n)
 print('PASS',mode,'25-asset STACK + Imp + player opt-in admission and unchanged resource budgets')
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
