"""v202 local-only, read-only candidate battle-response field inventory.

Input is a *locally decoded JSON* export. This is not a HAR decoder or
an authenticator of archived 2022 Brave Frontier Global enemy formations.
Nothing from the input is copied to the report except a SHA-256 digest,
counts and booleans. Do not upload account-bearing network captures.
"""
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
import hashlib
import json

MAX_BYTES = 8 * 1024 * 1024
MAX_NODES = 100_000
MAX_DEPTH = 32
FIELDS = {
    'U0v5IeJo': 'candidateMonsterRows',
    '75t0sx9z': 'candidateMonsterGroups',
    'pj41dy9g': 'candidateBattleGroups',
    '89ausgc4': 'candidateAIRecords',
}


def unique_keys(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError('duplicate JSON key')
        out[key] = value
    return out


def inventory(obj):
    if type(obj) not in (dict, list):
        raise ValueError('root must be a JSON object or array')
    stack = [(obj, 0)]
    counts = Counter()
    nodes = 0
    while stack:
        current, depth = stack.pop()
        nodes += 1
        if nodes > MAX_NODES or depth > MAX_DEPTH:
            raise ValueError('decoded JSON exceeds safe scan bounds')
        if type(current) is dict:
            for key, value in current.items():
                if key in FIELDS:
                    counts[key] += 1
                if type(value) in (dict, list):
                    stack.append((value, depth + 1))
        elif type(current) is list:
            for value in current:
                if type(value) in (dict, list):
                    stack.append((value, depth + 1))
    return nodes, counts


def inspect_bytes(raw):
    if len(raw) > MAX_BYTES:
        raise ValueError('file exceeds maximum size')
    doc = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_keys)
    nodes, counts = inventory(doc)
    present = {description: counts[key] > 0 for key, description in FIELDS.items()}
    return {
        'schema': 'bf-global-v202-readonly-candidate-MissionStart-key-inventory',
        'inputSha256': hashlib.sha256(raw).hexdigest(),
        'decodedJsonContainerNodesVisited': nodes,
        'packetFieldOccurrences': {key: counts[key] for key in FIELDS},
        'candidateFieldPresence': present,
        'allThreeBattleFieldNamesObserved': all(counts[key] > 0 for key in (
            'U0v5IeJo', '75t0sx9z', 'pj41dy9g'
        )),
        'original2022ProvenanceVerified': False,
        'original2022OrderedWavesVerified': False,
        'original2022EnemyAiAndDropsVerified': False,
        'mutatesGameOrSave': False,
        'sourceScope': 'untrusted decoded JSON field-name inventory only',
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True,
                        help='local decoded JSON export; never upload raw captures')
    args = parser.parse_args()
    source = args.input
    if not source.is_file() or source.stat().st_size > MAX_BYTES:
        parser.error('input missing or exceeds size bound')
    try:
        report = inspect_bytes(source.read_bytes())
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        parser.error('invalid input or unsafe source: ' + str(exc))
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
