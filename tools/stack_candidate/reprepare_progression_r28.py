#!/usr/bin/env python3
"""Review-only proposal for existing ephemeral CI source-repreparation guard."""
import argparse,pathlib,re,subprocess,sys
from verify_progression_r28 import directory
from restore_progression_r28_base import restore,verify_r1
HERE=pathlib.Path(__file__).resolve().parent
ORDER=(HERE/'prebuild-order-a12.txt').read_text().splitlines()
def main():
 p=argparse.ArgumentParser();p.add_argument('--checkout',type=pathlib.Path,required=True);p.add_argument('--execute-disposable',action='store_true');a=p.parse_args();root=a.checkout.resolve()
 if not a.execute_disposable:raise SystemExit('Explicit disposable source-only execution required')
 declared=re.findall(r"commandLine[^\n]*'([^']+\.py)'",(root/'app/build.gradle').read_text())
 if declared!=ORDER or len(set(ORDER))!=46:raise SystemExit('Unexpected preBuild inventory; no scripts executed')
 if not all((root/n).is_file() for n in ORDER):raise SystemExit('Incomplete source checkout; no scripts executed')
 assets=root/'app/src/main/assets';directory(assets,'prepared');restore(assets)
 for n in ORDER:
  subprocess.run([sys.executable,str(root/n)],cwd=root,check=True);verify_r1(assets);print('PASS preBuild',n,flush=True)
 subprocess.run([sys.executable,str(HERE/'prepare_progression_r28.py'),'--assets-dir',str(assets),'--apply'],check=True);directory(assets,'prepared')
 print('PASS all 46 source preparation scripts against exact R1, final R28 re-applied and 150 pins checked')
if __name__=='__main__':main()
