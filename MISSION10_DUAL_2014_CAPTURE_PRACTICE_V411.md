# Mission #10 — Two Captured 2014 Variants (v411)

Playability-first **historical-practice-only** source patch, not original 2022 battle reconstruction.

## Source comparison
Independently retrieved from cheahjs/bravefrontier_data/missions_parsed:
- Start of Adventure_2014-14-10-08-07.json: Git blob 556829bc0639e417ecd4dbc99ef28c44da25c621
- Start of Adventure_2014-14-10-08-34.json: Git blob c6a9d86b7e72a079ebdaa48b84864d078e5568e3 (donor's provenance-selected capture)

Both have five waves / eleven enemies; the complete parsed records for waves 1, 2, 3, and 5 are identical. Wave 4 differs in all three slots:
- Original: Squirty 20030 (780 HP, 330 ATK, 20 DEF); Gloomy 60030 (760, 370, 0); Sparky 40030 (760, 370, 0).
- Alternative: Burny 10030 (800 HP, 320 ATK, 50 DEF); Glowy 50030 (850, 340, 60); Mossy 30030 (830, 340, 90).

Both captured wave-four variants have one normal attack with 100% action weight, random target selection and unchanged item-drop tables. Unit-drop identities and enemy stats are different. These are 2014 captured observations, NOT original 2022 wave identities, AI or drops.

The donor generator infers positions and monster-text IDs, maps/simplifies AI/skills, and derives quest reward scalars from an MST. The donor's 56.7MB generated archive/mission.json was not extracted, so generated-record parity is UNVERIFIED.

## Playability-only changes
Optional capture selector appears for Mission #10 within the already-existing offline historical practice arena. Primary 08:07 default remains unchanged. The 08:34 alternative changes wave 4 only. Existing synthetic player training attacks, Burst, Guard, Heal Kit and synthetic damage remain; wave 4 uses simulated enemy replies instead of applying the 08:07 source-action adapter. No in-game drops, experience, Zel, quest clear, energy spend, save writes or canonical battle side effects.

The dedicated source CI checks capture identity, delta fields, historical labeling, no network/save bridge calls and prepares/validates the JS. The already-registered Chromium test_bf_historical_wave_lab_v200.py now tests selection, both variants, complete alternate five-wave practice and equality of player/session/v7 save before/after. Signed Android CI must pass on this exact head. Independent Claude exact-head review, latest-main compatibility, merge and owner APK release gates remain separate.
