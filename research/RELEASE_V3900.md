# v39.00 — Original Intro to Live Story Battle Handoff

Baseline: v38.00 optional original source dungeon art in the DEMO arena.

The recovered 2022 Global original dungeon dialogue viewer and the offline playable quest battle now have an explicit, source-gated connection. On the final line of the original event for the **currently selected and unlocked dungeon**, a touch-friendly **RETURN TO ACTIVE DEMO BATTLE** button appears. It closes the opt-in full-screen story theater and returns to the existing battle UI, preserving which quest is selected.

The action does **not** execute queued attacks, start an extra battle, grant rewards, skip quests, alter original source dialogue or mutate saved progress. The entry only appears in archive quest mode for the active, nonfinished and nonbusy mission matching the scene's original dungeon. Unsupported events and cleared Village messages remain in the existing reader.

Regression tests verify unlock gating, final-line requirement, source match, no battle turn execution, no save mutation and Android signing/offline safety.
