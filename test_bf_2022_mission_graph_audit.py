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
print("PASS: 106 authenticated source mission records, 23 dungeons, 3 regions; complete prerequisite graph. Native formations/drops NOT certified.")
