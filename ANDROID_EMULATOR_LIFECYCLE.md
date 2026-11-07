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
HOME and Activity return must deliver the real native pause callback, stop Auto, permit at most
the active round to finish, and leave Auto off after returning. Whole player and
canonical v7 storage values must stay unchanged; only hashes are compared/logged.
Actual Android BACK key dispatch must also return Quest, Units, Summon and Menu
to Home through the existing Java/WebView route bridge without exiting the app.
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

The first actual emulator run (42307922160) booted, installed and attached, but
failed because no DOM hidden event was observed. The Activity now explicitly
calls the existing battle pause operation before `WebView.onPause()` and emits
`bf-native-background` as a native callback acknowledgment. It does not forge a
DOM visibility event or alter `document.hidden`. The test requires that native
callback and reports DOM visibility delivery separately and truthfully. Corrected native acceptance passed in run42311511121 (Chrome124.0.6367.219),
including Auto pause, four Back routes and full player/canonical-save hashes;
DOM hidden events remained absent. This is emulator evidence, not phone acceptance.

The Quest music case starts the actual visible Play button, requires the bundled
MP3 media clock to advance, then checks the native background callback clears
playback intent and source and leaves music stopped after returning. This checks
WebView playback/decoder state, not audible hardware output (CI is headless).
Legacy optional music controls have browser callback coverage; no separate
native legacy-audio playback claim is made. New audio acceptance is pending CI.
