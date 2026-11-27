#!/usr/bin/env python3
"""Stage existing A17 plus atomic squad Imp feed; exact hashes, no partial writes."""
import argparse,os,pathlib,subprocess,sys,tempfile
from verify_stack_imp_r2 import check,EXPECTED,BASELINE,MODULE
from verify_stack_a17 import check as check_a17
from prepare_imp_squad_batch import patch
HERE=pathlib.Path(__file__).resolve().parent
IMP='bf16900_optional_imp_fusion.js'
def verify(root,mode):check(lambda n:(root/n).read_bytes(),lambda n:(root/n).is_file(),mode)
def prior(root,mode):check_a17(lambda n:(root/n).read_bytes(),lambda n:(root/n).is_file(),mode)
def main():
 p=argparse.ArgumentParser();p.add_argument('--assets-dir',required=True,type=pathlib.Path);p.add_argument('--apply',action='store_true');a=p.parse_args();root=a.assets_dir.resolve()
 try:verify(root,'prepared');print('Exact Imp R2 already present; no-op');return
 except (OSError,ValueError):pass
 try:prior(root,'prepared');mode='prepared'
 except (OSError,ValueError):prior(root,'baseline');mode='baseline'
 with tempfile.TemporaryDirectory(prefix='.stack-imp-r2-',dir=root.parent) as t:
  stage=pathlib.Path(t)/'stage';stage.mkdir();backup=pathlib.Path(t)/'backup';backup.mkdir()
  original={n:(root/n).read_bytes() for n in (EXPECTED if mode=='prepared' else BASELINE)}
  for n,b in original.items():(stage/n).write_bytes(b);(backup/n).write_bytes(b)
  subprocess.run([sys.executable,str(HERE/'prepare_stack_a17.py'),'--assets-dir',str(stage),'--apply'],check=True)
  target=stage/IMP;target.write_bytes(patch(target.read_text('utf8')).encode('utf8'))
  verify(stage,'prepared');prior(root,mode)
  if not a.apply:print('Dry run Imp R2 verified, no writes');return
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
 print('A17 + Imp R2 candidate applied; duplicate summon default off')
if __name__=='__main__':main()
