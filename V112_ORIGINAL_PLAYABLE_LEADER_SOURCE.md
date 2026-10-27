# v112 — Source-Verified 2022 Leader Skill Records for All 72 Playable Global Forms

Parent: v111 original source-qualified starter leader ATK/HP mechanics on newly built archive DEMO parties.

Original 2022 archive source: **mst-decoded.zip** SHA-256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`. Recovered unit records in F_UNIT_MST_1/2_Ver1084.json join to F_LEADER_SKILL_MST_Ver749.json on exact leader skill IDs. Do not replace master data with other regional versions.

- **72 original playable forms; 36 leader skill IDs.** The new source-data JSON preserves all unit IDs, rarity, element, `lsId`, `skillTypeId` string and raw `passiveSkillInfo`.
- **30** first-starter forms: single original type `2`, source-gated original +25%/+50% ATK and 6★ +10% max HP (existing v111).
- **25** second-starter single type `31` records: the historical Global reference calls Passive ID31 Spark Boost, but native 2022 parameter positions and proc timing are not reconstructed here.
- **12** alternate forms with single type `5`: historical Global reference associates Passive ID5 with elemental mitigation, but damage resistance ordering and stacking are not verified here.
- **5** compound second-starter six-star forms use exact `31@34`, `31@48`, `31@49`, `31@32` and `31@29` original strings. Preserve both `@` effect groups; never guess missing secondary mechanics.
- New optional in-app research panel lists every original leader skill and marks unimplemented raw types **RAW ONLY**; this v112 addition cannot modify party stats, summons, loot, save data or progression.

Browser regression tests check all 42 non-type2 original rows against the GitHub-stored source manifest, join the other 30 v110 starter records, validate 72/36 counts and passive strings, reject unknown forms, and confirm no v7 save mutation. APK tests check identity, Java loader order, exact JS source bytes, and no Internet permission.

Original spark/mitigation active combat is a future source implementation contingent on independent verification of hit/damage timing and parameters. Complete original damage, enemy AI, drop pickup and battle unit typing remain unverified. Android on-device acceptance remains separate from GitHub CI.
