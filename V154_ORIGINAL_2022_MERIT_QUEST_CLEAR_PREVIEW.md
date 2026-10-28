# v154 — 2022 original Merit achievement quest-clear readiness (read-only)

## Source-authentic 2022 Global evidence

Using the owner's `mst-decoded.zip` SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`, authenticated `3-mst-translated/F_ACHIEVEMENT_SUBJECT_MST_1_Ver503.json`, SHA256 `36850eac317faf97f6196d8078b56d8a2594847eb2a727917b0d1bd1485efb56`:

- **11 standard (non-SP) lifetime quest-clear thresholds**, original achievement type `8500`: 10, 100, 1,000, 5,000, 10,000, 20,000, 30,000, 40,000, 50,000, 60,000 and 70,000 total quests. Original source Merit rewards range from 100 to 7,000 (each specific value source-pinned). Canonical complete four-column 11-row SHA256 `9481225a123e6d5060321206082a90d1fe68889854c63793b182927676bc642b`.
- Three *separate* `(SP) 50 Quests Cleared` type-8500 offers are **excluded** from this standard long-term preview; their event conditions cannot safely be inferred from saved DEMO clears.
- Source `35000` type `8600`: **"Creator of the World" Cleared** requires archived mission `365` and yields original 100 Merit Points. Mission 365 exists in the reconstructed 106 playable quest catalog.
- Source `36000` type `8600`: **"Asleep in the Ice" Cleared** references mission 90, 1,000 Merit Points; mission 90 **does not exist** among the 106 playable quests and cannot be presented as clearable yet.
- The source includes 63 type-8600 quest-clear achievements; these two are the low-ID examples. Do not re-label unrelated 2022 quests as native 2022 enemy encounters or resurrect expired events.

## Implementation

A collapsed source reference in Units after the v153 original Legend Stone exchange panel compares archived threshold metadata to **local DEMO** `P.questClears` records and shows whether a saved clear is present for mission 365. It does not assert achievement *claims*, server-side 2022 lifetime totals, eligibility to spend Merit Points, or legitimate native reward triggers. The real original achievements ledger has not been reconstructed. Historical challenges are not granted for free.

Fail closed on missing 106-quest catalog / mission 365, missing v153 original source API, unexpected player version or malformed local clear counts. All UI uses textContent; no HTML injection or external services. A misformatted save yields an "unverifiable" note, not a guess.

## Compatibility

**No actual Merit Points, item grants, purchases, item inventory, battle changes, new playable quests, save schema changes or Android identity changes.** `P.version===7`, `bf_global_offline_demo_v7`, `org.bravefrontier.offline`, persistent signing and offline/no INTERNET remain intact; installed v124 APK untouched.

Automated verification cross-checks all 11 source rows and two story achievements against the existing v138 verified 657-entry SHA-pinned 2022 subset, as well as the current 106-mission source catalog (365 present; 90 absent), and optionally the full archived original 2022 MST by `BF_ORIGINAL_2022_MST_ZIP`. Playwright checks read-only local progress, invalid-counter fail-closed behavior, source/claim separation, duplicate insertion protection, and unchanged `P`, `S`, local save, and write count. APK test verifies byte-identical packaging.

Require **exact feature-head green GitHub Actions** and a fresh **merged-main green build** before promoting this checkpoint.

## True progression blockers

The next major step is reliable source-authenticated one-time **Merit achievement claim status**, legitimate earning/Exchange Hall cost accounting, typed original item inventory for Legend Stone #110100, six 7★ evolution material sources, original 7★ renderer/skill behavior and EXP/type-stat growth. Without these, do not grant currency or enable an arbitrary 7★ evolution shortcut. Issues #75 and #78 remain the tracking sources.
