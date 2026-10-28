# v148 — Six original 2022 Global 7★ starter source normal-attack combat proofs

This extends v147 Water #20016's throwaway **no-save test-only** battle proof to all six original 2022 Global elemental 7★ starter forms: **10016, 20016, 30016, 40016, 50016, 60016**. They remain non-playable in the production game.

Recovered from the owner's SHA256-verified original 2022 F_UNIT_MST source archives (v125) and original CGG/CGS attack sequences (v128), with all six 7★ provenance records protected by v127. Exact base levels, unit costs and evolution items remain reference-only; original 7★ max level 120, unit cost 38, EXP pattern ID 10, original material type2 Legend Stone item #110100 and 1.5M Zel prerequisites have not been enforced in gameplay. These six have original normal attack hit counts **10 Fire, 9 Water, 8 Earth, 1 Thunder, 8 Light, 7 Dark** (43 source damage-hit events total). Original source normal-hit event weights per form must sum to 100.

The new Chromium CI test checks all six source normal-hit records in the live v125 compressed original archive and all six original source attack CGS timeline entries via the v128 compressed CGG/CGS. For each unit, it creates a disposable **in-memory unit record only within a headless test browser**, executes one normal attack against a high-HP dummy through the preexisting DEMO battle engine, and immediately un-registers the actor. Source hit events/weights and 7★ source base stats are used. **No 7★ unit is made playable, no saved roster or evolution state changes, and no original damage formula or native targeting is asserted.** This is intentionally a contract test for future real 7★ readiness.

The test verifies production still has exactly **72 playable forms**, original source seven-star IDs are missing from production roster before and after, `P.version===7`, existing `P`, `bf_global_offline_demo_v7` localStorage and Android package/signing remain untouched.

The 2022 native combat damage, BB/SBB/UBB status, source CGG pixel blending, 7★ growth, original typed inventory consumption, pickups and enemy AI remain unverified. Next actual playable milestone requires those independently proven systems before adding permanent evolution or saved units.

v148 branch stacks on v147 Water ephemeral combat test PR #63 and consolidated v146 PNG PR #61, themselves stacked on v145/v142/v143. Promote only after exact prior feature and fresh merged-main CI success, then exact v148 feature CI and fresh main verification. Owner installed v124 until requested v150.
