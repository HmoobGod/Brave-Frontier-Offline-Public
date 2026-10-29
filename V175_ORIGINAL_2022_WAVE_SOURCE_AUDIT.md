# v175 — Reproducible original 2022 enemy-wave source candidate audit

**Purpose:** isolate a real research blocker, not imply source-to-wave decoding has happened.

## Established 2022 source facts

The original owner-supplied Global `mst-decoded.zip` SHA256 is `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`. The original `F_MISSION_MST_1_Ver1118.json` SHA256 is `d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83`.

The previous v152 fixture reproduces **142 exact 2022 mission raw encounter-reference strings**, including 106 playable missions and 36 Amdahl source-only missions. The existing cross-reference audit found exact opaque text reuse in 92 Grand Mission Spot rows' mission set, 99 Raid Point mission matches, and 73 shared. This **does not mean any of those two tables contains wave formations**.

Live `modeWaves()` already uses `QUEST.battles` for original archive missions; the 106 live wave *counts* and scalar rewards match the source. Current `buildEncounter(wave)` generates explicitly DEMO enemy identities/stat lines. Do not modify that generator based on opaque `MISSION_8f4NYKxb` numeric pairs.

## New v175 research tool

`audit_bf_original_2022_wave_sources_v17500.py` performs a local-only, reproducible full-master scan:

1. **Requires an exact full-ZIP SHA256 match** to the original owner source before inspecting any data on its normal CLI.
2. Validates the original mission-master SHA and all **142** exact raw mission references against the prior SHA-pinned v152 fixture. Rejects mismatching/duplicate IDs.
3. Examines only `3-mst-translated/F_*.json` tables, checking for **byte-for-byte-equivalent opaque reference strings** in top-level string fields. Neither numeric ID coincidences nor substrings qualify.
4. Reports table names, field names, *counts* of distinct matched missions and matching table rows, along with explicit `nativeFormationDecoded:false`, `nativeEnemyIdsDecoded:false`, `nativeAIDecoded:false`, and `nativeDropsDecoded:false` flags. It never emits underlying private source rows.
5. Skips oversized or malformed ancillary tables, does not extract ZIP entries or touch the Android game, and optionally writes a user-directed local JSON report. **No Google Drive, GitHub, or network upload of the original ZIP** occurs.

Example usage on a computer holding the owner's private original master:

```bash
python audit_bf_original_2022_wave_sources_v17500.py --archive "/private/path/mst-decoded.zip" --output "/private/path/wave-source-audit.json"
```

The private source ZIP **is not included** in this public repository or the CI runner. CI uses a synthetic archive with intentionally ambiguous reference reuse to test exact-match counting, duplication, bad/missing mission references, oversized primary table and full-source SHA refusal. A passing synthetic CI test **does not constitute execution on the original owner ZIP**.

## Scope, safety and next step

No Android asset, `app/build.gradle`, Java, save key, unit stats, battle engine, rewards, quest access or signing changes. Research checkpoint `v175` does **not** bump the distributable APK's v174 label. Canonical save `bf_global_offline_demo_v7` and P.version 7 stay intact.

After obtaining a report **from the verified original 2022 source**, review any candidate original mission group table joins independently. A matching token is evidence for future research only. Validate native wave order, enemy spawn IDs, enemy level/stats, enemy AI, and loot separately before implementing any gameplay changes.

**CLAUDE REVIEW REQUIRED** before promoting any inferred native 2022 wave/AI/drops into the playable engine. **Not required** for this read-only source-scanner and synthetic negative tests. The installed owner's v124 APK/save remain untouched.
