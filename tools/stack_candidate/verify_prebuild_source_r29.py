#!/usr/bin/env python3
"""Verify the exact reviewed preparation source before any prepared asset mutation."""
import argparse, hashlib, json, pathlib, re
HERE=pathlib.Path(__file__).resolve().parent
MANIFEST=json.loads((HERE/'prebuild_source_r29.json').read_text('utf-8'))
ORDER_PATH='tools/stack_candidate/prebuild-order-a12.txt'
TASKS=MANIFEST['tasks']; ORDER=[path for _,path in TASKS]
assert len(ORDER)==len(set(ORDER))==46
assert set(ORDER)<=set(MANIFEST['script_blobs']) and len(MANIFEST['script_blobs'])==50

def git_blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def verify(root,mode='registered'):
    if mode not in ('source','registered'):raise ValueError('Invalid mode')
    root=root.resolve()
    sources=MANIFEST['registered_blobs' if mode=='registered' else 'source_blobs']
    for path,wanted in {**sources,**MANIFEST['script_blobs']}.items():
        f=root/path
        if not f.is_file() or git_blob(f.read_bytes())!=wanted:raise ValueError('Exact preparation source mismatch: '+path)
    if (root/ORDER_PATH).read_text('utf-8').splitlines()!=ORDER:raise ValueError('Exact preparation order mismatch')
    gradle=(root/'app/build.gradle').read_text('utf-8')
    declared=re.findall(r"commandLine[^\n]*'([^']+\.py)'",gradle)
    if declared!=ORDER:raise ValueError('Unexpected preBuild inventory')
    if mode=='registered':
        if gradle.count('dependsOn verifyProgressionR29Source')!=1 or gradle.count('dependsOn predecessor')!=1:raise ValueError('Preparation order guard absent')
    print('PASS R29',mode,'46 preparation scripts, three helpers, order and three registration source blobs',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--checkout',type=pathlib.Path,required=True);p.add_argument('--mode',choices=['source','registered'],default='registered');a=p.parse_args();verify(a.checkout,a.mode)
