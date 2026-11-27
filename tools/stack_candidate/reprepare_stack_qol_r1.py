#!/usr/bin/env python3
"""Source-only re-preparation check. Execute ONLY in a disposable source checkout (including the ephemeral CI job checkout).
Uses existing declared Exec scripts in a dependency-respecting order; Gradle's
actual variant merge remains independently guarded. No Android build or APK.
"""
import argparse,pathlib,re,subprocess,sys
from prepare_stack_qol_r1 import verify
HERE=pathlib.Path(__file__).resolve().parent
ORDER=(HERE/'prebuild-order-a12.txt').read_text().splitlines()
def main():
 p=argparse.ArgumentParser();p.add_argument('--checkout',type=pathlib.Path,required=True);p.add_argument('--execute-disposable',action='store_true');a=p.parse_args();r=a.checkout.resolve()
 if not a.execute_disposable:raise SystemExit('Explicit disposable source-only execution required')
 g=(r/'app/build.gradle').read_text();declared=re.findall(r"commandLine[^\n]*'([^']+\.py)'",g)
 # Registration adds a multiline commandLine whose .py file is on its next line.
 if declared!=ORDER or len(set(ORDER))!=46:raise SystemExit('Unexpected preBuild script inventory; review dependencies before execution')
 if not all((r/n).is_file() for n in ORDER):raise SystemExit('Incomplete source checkout; no scripts executed')
 assets=r/'app/src/main/assets';verify(assets,'prepared')
 for name in ORDER:
  subprocess.run([sys.executable,str(r/name)],cwd=r,check=True)
  verify(assets,'prepared')
  print('PASS preBuild script',name,flush=True)
 print('PASS all 46 source preparation scripts; 25 asset hashes unchanged')
if __name__=='__main__':main()
