#!/usr/bin/env python3
"""Exact, serialized source re-preparation in an authorized disposable checkout.
No Android compilation, no owner data. Every original script still executes.
"""
import argparse,pathlib,subprocess,sys
from verify_prebuild_source_r29 import verify,ORDER,MANIFEST,git_blob
from verify_progression_r28 import directory
from restore_progression_r28_base import restore,verify_r1
HERE=pathlib.Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser();p.add_argument('--checkout',type=pathlib.Path,required=True);p.add_argument('--execute-disposable',action='store_true');a=p.parse_args();root=a.checkout.resolve()
    if not a.execute_disposable:raise SystemExit('Explicit disposable source-only execution required')
    verify(root,'registered') # fail closed before restoring or running any script
    assets=root/'app/src/main/assets';directory(assets,'prepared');restore(assets)
    for name in ORDER:
        if git_blob((root/name).read_bytes())!=MANIFEST['script_blobs'][name]:raise ValueError('Source changed after preflight: '+name)
        subprocess.run([sys.executable,str(root/name)],cwd=root,check=True)
        verify_r1(assets)
        print('PASS preBuild',name,flush=True)
    verify(root,'registered')
    subprocess.run([sys.executable,str(HERE/'prepare_progression_r28.py'),'--assets-dir',str(assets),'--apply'],check=True)
    directory(assets,'prepared')
    print('PASS all 46 source preparation scripts against exact R1, final R28 re-applied and 150 pins checked')
if __name__=='__main__':main()
