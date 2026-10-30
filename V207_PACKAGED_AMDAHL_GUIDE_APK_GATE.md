# v207 — Compiled Amdahl Story Guide APK integrity gate

**Scope: regression-only. No WebView runtime, gameplay, save, Gradle,
manifest, Android signing, unit data or source quest changes.**

Claude's v206 review requested an additional post-build check that the
read-only 36-quest Amdahl guide is really packaged into the signed Android
APK and referenced in the compiled Java. v206's original English text, 2022
mission SHA digests, and fail-closed source API are unchanged.

`test_bf_packaged_amdahl_story_guide_v20700.py` is executed **after**
`gradle assembleDebug` by the standard full Android GitHub Actions
workflow. It examines `app/build/outputs/apk/debug/app-debug.apk` directly:

- Exact byte equality of the four original Amdahl/encounter source modules
  in the APK to the prepared asset files; reject missing or corrupt files.
- Exact 64-character original 2022 mission master and Amdahl quest fixture
  SHA values in the packaged guide's shared source constants; original 36
  source-only missions and 106 live quest fixture remain unchanged.
- DEX binary string pool contains the Amdahl guide asset name **exactly
  once**, alongside the `evaluateJavascript` symbol in the same compiled
  DEX file; all three dependency module names also remain present.
- The Android Java source still loads `v149 -> v151 -> v206 -> v174`
  in order, with one `readPackagedText` reference to each.
- APK's bundled `index.html` equals staged bytes; canonical v7 save key
  and single save-writer anchor remain intact.
- Existing Android application ID and no INTERNET manifest permission.

This gate catches a missing APK asset, stale packaging, omitted compiled
script reference, checksum drift, and accidental injection-order drift.
It **cannot prove** that a real Android WebView executes the guide, that
`onPageFinished` double-injection is safe in actual lifecycle conditions,
that a phone saves/loads correctly, or that original enemy waves have been
recovered. Those release gates remain open.

The v206 gameplay PR #136 was independently reviewed by Claude and merged
on successful exact-head Build #1043. This v207 change is *test-only*.
Verify v207 on its own exact-head Android CI before merging.
