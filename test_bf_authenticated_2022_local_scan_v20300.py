"""v203 CI: pin findings from locally SHA-verified authentic 2022 MST.

CI checks *only this aggregate claim* against the already-merged v199
2022 source reference audit. Original private ZIP bytes are not in GitHub
and therefore are NOT claimed to be re-scanned by this CI test.
"""
from copy import deepcopy
from pathlib import Path
import json
import re

import audit_bf_original_2022_reference_collisions_v19900 as audit

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source_data/bf_v203_authenticated_2022_local_scan_summary.json"
report = audit.compare()
claim = json.loads(SOURCE.read_text("utf8"))
EXPECTED = {
    "F_RAID_POINT_MST_Ver57.json": (99, 110,
        "62433315a048dc83f50b4711ce633085ab76672ae6c5260e0f3b6445a2587009"),
    "F_GRAND_MISSION_SPOT_MST_Ver92.json": (92, 72,
        "ce9ac03cc8e1eb877d3afe6855336b2c7a6fe0b085cd75aed0a350bad7552eb5"),
    "F_MISSION_MST_2_Ver1118.json": (67, 66,
        "48409579dd9e6019aa50825486a17a3945ea1213550bc83e05030c1f17ac0c51"),
}
EXPECTED_COLUMNS = ["battleGroupId", "raidRouteId", "AI_CHANCE", "raidAiId"]
ZERO_FLAGS = (
    "native2022EncounterGroupJoinDecoded",
    "native2022OrderedWaveFormationsVerified",
    "native2022EnemyAiAndDropsVerified",
    "changesGameplay", "changesSaves", "changesAndroid"
)
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def validate(value):
    assert type(value) is dict
    assert set(value) == {
        "schema", "scope", "archiveSha256", "primaryMissionMasterSha256",
        "sourceIncludedInPublicRepository", "sourceVerifiedLocally",
        "scanMethod", "sourceMissionSelection", "sourceMissionCount",
        "areaMissionCounts", "distinctOpaqueReferenceStrings",
        "v152CanonicalCompressedFixtureSha256", "v152CanonicalMissionRowsSha256",
        "v152MissionReferencesExactMatchCount", "v152MissionReferencesMismatchCount",
        "referenceReuseHistogram", "scannedTranslatedMasterTableCount",
        "skippedTableCount", "topLevelCandidateFields",
        "nestedExactReferenceCandidatePathCount", "raidBattleGroupTable",
        *ZERO_FLAGS
    }
    assert value["schema"] == "bf-global-v203-authenticated-2022-local-master-candidate-scan"
    assert value["scope"] == (
        "Exact reused opaque mission-reference strings across original "
        "translated 2022 F_ tables; no enemy/wave decoding")
    assert value["archiveSha256"] == audit.ZIP2022 == report["sourceArchiveSha256"]
    assert value["primaryMissionMasterSha256"] == audit.MASTER2022 == report["sourceMissionMasterSha256"]
    assert value["sourceIncludedInPublicRepository"] is False
    assert value["sourceVerifiedLocally"] is True
    assert value["scanMethod"].startswith("Independent local read-only equivalent")
    assert "not claimed to have been executed" in value["scanMethod"]
    assert value["sourceMissionSelection"].startswith("area 100 excluding mission 90")
    assert value["sourceMissionCount"] == report["missionCount"] == 142
    assert value["v152CanonicalCompressedFixtureSha256"] == (
        "cc8aeda4a3f95555985bf4aada5c75f1f1dfdb67f0ee800d36b7aba56327f59a")
    assert value["v152CanonicalMissionRowsSha256"] == (
        "2acd1ab29b8a00b3c8804a89fdc9d7b99cba4853f5974f765bc7473c89e7a284")
    assert value["v152MissionReferencesExactMatchCount"] == 142
    assert value["v152MissionReferencesMismatchCount"] == 0
    assert value["distinctOpaqueReferenceStrings"] == report["distinctRawReferenceStrings"] == 29
    assert value["areaMissionCounts"] == report["sourceAreas"]
    assert value["referenceReuseHistogram"] == report["referenceReuseSizeHistogram"]
    assert type(value["scannedTranslatedMasterTableCount"]) is int
    assert value["scannedTranslatedMasterTableCount"] == 147
    assert value["skippedTableCount"] == 0
    assert value["nestedExactReferenceCandidatePathCount"] == 0
    rows = value["topLevelCandidateFields"]
    assert type(rows) is list and len(rows) == 3
    assert {row["table"] for row in rows} == set(EXPECTED)
    for row in rows:
        assert type(row) is dict and set(row) == {
            "table", "tableSha256", "field", "matchedMissionIds", "matchingTableRows"}
        mission_count, matched_rows, digest = EXPECTED[row["table"]]
        assert row["field"] == "MISSION_8f4NYKxb"
        assert row["matchedMissionIds"] == mission_count
        assert row["matchingTableRows"] == matched_rows
        assert row["tableSha256"] == digest
        assert HEX64.fullmatch(row["tableSha256"])
    raid = value["raidBattleGroupTable"]
    assert type(raid) is dict
    assert set(raid) == {"table", "sha256", "rows", "columns",
                         "authenticated2022StoryWaveJoin"}
    assert raid["table"] == "F_RAID_BATTLE_GROUP_MST_Ver52.json"
    assert raid["sha256"] == "7b055d3cda685624731e97cdc3b75dd96695419ac69a8c28118ea99b00998e03"
    assert raid["rows"] == 11121
    assert raid["columns"] == EXPECTED_COLUMNS
    assert raid["authenticated2022StoryWaveJoin"] is False
    assert all(value[k] is False for k in ZERO_FLAGS)
    assert all(report[k] is False for k in (
        "native2022EnemyIdsVerified", "native2022WaveFormationsVerified",
        "native2022EnemyAIAndDropsVerified", "changesGameplay", "changesSaves",
        "changesAndroid"
    ))


validate(claim)


def mutation_rejected(fn):
    altered = deepcopy(claim)
    fn(altered)
    try:
        validate(altered)
    except (AssertionError, KeyError, TypeError):
        return
    raise AssertionError("unsafe v203 finding mutation passed: " + fn.__name__)


def changed_source(x): x["archiveSha256"] = "0" * 64
def fake_waves(x): x["native2022OrderedWaveFormationsVerified"] = True
def fake_join(x): x["native2022EncounterGroupJoinDecoded"] = True
def fake_ai(x): x["native2022EnemyAiAndDropsVerified"] = True
def fake_nested(x): x["nestedExactReferenceCandidatePathCount"] = 1
def mismatched_v152(x): x["v152MissionReferencesMismatchCount"] = 1
def fake_found_table(x): x["topLevelCandidateFields"][0]["matchedMissionIds"] = 142
def fake_raid_join(x): x["raidBattleGroupTable"]["authenticated2022StoryWaveJoin"] = True
def changed_game(x): x["changesGameplay"] = True
def added_enemy_id(x): x["enemyIds"] = [1000]
def source_in_public(x): x["sourceIncludedInPublicRepository"] = True
for m in (changed_source, fake_waves, fake_join, fake_ai, fake_nested,
          fake_found_table, fake_raid_join, changed_game, added_enemy_id,
          source_in_public, mismatched_v152):
    mutation_rejected(m)
print("PASS v203: SHA-verified local 2022 aggregate gate, 11 negative probes, no native encounter promotion")
