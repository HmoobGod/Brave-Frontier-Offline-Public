# v178 — Six additional original 2014 captured enemy-wave sources (research only)

The older optional historical-wave lab (v200) preserves 21 research snapshots in the Android app: 4 v120 plus 17 v200. This **does not** establish original 2022 enemy formations.

A separate community [mission provenance ledger](https://github.com/joppe2001/bf-private-server-data/blob/main/archive/mission_sources.json) identified **six additional 2014 captured missions** absent from our currently stored historical research files. We independently fetched the original 2014 capture snapshots from [cheahjs/bravefrontier_data](https://github.com/cheahjs/bravefrontier_data/tree/master/missions_parsed), pinned each upstream Git blob SHA, and normalized only historical wave number, enemy name, unit ID, historical HP/ATK/DEF and AI identifier:

| Original 2014 captured mission | ID | Historical waves | Historical enemy slots |
|---|---:|---:|---:|
| Scorching Trails | 300 | 8 | 25 |
| The Tarnished Peaks | 330 | 8 | 23 |
| Float Like a Butterfly | 332 | 9 | 29 |
| The Riotous Thunderbird | 333 | 9 | 32 |
| The Raged Beast of Destruction | 334 | 11 | 42 |
| The Fourfold Pillar | 364 | 11 | 41 |
| **Total** | **6** | **56** | **192** |

All six have a wave **count** that matches the owner's SHA-pinned 2022 Global v142 mission record. This is a *cross-era count check only*. Do **not** assume their historical monster lineups, levels, HP, attack stats, AI, treasure, drops, bonus waves or boss scripts equal the original 2022 data. The source's mimic-chest metadata and many other fields are purposely NOT included; the normalized records are not complete native battle simulations.

These six original 2014 captured wave lists are kept isolated under `source_data/historical_2014_v178/`. We do **not** append them to the v200 JavaScript historical lab asset, change its existing totals or update any Android game data. All currently playable original 2022 quests still use the existing explicit DEMO encounter generator. Amdahl remains source-only.

## Verification and next gate

`test_bf_historical_six_2014_captures_v17800.py` checks six Git blob pins, exact record counts and contiguous historical stage order, positive integer combat fields, source 2022 wave-count equality only, strict 2014/2022 provenance wording, and no Android loader activation. Added to the existing full GitHub Actions suite.

The next useful gameplay development is a separately staged **opt-in historical 2014 battle preview**, after confirming 2014 capture identity and game stability. A faithful **2022** formation upgrade still requires independent 2022 MissionStart/per-wave evidence. **Claude independent review is REQUIRED before activating these new enemy waves or AI in any playable engine.**

No change to saves (`bf_global_offline_demo_v7`), progress, Gems, Imps, XP, rewards, user-installed v124, Android signing, or offline permissions. No source ZIP or online server is added to the APK. Merge only after v177 merged-main green, exact-head v178 CI, and a fresh main build.
