# v196 — Original 2022 / historical 2021 Mistral mimic-token crosscheck

**RESEARCH ONLY. No enemy waves, formations, AI, loot, battle parameters, user saves or APK game assets are changed.**

## Verified input sources

**Owner's original 2022 Global source:** existing committed
`source_data/bf_global_mistral_raw_mission_evidence_v056.json`,
extracted from `mst-decoded.zip` SHA-256
`69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`.
The raw `F_MISSION_MST_1_Ver1118.json` file SHA-256 is
`d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83`.
It provides **34** precise early Mistral mission IDs, original 2022
`rawMimicInfo` and *opaque* `rawEncounterRef` strings.

**Historical, independently extracted 2021 Global source:** public
`cheahjs/bravefrontier_data/missions.json`, pinned to
commit `7be4ee5ade8023580c83563fb306eb4e2b747256`
from **2021-11-17**, file Git blob SHA-1
`750871aa060478cc674e7d3e02c739f26364ef8e`:
https://github.com/cheahjs/bravefrontier_data/blob/7be4ee5ade8023580c83563fb306eb4e2b747256/missions.json

The historical full 3,146-ID JSON file was read as source, then a **small
34-row subset** was retained in
`source_data/bf_global_2021_mistral_mimic_history_v196.json`.
Every retained row preserves the historical original-name/dungeon,
battle-count and `mimic_info` object. Those **2021** battle counts and
labels are **not** validated as 2022 values, and are not imported into gameplay.

## Literal comparison results

All **34** original 2022 Mistral mission IDs also occur in the pinned
2021 historical record.

| 2022 source `rawMimicInfo` | Matching historical 2021 evidence | Missions |
|---|---|---:|
| `0,0,0:0,0:0` | `mimic_info: {}` | 21 |
| `1,10,100:1000,0:0` | 2021 extracted `group_1_chance="100"`, `group_1_monster_group="1000"`, group 2 chance/group both zero; historical guessed range `10.0~34.0` | 13 |

The **13** non-empty cases are original IDs
**60–63, 70–73, and 81–85**. This is a *cross-era numeric-token*
consistency check. It **does not prove** that `100` means the original
2022 spawn probability or that `1000` is a verified native enemy-group
identity. The historical field `spawn_chance_range_maybe` is explicitly
an extractor's guess. The 2022 `1,10` prefix is not decoded.

The 2022 `MISSION_8f4NYKxb` encounter strings (e.g.
`3:10400,2:10701,1:10702,0:10703`) are preserved byte-for-byte and
**never interpreted as enemy formations, spawn IDs or battle counts**.

## Implementation scope

- `source_data/bf_global_2021_mistral_mimic_history_v196.json`:
  34 historical records, pinned 2021 Git blob and true 2022 source hashes.
- `audit_bf_mistral_mimic_cross_era_v19600.py`:
  source/year and SHA gates, exact repository Git-blob fixture hashes, 34-ID joins, 21/13 token-class parity,
  fail-closed unknown raw strings; produces optional research-only JSON
  outside the repository.
- `test_bf_mistral_mimic_cross_era_v19600.py`:
  exact IDs/candidate groups, ten negative source/provenance/byte-drift probes,
  deterministic report, prevents source mutations and confirms the v7
  canonical save key remains in the unmodified game.
- Repository fixture Git-blob anchors detect changes to the 34-row source inputs; they do not independently authenticate the upstream 2022 archive or the 2021 history beyond the source provenance stated above.
- One workflow test registration. No modification of app assets, Gradle,
  `MainActivity`, source game config, saved EXP, Gems, Imps, quests, or
  current 106 DEMO mission battle logic.

## Remaining source gates

1. Recover an authenticated **2022** group-definition master, combat packet,
   or client-side parser that connects original mission raw encounter tokens
   to enemy wave compositions and identifiers.
2. Confirm original 2022 mimic spawn probability rules, group identities
   and battle timing independently; the **2021 extracted fields are not
   version-parity proof**.
3. Validate native enemy stats, targeting, AI/skills, drops, element and
   reward semantics against 2022 records, including Amdahl.
4. Keep original/DEMO modes isolated and retain v7 save compatibility.
   Require independent Claude review before any native combat change,
   exact-head GitHub CI, and owner Android testing.

**Bottom line:** A useful literal cross-era match has been recovered; no
new original 2022 enemy wave, AI, drop or spawn is authenticated or playable.
