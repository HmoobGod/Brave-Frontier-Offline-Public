"""v175: synthetic negative controls for read-only original wave-source scanner.

No original owner ZIP is redistributed to CI. The original archive's full SHA
is required for real CLI runs. These tests do not prove native 2022 AI data.
"""
import io,json,subprocess,sys,tempfile,zipfile
from pathlib import Path
import audit_bf_original_2022_wave_sources_v17500 as audit
R=Path(__file__).resolve().parent
refs=audit.pinned_refs(R)
assert len(refs)==142 and refs[1]=="3:10100,0:10101"
assert refs[400]=="3:50100,0:50101"
assert refs[404]=="3:50100,0:50101"
assert audit.ZIP_SHA=="69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
assert audit.MISSION_SHA=="d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83"

a="3:10100,0:10101";b="3:50100,0:50101"
sample={1:a,400:b,404:b}
mission=[{"missionId":str(id),"MISSION_8f4NYKxb":raw} for id,raw in sample.items()]
def fake_zip(primary=None,other=None):
 out=io.BytesIO()
 with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED) as z:
  z.writestr(audit.ORIGINAL_MISSION,json.dumps(primary if primary is not None else mission))
  records=other if other is not None else {
   "F_GRAND_MISSION_SPOT_MST_Ver92.json":[{"join":b},{"join":b},{"join":a},
    {"numericOnly":50100},{"junk":"3:50100"}],
   "F_RAID_POINT_MST_Ver57.json":[{"ref":a},{"ref":b}],
   "F_FALSE_LEAD_MST_Ver1.json":[{"raw":"50100"},{"raw":"10100"}]}
  for name,rows in records.items():
   z.writestr("3-mst-translated/"+name,json.dumps(rows))
 out.seek(0)
 return zipfile.ZipFile(out)

with fake_zip() as z:
 res=audit.scan_tables(z,sample,require_primary_sha=False)
 assert res["sourceMissionCount"]==3
 assert res["sourceMissionMasterSha256"]=="synthetic-fixture-only"
 assert res["nativeFormationDecoded"] is False
 assert res["nativeEnemyIdsDecoded"] is False
 assert res["nativeAIDecoded"] is False
 assert res["nativeDropsDecoded"] is False
 assert res["gameplayMutation"] is False and res["saveMutation"] is False
 assert res["candidateFields"]==[
  {"table":"F_GRAND_MISSION_SPOT_MST_Ver92.json","field":"join",
   "matchedMissionIds":3,"matchingTableRows":3,
   "nativeFormationDecoded":False,"nativeEnemyIdsDecoded":False,
   "nativeAIDecoded":False,"nativeDropsDecoded":False},
  {"table":"F_RAID_POINT_MST_Ver57.json","field":"ref",
   "matchedMissionIds":3,"matchingTableRows":2,
   "nativeFormationDecoded":False,"nativeEnemyIdsDecoded":False,
   "nativeAIDecoded":False,"nativeDropsDecoded":False}
 ]
 assert len(json.dumps(res))<10000
 try:
  audit.scan_tables(z,sample,require_primary_sha=True)
  assert False,"synthetic master unexpectedly matched original 2022 SHA"
 except ValueError as e:assert "SHA mismatch" in str(e)
 # Total size bounds explicitly fail closed, rather than skipping mission.
 try:
  audit.scan_tables(z,sample,require_primary_sha=False,max_bytes=100)
  assert False,"unbounded mission master"
 except ValueError as e:assert "safety limit" in str(e)

with fake_zip(primary=mission+[mission[0]]) as z:
 try:
  audit.scan_tables(z,sample,require_primary_sha=False)
  assert False,"duplicate mission was accepted"
 except ValueError as e:assert "duplicate" in str(e)

with fake_zip(primary=mission[1:]) as z:
 try:
  audit.scan_tables(z,sample,require_primary_sha=False)
  assert False,"missing mission was accepted"
 except ValueError as e:assert "cross-table mismatch" in str(e)

with fake_zip() as z:
 try:
  audit.scan_tables(z,{1:"invalid,notopaque"},require_primary_sha=False)
  assert False,"malformed source reference was accepted"
 except ValueError as e:assert "invalid" in str(e)
with fake_zip() as z:
 try:
  audit.scan_tables(z,{1:"3:99999"},require_primary_sha=False)
  assert False,"forged mission reference was accepted"
 except ValueError as e:assert "cross-table mismatch" in str(e)

with tempfile.TemporaryDirectory() as td:
 file=Path(td)/"forged-owner-source.zip"
 with fake_zip() as z:file.write_bytes(z.fp.getbuffer())
 result=subprocess.run([sys.executable,str(R/"audit_bf_original_2022_wave_sources_v17500.py"),
   "--archive",str(file)],capture_output=True,text=True)
 assert result.returncode!=0
 assert "Archive SHA mismatch" in (result.stderr+result.stdout)
 assert len(list(Path(td).iterdir()))==1
print("PASS v175: exact source fixture SHA, source-only 2022 cross-join candidate counts, ambiguity protections, hard SHA/fake/duplicate/size rejection, no output or gameplay mutation")
