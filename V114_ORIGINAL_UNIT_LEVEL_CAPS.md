# v114 — Original 2022 Global Unit Maximum Level Caps

Continues v113 source-verified 72-form elemental leader recipient gameplay, on a separate original maximum-level cap patch.

## Exact archive evidence
- User-owned `mst-decoded.zip` SHA-256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`.
- Extracted **unitMaxLevel** from original 2022 `F_UNIT_MST_1/2_Ver1084.json`, restricted to exactly the 72 playable forms already source-matched in v112.
- For each elemental family: first-series units #11–#15 are **12/40/60/80/100** (Fire/Water/Earth/Thunder) or **30/40/60/80/100** (Light/Dark); second-series #21–#25 are **30/40/60/80/100**; alternate #41–#42 are **30/40**.
- All 72 original maximum levels are explicitly stored in `source_data/bf_global_2022_playable_level_caps_v114.json` with master SHA256 provenance.

## Live integration, scoped
- When **a new archive DEMO battle starts**, clamp each source-identified unit's calculated DEMO level to its original 2022 max, before applying existing v111 original leader ATK/HP bonuses.
- When already within its native level cap, behavior is byte-for-byte identical to v112. On training battles, nothing is changed.
- The existing battle stat formulas use DEMO per-level increases (+30 HP / +12 ATK / +8 DEF / +6 REC); after the level clamp they are recalculated using those existing formulas. **These increments are not verified original unit leveling formulas.**
- No stored EXP is reduced, lost, reinterpreted or rewritten. Existing v7 saved progress, squad membership, evolution chains, EXP rewards, materials, item drops, Energy, summon rolls and enemy AI are unchanged. **This is not full native EXP/stat growth restoration.**
- v111 optional pre-leader hook is inactive when v114 module is absent, preserving previously verified v111 behavior.
- The raw source profile remains the historical provenance; unknown units/form IDs and malformed runtime states fail closed without mutation. This applies only to already owned valid party units during their freshly created battle state.

## Tests
New Chromium suite checks all 72 level caps, per-element 12 versus 30 exception, live capped battle levels, original leader bonus order and no double application, later evolution form caps, training isolation, repeated resets, non-mutating v7 saves, and UI idempotence. Signed APK gate checks exact new JS asset byte hash, prepared HTML byte hash, Android ID/signing, offline permission, and loader order.

## Remaining original mechanics
The game still uses DEMO EXP-to-level thresholds, interim stat growth, type-specific variance and damage calculation; original crystals are not distributed to units, and enemy waves/AI are not authentic. Future restoration must separately source the original 2022 leveling formula/type logic and validate it without harming existing saves.
