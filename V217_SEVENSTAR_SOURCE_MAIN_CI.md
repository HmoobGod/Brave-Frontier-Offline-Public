# v217 — Complete six-element 7★ integrity coverage and merged-main research CI

**Scope: read-only Python regression improvements. No APK gameplay, evolution unlock, source-data modification, server, real inventory, Gem/Imp, Java, HTML, signing or saved-game change.**

This independent follow-up to Claude's v216 review covers three outstanding research quality issues:

1. **Six-element 7★ completeness, independently exercised:** Duplicate source-authenticated Fire 7★ `50016` over Dark 7★ `60016` in **both synthetic** copies of the v130 and v127 source manifests, recompute the changed v130 typed-row SHA, and override the expected typed-row checksum *within the test only*. This intentionally disables other identity defenses so only the full six-element 7★ list check can reject the missing Dark 7★. The 8★ analogue from v216 is repeated with an exact expected error.
2. **Precise failure reasons:** Instead of accepting any `ValueError`, v217 asserts the exact source-integrity rejection for coordinated edits, incomplete 7★/8★ sets, malformed original source manifests and invalid nested Python-only values. The audit now normalizes non-JSON-serializable in-memory fixture input to `ValueError` and rejects empty original material-slot lists explicitly. The production manifests remain unchanged.
3. **CI checkout and merged-main guarantee:** The `sevenstar-source-preflight` GitHub Actions workflow now runs on every push to `main` in addition to relevant PRs and manual dispatch. Checkout uses the pull request's exact head SHA on PR events, or `github.sha` for a push, so a synthetic test run does not silently substitute GitHub's PR merge ref.

The new `test_bf_sevenstar_complete_elements_v21700.py` uses only copied original-source fixtures. A synthetically supplied resource balance can never authorize an actual evolution; `original2022EvolutionAuthorized`, `changesPlayability` and `readsOrWritesPlayerSaves` remain hard-coded false. The full v215/v216 tests continue to run unchanged.

## Evidence and unlock boundaries

The original owner's `mst-decoded.zip` archive and 2022 original Global source tables were authenticated in older research, not rehashed by this PR. The public v127/v130 source manifests only support the pinned typed recipes and original item identity, not authentic original EXP/level semantics, actual inventory storage/grants, sprite transform implementation, full original burst/skills or v7 save upgrade migration. Existing playable units remain at 72 and 7★/8★ remain unplayable.

## Merge gates

Get Claude independent exact-head review, green exact-head source and Android CI, SHA-guarded merge, post-merge Android **and newly enabled sevenstar source CI** on the actual main merge commit. Owner Android/save acceptance remains separate for any later real gameplay change. If build CI is pending, leave this PR unmerged.
