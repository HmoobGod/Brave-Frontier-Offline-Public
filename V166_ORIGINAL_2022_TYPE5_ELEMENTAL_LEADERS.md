# v166 — Source-gated 2022 Global type-5 elemental resistance leaders

## Source evidence
The owner's SHA-pinned 2022 Global `F_UNIT_MST` / `F_LEADER_SKILL_MST` join in `source_data/bf_global_2022_playable_leader_catalog_v112.json` maps twelve already-playable alternate forms (#10041/42 through #60041/42) to six **skillType 5** leader skills. Their exact archived raw passives are `1,10` through `6,10`. Independent original English Global records in `source_data/bf_global_2022_playable_leader_english_v114.json` explicitly state **“10% reduction in damage from [element] Types”** for leader IDs 500, 502, 504, 506, 508, and 510.

## Safe live scope
In **archive DEMO** fights only, when the first owned squad member is one of those twelve exact forms, an incoming enemy hit with a known matching elemental label is reduced by 10% **after** the existing DEMO elemental matchup and guard calculation. Only the built-in enemy-hit damage path is wrapped; no changes to offensive damage, unit stats, native skill claim state, rewards, the opponent's AI, or any save field. Training battles, unknown enemy elements, invalid/unowned leaders, other leader types, non-party targets, and already-ended battles remain unchanged.

The 10% amount and elemental association are original-source facts; this is a **source-gated overlay on the existing DEMO formula**. Native 2022 rounding, exact leader-skill stacking order, enemy formations/AI, server-side entitlement rules and precise original timing are not recovered. No original 2022 enemy elements are inferred from 2014 waves or opaque mission tokens.

## Regression and merge gate
An idempotent fail-closed build patch wraps exactly one established v69 incoming damage expression and retains the original `prototypeDamage` and elemental scaling operations. Playwright joins all 12 unit/leader/passive records to original Global English descriptions and verifies 10% matching-element protection, nonmatching/unknown/invalid target safety, original code path guards, training exclusion, nonmatching leader exclusion, no storage writes and no duplicate module insertion. The packaged Android APK test confirms the patched hit path, packaged source module and canonical v7 save behavior. CI checks JS syntax.

**Do not merge until v165 merged-main Build #572 succeeds and the v166 exact feature-head CI succeeds.** Guard merge using expected head SHA, then require a new green merged-main Android build. Do not request owner installation or update their installed v124 APK.
