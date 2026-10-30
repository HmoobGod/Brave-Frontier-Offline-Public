"""v214: fail-closed, non-disclosing CLI error regressions for local-only auditors."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest import mock

import audit_bf_server_battle_capture_fields_v20200 as v202
import audit_bf_server_battle_capture_colocation_v21200 as v212

ROOT = Path(__file__).resolve().parent
TOOLS = (
    ('v202', v202, ROOT / 'audit_bf_server_battle_capture_fields_v20200.py'),
    ('v212', v212, ROOT / 'audit_bf_server_battle_capture_colocation_v21200.py'),
)
SECRET = 'PRIVATE_CAPTURE_CREDENTIAL_214'


def subprocess_reject(script, target):
    run = subprocess.run(
        [sys.executable, str(script), '--input', str(target)],
        cwd=ROOT, text=True, capture_output=True, check=False, timeout=20
    )
    assert run.returncode == 2, (script, run.returncode, run.stderr[-500:])
    assert run.stdout == ''
    assert 'Traceback' not in run.stderr
    assert SECRET not in run.stderr
    assert 'invalid input or unsafe source' in run.stderr or (
        'input missing or exceeds size' in run.stderr
    )
    assert '0xff' not in run.stderr.lower()  # no invalid-byte disclosure
    assert 'position ' not in run.stderr.lower()  # no UTF-8 position disclosure
    return run.stderr


def mocked_io_error(cli_module, target, patched_method):
    # A deterministic error injection, independent of root/non-root file permissions.
    stderr = io.StringIO()
    stdout = io.StringIO()
    with (mock.patch.object(sys, 'argv', ['audit', '--input', str(target)]),
          mock.patch.object(Path, patched_method,
                            side_effect=PermissionError(SECRET)),
          contextlib.redirect_stderr(stderr),
          contextlib.redirect_stdout(stdout)):
        try:
            cli_module.main()
        except SystemExit as exc:
            assert exc.code == 2, (patched_method, exc.code)
        else:
            raise AssertionError('PermissionError was not rejected')
    assert stdout.getvalue() == ''
    assert SECRET not in stderr.getvalue()
    assert 'Traceback' not in stderr.getvalue()
    assert 'error:' in stderr.getvalue()


with tempfile.TemporaryDirectory() as directory:
    tmp = Path(directory)
    valid_file = tmp / 'decoded.json'
    valid_file.write_bytes(b'{"safe": 1}')
    bad_files = {
        'mid-depth.json': b'[' * 40 + b'0' + b']' * 40,
        'deep-object.json': b'{"a":' * 4096 + b'0' + b'}' * 4096,
        'invalid-utf8.json': b'{"secret":"' + SECRET.encode() + b'\xff"}',
        'malformed-private.json': (
            '{"secret":"' + SECRET + '","incomplete":'
        ).encode(),
        'empty.json': b'',
    }
    for filename, data in bad_files.items():
        path = tmp / filename
        path.write_bytes(data)
        for _, _, cli in TOOLS:
            subprocess_reject(cli, path)
        assert path.read_bytes() == data

    for name, module, cli in TOOLS:
        # A readable, ordinary file must still work with unchanged report schema.
        completed = subprocess.run(
            [sys.executable, str(cli), '--input', str(valid_file)],
            cwd=ROOT, text=True, capture_output=True, check=True, timeout=20
        )
        report = json.loads(completed.stdout)
        assert report['mutatesGameOrSave'] is False
        assert completed.stderr == ''
        # Exceptions raised after is_file()/stat() must not produce a traceback.
        mocked_io_error(module, valid_file, 'read_bytes')
        # Simulate stat failure before file read.
        mocked_io_error(module, valid_file, 'stat')

print('PASS v214: generic CLI errors, deep array/object, privacy and I/O failures')
