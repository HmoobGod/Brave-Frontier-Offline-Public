#!/usr/bin/env python3
"""Pinned source/APK admission, including unchanged Android resource budgets."""
import argparse,hashlib,pathlib,zipfile
HERE=pathlib.Path(__file__).resolve().parent
EXPECTED={line.split()[1]:line.split()[0] for line in (HERE/'a12-hashes.txt').read_text().splitlines() if line.strip()}
BASE={line.split()[1].removeprefix('assets/'):line.split()[0] for line in (HERE/'base-hashes.txt').read_text().splitlines() if line.strip()}
NAV={'bf_home_nav.js','bf_home_nav.css'};MODULE='bf_stack_copies.js'
assert set(EXPECTED)==set(BASE)|{'bf_home_nav.css','bf9800_qol_cleared_quest_repeat.js',MODULE}
MARKERS=(b'_bfUnitInstancesV1',b'_bfCopyOrganizationV1',b'OWNED_COPY_META',b'copyCommitProgress',b'customDuplicateSummon',b'BF_STACK_DISPOSABLE_UI',b'BFStackCopies',b'BF_STACK_COPY_UI_A12')
def check(read,exists,mode):
 for n in NAV:
  if not exists(n) or not 0<len(read(n))<=131072:raise ValueError('128 KiB navigation budget: '+n)
 for n in [MODULE,'bf10200_qol_unit_flags.js','bf10000_qol_squad_presets.js']:
  if exists(n) and not 0<len(read(n))<=65536:raise ValueError('64 KiB module budget: '+n)
 if mode=='prepared': expected=EXPECTED
 elif mode=='baseline':
  expected={**BASE,'bf_home_nav.css':EXPECTED['bf_home_nav.css'],'bf9800_qol_cleared_quest_repeat.js':EXPECTED['bf9800_qol_cleared_quest_repeat.js']}
  if exists(MODULE):raise ValueError('Unexpected STACK module in baseline')
 else:
  expected={n:h for n,h in BASE.items() if n!='index.html'}
  if exists(MODULE) or not read('index.html') or any(x in read('index.html') for x in MARKERS):raise ValueError('Unflagged STACK residue')
 for n,h in expected.items():
  if not exists(n) or hashlib.sha256(read(n)).hexdigest()!=h:raise ValueError('Asset hash mismatch: '+n)
 print('PASS',mode,'asset identity and unchanged resource budgets')
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
