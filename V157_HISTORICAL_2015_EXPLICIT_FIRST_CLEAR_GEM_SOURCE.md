# v157 — Independent historical Global first-clear Gem confirmation

## 2015 Global data, separate from the owner's 2022 original

Pinned historical repository: [BluuArc/bfmt-data](https://github.com/BluuArc/bfmt-data/tree/032f064db79c406fe4f027eb527085d09ea9b8af/gl/mission), commit `032f064db79c406fe4f027eb527085d09ea9b8af`, `gl/mission/{missionId}.json` (source `bfmtMetadata.updatedAt=2015-08-13T15:42:33.000Z`).

All **29** dungeon-final mission IDs identified independently in the owner's 2022 Global archive were fetched individually from the **historical 2015 Global** mission records. **29/29 have exactly `clear_bonus:[{"gem":"1"}]`.** Eight selected pre-finale/non-final negative controls (missions 1, 11, 20, 203, 300, 364, 400, 403) have `clear_bonus:[]`.

Each of these **37 independently retrieved files** is pinned by its actual Git blob SHA-1 in `source_data/bf_global_2015_explicit_first_clear_gem_crosscheck_v157.json`. Canonical complete 29-positive record tuples `[missionId,historicalGitBlobSha1,"gem",1]` SHA256 `057df7d457aadfd9cf466113934e99db161979e2613403ab7afa9a707a1b8352`. These are facts/metadata rather than copied gameplay source code.

Owner's original **2022** MST SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9` already verifies exact reward payload `8:0:1:0:0` for the **same 29** dungeon-final missions; v156 proves all 29 original 2022 source quests are final quests with direct preceding mission prerequisites (22 currently playable, seven Amdahl not playable). The cross-snapshot evidence makes a one-Gem original **dungeon-completion first-clear bonus** much more strongly supported.

**Limitations:** 2015 is not 2022 and proves neither original 2022 claim delivery, old-account Gem reimbursement, replay protection, current Gem currency capacity, nor an authentic save transaction. It does not authorize turning on rewards prematurely. A complete versioned save schema + one-time ledger + backup/restore regression remains a strict prerequisite (Issue #80).

## Implementation and reproducibility

This source-only checkpoint adds the 37-file exact-blob provenance manifest, offline automated cross-check against v155 and v156 source ledgers, and optional full-file verification with `BF_HISTORICAL_2015_MISSION_DIR=/path/to/gl/mission`. The optional check validates every Git blob's SHA-1 (including the `blob <size>\0` header), each `clear_bonus` and exact IDs. The entire public dataset is NOT copied to this repository.

No JavaScript assets, Java/Android, quest logic, save parser, rewards, source gems, original waves, roster or Android package/signing are altered. Current `P.version===7`, `bf_global_offline_demo_v7`, 106 playable quests, 72 playable unit forms, and installed v124 remain untouched.

Require exact feature-head CI SUCCESS, verify v156 merged-main CI SUCCESS before merging, and a fresh merged-main CI SUCCESS after merging.
