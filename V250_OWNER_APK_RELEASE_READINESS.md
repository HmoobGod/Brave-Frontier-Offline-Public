# v250 — Owner APK release checkpoint (preparation only)

**Not released, not merged, no device acceptance yet.** This source-only guard is intentionally stacked after v249 PR #183 `09f943c4c0a063e881c39afe14160e0f76a95dca`, itself dependent on v248 and v247. Original Global game parity remains incomplete. No user Current APK or saves have been changed or installed by this work.

## Purpose
Before offering the next owner-installable offline debug APK, verify all release gates while protecting the actual app identity and existing save migration.

### Mandatory source/CI checks
- Default installable APK keeps `org.bravefrontier.offline`, not `org.bravefrontier.offline.diagnostic`. The diagnostic app remains separate and must **never** be used to update the user's Current.
- Existing **persistent development debug keystore** restored from Actions secret is required for in-place upgrades; verify the certificate match to the owner's currently installed APK before installing. Never export/share the keystore or bypass signing checks.
- Gradle versionCode is CI-generated, and the same-signature / higher-versionCode update must be checked against the user's actual installed build. A green CI run **does not prove** an in-place update can install.
- Manifest stays offline (no INTERNET permission; cleartext traffic disabled).
- Existing v7/v124 save compatibility and full packaged migration/backup tests must pass at exact head; owner should back up/export data before test installation.
- All original-art Home UI tests v242–v249 and nav resource-budget tests remain enabled. Exact-head source-only checks and full Android signed APK build must pass.
- Android Actions `BraveFrontierOffline-demo-debug-apk` is the standard app update artifact, **not** either of the two isolated diagnostic APK artifacts. The artifact normally contains `app-debug.apk` and is accessible through GitHub Actions when run permissions permit it.

New test `test_bf_v250_release_readiness_v25000.py` audits these configuration and workflow guards in source CI and full Android workflow. It is not a device emulator test or a release approval.

## Strict merge sequence
1. v247 PR #181 — confirm exact-head Android Build #1455 success; merge only after green.
2. v248 PR #182 — retarget `main`, make a fresh exact-head CI run, confirm every required gate including signed Android APK, then merge.
3. v249 PR #183 — retarget `main`, fresh exact-head full Android UI regression/build, then merge.
4. v250 release-candidate PR — retarget `main`, exact-head source and full Android CI green; prepare **Claude independent milestone review** with exact SHA, artifact and preservation evidence; do not merge until approved.
5. Obtain owner device feedback and real save backup/upgrade checks. Keep current installation unchanged until the user deliberately installs the verified standard APK; never distribute diagnostic fault APK as an update.

### Evidence to capture for Claude
Exact source HEAD/base/merge-base, build run ID/conclusion, source preflights, owner-installable artifact name and hash (if obtained), source/packaged save migration tests, persistent signing identity check, unchanged app ID/versionCode and no network permission, original Home art fidelity/limitations and remaining original-gameplay blockers. Clearly distinguish source/CI tests from physical phone testing.

## Scope
New test, CI registration, and documentation only. Zero Android Java/asset/sprite/gameplay/reward/save-runtime changes. Overall full-game reconstruction remains estimated at ~30% (low-confidence), not a claim of a complete original 2022 Brave Frontier Global.
