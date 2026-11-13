"""v412: private, local-only, decoded MissionStart candidate VALUE-shape inventory.

Extends v202/v212's no-network, input-bound and duplicate-key gates.
This is NOT evidence that any input is from 2022, that candidate field names
mean what researchers think, or that Mission #10 waves/AI/drops were decoded.
No enemy IDs, payloads, key paths, values or per-packet details are exported.
"""
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
import json

import audit_bf_server_battle_capture_colocation_v21200 as v212
import audit_bf_server_battle_capture_fields_v20200 as v202

BATTLE = ("U0v5IeJo", "75t0sx9z", "pj41dy9g")
AI = "89ausgc4"
FIELDS = BATTLE + (AI,)
SHAPES = ("nonempty_array", "empty_array", "nonempty_object", "empty_object",
          "null", "scalar")
DATA_SHAPES = frozenset(("nonempty_array", "nonempty_object"))


def shape(value):
    if type(value) is list:
        return "nonempty_array" if value else "empty_array"
    if type(value) is dict:
        return "nonempty_object" if value else "empty_object"
    return "null" if value is None else "scalar"


def inspect_bytes(raw):
    # The earlier audit first applies v202 size/UTF-8/duplicate-key, depth and
    # node limits. No raw data is written by any of these tools.
    baseline = v212.inspect_bytes(raw)
    doc = json.loads(raw.decode("utf-8"), object_pairs_hook=v202.unique_keys)
    stack = [doc]
    hist = {key: Counter() for key in FIELDS}
    all_three_names = 0
    all_three_data = 0
    all_four_names = 0
    all_four_data = 0
    candidates_with_any_empty = 0
    candidates_with_any_scalar = 0
    while stack:
        node = stack.pop()
        if type(node) is dict:
            present = [key for key in FIELDS if key in node]
            for key in present:
                hist[key][shape(node[key])] += 1
            if all(key in node for key in BATTLE):
                all_three_names += 1
                if all(shape(node[key]) in DATA_SHAPES for key in BATTLE):
                    all_three_data += 1
                if any(shape(node[key]) in ("empty_array", "empty_object", "null")
                       for key in BATTLE):
                    candidates_with_any_empty += 1
                if any(shape(node[key]) == "scalar" for key in BATTLE):
                    candidates_with_any_scalar += 1
                if AI in node:
                    all_four_names += 1
                    if all(shape(node[key]) in DATA_SHAPES for key in FIELDS):
                        all_four_data += 1
            for item in node.values():
                if type(item) in (dict, list):
                    stack.append(item)
        elif type(node) is list:
            for item in node:
                if type(item) in (dict, list):
                    stack.append(item)
    if all_three_names != baseline["objectsWithCoLocatedThreeBattleFields"]:
        raise ValueError("candidate same-object source audit diverged")
    if all_four_names != baseline["objectsWithAllFourCandidateFields"]:
        raise ValueError("candidate same-object four-field count diverged")
    return {
        "schema": "bf-global-v412-local-2022-candidate-value-shape-inventory",
        "targetResearchMission": 10,
        "inputSha256": baseline["inputSha256"],
        "boundedContainerNodesVisited": baseline["decodedJsonContainerNodesVisited"],
        "candidateValueShapeCounts": {
            key: {kind: hist[key][kind] for kind in SHAPES}
            for key in FIELDS
        },
        "objectsWithAllThreeFieldNames": all_three_names,
        "objectsWithAllThreeNonemptyDataContainers": all_three_data,
        "objectsWithAllFourFieldNames": all_four_names,
        "objectsWithAllFourNonemptyDataContainers": all_four_data,
        "threeNameObjectsWithEmptyOrNullField": candidates_with_any_empty,
        "threeNameObjectsWithScalarField": candidates_with_any_scalar,
        "coLocatedNonemptyCandidateDataObserved": all_three_data > 0,
        "candidateKeysConfirmedAsNative2022": False,
        "original2022CaptureProvenanceVerified": False,
        "original2022Mission10PacketIdentityVerified": False,
        "original2022Mission10EnemyGroupJoinDecoded": False,
        "original2022Mission10OrderedFormationsVerified": False,
        "original2022EnemyStatsSkillsAiDropsVerified": False,
        "mutatesGameOrSave": False,
        "scope": "sanitized locally decoded untrusted JSON; shape counts ONLY",
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True,
                        help="local sanitized decoded JSON, NEVER raw HAR or save")
    args = parser.parse_args()
    try:
        if not args.input.is_file() or args.input.stat().st_size > v202.MAX_BYTES:
            parser.error("missing input or unsafe input size")
        report = inspect_bytes(args.input.read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError,
            ValueError, RecursionError):
        parser.error("invalid or unsafe sanitized decoded JSON")
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
