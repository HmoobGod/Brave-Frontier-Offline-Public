"""Synthetic read-only readiness tests; no Android APK, save, or enemy state."""
import copy
import json
from bf_2022_native_wave_readiness import SOURCE, TUPLE_SHA, report

source = json.loads(SOURCE.read_text(encoding="utf-8"))
result = report(source)
assert source["canonicalTupleSha256"] == TUPLE_SHA
assert result["missionsWithVerifiedWaveCounts"] == 106
assert result["totalVerifiedWaveSlots"] == sum(r[3] for r in source["records"])
assert result["nativeFormationsVerified"] == result["nativeWavesPlayableCertified"] == 0
assert result["rewardsExecutable"] is False and result["enemySpawnsAuthorized"] is False
assert result["readOnly"] is True
before = json.dumps(source, sort_keys=True)
for change in ("archive", "master", "count", "duplicate", "prerequisite", "wave", "positive_wave", "energy", "reward", "dungeon", "tuple_hash", "type", "schema", "missing"):
    damaged = copy.deepcopy(source)
    if change == "archive": damaged["sourceArchiveSha256"] = "0" * 64
    if change == "master": damaged["missionMasterSha256"] = "0" * 64
    if change == "count": damaged["total"] = 105
    if change == "duplicate": damaged["records"][1][0] = damaged["records"][0][0]
    if change == "prerequisite": damaged["records"][1][2] = 999
    if change == "wave": damaged["records"][1][3] = 0
    if change == "positive_wave": damaged["records"][1][3] += 1
    if change == "energy": damaged["records"][1][4] += 1
    if change == "reward": damaged["records"][1][5] += 1
    if change == "dungeon": damaged["records"][1][1] = damaged["records"][2][1]
    if change == "tuple_hash": damaged["canonicalTupleSha256"] = "0" * 64
    if change == "type": damaged["records"][1][3] = True
    if change == "schema": damaged["columns"][0] = "untrusted"
    if change == "missing": damaged["records"].pop()
    try:
        report(damaged)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted corrupt source: " + change)
assert json.dumps(source, sort_keys=True) == before
print("PASS: 106 read-only wave-count records; no formations, spawns, rewards, or saves authorized")
