#!/usr/bin/env python3
"""Prepare all A12 output atomically on ordinary errors, from exact generated inputs."""
import argparse,os,pathlib,subprocess,sys,tempfile
from verify_stack_a12 import check,EXPECTED,MODULE
HERE=pathlib.Path(__file__).resolve().parent

def verify(root,mode):check(lambda n:(root/n).read_bytes(),lambda n:(root/n).is_file(),mode)
def main():
 p=argparse.ArgumentParser();p.add_argument('--assets-dir',required=True,type=pathlib.Path);p.add_argument('--apply',action='store_true');a=p.parse_args();root=a.assets_dir.resolve()
 try:verify(root,'prepared');print('Exact A12 already present; no-op');return
 except (OSError,ValueError):pass
 verify(root,'baseline')
 with tempfile.TemporaryDirectory(prefix='.stack-a12-',dir=root.parent) as t:
  stage=pathlib.Path(t)/'stage';stage.mkdir();base=pathlib.Path(t)/'base';base.mkdir();original={n:(root/n).read_bytes() for n in EXPECTED if n!=MODULE}
  for n,b in original.items():(stage/n).write_bytes(b);(base/n).write_bytes(b)
  subprocess.run([sys.executable,str(HERE/'prepare_stack_a8.py'),'--assets-dir',str(stage),'--apply'],check=True)
  subprocess.run([sys.executable,str(HERE/'a12.py'),str(stage),str(base)],check=True)
  verify(stage,'prepared');verify(root,'baseline')
  if not a.apply:print('Dry run A12 verified, no writes');return
  installed=[]
  try:
   for n in EXPECTED:
    if n in original and (stage/n).read_bytes()==original[n]:continue
    os.replace(stage/n,root/n);installed.append(n)
   verify(root,'prepared')
  except BaseException:
   for n in reversed(installed):
    if n==MODULE:(root/n).unlink()
    else:os.replace(base/n,root/n)
   raise
 print('A12 source candidate applied; duplicate summon default off')
if __name__=='__main__':main()
