# Brave Frontier Global v79.00 — Correct Injury ATK Buff Stacking

Parent: v78.00 battle status candidate SHA `c792973830c4436dc18df3f637ed80d2dc24725b`. Promote v78 only if exact CI passes and artifact exists.

Independent archived-era Global mechanics references specify that **Injury reduces ATK by 50% subtractively** and that status ailments participate as -50% stat penalties in the damage stat stack. The 2022 original item master verifies the cure identity #20210 for Injury code 4. Sources:
- <https://bravefrontierglobal.fandom.com/wiki/Status_Infliction>
- <https://bravefrontierglobal.fandom.com/wiki/Damage>

**Existing v62 bug:** the Injury wrapper halved the base `unit.atk` *before* the existing DEMO `effectivePlayerAtk` positive ATK multiplier. With 100 base ATK and a +100% buff, it yielded 100 ATK instead of the subtractive result of **150 ATK** (100% base + 100% buff - 50% Injury). +30% and +50% source potions were similarly wrong.

v79 updates v62's existing action-bound wrapper to calculate `round(baseAtk * (1 + activeAtkBuff/100 - 0.5))`, then temporarily normalizes the input to the existing `effectivePlayerAtk` function so the final effective value matches this subtractive stack. Unbuffed Injury still yields the same rounded 50%-base behavior as before. The original base ATK is exactly restored after a successful/failed/aborted action. This is **actual source-described combat interaction** using the existing DEMO damage engine; original fractional rounding, enemy AI, native full buff cap and simultaneous effect order are still unverified.

New Chromium checks cover +30%, +50%, +100% ATK with Injury, no buff, zero leakage after action failures, cure behavior, expired buff, P and v7 save integrity, complete inherited gameplay tests and signed APK. No original data, source archive, Android signer, package name, permissions, inventory or saved schema modifications.
