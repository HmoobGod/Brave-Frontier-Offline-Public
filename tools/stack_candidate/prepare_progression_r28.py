#!/usr/bin/env python3
"""Source-only exact transform. Never embeds/extracts restricted image bytes into source."""
import argparse,hashlib,json,os,pathlib,subprocess,sys,tempfile,re
from verify_progression_r28 import directory,EXPECTED,EXTRA,OMITTED,verify_hashes
from prepare_stack_revised_qol_r1 import classify,runcheck
from verify_stack_revised_qol_r1 import check as check_r1, EXPECTED as R1_EXPECTED,BASELINE
HERE=pathlib.Path(__file__).resolve().parent
PATCH=json.loads((HERE/'progression_r28_patch.json').read_text())
ART=re.compile(rb'data:image/[^;\s"\']+;base64,[A-Za-z0-9+/=]+')
BLOB=re.compile(rb'data:image|[A-Za-z0-9+/=]{256,}',re.I)
sha=lambda b:hashlib.sha256(b).hexdigest()

def transform(name,raw,specs=PATCH):
 spec=specs[name]
 if sha(raw)!=spec['before']:raise ValueError('Wrong transform base: '+name)
 lines=raw.decode('utf-8').splitlines(keepends=True)
 result=[];cursor=0
 for start,stop,old_digest,new in spec['hunks']:
  if not cursor<=start<=stop<=len(lines):raise ValueError('Invalid source splice: '+name)
  old=''.join(lines[start:stop]).encode();new=new.encode()
  if sha(old)!=old_digest or BLOB.search(old) or BLOB.search(new):raise ValueError('Unsafe source splice: '+name)
  result.extend((''.join(lines[cursor:start]).encode(),new));cursor=stop
 result.append(''.join(lines[cursor:]).encode());out=b''.join(result)
 if len(out)!=spec['bytes'] or sha(out)!=spec['after'] or ART.findall(raw)!=ART.findall(out):
  raise ValueError('Output/inline image mismatch: '+name)
 return out

def admitted_r1(root):
 kind,fn,mode=classify(root)
 if kind not in ('revised','a17','baseline'):raise ValueError('Only exact baseline, A17, or revised QoL R1 admitted')
 verify_hashes(lambda n:(root/n).read_bytes(),lambda n:(root/n).is_file(),EXTRA)
 for n in OMITTED:
  if (root/n).exists():raise ValueError('Unadmitted optional visual file: '+n)
 return kind,fn,mode

def main():
 p=argparse.ArgumentParser();p.add_argument('--assets-dir',type=pathlib.Path,required=True);p.add_argument('--apply',action='store_true');a=p.parse_args();root=a.assets_dir.resolve()
 try:directory(root,'prepared')
 except (OSError,ValueError):pass
 else:print('Exact R28 already present; no-op');return
 kind,fn,mode=admitted_r1(root)
 # Each target is already in the exact pin set; no unrelated files copied or changed.
 with tempfile.TemporaryDirectory(prefix='.progression-r28-',dir=root.parent) as tmp:
  stage=pathlib.Path(tmp)/'stage';stage.mkdir();backup=pathlib.Path(tmp)/'backup';backup.mkdir()
  names=set(EXPECTED);original={n:(root/n).read_bytes() for n in names if (root/n).is_file()}
  for n,b in original.items():(stage/n).write_bytes(b);(backup/n).write_bytes(b)
  if kind!='revised':subprocess.run([sys.executable,str(HERE/'prepare_stack_revised_qol_r1.py'),'--assets-dir',str(stage),'--apply'],check=True)
  runcheck(stage,check_r1,'prepared')
  for n in PATCH:(stage/n).write_bytes(transform(n,(stage/n).read_bytes()))
  directory(stage,'prepared')
  # Refuse raced mutations before touching any target.
  admitted_r1(root)
  for n,b in original.items():
   if (root/n).read_bytes()!=b:raise ValueError('Asset changed during preparation: '+n)
  for n in names-original.keys():
   if (root/n).exists():raise ValueError('Asset appeared during preparation: '+n)
  if not a.apply:print('R28 dry run: no source asset writes');return
  installed=[]
  try:
   for n in sorted(names):
    if n in original and (stage/n).read_bytes()==original[n]:continue
    os.replace(stage/n,root/n);installed.append(n)
   directory(root,'prepared')
  except BaseException:
   for n in reversed(installed):
    if n in original:os.replace(backup/n,root/n)
    else:(root/n).unlink()
   raise
 print('R28 prepared against exact revised QoL lineage; no Android build')
if __name__=='__main__':main()
