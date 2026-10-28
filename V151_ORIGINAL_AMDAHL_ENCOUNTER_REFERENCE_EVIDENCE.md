# v151 — Original 2022 Amdahl encounter-reference evidence, 142-mission ledger

**Scope:** Extend the previously verified **106 original 2022 Global** Mistral / Morgan / St. Lamia mission reference records with the **36 original 2022 Amdahl source-only records** from v147. This yields 142 documented source missions, **not 142 playable quests**. Production remains at **106 playable quests**.

## Original archive evidence

Source: original owner's 2022 Global mission master F_MISSION_MST_1_Ver1118.json (SHA256 d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83), in mst-decoded.zip (SHA256 69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9).

v147 pins original 36 Amdahl mission IDs 400–404, 410–414, 420–424, 430–434, 440–444, 450–454 and 460–465; exact mission prerequisites, battle counts, English names and opaque MISSION_8f4NYKxb reference strings. Original quest canonical SHA256: f35a7b06bc9e6fae6facc1fd77422f74c04798da4fb87f64a2737a0483a572c3.

These 36 missions have seven dungeon-specific raw reference patterns and 14 distinct opaque numeric values. Their colon-prefixes and identifiers have **no proven native enemy, wave placement, probability, formation, AI or loot meaning**. They must not be interpreted as monster/unit IDs. Source missionBattleCount verifies number of waves, **not wave composition**.

## Implementation

The new bf15100_amdahl_encounter_evidence.js extends the existing v108/v109 evidence inspector in Quest. It adds the original 36 source-only Amdahl records, displaying 142 source records, while leaving the 106 live quest catalog untouched. It fails closed unless the expected v7 state, original 106-quest catalog, v109 source provenance and authenticated v149 read-only Amdahl map are all present. No gameplay mutation, currency rewards, roster entries, source guessing or save writes.

The inspector displays original 2022 Amdahl mission names, known wave counts and raw reference strings and explicitly says that native enemy formations, AI and loot are not decoded.

## Verification

- Assert every one of 36 embedded rows equals the SHA-pinned v147 source manifest.
- Verify seven source reference patterns, 14 distinct opaque numeric IDs and 106+36=142 inspector entries.
- Chromium verifies original source lookups, fail-closed v7 gating, repeated script injection without duplicate options, no mutation of P, S or localStorage.
- APK check verifies byte-exact packaged v151 JavaScript, package org.bravefrontier.offline, preserved debug-signing config and no INTERNET permission.
- Require successful exact-head feature CI plus independent fresh successful merged-main CI before promoting the checkpoint.

## Next original-playable development

Identify an authenticated 2022 primary-source mapping for mission group references to enemy formations and native wave order; verify enemy AI and drops before gameplay unlock. Historical 2014 Archive Trials content is not proof of 2022 Global mechanics. Independently validate legitimate Legend Stone acquisition, typed inventory and 7-star growth before any permanent 7-star evolution.

The owner's installed Android APK remains v124; no new device install is requested.
