"""v412 synthetic-only candidate VALUE-shape and privacy regressions.

No authentic 2022 capture is included or inferred. Tests are deterministic.
"""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile

import audit_bf_server_battle_candidate_shapes_v41200 as audit

SECRET = "PRIVATE-MISSIONSTART-ACCOUNT-TOKEN-SAVE-NEVER-PRINT"
BATTLE = ("U0v5IeJo", "75t0sx9z", "pj41dy9g")
AI = "89ausgc4"
ALL = BATTLE + (AI,)


def as_bytes(value):
    return json.dumps(value, separators=(",", ":")).encode()


def no_claims(report):
    for field in (
        "candidateKeysConfirmedAsNative2022",
        "original2022CaptureProvenanceVerified",
        "original2022Mission10PacketIdentityVerified",
        "original2022Mission10EnemyGroupJoinDecoded",
        "original2022Mission10OrderedFormationsVerified",
        "original2022EnemyStatsSkillsAiDropsVerified",
        "mutatesGameOrSave",
    ):
        assert report[field] is False, (field, report)


def test_nonempty_nested_envelope():
    raw = as_bytes({"outside": [
        {"packet": {BATTLE[0]: [{"secret": SECRET}],
                    BATTLE[1]: {"private": SECRET},
                    BATTLE[2]: [1], AI: {"private": SECRET}}},
        {"packet": {BATTLE[0]: [],
                    BATTLE[1]: {}, BATTLE[2]: None, AI: SECRET}},
        {"packet": {BATTLE[0]: SECRET, BATTLE[1]: 7, BATTLE[2]: True}},
    ], "auth": SECRET})
    before = bytes(raw)
    r = audit.inspect_bytes(raw)
    assert raw == before
    assert r["objectsWithAllThreeFieldNames"] == 3
    assert r["objectsWithAllThreeNonemptyDataContainers"] == 1
    assert r["objectsWithAllFourFieldNames"] == 2
    assert r["objectsWithAllFourNonemptyDataContainers"] == 1
    assert r["threeNameObjectsWithEmptyOrNullField"] == 1
    assert r["threeNameObjectsWithScalarField"] == 1
    assert r["candidateValueShapeCounts"][AI]["scalar"] == 1
    assert r["candidateValueShapeCounts"][BATTLE[0]]["nonempty_array"] == 1
    assert r["candidateValueShapeCounts"][BATTLE[0]]["empty_array"] == 1
    assert r["candidateValueShapeCounts"][BATTLE[0]]["scalar"] == 1
    assert r["coLocatedNonemptyCandidateDataObserved"] is True
    assert r["targetResearchMission"] == 10
    assert r["inputSha256"] == hashlib.sha256(raw).hexdigest()
    assert SECRET not in json.dumps(r)
    assert r == audit.inspect_bytes(raw)
    no_claims(r)
    return raw, r


def test_all_names_no_nonempty():
    raw = as_bytes({"packet": {BATTLE[0]: None, BATTLE[1]: [],
                               BATTLE[2]: {}, AI: False}})
    r = audit.inspect_bytes(raw)
    assert r["objectsWithAllThreeFieldNames"] == 1
    assert r["objectsWithAllThreeNonemptyDataContainers"] == 0
    assert r["objectsWithAllFourFieldNames"] == 1
    assert r["objectsWithAllFourNonemptyDataContainers"] == 0
    assert r["coLocatedNonemptyCandidateDataObserved"] is False
    assert r["threeNameObjectsWithEmptyOrNullField"] == 1
    no_claims(r)


def test_split_siblings_do_not_join():
    r = audit.inspect_bytes(as_bytes([
        {BATTLE[0]: [SECRET], BATTLE[1]: [SECRET]},
        {BATTLE[2]: [SECRET], AI: [SECRET]},
    ]))
    assert r["objectsWithAllThreeFieldNames"] == 0
    assert r["objectsWithAllThreeNonemptyDataContainers"] == 0
    no_claims(r)


def test_nonempty_three_not_native_proof():
    r = audit.inspect_bytes(as_bytes({BATTLE[0]: [1], BATTLE[1]: [2],
                                      BATTLE[2]: [3]}))
    assert r["objectsWithAllThreeNonemptyDataContainers"] == 1
    assert r["objectsWithAllFourNonemptyDataContainers"] == 0
    no_claims(r)


def test_invalid_inputs():
    for raw in (
        b'{"U0v5IeJo":[],"U0v5IeJo":[1]}',
        b'null', b'{"bad":',
        bytes([255]),
        b'[' * 35 + b'0' + b']' * 35,
    ):
        try:
            audit.inspect_bytes(raw)
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError,
                RecursionError):
            continue
        raise AssertionError("unsafe malformed candidate input accepted")


def test_cli_sanitized_no_writes():
    raw, report = test_nonempty_nested_envelope()
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / "decoded-sanitized.json"
        path.write_bytes(raw)
        output = subprocess.run(
            [sys.executable,
             str(Path(audit.__file__).resolve()), "--input", str(path)],
            check=True, capture_output=True, text=True)
        assert json.loads(output.stdout) == report
        assert path.read_bytes() == raw
        assert SECRET not in output.stdout + output.stderr


if __name__ == "__main__":
    test_nonempty_nested_envelope()
    test_all_names_no_nonempty()
    test_split_siblings_do_not_join()
    test_nonempty_three_not_native_proof()
    test_invalid_inputs()
    test_cli_sanitized_no_writes()
    print("PASS v412: nonempty same-object candidate field shapes, decoy rejection, "
          "privacy and false 2022 gates")
