"""v186: real-owner 2022 mission scan attestation + synthetic negative probes.

CI cannot access the user's original private MST archive; verification of its
fixed full-SHA source was performed locally, and only the result is checked in.
"""
from pathlib import Path
import io,json,zipfile
import audit_bf_real_original_2022_sources_v18600 as audit

R=Path(__file__).resolve().parent
snapshot=json.loads((R/"source_data/bf_global_verified_original_2022_mission_reference_scan_v186.json").read_text("utf8"))
assert snapshot["schema"]=="bf-global-owner-verified-2022-encounter-source-audit-v186"
assert snapshot["sourceZipSha256"]==audit.ZIP_SHA
assert snapshot["totalMissionRows"]==3433
assert snapshot["missionRowsWithValidRawReferences"]==3306
assert snapshot["distinctOpaqueReferenceStrings"]==327
assert snapshot["otherTranslatedTablesScanned"]==145
assert snapshot["nonArrayTables"]==[]
assert [(row["sourceRows"],row["rowsWithOpaqueRef"]) for row in snapshot["missionTables"]]==[(1717,1700),(1716,1606)]
assert snapshot["missionTables"][0]["sha256"]==audit.M1_SHA
assert snapshot["missionTables"][1]["sha256"]=="48409579dd9e6019aa50825486a17a3945ea1213550bc83e05030c1f17ac0c51"
assert [(x["table"],x["topLevelRowsWithExactRef"],x["distinctOpaqueRefStrings"],
         x["sourceMissionRowsWithSameRef"]) for x in snapshot["exactSourceTableReferenceReuse"]]==[
 ("F_GRAND_MISSION_SPOT_MST_Ver92.json",294,128,808),
 ("F_RAID_POINT_MST_Ver57.json",315,94,627)]
assert all(x["fieldMatches"]=={"MISSION_8f4NYKxb":x["topLevelRowsWithExactRef"]} for x in snapshot["exactSourceTableReferenceReuse"])
for key in ("original2022WaveFormationVerified","original2022EnemyAIRecorded",
            "original2022DropRateVerified","changesToAndroid","sourceZipUploaded"):
 assert snapshot[key] is False
assert snapshot["meaning"]=="source-level exact text reuse, not a verified encounter formation"

# Adversarial synthetic source proof: full token ONLY, not substring, number or
# an unrelated field. Synthetic does NOT establish what original 2022 data says.
blob=io.BytesIO()
with zipfile.ZipFile(blob,"w") as z:
 for path,rows in [
  (audit.MASTERS[0],[{"missionId":"1","MISSION_8f4NYKxb":"3:10100,1:10101,0:10102"},
                     {"missionId":"2","MISSION_8f4NYKxb":"bad"}]),
  (audit.MASTERS[1],[{"missionId":"3","MISSION_8f4NYKxb":"1:999,0:998"}]),
  ("3-mst-translated/F_GRAND_MISSION_SPOT_MST_Ver92.json",[
     {"MISSION_8f4NYKxb":"3:10100,1:10101,0:10102"},
     {"MISSION_8f4NYKxb":"prefix3:10100,1:10101,0:10102"},
     {"MISSION_8f4NYKxb":10100}]),
  ("3-mst-translated/F_RAID_POINT_MST_Ver57.json",[
     {"MISSION_8f4NYKxb":"1:999,0:998"}]),
  ("3-mst-translated/F_OTHER_MST_Ver1.json",[
     {"nested":{"MISSION_8f4NYKxb":"1:999,0:998"}}])]:
  z.writestr(path,json.dumps(rows))
blob.seek(0)
with zipfile.ZipFile(blob) as z:
 result=audit.scan(z,authentic=False)
 try:
  audit.scan(z,authentic=True)
 except ValueError as ex:
  assert "SHA mismatch" in str(ex)
 else:raise AssertionError("synthetic master incorrectly accepted as authenticated")
assert result["totalMissionRows"]==3
assert result["missionRowsWithValidRawReferences"]==2
assert result["distinctOpaqueReferenceStrings"]==2
assert result["otherTranslatedTablesScanned"]==3
assert [(x["topLevelRowsWithExactRef"],x["distinctOpaqueRefStrings"]) for x in result["exactSourceTableReferenceReuse"]]==[(1,1),(1,1)]
assert result["original2022WaveFormationVerified"] is False
source=(R/"app/src/main/java/org/bravefrontier/offline/MainActivity.java").read_text("utf8")
assert "v186" not in source
assert "bf_global_offline_demo_v7" in (R/"app/src/main/assets/index.html").read_text("utf8")
print("PASS v186: real authenticated 2022 source-scan attestation protected; synthetic negative gates; no source ZIP, Android or saves touched")
