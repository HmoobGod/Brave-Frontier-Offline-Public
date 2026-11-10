"""Boot a disposable CI emulator and test only the isolated diagnostic APK.

Never targets a phone, an existing AVD, the standard app, or a real save.
"""
import argparse
import importlib.util
import os
from pathlib import Path
import re
import signal
import socket
import subprocess
import tempfile
import time

SERIAL = 'emulator-5556'
PACKAGE = 'org.bravefrontier.offline.diagnostic'
IMAGE = 'system-images;android-35;google_apis;x86_64'


def require_empty_devices(output):
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if lines != ['List of devices attached']:
        raise RuntimeError('Existing ADB device or unexpected response; refusing test')


def require_target(serial, qemu):
    if serial != SERIAL or qemu.strip() != '1':
        raise RuntimeError('Only the dedicated emulator target is permitted')


def diagnostic_component(badging):
    package = re.search(r"(?m)^package: name='([^']+)'", badging)
    activity = re.search(r"(?m)^launchable-activity: name='([^']+)'", badging)
    if not package or package[1] != PACKAGE or not activity:
        raise RuntimeError('Expected the isolated diagnostic APK and launch activity')
    if not re.fullmatch(r'[A-Za-z0-9_.]+', activity[1]):
        raise RuntimeError('Unexpected activity identifier')
    return PACKAGE + '/' + activity[1]


def install_ci_emulator_image(manager, image, env, log):
    """Bounded retry for SDK downloads; never skip native emulator acceptance."""
    command = [str(manager), '--install', 'emulator', image]
    for attempt in range(1, 4):
        log.write(f'\\n[Android CI sdkmanager attempt {attempt}/3]\\n')
        log.flush()
        try:
            subprocess.run(command, input='y\\n'*20, text=True, stdout=log,
                           stderr=subprocess.STDOUT, env=env, check=True, timeout=600)
            return
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            log.write(f'\\n[SDK install attempt {attempt}/3 failed: {type(exc).__name__}]\\n')
            log.flush()
            if attempt < 3:
                time.sleep(5 * attempt)
    # The disposable sdk.log is deleted on failure. Preserve a bounded excerpt
    # so persistent SDK/package/network failures can be diagnosed in CI.
    log.seek(0)
    tail = log.read()[-3000:]
    raise RuntimeError('Required Android CI emulator image unavailable after 3 '
                       'attempts; native acceptance was NOT run. sdkmanager tail:\\n'
                       + tail)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apk', type=Path, required=True)
    args = parser.parse_args()
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('Disposable emulator bootstrap is CI-only')
    if not args.apk.is_file():
        raise RuntimeError('Diagnostic APK unavailable')
    sdk = Path(os.environ.get('ANDROID_HOME', ''))
    adb, emulator, aapt = (sdk/'platform-tools/adb', sdk/'emulator/emulator',
                           sdk/'build-tools/35.0.0/aapt')
    managers = sorted(sdk.glob('cmdline-tools/*/bin/sdkmanager'))
    if not managers or not adb.is_file() or not aapt.is_file():
        raise RuntimeError('Existing Android CI SDK tools unavailable')
    manager = managers[-1]
    avdmanager = manager.with_name('avdmanager')
    if not avdmanager.is_file():
        raise RuntimeError('Android AVD manager unavailable')
    if not Path('/dev/kvm').exists():
        raise RuntimeError('KVM unavailable; native emulator acceptance cannot run')
    if not os.access('/dev/kvm', os.R_OK | os.W_OK):
        subprocess.run(['sudo', 'chmod', 'a+rw', '/dev/kvm'], check=True, timeout=15)
    require_empty_devices(subprocess.check_output([str(adb), 'devices'], text=True))
    for port in (5556, 5557):
        with socket.socket() as check:
            check.bind(('127.0.0.1', port))
    component = diagnostic_component(subprocess.check_output(
        [str(aapt), 'dump', 'badging', str(args.apk)], text=True))
    playwright = importlib.util.find_spec('playwright')
    if not playwright or not playwright.origin:
        raise RuntimeError('Existing Playwright dependency unavailable')
    driver = Path(playwright.origin).parent/'driver'
    node, package = driver/'node', driver/'package'
    if not node.is_file() or not (package/'index.js').is_file():
        raise RuntimeError('Playwright Node runtime unavailable')
    with tempfile.TemporaryDirectory(prefix='bf-native-ci-') as folder:
        work = Path(folder)
        env = {**os.environ, 'ANDROID_AVD_HOME': str(work/'avds'),
               'ANDROID_EMULATOR_HOME': str(work/'emulator-home')}
        Path(env['ANDROID_AVD_HOME']).mkdir()
        Path(env['ANDROID_EMULATOR_HOME']).mkdir()
        with (work/'sdk.log').open('w+', encoding='utf-8') as log:
            install_ci_emulator_image(manager, IMAGE, env, log)
            subprocess.run([str(avdmanager), 'create', 'avd', '--name', 'bf-ci-lifecycle',
                            '--package', IMAGE, '--device', 'pixel_5',
                            '--path', str(work/'fresh.avd')], input='no\n', text=True,
                           stdout=log, stderr=subprocess.STDOUT, env=env,
                           check=True, timeout=60)
        if not emulator.is_file():
            raise RuntimeError('Android emulator executable unavailable')
        with (work/'emulator.log').open('w') as log:
            proc = subprocess.Popen([str(emulator), '-avd', 'bf-ci-lifecycle',
                '-port', '5556', '-no-window', '-no-audio', '-no-boot-anim',
                '-no-snapshot', '-gpu', 'swiftshader_indirect', '-accel', 'on',
                '-cores', '2', '-memory', '2048'], stdout=log,
                stderr=subprocess.STDOUT, env=env, start_new_session=True)
            try:
                def command(*parts, timeout=20):
                    return subprocess.check_output([str(adb), '-s', SERIAL, *parts],
                        text=True, stderr=subprocess.STDOUT, timeout=timeout).strip()
                deadline = time.monotonic()+240
                while True:
                    if proc.poll() is not None:
                        raise RuntimeError('Disposable emulator exited before boot')
                    try:
                        if command('shell', 'getprop', 'sys.boot_completed') == '1':
                            break
                    except (subprocess.SubprocessError, OSError):
                        pass
                    if time.monotonic() >= deadline:
                        raise RuntimeError('Disposable emulator boot timed out')
                    time.sleep(2)
                require_target(SERIAL, command('shell', 'getprop', 'ro.kernel.qemu'))
                # Every mutating device command names the verified emulator.
                command('shell', 'svc', 'wifi', 'disable')
                command('shell', 'svc', 'data', 'disable')
                command('shell', 'input', 'keyevent', 'KEYCODE_WAKEUP')
                command('shell', 'wm', 'dismiss-keyguard')
                command('install', str(args.apk.resolve()), timeout=90)
                command('shell', 'am', 'start', '-W', '-n', component, timeout=60)
                test_env = {**env, 'BF_PLAYWRIGHT_PACKAGE': str(package),
                    'BF_TEST_ADB': str(adb), 'BF_TEST_COMPONENT': component}
                subprocess.run([str(node), str(Path(__file__).with_name(
                    'android_lifecycle_case.cjs'))], env=test_env, check=True, timeout=240)
            finally:
                if proc.poll() is None:
                    os.killpg(proc.pid, signal.SIGTERM)
                    try:
                        proc.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        os.killpg(proc.pid, signal.SIGKILL)
                        proc.wait(timeout=15)


if __name__ == '__main__':
    main()
