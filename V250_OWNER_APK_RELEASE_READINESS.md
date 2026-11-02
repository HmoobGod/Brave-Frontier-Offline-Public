# v250 — Owner APK release checkpoint (preparation only)

**Not released, not merged, no device acceptance yet.** v249 PR #183 is now independently verified and merged into `main` at `f7437271e0913030eed83de412fb6961acdfb21a` (Android Build #1476 SUCCESS and all six source preflights SUCCESS). v250 PR #184 is now retargeted to merged `main`. This checkpoint update triggers a **fresh exact-head Android build**, not a release or device acceptance. Original Global game parity remains incomplete. No user Current APK or saves have been changed or installed by this work.

## Purpose
Before offering the next owner-installable offline debug APK, verify all release gates while protecting the actual app identity and existing save migration.

### Mandatory source/CI checks
- Default installable APK keeps `org.bravefrontier.offline`, not `org.bravefrontier.offline.diagnostic`. The diagnostic app remains separate and must **never** be used to update the user's Current.
- Existing **persistent development debug keystore** restored from Actions secret is required for in-place upgrades; verify the certificate match to the owner's currently installed APK before installing. Never export/share the keystore or bypass signing checks.
- Gradle versionName is updated from stale `174.00.0-demo` to **`250.00.0-demo`** so the owner-facing Android display version matches this checkpoint; `applicationId`, signing configuration and CI-derived versionCode are unchanged. This does **not** prove the app is complete or safe to upgrade by itself.
- Gradle versionCode is CI-generated, and the same-signature / higher-versionCode update must be checked against the user's actual installed build. A green CI run **does not prove** an in-place update can install.
- Manifest stays offline (no INTERNET permission; cleartext traffic disabled).
- Existing v7/v124 save compatibility and full packaged migration/backup tests must pass at exact head; owner should back up/export data before test installation.
- All original-art Home UI tests v242–v249 and nav resource-budget tests remain enabled. Exact-head source-only checks and full Android signed APK build must pass.
- Android Actions `BraveFrontierOffline-demo-debug-apk` is the standard app update artifact, **not** either of the two isolated diagnostic APK artifacts. The artifact normally contains `app-debug.apk` and is accessible through GitHub Actions when run permissions permit it.

New test `test_bf_v250_release_readiness_v25000.py` audits these configuration and workflow guards in source CI and full Android workflow. It is not a device emulator test or a release approval.

## Strict merge sequence
1. v247 PR #181 — MERGED after Android Build #1455 SUCCESS.
2. v248 PR #182 — MERGED after Android Build #1468 SUCCESS.
3. v249 PR #183 — MERGED after corrected exact-head Android Build #1476 SUCCESS; the original browser selector ambiguity was corrected without runtime changes.
4. v250 PR #184 — now targeting merged `main`; require fresh exact-head source and full Android CI SUCCESS, then obtain **Claude independent milestone review** on the final SHA, artifact and preservation evidence; do not merge until approved.
5. Obtain owner device feedback and real save backup/upgrade checks. Keep current installation unchanged until the user deliberately installs the verified standard APK; never distribute diagnostic fault APK as an update.

### Evidence to capture for Claude
Exact source HEAD/base/merge-base, build run ID/conclusion, source preflights, owner-installable artifact name and hash (if obtained), source/packaged save migration tests, persistent signing identity check, unchanged app ID/versionCode and no network permission, original Home art fidelity/limitations and remaining original-gameplay blockers. Clearly distinguish source/CI tests from physical phone testing.

## Scope
New test, CI registration, documentation and **only the Gradle display `versionName`**. Zero Android Java/asset/sprite/gameplay/reward/save-runtime, package ID, signing key, or versionCode behavior changes. Overall full-game reconstruction remains estimated at ~30% (low-confidence), not a claim of a complete original 2022 Brave Frontier Global.
