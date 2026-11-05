# Offline CI artifact verification

`tools/verify_ci_apk.py` independently checks downloaded standard APK and v251
identity artifact ZIPs without installing or updating an app. Supply trusted
GitHub artifact SHA-256 ZIP digests, current PR head, actual checked-out build
commit, build run number and the previously accepted signer certificate digest.
Do not obtain expected values from the unverified identity receipt itself.

Example (replace every placeholder with verified evidence):

```
python3 tools/verify_ci_apk.py \
  --apk-zip standard.zip --identity-zip identity.zip \
  --apk-zip-sha256 APK_ARTIFACT_DIGEST --identity-zip-sha256 IDENTITY_ARTIFACT_DIGEST \
  --head PR_HEAD --checkout TESTED_CHECKOUT --run BUILD_RUN_NUMBER \
  --certificate TRUSTED_CERTIFICATE_SHA256 --build-tools /path/to/android/build-tools/35.0.0
```

The CLI authenticates both ZIP byte digests, requires one matching payload per
archive, checks v2 PR provenance and every package/version/hash/size/signer field,
then invokes Android SDK `apksigner verify` on a temporary APK and independently
reads package/version/permissions with `aapt`. It rejects the diagnostic package,
Internet permission, unexpected signer, stale source or checkout, unsigned or
invalid signature, mismatched artifact bytes and ambiguous payloads. ZIP payloads
are read directly without extracting archive paths; size is limited to 64 MiB.
There is no network request, signing operation, key access, APK installation,
owner profile mount, or real-save input. Temporary APK bytes are cleaned up.

This tool verifies PR builds only. It cannot establish that the supplied build
commit actually belongs to the supplied tree/head: independently verify the
GitHub commit parents/tree and run metadata before invoking it. GitHub artifact
digests prove byte identity against that supplied evidence, not publisher trust.
Real-device behavior, installed app signer/version, and save compatibility remain
separate acceptance gates. Offline standard package/version expectations match
the current repository v251 identity schema and intentionally fail on changes.

Tests use clearly synthetic payloads: one positive receipt plus rejection of all
15 mismatched fields, payload tamper, wrong source head and wrong trusted
certificate, ZIP digest mismatch and multiple payloads. They do not assert a
synthetic payload is a signed Android APK. The real SDK cryptographic acceptance
path requires actual downloaded artifacts and Android tools; no real signed APK
acceptance is claimed from these unit tests. Run `python3 test_ci_apk_verifier.py`.

This standalone source/test tool is based on merged main and has no dependency
on unmerged UI or capture-audit PRs. Keep draft until review and actual CI pass;
merges remain manual under the current owner policy. Preserve existing APKs,
signing identity, saves, custom Gems and Imp settings. No release is created.
