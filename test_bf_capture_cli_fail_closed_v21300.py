"""v213: malformed decoded JSON must fail closed in both research CLIs.

Synthetic inputs only. No real MissionStart packets, account data or saves.
"""
from pathlib import Path
import json
import subprocess
import sys
import tempfile

import audit_bf_server_battle_capture_fields_v20200 as v202
import audit_bf_server_battle_capture_colocation_v21200 as v212

ROOT = Path(__file__).resolve().parent
CLIS = (
    ROOT / 'audit_bf_server_battle_capture_fields_v20200.py',
    ROOT / 'audit_bf_server_battle_capture_colocation_v21200.py',
)
PRIVATE_MARKER = 'DO_NOT_DISCLOSE_PRIVATE_SAVE_TOKEN_213'


def rejects_cli(script, file_path):
    run = subprocess.run(
        [sys.executable, str(script), '--input', str(file_path)],
        cwd=ROOT, capture_output=True, text=True, check=False,
        timeout=20,
    )
    assert run.returncode == 2, (script.name, file_path.name, run.returncode,
                                  run.stderr[-1000:])
    assert run.stdout == '', (script.name, file_path.name)
    assert 'Traceback' not in run.stderr, (script.name, file_path.name)
    assert PRIVATE_MARKER not in run.stderr, (script.name, file_path.name)
    assert 'error:' in run.stderr, (script.name, file_path.name)


# Valid but pathological nesting reaches CPython's decoder recursion bound
# before the auditors' own 32-level traversal bound. Both CLIs must reject
# with a clean argparse error rather than a traceback.
very_deep = b'[' * 4096 + b'0' + b']' * 4096
for inspector in (v202.inspect_bytes, v212.inspect_bytes):
    try:
        inspector(very_deep)
    except (RecursionError, ValueError):
        pass
    else:
        raise AssertionError('deep JSON unexpectedly accepted')


# Co-location is NOT all-four "battle evidence"; having two of the three
# battle keys plus the candidate AI key cannot satisfy all battle fields.
two_battle_plus_ai = json.dumps({
    'outer': {
        'U0v5IeJo': [PRIVATE_MARKER],
        '75t0sx9z': [],
        '89ausgc4': {'secret': PRIVATE_MARKER},
    }
}).encode()
counter = v212.inspect_bytes(two_battle_plus_ai)
assert counter['objectsWithExactlyThreeCandidateFields'] == 1
assert counter['objectsWithCoLocatedThreeBattleFields'] == 0
assert counter['objectsWithAllFourCandidateFields'] == 0
assert counter['sameObjectCandidateBattleFieldsObserved'] is False
assert counter['sameObjectFourCandidateFieldsObserved'] is False
assert PRIVATE_MARKER not in json.dumps(counter)
assert all(counter[key] is False for key in (
    'original2022CaptureProvenanceVerified',
    'original2022BattleFieldSemanticsDecoded',
    'original2022EncounterGroupJoinVerified',
    'original2022OrderedWavesVerified',
    'original2022EnemyAiAndDropsVerified',
))

with tempfile.TemporaryDirectory() as directory:
    temp = Path(directory)
    fixtures = {
        'nested-too-deep.json': very_deep,
        'broken.json': (
            '{"packet":"' + PRIVATE_MARKER + '","incomplete":'
        ).encode(),
        'duplicate.json': (
            '{"U0v5IeJo":1,"U0v5IeJo":2,"sentinel":"' +
            PRIVATE_MARKER + '"}'
        ).encode(),
        'non-utf8.json': b'{"invalid":' + bytes([255]) + b'}',
        'scalar-root.json': b'1234',
        'oversized.json': b' ' * (v202.MAX_BYTES + 1),
    }
    for name, raw in fixtures.items():
        file_path = temp / name
        file_path.write_bytes(raw)
        for cli in CLIS:
            rejects_cli(cli, file_path)
        assert file_path.read_bytes() == raw, name
    for cli in CLIS:
        rejects_cli(cli, temp / 'does-not-exist.json')

print('PASS v213: both CLIs cleanly reject deep/invalid/missing JSON; no secret leakage')
