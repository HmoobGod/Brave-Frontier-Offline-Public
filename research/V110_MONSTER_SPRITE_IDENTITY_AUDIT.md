# v110 research checkpoint — monster identity vs sprite fidelity

Base: verified v109 main commit `119f307389200e9ae055c83cf5e65c04d62be9d1` (Build #155 PASS).

## Existing source evidence

| Source | Evidence | What it **does not** establish |
| --- | --- | --- |
| `source_data/bf_global_historical_encounters_v120.json` | 2014 mission wave order, named enemies, unit IDs, HP/ATK/DEF and AI identifiers | 2022 enemy placement, native 2022 AI/drops, image linkage |
| `source_data/bf_global_monster_training_v053.json` | 2022 archived `monster_anime_####.png` images, `monster_cgg_####.csv` layouts and original frame coordinates | Native enemy unit IDs, original frame timings, combat stats or AI |
| `source_data/bf_global_st_lamia_raw_encounter_refs_v109.json` | 2022 St. Lamia `MISSION_8f4NYKxb` opaque group tokens | Which unit spawns in each group, wave or encounter weights |
| `source_data/bf_global_mistral_boss_intel_v052.json` | Historically documented boss identity, selected HP and archived Juggernaut 0001 sprite | Full native encounter formation, AI or drops |
| DecompFrontier `client/src/AIMst.hpp` | Named AI ID and priority fields | Executable AI decision tree or mission-to-unit join |

## Safe next integration

1. Recover a direct **2022** monster-master unit-ID to monster-graphics-ID join, with exact archive file, record keys and reproducible checksum.
2. Cross-check only exact IDs against archived PNG+CGG assets. An identical name, visual resemblance or 2014 ID is insufficient.
3. Keep unsupported links and opaque mission group tokens explicitly unresolved; never infer wave formation from `3:30100`-style tokens.
4. Once verified, render confirmed sprites in a read-only research preview first; introduce them into real battles only with source-backed formation and combat metadata.
5. Keep app ID `org.bravefrontier.offline`, original debug signing and v7 save schema unchanged.

## Scope and status

This checkpoint is **documentation/research only**, not a gameplay implementation. It does not edit the Android app, add enemies, change damage, alter saved progress, or award rewards. A verified mapping requires additional original source evidence. No Android APK needs installing for this research branch.
