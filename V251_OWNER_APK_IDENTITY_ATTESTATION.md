# v251 — Standard owner APK certificate and upgrade evidence (source/CI only)

**Base:** verified v250 merge `496c7366eaa9a27f4ced34b73c3faa132090873d` (PR #184). No changes to Brave Frontier original gameplay, Java, original sprites, packaged save schema, Android manifest, signing key, or applicationId.

## The gap this patch closes

v250's APK artifact is available, and full Android tests passed, but CI did not publish a compact, independently readable **certificate fingerprint + APK SHA-256 + package/versionCode** report that the owner can compare to their actually installed v124 app. v251 emits that evidence from the signed **standard** APK, not from the diagnostic package or a private keystore.

`test_bf_owner_apk_identity_v25100.py --source-only` checks fail-closed parsers, workflow wiring, offline manifest, signing config and canonical identity. After `assembleDebug` and packaged tests, `--packaged` uses Android SDK `aapt` and `apksigner verify --print-certs` to inspect `app/build/outputs/apk/debug/app-debug.apk`. It refuses wrong package ID, wrong CI-derived versionCode, wrong historical display versionName, INTERNET permission, an absent/multiple certificate digest, a missing APK, or bad signature verification. It hashes the APK using SHA-256.

The separate GitHub Actions artifact `BraveFrontierOffline-v251-owner-apk-identity` contains only `source_audit_reports/BraveFrontier-v251-owner-apk-identity.json`. The **existing installable** `BraveFrontierOffline-demo-debug-apk` artifact and path are unchanged. The report carries **separate provenance fields**: `github_sha` (the event/checkout commit, normally a synthetic merge commit for a pull_request build), `github_event_name`, `pull_request_head_sha` (the exact PR head for PR runs; null for push/dispatch), `source_head_sha` (the logical PR head or push/dispatch commit), and `checked_out_commit_sha` (verified with `git rev-parse HEAD` to equal `github_sha`). The `source_head_sha` on a PR build is **not** a claim that its artifact was built directly from the head without the PR merge; the APK is built from the checked-out merge commit. All SHA values must be exactly 40 lowercase hexadecimal digits, and PR events without a valid head fail closed. It also reports workflow run number, standard APK SHA-256, package ID, versionCode, historical display versionName `174.00.0-demo`, and certificate SHA-256. It contains no keystore, credentials, user data, save content, or installation instructions that bypass validation.

## Independent review B1 provenance correction

Claude reviewed original exact PR HEAD `c4a409941ad6e332ce9e5495a8c12503fd5c43f1` and returned **REQUEST CHANGES** because the original single `source_commit = GITHUB_SHA` mislabeled the pull_request synthetic merge as the exact PR head. The revised workflow explicitly passes `BF_PR_HEAD_SHA` and `BF_EVENT_NAME` into the packaged step, while keeping the original checkout behavior unchanged. The source script validates event/SHA inputs, rejects absent/malformed PR heads, and uses separate actual checkout and logical PR head fields described above. The old Build #1495 SUCCESS is not sufficient provenance approval for the updated PR. Require fresh exact-head source and full Android CI, an updated JSON artifact, and Claude's independent re-review at the **new** HEAD before any merge.

## Owner upgrade gate — NOT DONE BY CI

Before installing over the existing v124 app:

1. Identify the owner's current package ID, actual installed versionCode, and SHA-256 **signing certificate**. An exported copy of the owner's original v124 APK can be checked locally with the Android SDK `apksigner verify --print-certs original-v124.apk` and `aapt dump badging original-v124.apk`. Alternatively an owner-controlled Android Debug Bridge connection can list installed package/version; never use unknown third-party extraction tools or expose private files unnecessarily.
2. Compare installed package ID to `org.bravefrontier.offline`, certificate SHA-256 to v251's JSON value, and require installed versionCode to be **lower** than the candidate artifact's versionCode. A matching displayed versionName is **not** enough; v251 deliberately keeps the historical `174.00.0-demo` label.
3. While the current app still works, explicitly export/back up the real v7/v124 save through the app's supported export feature, move a copy outside the app's private storage, and verify it can be recovered. A CI synthetic-save test is **not** a real device backup.
4. Only then, after the owner opts in, install the **standard** APK over Current and smoke-test launch, Quest/Summon/Units, offline operation and restored progress. Do not uninstall, clear data, or install either diagnostic/fault APK over Current.

If the installed certificate differs or backup cannot be verified, **stop**; do not overwrite Current. In that case review the owner's original APK/signature and alternate update or migration plan separately.

## Acceptance evidence and limits

v251 is a **reporting/test-only** patch. Source-only and exact-head full Android CI must pass before merge. All prior original art, gameplay, save recovery and v250 release-safety checks stay enabled. This attestation verifies **only the newly built standard APK**, not the owner phone or a v124-installed signing certificate. It cannot prove successful device migration or complete original 2022 Brave Frontier Global gameplay (rough full-game progress remains ~30%, provisional).
