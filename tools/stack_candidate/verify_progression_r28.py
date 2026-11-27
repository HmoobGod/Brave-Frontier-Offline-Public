#!/usr/bin/env python3
"""R28 review candidate: exact revised lineage, existing legacy admission unchanged."""
import argparse, hashlib, json, pathlib, zipfile
from verify_stack_revised_qol_r1 import check as check_r1
HERE=pathlib.Path(__file__).resolve().parent
PINS=json.loads((HERE/'progression_r28_pins.json').read_text())
EXPECTED=PINS['prepared']; EXTRA=PINS['r1_extra']; OMITTED=PINS['omitted']
ORDER=PINS['order']; NAV={'bf_home_nav.js','bf_home_nav.css'}
assert len(ORDER)==len(set(ORDER))==147 and len(EXPECTED)==150

def verify_hashes(read,exists,pins):
 for name,wanted in pins.items():
  if not exists(name) or hashlib.sha256(read(name)).hexdigest()!=wanted:
   raise ValueError('R28 asset hash mismatch: '+name)

def check(read,exists,mode):
 if mode=='legacy':
  check_r1(read,exists,mode)
  if b'bfR27Drain' in read('index.html'):raise ValueError('Unflagged progression residue')
  return
 if mode=='baseline':
  check_r1(read,exists,mode);verify_hashes(read,exists,EXTRA)
 elif mode=='prepared':verify_hashes(read,exists,EXPECTED)
 else:raise ValueError('Unsupported admission mode: '+mode)
 for n in OMITTED:
  if exists(n):raise ValueError('Optional visual overlay not admitted: '+n)
 for n in [*ORDER,'bf_home_nav.css','bf_global_unit_archive.css']:
  if mode=='baseline' and n=='bf_stack_copies.js':continue
  if not exists(n) or not 0<len(read(n))<=(131072 if n in NAV else 65536):
   raise ValueError('Native resource budget: '+n)
 print('PASS R28',mode,'exact asset pins and native resource budgets')

def directory(root,mode):check(lambda n:(root/n).read_bytes(),lambda n:(root/n).is_file(),mode)

def main():
 p=argparse.ArgumentParser();src=p.add_mutually_exclusive_group(required=True)
 src.add_argument('--assets-dir',type=pathlib.Path);src.add_argument('--apk',type=pathlib.Path)
 p.add_argument('--mode',choices=['baseline','prepared','legacy'],required=True);a=p.parse_args()
 if a.assets_dir:directory(a.assets_dir,a.mode)
 else:
  with zipfile.ZipFile(a.apk) as z:
   entries=z.namelist()
   def exists(n):
    count=entries.count('assets/'+n)
    if count>1:raise ValueError('Duplicate APK entry: '+n)
    return count==1
   check(lambda n:z.read('assets/'+n),exists,a.mode)
if __name__=='__main__':main()
