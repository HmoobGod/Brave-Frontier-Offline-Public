#!/usr/bin/env python3
"""Strict atomic staging of combined QoL, shard training and internal save compatibility."""
import argparse,os,pathlib,subprocess,sys,tempfile
from verify_stack_revised_qol_r1 import check,EXPECTED,BASELINE,MODULE
from verify_stack_qol_r1 import check as check_qol
from verify_stack_a17 import check as check_a17
from prepare_smart_training import transform as training
from prepare_copy_save_compat import transform as compat
HERE=pathlib.Path(__file__).resolve().parent
def runcheck(root,fn,mode):fn(lambda n:(root/n).read_bytes(),lambda n:(root/n).is_file(),mode)
def verify(root,mode):runcheck(root,check,mode)
def classify(root):
 for kind,fn,mode in [('revised',check,'prepared'),('qol',check_qol,'prepared'),('a17',check_a17,'prepared'),('baseline',check_a17,'baseline')]:
  try:runcheck(root,fn,mode);return kind,fn,mode
  except (OSError,ValueError):continue
 raise ValueError('No exact admitted input')
def main():
 p=argparse.ArgumentParser();p.add_argument('--assets-dir',required=True,type=pathlib.Path);p.add_argument('--apply',action='store_true');a=p.parse_args();root=a.assets_dir.resolve();kind,fn,mode=classify(root)
 if kind=='revised':print('Exact revised QoL R1 already present; no-op');return
 with tempfile.TemporaryDirectory(prefix='.stack-fusion-r1-',dir=root.parent) as t:
  stage=pathlib.Path(t)/'stage';stage.mkdir();backup=pathlib.Path(t)/'backup';backup.mkdir()
  original={n:(root/n).read_bytes() for n in (BASELINE if kind=='baseline' else EXPECTED)}
  for n,b in original.items():(stage/n).write_bytes(b);(backup/n).write_bytes(b)
  if kind!='qol':subprocess.run([sys.executable,str(HERE/'prepare_stack_qol_r1.py'),'--assets-dir',str(stage),'--apply'],check=True)
  target=stage/'index.html';raw=target.read_bytes()
  target.write_bytes(compat(training(raw)));verify(stage,'prepared');runcheck(root,fn,mode)
  if not a.apply:print('Dry run revised QoL R1 verified, no writes');return
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
 print('Combined QoL + training + internal save compatibility applied')
if __name__=='__main__':main()
