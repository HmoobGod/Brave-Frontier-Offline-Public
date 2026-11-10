# v341 — All 106 story missions: Continue must respect committed victory

**Base:** `main` `493f40feb216f6898835d24dd9e6b97d2e454c64` (#332).
**Integration:** Separate from pending #340, touching no #340 changed paths.
**Scope:** Existing 106-mission `bf101_story_continue.js` read-only progression gate and its two already-registered Chromium/APK regression suites.

## Player-facing defect

The result screen and story battle HUD already fail closed when a victorious mission appears in memory but its canonical `bf_global_offline_demo_v7` quest-clear count is missing, stale, corrupt, or unreadable. The global **Continue Story** shortcut had only the native `saveEnabled` and `saveRecoveryPending` booleans. A successful-looking or stale adapter could leave those true with a different canonical v7 record and incorrectly enable the next original story mission.

## Gameplay correction

When an archived battle has ended in victory, the Continue Story shortcut now reads the *already existing*, read-only `BFGlobalBattleResultsV3000.committedClearCount(missionId)` at action/refresh time and compares it with the current positive, safe-integer clear count of the exact victorious mission. If the result API is present but incomplete, throws, or differs from the in-memory clear, the shortcut refuses the next mission and shows the existing unsaved-victory recovery message. After an actual canonical v7 save succeeds and the counts match, normal next-mission routing resumes.

The results extension loads after v101 in the real Android WebView. The lookup is therefore intentionally deferred. An isolated historic embed with no v3000 results module keeps the prior save gate, but an **invalid present provider does not bypass** the gate. The 106 archived mission order, all 23 dungeon unlocks, DEMO combat, enemy/NPC AI, v7 save schema, rewards, Energy, UI navigation, Android identity and original 2022 source data are unchanged.

## Regression

- `test_bf_story_continue_v101.py` adds Chromium checks for stale count, nonfinite count, thrown provider, missing function, exact valid receipt and legacy-absent results module, including preservation of selected mission and stored v7 bytes.
- `test_bf_packaged_story_continue_v101.py` checks the gate exists in the actual APK asset and retains the original v7 save key and Android packaging.
- Both are already registered in `.github/workflows/build-debug-apk.yml`. Full signed exact-head Android/Chromium/packaged native emulator CI must pass before merge.

**Gate:** Keep this source-only PR draft pending green exact-head CI, independent source review and reconciliation after #340. Do not merge #340 without its own separate independent approval; do not alter or reset the owner's installed APK or existing v7 save.
