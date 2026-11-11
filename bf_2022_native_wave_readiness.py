"""Read-only source-backed native-wave readiness report; never simulates combat."""
import json
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "source_data/bf_global_original_2022_live_quest_economy_v142.json"
ARCHIVE_SHA = "69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
MASTER_SHA = "d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83"
COLUMNS = ["missionId", "missionDungeonId", "requiredMissionId", "missionBattleCount", "missionEnergyUse", "exp", "zel", "karma"]

def report(data):
    if not isinstance(data, dict) or data.get("readOnly") is not True or data.get("year") != 2022:
        raise ValueError("unauthenticated source")
    if data.get("sourceArchiveSha256") != ARCHIVE_SHA or data.get("missionMasterSha256") != MASTER_SHA:
        raise ValueError("unverified source lineage")
    if data.get("columns") != COLUMNS or data.get("total") != 106:
        raise ValueError("unexpected mission schema")
    rows = data.get("records")
    if not isinstance(rows, list) or len(rows) != 106:
        raise ValueError("incomplete mission ledger")
    if any(not isinstance(row, list) or len(row) != 8 or any(type(v) is not int or v < 0 for v in row) or row[3] < 1 for row in rows):
        raise ValueError("invalid mission record")
    if len({r[0] for r in rows}) != 106 or len({r[1] for r in rows}) != 23:
        raise ValueError("duplicate mission or invalid dungeon count")
    if rows[0][2] != 0 or any(row[2] != rows[i-1][0] for i,row in enumerate(rows) if i):
        raise ValueError("broken prerequisite chain")
    return {
        "readOnly": True,
        "missionsWithVerifiedWaveCounts": 106,
        "totalVerifiedWaveSlots": sum(r[3] for r in rows),
        "dungeons": 23,
        "nativeFormationsVerified": 0,
        "nativeWavesPlayableCertified": 0,
        "rewardsExecutable": False,
        "enemySpawnsAuthorized": False,
        "sourceArchiveSha256": ARCHIVE_SHA,
    }

if __name__ == "__main__":
    print(json.dumps(report(json.loads(SOURCE.read_text(encoding="utf-8"))), sort_keys=True, indent=2))
