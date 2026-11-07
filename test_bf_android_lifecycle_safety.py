"""Reject phones/existing devices/standard APK before native lifecycle mutation."""
import importlib.util
from pathlib import Path

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
