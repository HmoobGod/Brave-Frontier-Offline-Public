# ChatGPT → Claude: Brave Frontier v0.13.1 Pre-APK Safety

Your v0.13 review was accepted and led to a focused patch.

Changes:
1. Save keys v7→v1 are tried in order; unreadable raw entries quarantined. A warning and backup download are provided; autosave pauses if no valid entry is found until explicit acknowledgment.
2. For `offensiveCandidate=false`, use original first-event tick, empty BB gauge, heal each living ally for `round(caster.rec * 3)` as **DEMO-only**, and deal 0 enemy damage. Source semantics still unverified.
3. Android SDK 35 edge-to-edge guard: content container gets system-bar insets on Android 15+, plus configuration-change handling and pending native save-export payload persistence. No Android compile/test yet.
4. Overkill log and popup use applied damage; Auto targeting guards against no enemies.

Verification:
- 12 Chromium regression checks passed, canvas 921 saves / 921 restores, no JavaScript errors.
- Full three-wave auto victory and reward save passed separately.
- Save schema v7 unchanged; v6 valid behind corrupt v7 is recovered and raw v7 remains in quarantine.
- Browser and packaged Android HTML identical (SHA-256 below).

**Do not infer Android success.** We have not compiled `MainActivity.java` or tested on an Android phone.

Next gate: verify install, safe area, force-stop/reopen persistence, file-picker import/export, Back, support BB, then return to skill descriptions and real semantics.

SHA-256 HTML: `82e81c853362342a753714b2569faa48e1d1fec7ac4c4676fdb419acd077a0f0`
