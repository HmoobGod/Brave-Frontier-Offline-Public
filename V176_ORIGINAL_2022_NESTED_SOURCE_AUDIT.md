# v176 — Read-only nested 2022 encounter-reference audit

This adds a **research-only** extension to v175. It examines nested dictionaries and arrays in original `3-mst-translated/F_*.json` tables for **exact full-string reuse** of the 142 pinned `MISSION_8f4NYKxb` values. Numeric coincidences, string substrings, and unrelated synthetic references are not joins.

## Provenance, output and limits

- Production CLI first verifies the **full SHA256** of the owner's original 2022 `mst-decoded.zip` using chunked reads. The v175 gate then validates the mission-master SHA256 and all 142 source-pinned encounter strings. No unverified archive is accepted through the CLI.
- Output is only table names, JSON-pointer-style paths, distinct mission counts, number of matching top-level rows, and explicit **false** native-formation, enemy-ID, AI, and drop decoding flags. If the same text occurs multiple times within one top-level row at one path, that row is counted once.
- Scan depth is capped at 8, visits at 2,000,000 per table, and JSON table size at 80 MB. An exhausted limit **skips the whole table rather than silently reporting partial findings**. Each skipped table and reason is recorded, so a zero-match report does not establish absence of original formations.
- Optional local output: `python audit_bf_original_2022_nested_sources_v17600.py --archive "/local/private/mst-decoded.zip" --output "/local/private/nested-audit.json"`.
- Public CI tests *synthetic* deep references, duplicates within arrays, ambiguous mission IDs sharing a reference string, malformed tables, bounds, path escaping, SHA refusal, and absence of output on rejection. This **does not constitute running the scanner on the genuine original ZIP**.

This does not change any Android files, build-time game assets, playable quests, levels, combat, saves, Gem/Imp states, package/signing, or network permission. Installed v124 and canonical `bf_global_offline_demo_v7` remain untouched. Distributable APK version stays v174.

**Next gate:** obtain an authentic local result from the owner-verified 2022 ZIP; independently review a candidate's schema, source wave ordering, enemy IDs, AI and drops before any gameplay promotion. **Claude review is required for such a gameplay change, but not for this source-only bounded audit.** Require exact feature-head and post-merge main GitHub Actions success.
