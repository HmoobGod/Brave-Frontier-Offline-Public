# v203 — Actual authenticated 2022 master ZIP scan, source-only

**Result: SOURCE VERIFIED; NATIVE ENCOUNTER FORMATIONS STILL BLOCKED.**
On 30 October 2026, the owner-accessible `mst-decoded.zip` under their
Brave Frontier/Original Assets Drive folder was copied into a temporary
private working directory. The archive SHA-256 was independently verified as
`69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`.
The contained original 2022
`3-mst-translated/F_MISSION_MST_1_Ver1118.json` SHA-256 verified as
`d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83`.

## What actually ran

A **separate local read-only scan** applied v175-equivalent exact
full-string top-level matching and v176-equivalent bounded nested matching,
over `3-mst-translated/F_*.json` tables in the locally SHA-authenticated
2022 archive. It did not execute the v175/v176 *repository CLI scripts*
byte-for-byte. That distinction matters for auditability.

The mission filter selected 34 Mistral rows (source area 100, excluding
mission 90), 36 Morgan (200), 36 St. Lamia (300) and 36 source-only Amdahl
(400): 142 distinct mission IDs and 29 distinct opaque encounter reference
strings. The observed reuse frequency 6×4, 20×5 and 3×6 exactly matches
the previously merged v199 reference-collision profile.

**Results:** 147 translated source tables inspected (the primary mission
master is the reference source), zero skipped tables. Three top-level
`MISSION_8f4NYKxb` matching columns were observed outside the primary
mission table:

| Exact 2022 table | Distinct source missions whose opaque refs match | Matching table rows |
| --- | ---: | ---: |
| `F_RAID_POINT_MST_Ver57.json` | 99 | 110 |
| `F_GRAND_MISSION_SPOT_MST_Ver92.json` | 92 | 72 |
| `F_MISSION_MST_2_Ver1118.json` | 67 | 66 |

There were **zero nested exact-string candidate paths** under the bounded
nested scan. This is a negative result **for the exact-reference search in
the scanned 2022 tables**, not a general proof that encounter mappings or
enemy information do not exist elsewhere. The second mission table match
does **not** imply the same battle lineup or enemy AI.

An independently inspected
`F_RAID_BATTLE_GROUP_MST_Ver52.json` has 11,121 original 2022 rows and
the field names `battleGroupId`, `raidRouteId`, `AI_CHANCE` and
`raidAiId`. That provides a native **raid-specific master schema**,
not an authenticated join from a 2022 story mission to enemy waves.
Do not substitute its group IDs for the unrecovered `MissionStart` data.

The public `source_data/bf_v203_authenticated_2022_local_scan_summary.json`
contains **only the checksums, aggregate counts, table names and all-false
native encounter readiness flags**. The 59 MB source ZIP, mission records,
source rows, any save data and packet captures are **not** uploaded to GitHub.

## CI and reproducibility boundary

The new standard-library test
`test_bf_authenticated_2022_local_scan_v20300.py` crosschecks the
aggregate's stable source identity and 142-mission/29-ref collision profile
against the merged v199 source audit and runs ten adversarial
false-promotion/mutation probes. Public CI cannot re-open the original
private ZIP and **is not evidence that public runners scanned the original
archive**.

For local source reproduction use the repo's existing independently pinned
`audit_bf_original_2022_wave_sources_v17500.py` and
`audit_bf_original_2022_nested_sources_v17600.py` against the same
SHA-verified archive. Compare their aggregate reports to v203 findings;
their exact output is a follow-up reproducibility check, not claimed
completed here.

## Next actual gameplay evidence

The original enemy formations, monster group contents, skills, AI and drops
remain **unrecovered** from this 2022 client/master ZIP.
Network-side `MissionStart` battle responses with authentic 2022
provenance (or comprehensive original fight recordings) are needed.
Never infer wave rosters from repeated `8f4NYKxb` strings, a raid
group ID or a community-authored 2014/2026 replacement.

No runtime patches, save schema changes, signed APK source, Java/JS
combat, Quest, Imp, Gem, Gradle or signing changes were made in v203.
Claude review is required before changing playable encounter, AI, drop
or save behavior, followed by exact-head successful full Android CI,
SHA-guarded merge and owner device smoke testing.
