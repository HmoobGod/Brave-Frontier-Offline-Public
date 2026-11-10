# V334 — Source-verified Auto Repeat rejects invalid live wave counts

## Defect in merged #332
The optional Auto Repeat module reads the original 2022 source wave count and checks it against `QUEST.battles`, but its previous check of `S.totalWaves` was conditional: `Number.isSafeInteger(S.totalWaves) && mismatch`. If `S.totalWaves` was malformed, absent, `NaN`, fractional, infinite or string-coerced, that comparison was skipped, and unattended replay could start using an unverified live DEMO wave layout.

## Gameplay correction
When the source campaign is present, require `S.totalWaves` to be an exact positive safe integer equal to the authenticated recorded 2022 wave count. Native `reset()` always initializes this field from `modeWaves()`. This applies before any Auto Repeat replay and on every active repeat poll. Invalid data blocks the start or disarms the existing repeat, without queuing an extra battle.

Older isolated pages without any source campaign retain the preexisting fallback; the production Android page has the source campaign. **This checks wave counts only**, not original 2022 foe compositions, drops, native enemy AI or combat math.

## Verification
The full browser regression now rejects nine distinct corrupt live wave values while preserving native Auto, player P, canonical v7 stored bytes and replay count; unchanged valid count still starts. The packaged APK regression checks that the stricter validation ships in the Android bundle, preserving signing, manifest and offline identity. Full exact-head signed Android + Chromium + save tests required before merging.

No change to rewards, Auto strategy, enemy/NPC AI, owner save format, APK signing or installed owner APK.
