# v337 — Android emulator SDK installation reliability (native gate unchanged)

Base: merged main `493f40feb216f6898835d24dd9e6b97d2e454c64` (#332). Independent of draft #335 and #336, with no overlapping paths.

## Observed CI failure

The main Android workflow run [42816839101](https://github.com/HmoobGod/Brave-Frontier-Offline-Public/actions/runs/42816839101) failed at **Verify built APK IDs, original assets, and offline permissions** after the diagnostic binary/source checks had passed. The traceback was in `tools/android_lifecycle_ci.py`: `sdkmanager --install emulator system-images;android-35;google_apis;x86_64` returned code 1. Its stdout/stderr had been redirected to a disposable temporary `sdk.log` and deleted by `TemporaryDirectory`, so the root SDK failure message could not be inspected from workflow logs. This is a native acceptance *not run*, not a game behavior PASS.

## Fix

- Retry only failed/timed-out Android SDK emulator/system-image installation, up to **three** attempts with waits of 5 and 10 seconds. Keep package identity, SDK source, AVD name, emulator serial, target, KVM and all device guards unchanged.
- On persistent failure, expose only the last 3000 characters of the disposable SDK installer log and raise `RuntimeError`, retaining **hard CI failure**. Never skip native acceptance, never mark success on SDK provisioning failures.
- Add source unit regression cases in `test_bf_android_lifecycle_safety.py` for failed-then-successful SDK installation, all-three nonzero exits, and all-three timeouts. The source test does not stand in for an emulator run.

## Promotion

Exact-head signed Android full workflow, source-only/packaged checks and independent source review before merge. No owner APK/save, Android app/signing identity, UI assets, or gameplay mechanics changed.
