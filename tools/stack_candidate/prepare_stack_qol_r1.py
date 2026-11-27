#!/usr/bin/env python3
"""Stage existing A17/Imp plus opt-in; exact hashes, no partial writes."""
import argparse,os,pathlib,subprocess,sys,tempfile
from verify_stack_qol_r1 import check,EXPECTED,BASELINE,MODULE
from verify_stack_imp_r2 import check as check_imp
from prepare_duplicate_optin import transform
from verify_stack_a17 import check as check_a17
HERE=pathlib.Path(__file__).resolve().parent
def verify(root,mode):check(lambda n:(root/n).read_bytes(),lambda n:(root/n).is_file(),mode)
def prior(root,mode):
 (check_imp if mode=='imp' else check_a17)(lambda n:(root/n).read_bytes(),lambda n:(root/n).is_file(),'prepared' if mode=='imp' else mode)
def main():
 p=argparse.ArgumentParser();p.add_argument('--assets-dir',required=True,type=pathlib.Path);p.add_argument('--apply',action='store_true');a=p.parse_args();root=a.assets_dir.resolve()
 try:verify(root,'prepared');print('Exact QoL R1 already present; no-op');return
 except (OSError,ValueError):pass
 try:prior(root,'imp');mode='imp'
 except (OSError,ValueError):
  try:prior(root,'prepared');mode='prepared'
  except (OSError,ValueError):prior(root,'baseline');mode='baseline'
 with tempfile.TemporaryDirectory(prefix='.stack-qol-r1-',dir=root.parent) as t:
  stage=pathlib.Path(t)/'stage';stage.mkdir();backup=pathlib.Path(t)/'backup';backup.mkdir()
  original={n:(root/n).read_bytes() for n in (BASELINE if mode=='baseline' else EXPECTED)}
  for n,b in original.items():(stage/n).write_bytes(b);(backup/n).write_bytes(b)
  subprocess.run([sys.executable,str(HERE/'prepare_stack_imp_r2.py'),'--assets-dir',str(stage),'--apply'],check=True)
  target=stage/'index.html';target.write_bytes(transform(target.read_bytes()))
  verify(stage,'prepared');prior(root,mode)
  if not a.apply:print('Dry run QoL R1 verified, no writes');return
  installed=[]
  try:
   for n in EXPECTED:
    if n in original and (stage/n).read_bytes()==original[n]:continue
    os.replace(stage/n,root/n);installed.append(n)
   verify(root,'prepared')
  except BaseException:
   for n in reversed(installed):
    if n not in original:(root/n).unlink()
    else:os.replace(backup/n,root/n)
   raise
 print('A17 + Imp + player duplicate opt-in applied; default off')
if __name__=='__main__':main()
