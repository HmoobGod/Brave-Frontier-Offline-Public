"""Read-only audit of owner-authenticated original 2022 Global encounter tokens.

The owner ZIP is PRIVATE and never in the public repo or CI. No token or
original source row is emitted. Exact token reuse is not enemy formation proof.

Usage: python audit_bf_real_original_2022_sources_v18600.py --archive /private/mst-decoded.zip
"""
from collections import defaultdict, Counter
from pathlib import Path
import argparse,hashlib,json,re,zipfile

ZIP_SHA="69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
M1_SHA="d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83"
MASTERS=["3-mst-translated/F_MISSION_MST_1_Ver1118.json",
         "3-mst-translated/F_MISSION_MST_2_Ver1118.json"]
TOKEN=re.compile(r"\d+:\d+(?:,\d+:\d+)*\Z")
def sha(b):return hashlib.sha256(b).hexdigest()
def source_file_sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as src:
  for chunk in iter(lambda:src.read(1024*1024),b""):h.update(chunk)
 return h.hexdigest()
def scan(z,authentic=True,max_bytes=80_000_000):
 entries=set(z.namelist())
 if not set(MASTERS).issubset(entries):raise ValueError("Original mission masters missing")
 refs=defaultdict(set);master_summaries=[]
 for index,path in enumerate(MASTERS):
  if z.getinfo(path).file_size>max_bytes:raise ValueError("oversized mission master")
  blob=z.read(path)
  if authentic and index==0 and sha(blob)!=M1_SHA:raise ValueError("2022 mission master SHA mismatch")
  rows=json.loads(blob)
  if not isinstance(rows,list):raise ValueError("mission master not a list")
  n=0
  for row in rows:
   if isinstance(row,dict) and isinstance(row.get("MISSION_8f4NYKxb"),str):
    token=row["MISSION_8f4NYKxb"]
    if TOKEN.fullmatch(token):
     refs[token].add((path,row.get("missionId")))
     n+=1
  master_summaries.append({"table":path.rsplit("/",1)[-1],"sha256":sha(blob),
                           "sourceRows":len(rows),"rowsWithOpaqueRef":n})
 candidates=[];non_arrays=[];checked=0
 for entry in sorted(z.infolist(),key=lambda x:x.filename):
  name=entry.filename
  if name in MASTERS or not name.startswith("3-mst-translated/F_") or not name.endswith(".json"):
   continue
  checked+=1
  if entry.file_size>max_bytes:raise ValueError("oversized original table")
  rows=json.loads(z.read(entry))
  if not isinstance(rows,list):
   non_arrays.append(name);continue
  matched=0;tokens=set();joined=set();fields=Counter()
  for row in rows:
   if not isinstance(row,dict):continue
   source=[(k,v) for k,v in row.items() if isinstance(v,str) and v in refs]
   if not source:continue
   matched+=1
   for field,value in source:
    fields[field]+=1
    tokens.add(value)
    joined.update(refs[value])
  if fields:
   candidates.append({"table":name.rsplit("/",1)[-1],
    "topLevelRowsWithExactRef":matched,"distinctOpaqueRefStrings":len(tokens),
    "sourceMissionRowsWithSameRef":len(joined),
    "fieldMatches":dict(sorted(fields.items()))})
 return {"schema":"bf-global-owner-verified-2022-encounter-source-audit-v186",
  "sourceZipSha256":ZIP_SHA if authentic else "synthetic-test-only",
  "missionTables":master_summaries,
  "totalMissionRows":sum(x["sourceRows"] for x in master_summaries),
  "missionRowsWithValidRawReferences":sum(x["rowsWithOpaqueRef"] for x in master_summaries),
  "distinctOpaqueReferenceStrings":len(refs),
  "otherTranslatedTablesScanned":checked,"nonArrayTables":non_arrays,
  "exactSourceTableReferenceReuse":candidates,
  "meaning":"source-level exact text reuse, not a verified encounter formation",
  "original2022WaveFormationVerified":False,
  "original2022EnemyAIRecorded":False,"original2022DropRateVerified":False,
  "changesToAndroid":False,"sourceZipUploaded":False}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--archive",required=True,type=Path);p.add_argument("--output",type=Path)
 args=p.parse_args()
 if source_file_sha(args.archive)!=ZIP_SHA:raise SystemExit("Private original archive SHA mismatch")
 with zipfile.ZipFile(args.archive) as z: data=scan(z)
 result=json.dumps(data,sort_keys=True,indent=2)+"\n"
 if args.output:args.output.write_text(result,encoding="utf8")
 else:print(result,end="")
if __name__=="__main__":main()
