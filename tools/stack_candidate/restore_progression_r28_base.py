#!/usr/bin/env python3
"""Temporary exact R1 demotion before existing preBuild scripts; no gameplay or art loss."""
import argparse,json,os,pathlib,tempfile
from prepare_progression_r28 import transform,admitted_r1
from verify_progression_r28 import directory
from verify_stack_revised_qol_r1 import check as check_r1
from prepare_stack_revised_qol_r1 import runcheck
HERE=pathlib.Path(__file__).resolve().parent
REVERSE=json.loads((HERE/'progression_r28_reverse.json').read_text())

def verify_r1(root):
 kind,fn,mode=admitted_r1(root)
 if kind!='revised':raise ValueError('Exact revised R1 required before preBuild')

def restore(root):
 try:verify_r1(root)
 except (OSError,ValueError):pass
 else:print('Exact revised R1 already present; no-op');return
 directory(root,'prepared')
 original={n:(root/n).read_bytes() for n in REVERSE};staged={n:transform(n,b,REVERSE) for n,b in original.items()}
 # Validate resulting exact R1 pins without modifying existing assets.
 runcheck(root,lambda read,exists,mode:check_r1(lambda n:staged[n] if n in staged else read(n),exists,mode),'prepared')
 from verify_progression_r28 import EXTRA,verify_hashes
 verify_hashes(lambda n:staged[n] if n in staged else (root/n).read_bytes(),lambda n:(root/n).is_file(),EXTRA)
 with tempfile.TemporaryDirectory(prefix='.r28-restore-',dir=root.parent) as tmp:
  a=pathlib.Path(tmp);(a/'base').mkdir();(a/'backup').mkdir()
  for n in staged:(a/'base'/n).write_bytes(staged[n]);(a/'backup'/n).write_bytes(original[n])
  directory(root,'prepared');installed=[]
  try:
   for n in sorted(staged):os.replace(a/'base'/n,root/n);installed.append(n)
   verify_r1(root)
  except BaseException:
   for n in reversed(installed):os.replace(a/'backup'/n,root/n)
   raise
 print('PASS restored exact revised R1 before legacy preparation')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--assets-dir',type=pathlib.Path,required=True);a=p.parse_args();restore(a.assets_dir.resolve())
