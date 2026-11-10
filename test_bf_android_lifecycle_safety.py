"""Reject phones/existing devices/standard APK before native lifecycle mutation."""
import importlib.util
from pathlib import Path
from io import StringIO
import subprocess
from unittest.mock import patch

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('native_ci',ROOT/'tools/android_lifecycle_ci.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
native.require_empty_devices('List of devices attached\n\n')
native.require_target('emulator-5556','1\n')
assert native.diagnostic_component("package: name='org.bravefrontier.offline.diagnostic'\nlaunchable-activity: name='org.bravefrontier.offline.MainActivity'").endswith('/org.bravefrontier.offline.MainActivity')
for callback in (
 lambda:native.require_empty_devices('List of devices attached\nPHONE\tdevice\n'),
 lambda:native.require_empty_devices('List of devices attached\nemulator-5554\tdevice\n'),
 lambda:native.require_target('PHONE','1'),
 lambda:native.require_target('emulator-5556','0'),
 lambda:native.diagnostic_component("package: name='org.bravefrontier.offline'\nlaunchable-activity: name='org.bravefrontier.offline.MainActivity'"),
):
 try:callback()
 except RuntimeError:pass
 else:raise AssertionError('Unsafe native test target was accepted')
print('PASS native lifecycle safety: phones, existing devices and standard package rejected')


# The real emulator is still mandatory. These offline unit tests exercise only
# SDK installer retries and prove that three failures never become a pass.
call_args = []
def recover_after_transient(argv, **kwargs):
    call_args.append((argv, kwargs))
    if len(call_args) == 1:
        raise subprocess.CalledProcessError(1, argv)
    return subprocess.CompletedProcess(argv, 0)

with patch.object(native.subprocess, 'run', side_effect=recover_after_transient), \
     patch.object(native.time, 'sleep', return_value=None) as sleeper:
    native.install_ci_emulator_image('/ci/sdkmanager', native.IMAGE,
                                     {'ANDROID_HOME': '/ci'}, StringIO())
assert len(call_args) == 2
assert call_args[0][0] == ['/ci/sdkmanager', '--install', 'emulator', native.IMAGE]
assert all(kwargs['input'] == 'y\n' * 20 and kwargs['check'] is True
           and kwargs['timeout'] == 600 for _, kwargs in call_args)
assert sleeper.call_count == 1

fail_calls = []
def always_fails(argv, **kwargs):
    fail_calls.append(argv)
    raise subprocess.CalledProcessError(1, argv)

output = StringIO()
with patch.object(native.subprocess, 'run', side_effect=always_fails), \
     patch.object(native.time, 'sleep', return_value=None) as sleeper:
    try:
        native.install_ci_emulator_image('/ci/sdkmanager', native.IMAGE, {}, output)
    except RuntimeError as exc:
        assert 'native acceptance was NOT run' in str(exc)
        assert 'sdkmanager attempt 3/3' in str(exc)
        assert len(str(exc)) < 4000
    else:
        raise AssertionError('Three SDK installation failures must fail CI')
assert len(fail_calls) == 3
assert sleeper.call_count == 2

# A hung SDK manager must receive the same bounded retry and fail closed.
with patch.object(native.subprocess, 'run', side_effect=subprocess.TimeoutExpired(
      ['/ci/sdkmanager', '--install', 'emulator', native.IMAGE], 600)), \
     patch.object(native.time, 'sleep', return_value=None):
    try:
        native.install_ci_emulator_image('/ci/sdkmanager', native.IMAGE, {}, StringIO())
    except RuntimeError as exc:
        assert 'TimeoutExpired' in str(exc)
    else:
        raise AssertionError('Three SDK timeouts must fail CI')
print('PASS v337 SDK resilience: retry recovery and fail-closed 3x exit/timeout with bounded logs')
