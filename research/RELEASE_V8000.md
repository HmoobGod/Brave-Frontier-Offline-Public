# Brave Frontier Global v80.00 — Correct Weakness DEF Buff Stacking

Parent candidate: v79.00 `4c00e728fcad1e3f5d1bfb312b6743c649ed2711`. The v79 Injury ATK additive fix is preserved. Exact success and signed APK must be checked before promoting either revision.

The archived 2022 item master verifies source items **#20600 +30% DEF**, **#50600 +50% party DEF**, and **#50601 +100% DEF**, each with a three-turn effect. Independent Global-era sources specify **Weakness applies -50% DEF subtractively**, not a multiplicative halving of the already-buffed DEF:
- <https://bravefrontierglobal.fandom.com/wiki/Status_Infliction>
- <https://bravefrontierglobal.fandom.com/wiki/Damage>

**Existing v61 bug:** after a +100% DEF item, Weakness halved 200% DEF to 100%, whereas the documented subtractive stack is **150% base DEF**. The same error affected +30% (should yield 80% base) and +50% (should yield 100% base).

v80 corrects the existing v61 Weakness wrapper without introducing a new battle framework. It consults the existing battle-local item modules' live `activeBuffs` (including independently recorded `baseDef`) and recomputes **base DEF × (1 + sourced DEF bonus − 0.5)** for each affected living ally. The altered value exists only within the awaited enemy phase; a `finally` restores the exact pre-phase buffed DEF, including on throws. Unknown DEF modifications still use the previous -50% fallback; no unverified stacking is invented. Buff expiry and ailment expiry remain independently owned by the original modules.

Browser regressions check all 3 source buff percentages with concurrent Weakness, selective cure, precise restoration, expired-buff fallback, mode/reset isolation, untouched P and local save v7, and all inherited suites. Signed APK includes the correction while retaining `org.bravefrontier.offline`, the development signer, offline manifest, source data/art and original save compatibility. Not promoted until CI green.
