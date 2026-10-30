"""v201: fail-closed original-2022 encounter evidence gate regression.

This tests the integrity of *read-only* pinned 2022 mission references.
It does not decode or implement an enemy encounter.
"""
from copy import deepcopy
from pathlib import Path
import json

import audit_bf_original_2022_reference_collisions_v19900 as v199

ROOT = Path(__file__).resolve().parent
POLICY = ROOT / "source_data/bf_v201_native_2022_encounter_gate.json"
REQUIRED_MISSING = [
    "original2022ReferenceDecoder",
    "original2022EnemyGroupJoin",
    "original2022OrderedWaveFormations",
    "original2022EnemyStatsAndSkills",
    "original2022EnemyAiAndDrops",
]
OBSERVED_KEYS = (
    "missionCount",
    "distinctRawReferenceStrings",
    "sourceArchiveSha256",
    "sourceMissionMasterSha256",
    "crossAreaExactReuseGroups",
)


def validate(report, manifest):
    assert type(manifest) is dict
    assert set(manifest) == {
        "schema", "purpose", "observedSource", "missingEvidence",
        "native2022FormationsVerified", "native2022EnemyAIAndDropsVerified",
        "changesGame", "releaseGate",
    }
    assert manifest["schema"] == "bf-global-v201-native-2022-encounter-evidence-gate"
    assert manifest["purpose"] == (
        "Read-only safety ledger; NOT a decoded enemy formation or gameplay implementation"
    )
    assert type(manifest["observedSource"]) is dict
    observed = manifest["observedSource"]
    assert set(observed) == set(OBSERVED_KEYS)
    assert observed == {key: report[key] for key in OBSERVED_KEYS}
    assert report["missionCount"] == 142
    assert report["distinctRawReferenceStrings"] == 29
    assert report["missionsSharingSomeRawReference"] == 142
    assert report["sourceAreas"] == {
        "mistral": 34, "morgan": 36, "stlamia": 36, "amdahl": 36
    }
    assert report["referenceReuseSizeHistogram"] == {"4": 6, "5": 20, "6": 3}
    assert report["crossAreaExactReuseGroups"] == 0
    assert report["sourceArchiveSha256"] == v199.ZIP2022
    assert report["sourceMissionMasterSha256"] == v199.MASTER2022
    assert type(manifest["missingEvidence"]) is list
    assert manifest["missingEvidence"] == REQUIRED_MISSING
    assert manifest["native2022FormationsVerified"] is False
    assert manifest["native2022EnemyAIAndDropsVerified"] is False
    assert manifest["changesGame"] is False
    assert manifest["releaseGate"] == "BLOCKED"
    assert all(report[key] is False for key in (
        "native2022EnemyIdsVerified",
        "native2022WaveFormationsVerified",
        "native2022EncounterWeightsVerified",
        "native2022EnemyAIAndDropsVerified",
        "changesGameplay", "changesSaves", "changesAndroid",
    ))


report = v199.compare()  # v199 verifies SHA-pinned original 2022 source excerpts
manifest = json.loads(POLICY.read_text(encoding="utf8"))
validate(report, manifest)


def reject(mutator):
    corrupted = deepcopy(manifest)
    mutator(corrupted)
    try:
        validate(report, corrupted)
    except (AssertionError, TypeError, KeyError):
        return
    raise AssertionError("v201 accepted unsafe readiness change: " + mutator.__name__)


def false_decoder_claim(x):
    x["missingEvidence"].remove("original2022ReferenceDecoder")

def claimed_native_wave(x):
    x["native2022FormationsVerified"] = True

def claimed_native_ai(x):
    x["native2022EnemyAIAndDropsVerified"] = True

def released_without_evidence(x):
    x["releaseGate"] = "READY"

def altered_archive(x):
    x["observedSource"]["sourceArchiveSha256"] = "0" * 64

def promoted_ref_count(x):
    x["observedSource"]["distinctRawReferenceStrings"] = 142

def duplicate_missing_gate(x):
    x["missingEvidence"][1] = x["missingEvidence"][0]

def added_claim_field(x):
    x["nativeEnemyWaveIds"] = [1234]

def changed_game_flag(x):
    x["changesGame"] = True

def altered_schema(x):
    x["schema"] = "native-2022-ready"


for mutation in (
    false_decoder_claim, claimed_native_wave, claimed_native_ai,
    released_without_evidence, altered_archive, promoted_ref_count,
    duplicate_missing_gate, added_claim_field, changed_game_flag,
    altered_schema,
):
    reject(mutation)

print(
    "PASS v201: original 2022 mission references pinned; "
    "10 negative readiness probes; native encounter and AI gates BLOCKED"
)
