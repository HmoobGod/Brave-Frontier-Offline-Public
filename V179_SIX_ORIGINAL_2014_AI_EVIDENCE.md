# v179 — Original 2014 captured AI patterns for six missions, research only

The new v178 historical source records preserve unit identity, stats and the numeric AI identifiers of six archived 2014 Global mission captures. This v179 follow-up preserves the original **action definitions and action-count ranges** *as literal source strings*, rather than pretending those IDs explain their combat behavior.

## Historical evidence (not original 2022 proof)

- Original upstream source: [cheahjs/bravefrontier_data / missions_parsed](https://github.com/cheahjs/bravefrontier_data/tree/master/missions_parsed), individually Git-blob SHA-pinned through the six v178 records.
- Six historical mission captures: 300, 330, 332, 333, 334, 364.
- 56 historical wave lists, **192 ordered AI slot assignments**, **13 distinct observed action-list patterns**.
- In those 192 assigned lists, historical action types appear **330 attack**, **25 turn_end**, and **28 skill** times, including repeats. These are **source rule entries**, NOT battle actions executed, damage counts, probabilities, or results.
- Preserve each source action's type, raw parameters, chance percentage, target wording, conditional expressions and integer target-type code. Also preserve an enemy's literal 2014 `act counts` min/max range.
- **No interpreting the source AI semantics**, choosing targets, triggering abilities, or granting drops in the 2022 demo. AI conditions in the historical parser and their current-game application require separate proof and review.

The report `source_data/bf_global_historical_six_ai_evidence_v179.json` deduplicates 13 literal source AI patterns and maps each to the original ordered six mission/wave/slot arrays. The new `test_bf_historical_six_ai_evidence_v17900.py` checks all 192 slot identities against the original v178 records, the 56 wave count, each raw pattern's action shape, and strict no-activation safeguards.

This is **source-only data**: no Java, JS assets, HTML, Gradle, Android manifest, packaged app data, network, historical practice, gameplay, AI, level progression, gems, v7 save, or debug signing change.

**Claude review is not required for v179 source retention. Claude review IS required before any of these AI patterns control even optional practice battles.** Matching six 2014 and 2022 wave *counts* alone does not validate 2022-native enemy identity, AI conditions, or behavior.
