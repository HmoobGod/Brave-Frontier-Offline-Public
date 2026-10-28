"""v135: independently guard candidate DecompFrontier progression extraction.
No AGPL server code or entire source tables copied; no live owner save mutation.
"""
from pathlib import Path
from collections import Counter
import base64,gzip,hashlib,json,re

R=Path(__file__).resolve().parent
A=R/"app/src/main/assets"
m=json.loads((R/"source_data/bf_decompfrontier_progression_candidates_v135.json").read_text("utf8"))
assert m["schema"]=="bf-decompfrontier-candidate-progression-v135"
assert m["researchOnly"] is True
src=m["source"]
assert src["repository"]=="decompfrontier/server"
assert src["commit"]=="7cc0ebd3be79ca561874f70224c3ed924224583b"
assert src["license"]=="AGPL-3.0-or-later"
assert src["copiedThirdPartyCode"] is False and src["rawExternalTablesBundled"] is False
assert src["localFiles"]==[
 {"path":"deploy/system/user_level.json",
  "gitBlobSha":"32a0510835917dd1a41f360de4ac1c62eda1db60","sourceRows":1000},
 {"path":"deploy/system/unit_exp_pattern.json",
  "gitBlobSha":"c109ff5059f3fad457d95ad196552d601716d4db","sourceRows":804}]
rows=m["summonerLevel"]["samples"]
assert len(rows)==17 and len({r[0] for r in rows})==17
assert rows[:5]==[[1,0,15,100,10],[2,20,16,102,10],[3,40,16,104,11],
                  [5,110,17,108,12],[10,460,18,117,14]]
assert rows[-3:]==[[200,150320,147,310,50],
                    [500,856245,263,510,50],[1000,1023143,431,844,50]]
assert all(len(r)==5 and all(isinstance(n,int) for n in r) for r in rows)
assert all(b[1]>=a[1] and b[3]>=a[3] for a,b in zip(rows,rows[1:]))
assert not m["summonerLevel"]["original2022Verified"]
ps=m["unitExp"]["patterns"]
assert set(ps)=={"10","15","20","25"}
for name,row in ps.items():
 assert row["rowCount"]==201
 assert len(row["examples"])==14
 levels=[a[0] for a in row["examples"]]
 assert levels==[1,2,3,5,10,12,20,30,60,100,120,150,200,201]
 assert row["examples"][0][1]==0
 if name=="25":
  assert row["nonzeroRows"]==0
  assert all(v==0 for _,v in row["examples"])
 else:
  assert row["nonzeroRows"]==200
  assert row["examples"][1][1]=={"10":10,"15":15,"20":21}[name]
  assert all(n>=0 for _,n in row["examples"])
assert m["unitExp"]["zeroPattern25Unsafe"] is True
assert not m["unitExp"]["original2022NumericLevelsVerified"]

# Cross-check independent OWNER 2022 original Global identifiers, not the
# historical emulator's numeric XP values (which are intentionally untrusted).
catalog=json.loads(gzip.decompress(base64.b64decode(
 (R/"source_data/bf_global_original_unit_catalog.json.gz.b64").read_text("ascii"))))
units=catalog["units"]
assert len(units)==m["ownerOriginalGlobal2022"]["unitCount"]==2291
originalIDs=sorted(u["id"] for u in units)
assert len(set(originalIDs))==2291
code=(A/"bf12100_original_all_unit_exp_ids.js").read_text("utf8")
s=re.search(r"atob\('([A-Za-z0-9+/=]+)'\)",code)
assert s,"2022 original exp-pattern archive missing"
packed=base64.b64decode(s.group(1),validate=True)
assert hashlib.sha256(packed).hexdigest()=="29b69acf743c50267c92c1022ab7c0f5032bcd22494974afcc100c54c27b4c64"
assert len(packed)==573
byID={}
for i,uid in enumerate(originalIDs):
 raw=(packed[i//4]>>(6-2*(i%4)))&3
 assert raw in (0,1,2)
 byID[uid]=(10,15,20)[raw]
assert {str(k):v for k,v in Counter(byID.values()).items()}==m["ownerOriginalGlobal2022"]["patternIdDistribution"]
playable=json.loads((R/"source_data/bf_global_2022_playable_lord_stat_endpoints_v116.json").read_text("utf8"))["rows"]
assert len(playable)==m["ownerOriginalGlobal2022"]["playableForms"]==72
assert all(byID[r["unitId"]]==r["expPatternId"] for r in playable)
# Owner 2022 unit patterns contain 10/15/20, NOT candidate all-zero 25.
assert set(byID.values())=={10,15,20}
# Safe boundary: read-only research only. No new Android runtime asset, level
# cap, summoner-cost gate, experience interpolation or v7 save migration.
assert not (A/"bf13500_decomp_progression.js").exists()
java=(R/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
assert "bf13500_decomp_progression.js" not in java
html=(A/"index.html").read_text("utf8")
assert "bf_global_offline_demo_v7" in html
assert "'version': 8" not in html
print("PASS v135: decompfrontier source-pinned 1000 levels/804 XP rows; 2022 IDs 2291, 72 playable, zero-pattern25 rejected; v7 game untouched")
