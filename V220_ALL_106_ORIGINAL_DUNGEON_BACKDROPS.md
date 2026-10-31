# v220 — Authentic original 2022 dungeon backdrops for all 106 playable quests

**Status: CANDIDATE DRAFT requiring independent Claude exact-head review and CI.** This patch expands the already existing **opt-in, default-OFF** v38/v191 visual-only feature. It does not change enemy waves, combat AI, skills, loot, inventory, Gems, Imps, saves, unlocking or native client animation.

## Exact original source

- Owner's archived `mst-decoded.zip` SHA-256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`, verified against its Drive file on 2026-10-30.
- Source original `3-mst-translated/F_DUNGEON_MST_Ver1002.json` SHA-256 `16f090514d65846f6bd4a9998b50d6c810bc806a79858c0ff766cdb1a22536fc`; exact join to the original 2022 live mission master and the existing v142 106-playable source fixture, cross-checked with the immutable v152 142-mission reference fixture.
- Owner's BF1 original dungeon art pack SHA-256 `a748f675fd8271c0f41bb0b9244c83ffc5d23b4051cfd757494d16735c506644`; all 22 matching original JPG files independently checked by exact SHA-256 and byte length. Their mission cross-join canonical digest `efdaf2c44abacb2d939d42a24631af8b16fd175b78e3c27f298f872dba5fe4ce`.
- The preexisting v191 feature covers 29 Mistral missions using 7 byte-original JPGs. Fifteen additional original JPGs extend the art option to the remaining 77: five more Mistral missions, 36 Morgan, and 36 St. Lamia. The exact final coverage is **34 Mistral + 36 Morgan + 36 St. Lamia = 106/106**, across **23 dungeon IDs** and **22 unique original JPEGs**.

## Implementation and non-goals

- Source `source_data/bf_global_2022_dungeon_art_v220.json`: exact 2022 dungeon-ID-to-original-JPG source lookup and full byte-provenance metadata, separately pinned to the source master and art pack.
- `source_assets/bf1/dungeon/BF1_Global_2022_15_Dungeon_Backdrops_v220.zip`: 15 exact JPG source bytes + unchanged source manifest, package ZIP SHA-256 `c6ff4f67493839c6af1cc86cce19384899d56c9fa25762edeb96d06f3306a7e9`. No private save, raw original masters or player information.
- Build-time preparation independently compares each ZIP entry against its source hash, rejects any unexpected paths or overwrite of unlike asset files, stages 15 JPEGs offline into the APK, and generates a separate fail-closed v220 adapter for the newly covered 77 missions. It preserves the existing v191 29-quest source adapter.
- The v38 background panel remains OPTIONAL and OFF by default; the old v191 lookup runs first, then v220 fallback. No combat or save write. The v220 source module checks the authentic v174 encounter reference lookup and explicitly refuses to interpret the opaque 2022 reference as waves, AI or drops.
- New Chromium and real packaged-APK regressions must prove 106 original source joins, 22 JPEG byte identity, the old 29 v191 mappings unchanged, default OFF, training battle exclusion, and unchanged `P`, `S`, canonical v7 save and app identity.

**Hard boundary:** Background filename/bytes are original; *enemy formation, AI, drops, encounter animation and combat mechanics remain DEMO or unverified*. The visual option MUST NOT imply full native 2022 quest parity. Original 7★/8★ evolution is still unavailable, and source-only tests are not physical Android device acceptance.

## Merge and promotion gates

Obtain a separate independent Claude review at the final v220 PR head, successful exact-head Android CI including Chromium and packaged binary assertions, verify v219 merged-main Build #1152 SUCCESS at its exact SHA, then SHA-guard merge. Verify full Android and source CI if triggered on the actual merge SHA, and preserve the owner's Current APK/save until explicit Android acceptance. Do not merge an unreviewed or failing head.
