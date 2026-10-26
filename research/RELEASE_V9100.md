# Brave Frontier Global v91.00 — Original Unit Innate Status Resistance

**Verified parent:** v90.00 Build #331, commit `1377e60e26342c32b3a360775f76ba96d6101aeb`, 152 workflow steps successful, signed debug APK artifact `12596405690`.

## Source and decoding evidence
The 2022 Global Grand Archive `mst-decoded.zip`, SHA-256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`, contains exactly 2,291 distinct unit rows in:
- `3-mst-translated/F_UNIT_MST_1_Ver1084.json`, SHA-256 `1146f09489a07b9187cd3f04bf7dc3ef3bb74e35385869534671af95bf8ea645`
- `3-mst-translated/F_UNIT_MST_2_Ver1084.json`, SHA-256 `0696ccda59fccf48598c5267eaeb8a306e994618384151cead38cec6a9195b2b`

`unitInnateStatusResist` has 2,259 `0:0:0:0:0:0` rows, 28 `100:100:100:100:100:100` rows and exactly 2 `0:0:0:0:0:100` rows (unit IDs `810212` and `820212`). Two malformed rows (`820518`, `830328`) contain a blank fifth element and are conservatively **excluded**, not silently normalized. The six ailment codes align with existing v57 status identities: Poison, Weakness, Sickness, Injury, Curse, Paralysis (see https://bravefrontierglobal.fandom.com/wiki/Status_Counter).

## Gameplay change
Unlike prior crystal ledger/read-only research, **the real current DEMO ailment engine now refuses to inflict any status on source-verified 100%-immune owned units**. Original 100% paralysis immunity is applied to IDs `810212` and `820212`; the 28 exact all-100 identities are immune to all six tracked ailments. All-zero, malformed, unsupported, absent module, training, KO, and invalid-code paths preserve existing behavior.

This gate applies to **new** infliction attempts only and never retroactively purges already-existing ailments, changes enemy behavior, or invents original skill proc rates/turn duration. The master tables contain no usable nonzero partial innate resistance rates beyond these 100% values. There are no random rolls and no new save fields.

It is not an original mission encounter/AI implementation. The previously simulated enemy encounters and status-related duration/damage remain as before.

## Backwards compatibility and release gates
- Existing v57 `inflict` API and v58–v80 status mechanics remain unchanged except a one-line optional fail-open source immunity guard.
- No writes to `P`, `localStorage`, quest progress, HP, BB, inventory or original unit master.
- `P.version=7`; save key `bf_global_offline_demo_v7`; package `org.bravefrontier.offline`; original development signing keystore; no INTERNET permission.
- Source module loads after v57 only. The full GitHub Actions browser suite adds explicit before/after source immunity tests, ordinary-unit compatibility, malformed exclusions, training/KO and signed Android APK contents tests. Promote only if the exact commit passes with signed APK uploaded. No physical Android verification claimed.

**Next:** reconstruct 2022 battle encounters and native enemy AI when original mission-to-wave mapping becomes available; independently verify crystal collection/recipient distributions before enabling BC/HC charging and healing.
