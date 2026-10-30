"""v204 synthetic format tests and fail-closed pinned original mimic histogram.

Public CI CANNOT re-open the private original 2022 ZIP. The real histogram
was independently derived from the SHA-matched source and is checked here
for self-consistency and against the pinned v175/v203 identities.
"""
from copy import deepcopy
from pathlib import Path
import json
import tempfile
import zipfile

import audit_bf_original_2022_mimic_profiles_v20400 as mimic

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "source_data/bf_v204_2022_mimic_opaque_profiles.json").read_text("utf8"))
EXPECTED = {
    "0,0,0:0,0:0": 21,
    "1,10,0:1000,0:0": 1,
    "1,10,100:1000,0:0": 38,
    "1,10,50:1000,5:1100": 1,
    "1,10,50:1000,50:1100": 29,
    "1,10,60:1000,40:1100": 16,
    "1,10,70:1000,30:1100": 36,
}
BY_AREA = {
    "mistral": {"0,0,0:0,0:0": 21, "1,10,100:1000,0:0": 13},
    "morgan": {"1,10,0:1000,0:0": 1, "1,10,100:1000,0:0": 19,
               "1,10,70:1000,30:1100": 16},
    "stlamia": {"1,10,60:1000,40:1100": 16, "1,10,70:1000,30:1100": 20},
    "amdahl": {"1,10,100:1000,0:0": 6, "1,10,50:1000,5:1100": 1,
               "1,10,50:1000,50:1100": 29},
}
FALSE_FLAGS = (
    "interpretsRawTokensAsProbabilities", "originalMimicEnemyIdsVerified",
    "originalMimicEncounterTriggerVerified", "originalMimicRewardsAndDropsVerified",
    "changesGame", "changesSaves",
)


def verify(value):
    assert type(value) is dict
    assert set(value) == {
        "schema", "sourceArchiveSha256", "sourceMissionMasterSha256",
        "sourceMissionCount", "sourceAreas", "opaqueRawPatternCounts",
        "opaqueRawPatternCountsByArea", "distinctOpaquePatterns",
        "unverifiedSingleOccurrencePatterns", *FALSE_FLAGS,
    }
    assert value["schema"] == "bf-global-v204-original-2022-mimic-opaque-profile-audit"
    assert value["sourceArchiveSha256"] == mimic.ZIP_SHA
    assert value["sourceMissionMasterSha256"] == mimic.MISSION_SHA
    assert value["sourceMissionCount"] == 142
    assert value["sourceAreas"] == mimic.AREA_COUNTS
    assert value["opaqueRawPatternCounts"] == EXPECTED
    assert value["opaqueRawPatternCountsByArea"] == BY_AREA
    assert value["distinctOpaquePatterns"] == 7
    assert value["unverifiedSingleOccurrencePatterns"] == sorted(
        [raw for raw, count in EXPECTED.items() if count == 1])
    assert all(value[key] is False for key in FALSE_FLAGS)
    assert sum(EXPECTED.values()) == 142
    for name, area_count in mimic.AREA_COUNTS.items():
        assert sum(BY_AREA[name].values()) == area_count
        for raw, count in BY_AREA[name].items():
            assert type(count) is int and count > 0
            assert mimic.RAW_PATTERN.fullmatch(raw)
    for raw in EXPECTED:
        assert sum(BY_AREA[a].get(raw, 0) for a in mimic.AREA_COUNTS) == EXPECTED[raw]


verify(DATA)
refmap = {1: "1:101", 2: "2:102", 3: "3:103"}
rows = [
    {"missionId": "1", "missionAreaId": "100",
     "MISSION_8f4NYKxb": "1:101", "missionMimicInfo": "0,0,0:0,0:0"},
    {"missionId": "2", "missionAreaId": "100",
     "MISSION_8f4NYKxb": "2:102", "missionMimicInfo": "1,10,70:1000,30:1100"},
    {"missionId": "3", "missionAreaId": "200",
     "MISSION_8f4NYKxb": "3:103", "missionMimicInfo": "1,10,60:1000,40:1100"},
]
synthetic = mimic.scan_rows(rows, refmap)
assert synthetic["sourceMissionCount"] == 3
assert synthetic["sourceAreas"] == {"mistral": 2, "morgan": 1, "stlamia": 0, "amdahl": 0}
assert synthetic["distinctOpaquePatterns"] == 3
assert all(synthetic[key] is False for key in FALSE_FLAGS)


def rejected(test_rows, test_refs=refmap):
    try:
        mimic.scan_rows(test_rows, test_refs)
    except (ValueError, TypeError, KeyError):
        return
    raise AssertionError("unsafe original-source row unexpectedly accepted")


rejected(rows[:2])
rejected([*rows, deepcopy(rows[0])])
bad = deepcopy(rows)
bad[0]["MISSION_8f4NYKxb"] = "9:999"
rejected(bad)
bad = deepcopy(rows)
bad[0]["missionMimicInfo"] = "1,10,70:1000,30:1100,extra"
rejected(bad)
bad = deepcopy(rows)
bad[0]["missionMimicInfo"] = None
rejected(bad)
bad = deepcopy(rows)
bad[0]["missionId"] = "02"
rejected(bad)
rejected(None)

with tempfile.TemporaryDirectory() as temp:
    path = Path(temp) / "untrusted.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(mimic.ORIGINAL_MISSION, json.dumps(rows))
    try:
        mimic.source_scan(path)
    except ValueError as err:
        assert "SHA-256 mismatch" in str(err)
    else:
        raise AssertionError("untrusted archive passed exact source hash gate")


def corrupt(edit):
    altered = deepcopy(DATA)
    edit(altered)
    try:
        verify(altered)
    except (AssertionError, TypeError, KeyError):
        return
    raise AssertionError("unsafe mimic readiness / source claim was accepted")


def fake_odds(x): x["interpretsRawTokensAsProbabilities"] = True
def fake_enemies(x): x["originalMimicEnemyIdsVerified"] = True
def fake_trigger(x): x["originalMimicEncounterTriggerVerified"] = True
def fake_drops(x): x["originalMimicRewardsAndDropsVerified"] = True
def fake_game(x): x["changesGame"] = True
def wrong_area(x): x["sourceAreas"]["morgan"] = 35
def wrong_rare(x): x["opaqueRawPatternCounts"]["1,10,0:1000,0:0"] = 2
def deleted_rare(x): x["unverifiedSingleOccurrencePatterns"] = []
def ungrounded_ids(x): x["originalMimicEnemyIds"] = [1000, 1100]
def changed_sha(x): x["sourceArchiveSha256"] = "0" * 64
for mutation in (fake_odds, fake_enemies, fake_trigger, fake_drops, fake_game,
                 wrong_area, wrong_rare, deleted_rare, ungrounded_ids,
                 changed_sha):
    corrupt(mutation)

print("PASS v204: 142 original missions, seven opaque mimic patterns, "
      "safe synthetic parser probes and ten false-promotion mutation probes")
