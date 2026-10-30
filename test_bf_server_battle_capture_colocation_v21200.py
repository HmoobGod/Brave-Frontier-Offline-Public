"""v212 synthetic privacy/co-location tests; no real account or capture data."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile
import audit_bf_server_battle_capture_colocation_v21200 as audit
import audit_bf_server_battle_capture_fields_v20200 as v202

SECRET = 'DONT-LEAK-PRIVATE-SAVE-OR-AUTH-TOKEN'
bundle = {
    'messages': [
        {'onlyMonsters': {'U0v5IeJo': [{'secret': SECRET}]}},
        {'onlyGroups': {'75t0sx9z': [1], 'pj41dy9g': [2]}},
        {'unrelated': {'89ausgc4': [3]}},
    ],
    'headers': [{'authorization': SECRET}],
}
raw = json.dumps(bundle).encode('utf-8')
original = bytes(raw)
result = audit.inspect_bytes(raw)
assert result['inputSha256'] == hashlib.sha256(raw).hexdigest()
assert result['decodedJsonContainerNodesVisited'] > 1
assert result['globallyAllThreeBattleFieldNamesObserved'] is True
assert result['sameObjectCandidateBattleFieldsObserved'] is False
assert result['sameObjectFourCandidateFieldsObserved'] is False
assert result['objectsWithCoLocatedThreeBattleFields'] == 0
assert result['objectsWithAnyCandidateField'] == 3
assert result['objectsWithExactlyOneCandidateField'] == 2
assert result['objectsWithExactlyTwoCandidateFields'] == 1
assert result['objectsWithExactlyThreeCandidateFields'] == 0
assert result['objectsWithAllFourCandidateFields'] == 0
assert all(result[field] is False for field in (
    'original2022CaptureProvenanceVerified',
    'original2022BattleFieldSemanticsDecoded',
    'original2022EncounterGroupJoinVerified',
    'original2022OrderedWavesVerified',
    'original2022EnemyAiAndDropsVerified',
    'mutatesGameOrSave',
))
assert SECRET not in json.dumps(result)
assert raw == original
assert result == audit.inspect_bytes(raw)

same_obj = {'packet': {
    'U0v5IeJo': [{'value': SECRET}],
    '75t0sx9z': [SECRET],
    'pj41dy9g': {'secret': SECRET},
    '89ausgc4': [SECRET],
}}
same = audit.inspect_bytes(json.dumps(same_obj).encode())
assert same['objectsWithCoLocatedThreeBattleFields'] == 1
assert same['objectsWithAllFourCandidateFields'] == 1
assert same['objectsWithExactlyThreeCandidateFields'] == 0
assert same['sameObjectFourCandidateFieldsObserved'] is True
assert SECRET not in json.dumps(same)

three_only = audit.inspect_bytes(json.dumps({'packet': {
    'U0v5IeJo': None, '75t0sx9z': None, 'pj41dy9g': None,
}}).encode())
assert three_only['sameObjectCandidateBattleFieldsObserved'] is True
assert three_only['sameObjectFourCandidateFieldsObserved'] is False
assert three_only['objectsWithExactlyThreeCandidateFields'] == 1
assert three_only['objectsWithAllFourCandidateFields'] == 0

# Two distinct packets under one array never prove same-object presence.
packets = audit.inspect_bytes(json.dumps([
    {'U0v5IeJo': [], '75t0sx9z': []},
    {'pj41dy9g': [], '89ausgc4': []},
]).encode())
assert packets['globallyAllThreeBattleFieldNamesObserved'] is True
assert packets['sameObjectCandidateBattleFieldsObserved'] is False
assert packets['objectsWithExactlyTwoCandidateFields'] == 2
assert audit.inspect_bytes(b'{"text":"U0v5IeJo,75t0sx9z,pj41dy9g"}')[
    'objectsWithAnyCandidateField'] == 0


def rejects(data):
    try:
        audit.inspect_bytes(data)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return
    raise AssertionError('unsafe or malformed input accepted')


rejects(b'{"U0v5IeJo":1,"U0v5IeJo":2}')
rejects(b'{"bad":')
rejects(bytes([255]))
rejects(b'null')
rejects(b'[' + b'0,' * (v202.MAX_BYTES // 2) + b'0]')
rejects(b'[' * (v202.MAX_DEPTH + 2) + b'0' +
        b']' * (v202.MAX_DEPTH + 2))
rejects(json.dumps([{}] * (v202.MAX_NODES + 1)).encode())

with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / 'sanitized-decoded.json'
    path.write_bytes(raw)
    cli = subprocess.run([sys.executable, str(Path(audit.__file__)),
                          '--input', str(path)],
                         capture_output=True, text=True, check=True)
    assert json.loads(cli.stdout) == result
    assert path.read_bytes() == raw
    assert SECRET not in cli.stdout + cli.stderr

print('PASS v212: same-object vs global co-occurrence, 7 safety probes, privacy, repeatability')
