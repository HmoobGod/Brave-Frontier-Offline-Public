# Brave Frontier Offline v0.9.1 — Shared Save File and Future Cloud Roadmap

## Working now in source (APK build pending)
- Save format: `bf-global-offline-demo`, version 4, same as v0.9.
- Browser: **Download Save File** creates a `.json` file; **Import Save File** reads it and validates all values before confirmation.
- Android (after compiling APK): native Android Storage Access Framework chooser for JSON import/export. Save JSON is passed between the packaged HTML and the Android Java activity via a JavaScript bridge.
- Import replaces only the local destination's progress; it does not merge saves or update other devices. A pre-import local one-step undo backup is kept, though a separate exported backup is safer.
- Previously supported Save Code copy/paste remains available.
- Data transfers can occur over USB, email to yourself, Google Drive, or local files. There is no cloud login in this release and no need to give ChatGPT access to personal Google accounts.

## Future: Google Play Games Services Saved Games for Android
Requirements:
1. Google Play Console developer enrollment and a Play Games Services project with Saved Games enabled.
2. Registered package name and signing certificate fingerprints; Google Play Games Services v2 SDK authentication.
3. Android native layer uses `SnapshotsClient` to read/write the exact same validated v4 save JSON bytes; no gameplay code rewrite needed.
4. Resolve cross-device conflicts safely, e.g. ask which of two copies to keep, showing timestamp and progress. Never overwrite cloud data silently.
5. Offline-first: local progress always works and can be exported manually. Upload on explicit consent and handle signed-out/network errors.
6. Test with authorized Play Games testing accounts and signed Android builds.

Android Play Games Saved Games does NOT automatically sync an ordinary Chrome/browser version. For true web + APK cloud sync, add a separate web-capable authentication/storage architecture (e.g. Firebase Authentication + Firestore with strict security rules and verified linked identity), or a secure backend which associates a Play Games player ID with another account. This entails extra setup, security, costs and conflict handling.

### Rights consideration
The original Brave Frontier images and game content remain copyrighted. Public Google Play Store release or distribution may require rights-holder permission. A private debug APK does not establish permission to publish; seek authorization before public release.

Official sources:
- https://developer.android.com/games/pgs/savedgames
- https://developer.android.com/games/pgs/android/saved-games
- https://developer.android.com/games/pgs/android/android-signin

## Tests
- Chromium browser export, JSON validation, import, pre-import undo, malformed-save rejection, v3 migration, Android JS bridge contract, and separate-session persisted save reload: passed using mocked localStorage (browser harness cannot navigate a local HTML file).
- A complete three-wave Auto Battle in Chromium ended in victory; demo quest rewards persisted.
- Android Java project not compiled or device-tested in this environment.
