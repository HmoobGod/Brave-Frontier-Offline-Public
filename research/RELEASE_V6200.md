# Brave Frontier Global v62.00 — Injury ATK Debuff

**Prerequisite:** exact successful v61.00 APK and status-token fix. The 2022 original translated item master verifies that source item #20210 clears ailment codes **2–4** (Weakness, Sickness, Injury). Community [Global Status Infliction](https://bravefrontierglobal.fandom.com/wiki/Status_Infliction) reports Injury as **-50% ATK subtractively**, lasting three turns on player units. The original executable's stat stacking and rounding remain unverified.

v62 integrates status code **4** into the existing DEMO `performUnit` attack path, temporarily reducing the afflicted unit's current `atk` with `round(atk * .5)` during its action, restoring the exact prior `atk` in a `finally` after animation or failure. This changes the attack/BB effect by reading the existing `effectivePlayerAtk` path. It is a documented consequence layered onto a simulated combat model, **not** authentic native damage math. Infliction probabilities and original enemy skill data remain unknown and are not invented.

Duration is three **observed enemy phases**, with per-code generation tokens from v61 so repeat inflictions receive new lifetimes. Expiration removes only code **4**, preserving coexisting Weakness (2) and Sickness (3), while item #20210 still correctly cures all 2–4. All changes are battle-local: no `P`, localStorage, saved units or original item inventory writes; no package ID, signing, manifest or source-art changes.

Regression gates: in-action reduced ATK and exact restoration after normal and thrown callback; one-ally only, buff interaction, selective cure and three-turn expiry, stable re-infliction, mode/new battle behavior, full inherited Chromium and APK tests. Exact-green GitHub Actions artifact required before promotion.
