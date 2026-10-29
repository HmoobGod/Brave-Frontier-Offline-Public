"""v187: research-only archived BF1 CGG/CGS source-layout safety audit.

Do NOT infer original 2022 combat sprite timing or enable any animation.
Uses only byte-verified v184/v185 source archives. No Android asset writes.
"""
from pathlib import Path
from collections import Counter
import base64,csv,hashlib,io,json,re,struct,zipfile

R=Path(__file__).resolve().parent
SRC=R/"source_assets/bf1"
PREVIOUS=[
 ("BF1_Global_54_Historical_Battle_Visuals_v184.zip.b64","1c450f3487cbb4ec4c6a7103d35ec5b6680d575de4094c6fc39f0ff4084d9914"),
 ("BF1_Global_13_Historical_Battle_Visuals_v185.zip.b64","81136fa4ba29f7d8a58da3d5583ea10536c6d2ba48d383338d94dfa6b9e5dd3a")]
def sha(data):return hashlib.sha256(data).hexdigest()
def members():
 raw={}
 for file,expected in PREVIOUS:
  binary=base64.b64decode((SRC/file).read_text("ascii"),validate=True)
  assert sha(binary)==expected,file
  with zipfile.ZipFile(io.BytesIO(binary)) as outer:
   assert outer.testzip() is None
   if "v184" in file:
    subarchives=[outer.read(n) for n in outer.namelist() if n.endswith(".zip")]
    assert len(subarchives)==3
   else:subarchives=[binary]
  for sub in subarchives:
   with zipfile.ZipFile(io.BytesIO(sub)) as inner:
    assert inner.testzip() is None
    for name in inner.namelist():
     if not name.endswith((".png",".csv")):continue
     assert name.startswith("content/unit/") and name not in raw,name
     raw[name]=inner.read(name)
 return raw
def read_csv(raw):
 return [[int(cell) for cell in line if cell.strip()] for line in
         csv.reader(raw.decode("utf-8-sig").splitlines()) if any(x.strip() for x in line)]
def scan():
 raw=members()
 ids=set();groups={};seqs={};atlas_sizes=Counter();battle_sizes=Counter()
 nonstandard=[];zero=[];cgg_rows=cgs_rows=0
 for name,blob in sorted(raw.items()):
  match=re.search(r"_(\d+)\.(?:png|csv)$",name)
  assert match,name
  uid=int(match.group(1));ids.add(uid)
  if name.endswith(".png"):
   assert blob[:8]==b"\x89PNG\r\n\x1a\n" and blob[12:16]==b"IHDR"
   w,h=struct.unpack(">II",blob[16:24])
   assert 0<w<=4096 and 0<h<=4096
   if "/unit_anime_" in name:
    atlas_sizes[(w,h)]+=1
    if w not in (128,256,512) or h not in (128,256,512):
     nonstandard.append({"unitId":uid,"width":w,"height":h})
   else:
    assert "/unit_ills_battle_" in name
    battle_sizes[(w,h)]+=1
  elif "/cgg/" in name:
   data=read_csv(blob);assert data and 1<=len(data)<=256
   for row in data:
    assert len(row)>=13 and (len(row)-2)%11==0,name
   groups[uid]=data;cgg_rows+=len(data)
  elif "/cgs/" in name:
   seq=read_csv(blob);assert seq
   assert all(len(row)==4 and row[0]>=0 and row[3]>=0 for row in seq)
   seqs[name]=(uid,seq);cgs_rows+=len(seq)
  else:raise AssertionError("unexpected source path "+name)
 assert len(ids)==len(groups)==67 and len(seqs)==173
 assert len(raw)==374 and cgg_rows==1111 and cgs_rows==1371
 assert sum(atlas_sizes.values())==sum(battle_sizes.values())==67
 assert battle_sizes=={(108,108):67}
 assert len(nonstandard)==7
 for name,(uid,seq) in seqs.items():
  assert uid in groups
  for lineno,row in enumerate(seq,1):
   assert row[0]<len(groups[uid]),(name,lineno,row[0],len(groups[uid]))
   if row[3]==0:zero.append({"path":name,"line":lineno,"rawRow":row})
 assert len(zero)==1
 assert zero[0]=={"path":"content/unit/cgs/unit_atk_cgs_10103.csv",
                   "line":11,"rawRow":[18,-10,0,0]}
 return {"schema":"bf-global-historical-2014-art-layout-audit-v187",
  "historicalBF1UnitIds":67,"totalOriginalSourceVisualFiles":374,
  "unitAnimationAtlases":67,"unitBattleIllustrations":67,
  "sourceCGGFiles":67,"sourceCGSFiles":173,
  "sourceCGGRows":cgg_rows,"sourceCGSRows":cgs_rows,
  "battleIllustrationSize":[108,108],
  "atlasSizeCounts":[{"width":w,"height":h,"count":n}
                     for (w,h),n in sorted(atlas_sizes.items())],
  "nonstandardAtlasDimensions":sorted(nonstandard,key=lambda x:x["unitId"]),
  "zeroDurationSequenceRows":zero,
  "allCGSFirstColumnReferencesWithinOwnCGGRowCount":True,
  "sourceEra":"combined historical BF1; exact 2022 Global client art revision unverified",
  "native2022EnemyWaveFormationsVerified":False,
  "native2022SpritePlaybackVerified":False,
  "androidSpritesActivated":False,"gameplayMutation":False,"saveMutation":False}
if __name__=="__main__":
 report=scan()
 out=R/"source_audit_reports/BraveFrontier-v187-archived-art-layout-audit.json"
 out.parent.mkdir(exist_ok=True)
 payload=json.dumps(report,sort_keys=True,indent=2)+"\n"
 out.write_text(payload,"utf8")
 print("PASS v187: 67 art sets, 374 files, 1111 CGG and 1371 CGS rows; 1 zero-duration sequence row; 7 nonstandard atlases. No animation activation.")
 print("ART_LAYOUT_AUDIT="+str(out.relative_to(R)))
