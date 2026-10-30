# v199 — Authenticated 2022 opaque encounter-reference collision audit

**Research-only. Not a new 2022 battle formation or a gameplay update.**

## Evidence and findings

v152 already verified **142 original 2022 mission-reference strings**
against the owner's SHA-pinned original master archive:
`mst-decoded.zip` SHA-256
`69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`.
The original mission-master digest is
`d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83`.
This audit reuses **only the already-committed and byte-pinned excerpts** from
v056 Mistral, v080 Morgan, v109 St Lamia, v147 Amdahl, and the compressed v152
cross-table evidence. It does not need to reaccess or upload the private ZIP.

Findings from those 142 missions:

| Area | Mission records | Distinct opaque strings |
|---|---:|---:|
| Mistral | 34 | 8 |
| Morgan | 36 | 7 |
| St Lamia | 36 | 7 |
| Amdahl (not playable) | 36 | 7 |
| **Total** | **142** | **29** |

- **Every one of the 142 missions shares its entire raw encounter-reference
  string with other missions.** There are zero single-use references.
- Of the 29 distinct strings, **6** occur in **4** missions, **20** occur in
  **5** missions, and **3** occur in **6** missions.
- None of the 29 full reference strings is shared *across* these four areas.
- Counting only literal comma-separated terms within each opaque string:
  **31** mission rows have one term, **84** have two, and **27** have at least
  three. These are **textual token counts, not wave or enemy counts**.

## Why this matters

A mission ID cannot be mapped one-to-one to an authentic 2022 formation merely
by taking its `MISSION_8f4NYKxb` string. The string is demonstrably reused
by multiple missions. Even within one area, reference reuse does **not** prove
that the missions' actual enemy waves are identical: it may be a higher-level
join key, and the 2022 parser/group definitions remain missing.

The v199 audit deliberately does not infer enemy IDs, encounter positions,
wave order, encounter weights, boss skills, AI, drops or mimic probabilities.
The v177 wave-readiness report still marks native formations unverified.

## Changes and gates

- `audit_bf_original_2022_reference_collisions_v19900.py` checks all four
  committed fixture Git-blob hashes, checks the exact v152 compressed and
  decompressed SHA-256 fingerprints, compares all 142 mission IDs and literal
  reference strings, then emits aggregate research counts only.
- `test_bf_original_2022_reference_collisions_v19900.py` asserts the 29
  distinct strings, 6/20/3 reuse histogram, zero cross-area reuse, nine
  corrupt-input probes, repeatable optional report and blocked repo overwrites.
- Register one read-only test in the Android GitHub Actions workflow.
- No `app/src`, Android manifest, APK game asset, combat, Java, unit XP,
  `P.version=7`, original Gems, personal Gems, Imps, player saves, or signing
  changes. No original enemy data has been promoted into gameplay.

**Next:** The missing prerequisite remains an authenticated 2022 enemy-group
definition or original client decoder linking the opaque reference to actual
ordered enemy records, and independent 2022 evidence for AI, stats and drops.
Do not import guessed 2014/2021 encounters as if they were 2022 original.
Any future runtime change needs independent Claude review, exact-head CI,
merged-main CI and owner Android validation. This read-only audit is
self-contained and cannot close any native 2022 enemy formation gate.
