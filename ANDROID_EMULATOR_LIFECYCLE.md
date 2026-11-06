# Isolated Android lifecycle acceptance

The owner explicitly approved installing the diagnostic APK on a fresh disposable
CI emulator on November 6, 2026. The existing diagnostic verification command
runs `--packaged --emulator`. This permission does not authorize installation on
the owner's phone, use of real saves, or installation of the standard app.
It boots a newly created Android35 AVD on CI, with KVM and a bounded boot timeout,
and installs only `org.bravefrontier.offline.diagnostic` on `emulator-5556` after
checking the guest's QEMU property. Any existing ADB device aborts the test.
Every device mutation specifies that serial. The standard APK is never installed.

Wi-Fi/mobile data are disabled before app launch. Playwright attaches to the
diagnostic WebView with automatic helper-APK installation disabled. Test battle
state is temporary; enemies survive, so there are no quest rewards. Real Android
HOME and Activity return must deliver a hidden event, stop Auto, permit at most
the active round to finish, and leave Auto off after returning. Whole player and
canonical v7 storage values must stay unchanged; only hashes are compared/logged.
No owner phone, user save, signing key or real progression participates.

WebView debugging is explicitly enabled only for the existing debuggable,
isolated diagnostic variant. Standard app permissions, signing and identity are
unchanged. Existing workflow triggers/permissions and diagnostic fail-closed
rules stay intact; no new workflow or bypass is added. Native acceptance fails
if SDK/KVM/boot/WebView/lifecycle checks fail; it is never reported as a pass
merely because a source test succeeded.

An emulator pass is Android runtime evidence, not physical-device acceptance or
full gameplay completion. Until the actual CI run succeeds, this is a prepared
test and must not be described as native lifecycle verification.
