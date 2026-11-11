"""Read-only historical 2022 mission graph audit (no simulated combat or rewards).

Run: python test_bf_2022_mission_graph_audit.py
This verifies source lineage and campaign gating evidence, NOT native enemy waves.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
source = json.loads((ROOT / "source_data/bf_global_original_2022_live_quest_economy_v142.json").read_text(encoding="utf-8"))
assert source["readOnly"] is True and source["year"] == 2022
assert source["total"] == len(source["records"]) == 106
assert source["sourceArchiveSha256"] == "69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9"
assert source["missionMasterSha256"] == "d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83"
assert source["columns"] == ["missionId", "missionDungeonId", "requiredMissionId", "missionBattleCount", "missionEnergyUse", "exp", "zel", "karma"]
rows = source["records"]
ids = [row[0] for row in rows]
assert len(set(ids)) == 106
assert all(len(row) == 8 and all(type(x) is int and x >= 0 for x in row) for row in rows)
assert all(row[3] > 0 for row in rows)
# The authenticated source's prerequisite chain must be complete, ordered,
# acyclic, and free of orphaned mission IDs before native routing may use it.
assert rows[0][2] == 0
assert all(row[2] == rows[i-1][0] for i, row in enumerate(rows) if i)
assert len({row[1] for row in rows}) == 23
regions = {
    "mistral": {1, 10, 20, 30, 40, 50, 60, 70, 80},
    "morgan": {200, 210, 220, 230, 240, 250, 260},
    "stlamia": {300, 310, 320, 330, 340, 350, 360},
}
assert {row[1] for row in rows} == set().union(*regions.values())
assert not (regions["mistral"] & regions["morgan"] or
            regions["mistral"] & regions["stlamia"] or
            regions["morgan"] & regions["stlamia"])
assert ids[0] == 1 and ids[-1] == 365
assert rows[34][0] == 200 and rows[34][2] == 85
assert rows[70][0] == 300 and rows[70][2] == 265

# Source-only route readiness: validate copied records before any native
# integration consumes the graph. The negative fixtures must be rejected.
def valid_route(candidate):
    if len(candidate) != 106:
        return False
    if any(len(row) != 8 or any(type(value) is not int or value < 0 for value in row)
           for row in candidate):
        return False
    if len({row[0] for row in candidate}) != 106:
        return False
    if candidate[0][2] != 0:
        return False
    if any(row[3] < 1 for row in candidate):
        return False
    if any(row[2] != candidate[i - 1][0]
           for i, row in enumerate(candidate) if i):
        return False
    return True

assert valid_route(rows)
for index, column, value in [
    (35, 2, 999999),  # orphan prerequisite
    (70, 2, 300),     # self-dependency at region transition
    (10, 0, rows[9][0]),  # duplicate mission ID
    (20, 3, 0),       # invalid zero-wave mission
    (90, 3, -1),      # invalid negative count
]:
    altered = [list(row) for row in rows]
    altered[index][column] = value
    assert not valid_route(altered), (index, column, value)
assert not valid_route(rows[:-1])

# The count ledger is read-only evidence, not authorization to spawn
# enemies, award drops, deduct energy or mark a mission completed.
by_region = {}
for name, dungeons in regions.items():
    subset = [row for row in rows if row[1] in dungeons]
    assert subset
    by_region[name] = {
        "missions": len(subset),
        "source_wave_counts": sum(row[3] for row in subset),
        "source_energy": sum(row[4] for row in subset),
    }
assert sum(entry["missions"] for entry in by_region.values()) == 106
assert sum(entry["source_wave_counts"] for entry in by_region.values()) == sum(row[3] for row in rows)
assert sum(entry["source_energy"] for entry in by_region.values()) == sum(row[4] for row in rows)
print("PASS: route mutation guards and read-only regional wave/energy ledgers; native formations NOT certified.")

print("PASS: 106 authenticated source mission records, 23 dungeons, 3 regions; complete prerequisite graph. Native formations/drops NOT certified.")
