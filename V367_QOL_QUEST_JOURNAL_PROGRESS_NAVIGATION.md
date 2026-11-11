# v367 — Quest Journal: next mission, sorting, progress

## Actual user-facing improvements (one coherent QoL batch)

1. **Next available story mission**: a 44px-tall explicit navigation control opens the first original story-order mission which is unlocked but has zero clears, independent of journal search, region filters or sort. This merely navigates to existing mission selection through the old `BFQuestAreas.choose(q)` and region tab handlers; it does **not** launch/complete a quest, spend Energy, award anything or save.
2. **Source-stat sorting**: leave default original chronological order intact, or sort only visible matching rows by archived original Energy cost (ascending), archived original EXP (descending), or *actual local* clear count (descending), with stable mission-ID tie breakers. Energy and EXP are strictly **2022 archived reference values**, not an assertion that the DEMO enforces Energy or awards those original amounts.
3. **Region completion status**: count unique original missions with one or more canonical in-memory clears out of all 106, and provide corresponding Mistral/Morgan/St. Lamia totals. Counts are read only, recalculated on existing list mutations, navigation refresh and filter changes. No new save key, progression mutation, misleading 2022 enemy formation claim.

## Code scope

Change only `app/src/main/assets/bf110_quest_journal.js` and its existing registered Chromium and packaged regression tests. No changes to base HTML, Java, manifest, Gradle, signing, original source archive, enemy/NPC partner AI, wave hooks, evolution patch (#362), precombat guard (#363), Save Retry story HUD (#364), or source capture research (#366). The patch uses the existing journal insertion point and public `BFGlobalQuestJournalV110` API.

## Safety / CI

- Existing `questUnlocked(q)` and `S.busy` gates apply to the new one-tap navigation, just as to journal OPEN.
- Sorting uses a fresh `archive.filter` array, leaving canonical QUESTS and original order unchanged. All inserted UI text uses DOM `textContent`; no untrusted HTML injection.
- No `localStorage`, `saveProgress`, `P` mutation or retroactive quest clears added.
- Chromium regression checks story vs archived-source sort, progress count, first genuinely available uncleared mission after earlier clears, S.busy gate, navigation and P/storage isolation.
- Packaged APK regression checks the actual JS and unchanged v7 package.
- This is **not** original-native combat development. Authentic 2022 enemy formation certification remains **0/106**.

New independent Claude exact-head source approval and full signed Android/Chromium/packaged/emulator CI are required before merge, with fresh merged-main CI and separate owner Android device acceptance before releasing a new APK. No owner-installed APK or canonical `bf_global_offline_demo_v7` save touched by authoring this draft.
