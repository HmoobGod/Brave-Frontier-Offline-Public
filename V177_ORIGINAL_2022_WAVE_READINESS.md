# v177 — 142-mission original 2022 wave-readiness matrix

**What this does:** Creates a deterministic **offline research report**, using only the existing SHA-pinned v142 playable quest metadata, v147 Amdahl quest source, and v152 original 2022 opaque reference fixture. It is NOT an Android patch and does not update the game's displayed version.

The report covers **106 playable quests in the current DEMO** and **36 Amdahl source-only missions**. Every mission has a 2022 source wave count, an opaque mission reference, and four explicit false flags for authentic 2022 wave formation, enemy identity, AI, and drops. Actual 2022 per-wave contents are **not established** by the current evidence; **0 original wave formations are marked verified**. Do not interpret `3:10100,1:10101,0:10102` as enemy IDs, and do not turn Amdahl on just because the wave counts are known.

Run from the repository root:

```bash
python prepare_bf_2022_wave_readiness_v177.py
python prepare_bf_2022_wave_readiness_v177.py --output /local/private/mission-readiness.json
```

The output can be compared to the candidate field/path reports from v175 and v176 when the owner-verified `mst-decoded.zip` is available. v177 itself requires no private master file or public upload. CI separately checks all 142 exact identifiers, positive source wave counts, 106/36 separation, selected known source rows, and absence of native mechanics claims or game mutation.

## External research (not imported into the Android project)

A distinct community revival project, [joppe2001/bf-private-server](https://github.com/joppe2001/bf-private-server), documents a *client-side* distinction between authored mission stages, battle group records, and monster records in its [mission schema](https://github.com/joppe2001/bf-private-server/blob/main/server/packet-generator/assets/archive/mission.kdl). It describes its content as community-authored and its [README](https://github.com/joppe2001/bf-private-server/blob/main/README.md) specifies an **online C++ server**, version v2.19.6, and **AGPL-3.0** licensing. Its authored mission records are *not* proof of exact 2022 Global native wave rosters. No source code or battle records from that repository are copied into this project; only links and the distinction between protocol structure and original game data are noted.

**Scope:** no Android or JS asset, battle formation, campaign unlock, EXP, damage, drops, 2022 original data, save v7, signature, or application ID changed. v124 device install remains untouched.

**Next:** Run source-gated v175/v176 scanners against the original, SHA-verified 2022 master. Review any candidate table against the client schema **without conflating invented server-stage definitions with original 2022 data**. Reconstruct a single proven ordered formation with original enemy IDs and battle AI only after a separate Claude review, exact-head CI, and save-safe Android integration.
