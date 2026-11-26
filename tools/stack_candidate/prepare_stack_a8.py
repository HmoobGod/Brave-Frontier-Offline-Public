#!/usr/bin/env python3
"""Disabled-by-default, pinned post-generator candidate for CI or direct Gradle.
Usage: python prepare_stack_candidate.py --assets-dir PATH [--apply]
No APK/build/CI actions. Never point at an installed game or player data.
"""
import argparse, hashlib, os, pathlib, subprocess, sys, tempfile
HERE=pathlib.Path(__file__).resolve().parent
BASE={line.split()[1].removeprefix('assets/'):line.split()[0] for line in (HERE/'base-hashes.txt').read_text().splitlines() if line.strip()}
RESULT={line.split()[1]:line.split()[0] for line in (HERE/'a8-hashes.txt').read_text().splitlines() if line.strip()}
assert set(BASE)==set(RESULT)
def hashes(root):
 return {name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in BASE}
def main():
 a=argparse.ArgumentParser();a.add_argument('--assets-dir',required=True,type=pathlib.Path);a.add_argument('--apply',action='store_true');args=a.parse_args();root=args.assets_dir.resolve()
 current=hashes(root)
 if current==RESULT:print('STACK A8 exact output already present; no-op');return
 if current!=BASE:raise SystemExit('STACK A8 refuses unknown or mixed generated source; no files written')
 with tempfile.TemporaryDirectory(prefix='.stack-a7-',dir=root.parent) as temp:
  stage=pathlib.Path(temp);original={name:(root/name).read_bytes() for name in BASE}
  for name,data in original.items():(stage/name).write_bytes(data)
  # Original A5 spec hard-coded the disposable path. Rebase ONLY that one anchor.
  source=(HERE/'patch.py').read_text();anchor="root=Path('/tmp/bf-a5/assets')";assert source.count(anchor)==1
  portable=stage/'portable_a5.py';portable.write_text(source.replace(anchor,'import sys\nroot=Path(sys.argv[1])'))
  subprocess.run([sys.executable,str(portable),str(stage)],check=True)
  subprocess.run([sys.executable,str(HERE/'a6.py'),str(stage/'index.html')],check=True)
  subprocess.run([sys.executable,str(HERE/'a7.py'),str(stage)],check=True)
  subprocess.run([sys.executable,str(HERE/'a8.py'),str(stage)],check=True)
  if hashes(stage)!=RESULT:raise SystemExit('STACK A8 staged output differs from reviewed hashes')
  if hashes(root)!=BASE:raise SystemExit('STACK A8 input changed during staging; no files written')
  if not args.apply:print('STACK A8 dry run verified; no files written');return
  installed=[]
  try:
   for name in BASE:
    os.replace(stage/name,root/name);installed.append(name)
   if hashes(root)!=RESULT:raise RuntimeError('installed result mismatch')
  except BaseException:
   for name in installed:
    rollback=stage/(name+'.rollback');rollback.write_bytes(original[name]);os.replace(rollback,root/name)
   raise
  print('STACK A8 candidate applied to generated source only; disposable UI remains off')
if __name__=='__main__':main()
