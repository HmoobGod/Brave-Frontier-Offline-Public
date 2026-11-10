# v339 — Source-qualified final-wave Smart Auto checks the live battle wave count

Base: signed `main` `493f40feb216f6898835d24dd9e6b97d2e454c64` (#332). Independent of pending gameplay/save/CI integration #338: no shared changed paths.

## Actual player-side gameplay defect

In optional **Advanced Smart Auto → Save offensive BB until final recorded quest wave**, the existing source-backed path validated `QUEST.battles` and the authenticated 2022 `waveReadiness()` count but did not check `S.totalWaves`, the current native DEMO battle's real wave count. If the source said 3 waves while the active battle only had 2 (or the live total was missing, coercible, fractional, infinite, or otherwise corrupt), the player Auto planner could withhold a ready offensive Brave Burst until a nonexistent third wave.

## Change

When `BFGrandGaiaCampaignV100` is present and authentic source wave readiness is used, suppress an offensive BB in an earlier wave **only** if `S.totalWaves` is a positive safe integer equal to the independently verified original 2022 wave count. Missing or mismatched live total returns the existing action (`previous`) without attempting conservation. Normal Smart Auto, opt-out, manual actions, enemy/NPC/partner AI, healing and support bursts are unchanged. Isolated older pages with no campaign API retain their legacy final-wave behavior.

## Coverage

- Existing Chromium test `test_bf_qol_advanced_smart_auto_v10500.py` now checks valid 3-wave suppression, 10 malformed/mismatched live wave totals (all preserve the ready offensive burst), unavailable/mismatching/throwing source evidence, and legacy no-campaign behavior; verifies no player/v7-save mutations.
- Existing `test_bf_packaged_qol_advanced_smart_auto_v10500.py` checks the exact guard is present in APK asset.
- Source edits never write `P`, `S`, save keys or original battle mechanics.

## Promotion

Keep **draft** until exact-head complete signed Android, Chromium, packaged and v7 save tests, source review and main reconciliation. Separate native CI #338 must be merged via its own gate before reconciling this change. No original enemy formations, drops or AI authenticity is implied; this is a player-side DEMO strategy safety correction.
