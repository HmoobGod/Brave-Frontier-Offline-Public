# v251 — Standard owner APK certificate and upgrade evidence (source/CI only)

**Base:** verified v250 merge `496c7366eaa9a27f4ced34b73c3faa132090873d` (PR #184). No changes to Brave Frontier original gameplay, Java, original sprites, packaged save schema, Android manifest, signing key, or applicationId.

## The gap this patch closes

v250's APK artifact is available, and full Android tests passed, but CI did not publish a compact, independently readable **certificate fingerprint + APK SHA-256 + package/versionCode** report that the owner can compare to their actually installed v124 app. v251 emits that evidence from the signed **standard** APK, not from the diagnostic package or a private keystore.

`test_bf_owner_apk_identity_v25100.py --source-only` checks fail-closed parsers, workflow wiring, offline manifest, signing config and canonical identity. After `assembleDebug` and packaged tests, `--packaged` uses Android SDK `aapt` and `apksigner verify --print-certs` to inspect `app/build/outputs/apk/debug/app-debug.apk`. It refuses wrong package ID, wrong CI-derived versionCode, wrong historical display versionName, INTERNET permission, an absent/multiple certificate digest, a missing APK, or bad signature verification. It hashes the APK using SHA-256.

The separate GitHub Actions artifact `BraveFrontierOffline-v251-owner-apk-identity` contains only `source_audit_reports/BraveFrontier-v251-owner-apk-identity.json`. The **existing installable** `BraveFrontierOffline-demo-debug-apk` artifact and path are unchanged. The report includes the exact source SHA, workflow run number, standard APK SHA-256, package ID, versionCode, historical display versionName `174.00.0-demo`, and certificate SHA-256. It contains no keystore, credentials, user data, save content, or installation instructions that bypass validation.

## Owner upgrade gate — NOT DONE BY CI

Before installing over the existing v124 app:

1. Identify the owner's current package ID, actual installed versionCode, and SHA-256 **signing certificate**. An exported copy of the owner's original v124 APK can be checked locally with the Android SDK `apksigner verify --print-certs original-v124.apk` and `aapt dump badging original-v124.apk`. Alternatively an owner-controlled Android Debug Bridge connection can list installed package/version; never use unknown third-party extraction tools or expose private files unnecessarily.
2. Compare installed package ID to `org.bravefrontier.offline`, certificate SHA-256 to v251's JSON value, and require installed versionCode to be **lower** than the candidate artifact's versionCode. A matching displayed versionName is **not** enough; v251 deliberately keeps the historical `174.00.0-demo` label.
3. While the current app still works, explicitly export/back up the real v7/v124 save through the app's supported export feature, move a copy outside the app's private storage, and verify it can be recovered. A CI synthetic-save test is **not** a real device backup.
4. Only then, after the owner opts in, install the **standard** APK over Current and smoke-test launch, Quest/Summon/Units, offline operation and restored progress. Do not uninstall, clear data, or install either diagnostic/fault APK over Current.

If the installed certificate differs or backup cannot be verified, **stop**; do not overwrite Current. In that case review the owner's original APK/signature and alternate update or migration plan separately.

## Acceptance evidence and limits

v251 is a **reporting/test-only** patch. Source-only and exact-head full Android CI must pass before merge. All prior original art, gameplay, save recovery and v250 release-safety checks stay enabled. This attestation verifies **only the newly built standard APK**, not the owner phone or a v124-installed signing certificate. It cannot prove successful device migration or complete original 2022 Brave Frontier Global gameplay (rough full-game progress remains ~30%, provisional).
