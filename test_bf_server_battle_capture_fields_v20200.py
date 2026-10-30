"""v202 synthetic candidate-key intake smoke, no user captures or APK mutation."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile
import audit_bf_server_battle_capture_fields_v20200 as audit

payload = {
    'log': {'entries': [
        {'response': {'decoded': {'pj41dy9g': [{'75t0sx9z': [
            {'U0v5IeJo': [{'hp': 900, 'ai': 'not verified'}]}]}]}}},
        {'request': {'headers': [{'name': 'Authorization', 'value': 'SECRET-DONT-LEAK'}]}},
    ]},
    '89ausgc4': [{'untrusted': True}],
}
raw = json.dumps(payload).encode()
summary = audit.inspect_bytes(raw)
assert summary['inputSha256'] == hashlib.sha256(raw).hexdigest()
assert summary['allThreeBattleFieldNamesObserved'] is True
assert all(summary['candidateFieldPresence'].values())
assert summary['decodedJsonContainerNodesVisited'] > 5
assert all(summary[key] is False for key in (
    'original2022ProvenanceVerified', 'original2022OrderedWavesVerified',
    'original2022EnemyAiAndDropsVerified', 'mutatesGameOrSave'))
assert 'SECRET-DONT-LEAK' not in json.dumps(summary)
assert audit.inspect_bytes(raw) == summary
assert audit.inspect_bytes(b'{"decoy":"U0v5IeJo 75t0sx9z pj41dy9g"}')[
    'allThreeBattleFieldNamesObserved'] is False
assert audit.inspect_bytes(b'{"U0v5IeJo":1}')['allThreeBattleFieldNamesObserved'] is False


def rejects(raw):
    try:
        audit.inspect_bytes(raw)
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return
    raise AssertionError('malformed/unsafe candidate input was accepted')


rejects(b'{"U0v5IeJo":1,"U0v5IeJo":2}')  # duplicate key
rejects(b'{"data":')  # malformed
rejects(bytes([255]))  # non-UTF8 input
rejects(b'1234')  # not an object/array
rejects(b'[' + b'0,' * (audit.MAX_BYTES // 2) + b'0]')  # size
rejects(b'[' * (audit.MAX_DEPTH + 2) + b'0' + b']' * (audit.MAX_DEPTH + 2))
rejects(json.dumps([{}] * (audit.MAX_NODES + 1)).encode())

with tempfile.TemporaryDirectory() as temp:
    source = Path(temp) / 'sample-decoded.json'
    source.write_bytes(raw)
    check = subprocess.run([sys.executable, str(Path(audit.__file__)),
                            '--input', str(source)],
                           check=True, capture_output=True, text=True)
    assert json.loads(check.stdout) == summary
    assert source.read_bytes() == raw
    assert 'SECRET-DONT-LEAK' not in check.stdout
print('PASS v202: candidate field inventory, 7 invalid-input probes, no source-body disclosure')
