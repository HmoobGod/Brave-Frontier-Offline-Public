# v204 — Verified 2022 raw mission mimic configurations (research only)

**Gameplay unchanged.** The original 2022 Global `mst-decoded.zip` was
read locally from the owner's connected Drive, with archive SHA-256
`69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`
and mission master SHA-256
`d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83`.

The SHA-verified `F_MISSION_MST_1_Ver1118.json` contains a
`missionMimicInfo` string for each of the 142 selected original
Mistral/Morgan/St Lamia/Amdahl missions. This field is different from
the opaque `MISSION_8f4NYKxb` battle-reference string and was **not**
previously decoded into native enemy waves or mimic encounters.

## What the original 2022 source actually says

The source has exactly **seven distinct raw strings** in the 142
missions. The table below gives unmodified **opaque configuration text**,
not percentages or inferred monster IDs.

| Raw 2022 string | Mistral | Morgan | St Lamia | Amdahl | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| `0,0,0:0,0:0` | 21 | 0 | 0 | 0 | 21 |
| `1,10,0:1000,0:0` | 0 | 1 | 0 | 0 | 1 |
| `1,10,100:1000,0:0` | 13 | 19 | 0 | 6 | 38 |
| `1,10,50:1000,5:1100` | 0 | 0 | 0 | 1 | 1 |
| `1,10,50:1000,50:1100` | 0 | 0 | 0 | 29 | 29 |
| `1,10,60:1000,40:1100` | 0 | 0 | 16 | 0 | 16 |
| `1,10,70:1000,30:1100` | 0 | 16 | 20 | 0 | 36 |
| **Total** | **34** | **36** | **36** | **36** | **142** |

The two single-occurrence raw profiles are preserved *as authored*
without automatic correction, normalization, or probability interpretation.
Tokens `1000`/`1100` may look like IDs and numeric prefixes may look
like weights, but the exact client/server grammar, encounter timing,
monster group join, rolls, drops, save behavior and 2022 AI have
**not** been authenticated. The data alone cannot justify implementing
mimics or interpreting those fields as odds.

## Reproducibility and privacy

`audit_bf_original_2022_mimic_profiles_v20400.py` is a new pure
Python local scanner. It checks the **full source ZIP SHA-256**, the
original mission master SHA-256, the already pinned v152 142-mission
identity/reference fixture and exact raw string grammar, and it rejects
missing/duplicate/malformed rows. Usage:

```bash
python audit_bf_original_2022_mimic_profiles_v20400.py --archive /private/mst-decoded.zip
```

Optional `--output /private/mimic-profile-summary.json` writes only the
aggregates listed in the table. No original ZIP, underlying source
mission rows, account information, saved game, or packet response is
published. `source_data/bf_v204_2022_mimic_opaque_profiles.json` holds
only these stable aggregate observations and explicit false readiness flags.

Public CI tests synthetic malformed input and the source-aggregate
self-consistency. **It cannot rerun the owner's private original ZIP**.
The optional local production scanner may be rerun on the exact source
archive; a passing public synthetic test is not equivalent to an
authenticated original runtime encounter test.

## Promotion gate

Original mimic spawning is **BLOCKED** until original behavior
(including exact chance/rate meanings, action trigger, correct enemy
identity and composition, HP/ATK/DEF, skill AI and reward/drop outcome)
is independently validated. Historical walkthroughs or third-party
server code can inform research, but are not themselves proof of
2022 original behavior. Ask Claude to independently review *any*
eventual gameplay/save change before merging.

No Android app, assets, save schema, signing, Quest rewards, personal
offline Gems, original Gem logic, Imp caps or battle engine were changed.
