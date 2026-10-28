# v164 — Export the current canonical v7 save, not only a rotating backup

## Motivation
The existing optional v97 backup panel stores up to three local snapshots and can export one. Those snapshots may lag the current game save. Older APKs can silently discard the original first-clear evidence introduced in v160/v161 when they parse and rewrite the same v7 JSON key. Uninstall can also delete app-local backup slots.

## User-visible behavior
Under **QoL · LOCAL SAVE BACKUPS**, an additional **EXPORT CURRENT SAVE** button exports the exact currently stored `bf_global_offline_demo_v7` JSON. It does not capture a new snapshot, alter the current save, trigger a Gem grant, or require internet.

- The existing **EXPORT A BACKUP** button still exports the selected prior snapshot.
- A missing, malformed or out-of-size current save is rejected.
- Android's existing `BFAndroid.exportSaveFile` Storage Access Framework callback is used directly from the click. The browser-only fallback continues to use a downloadable JSON blob.
- The backup panel now warns specifically to export the current save before using an older APK because old parsers can discard newer fields.
- Current progress remains in v7 format, the existing canonical storage key and signing identity are unchanged. The optional backup panel and its existing opt-out behavior are preserved.

## Regression
The existing v97 GitHub Actions Playwright test now puts v160/v161 first-clear ledger and pending evidence into the current canonical JSON without updating the rotating snapshot. It clicks **EXPORT CURRENT SAVE**, asserts byte-exact JSON and preserved marker, verifies that neither active storage nor snapshots are overwritten, and checks invalid saves are not exported. Existing snapshot export, rotation, opt-out and re-enable checks remain active.

This is a **backup mechanism**, not a reversible old-APK downgrade guarantee. It cannot prevent an old app from dropping unknown fields; safe recovery requires keeping the exported file outside the app and importing it into a compatible newer APK.

## Gate
Exact v164 head CI success, v162 merged-main CI success, guarded merge after resolving v163, fresh merged-main CI success. No install of v164 is requested before verification.
