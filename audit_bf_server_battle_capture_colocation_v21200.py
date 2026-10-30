"""v212: privacy-preserving, local-only co-location audit for candidate battle fields.

Does NOT decode, authenticate or reconstruct native 2022 encounter waves.
Read only decoded JSON on the owner's machine. Never upload captures or saves.
The output includes only source SHA-256, bounded counts and false proof gates.
"""
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
import json
import audit_bf_server_battle_capture_fields_v20200 as v202

BATTLE_FIELDS = frozenset(('U0v5IeJo', '75t0sx9z', 'pj41dy9g'))
AI_FIELD = '89ausgc4'
CANDIDATE_FIELDS = BATTLE_FIELDS | {AI_FIELD}


def inspect_bytes(raw):
    # First apply v202's duplicate-key, UTF-8, size, depth and node limits.
    baseline = v202.inspect_bytes(raw)
    document = json.loads(raw.decode('utf-8'), object_pairs_hook=v202.unique_keys)

    # A shared file, response envelope or outer array is not co-location.
    # Only literal candidate keys in the SAME JSON object count.
    stack = [document]
    histogram = Counter()
    objects_with_any = 0
    objects_with_all_battle = 0
    objects_with_all_four = 0
    while stack:
        current = stack.pop()
        if type(current) is dict:
            present = frozenset(current.keys()) & CANDIDATE_FIELDS
            if present:
                objects_with_any += 1
                histogram[len(present)] += 1
                if BATTLE_FIELDS <= present:
                    objects_with_all_battle += 1
                    if AI_FIELD in present:
                        objects_with_all_four += 1
            for value in current.values():
                if type(value) in (dict, list):
                    stack.append(value)
        elif type(current) is list:
            for value in current:
                if type(value) in (dict, list):
                    stack.append(value)

    # Suppress values, JSON paths, offsets, identifiers and original records.
    return {
        'schema': 'bf-global-v212-local-candidate-field-colocation',
        'inputSha256': baseline['inputSha256'],
        'decodedJsonContainerNodesVisited': baseline['decodedJsonContainerNodesVisited'],
        'candidateKeyOccurrences': baseline['packetFieldOccurrences'],
        'globallyAllThreeBattleFieldNamesObserved':
            baseline['allThreeBattleFieldNamesObserved'],
        'objectsWithAnyCandidateField': objects_with_any,
        'objectsWithExactlyOneCandidateField': histogram[1],
        'objectsWithExactlyTwoCandidateFields': histogram[2],
        'objectsWithExactlyThreeCandidateFields': histogram[3],
        'objectsWithAllFourCandidateFields': objects_with_all_four,
        'objectsWithCoLocatedThreeBattleFields': objects_with_all_battle,
        'sameObjectCandidateBattleFieldsObserved':
            objects_with_all_battle > 0,
        'sameObjectFourCandidateFieldsObserved':
            objects_with_all_four > 0,
        'original2022CaptureProvenanceVerified': False,
        'original2022BattleFieldSemanticsDecoded': False,
        'original2022EncounterGroupJoinVerified': False,
        'original2022OrderedWavesVerified': False,
        'original2022EnemyAiAndDropsVerified': False,
        'mutatesGameOrSave': False,
        'sourceScope': 'untrusted decoded JSON key co-location only; no field values read',
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path,
                        help='local sanitized decoded JSON; never upload raw captures')
    args = parser.parse_args()
    if not args.input.is_file() or args.input.stat().st_size > v202.MAX_BYTES:
        parser.error('input missing or exceeds size limit')
    try:
        report = inspect_bytes(args.input.read_bytes())
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, RecursionError):
        parser.error('input invalid or exceeds safety bounds')
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
