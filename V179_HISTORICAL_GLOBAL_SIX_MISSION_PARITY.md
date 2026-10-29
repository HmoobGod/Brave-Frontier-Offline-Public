# v179 — Independent historic Global mission source cross-check

This is a **source-only research gate**, not an Android gameplay patch.

From [BluuArc/bfmt-data historical Global mission records](https://github.com/BluuArc/bfmt-data/tree/master/gl/mission), six mission records preserve BFMT metadata timestamps of **2015-08-13**. Their Git content blobs are pinned independently in `source_data/bf_global_2015_six_mission_metadata_v179.json`; this proves the record bytes we selected, not that the original game server did not change later.

For missions **300, 330, 332, 333, 334, 364**, the six metadata fields that can be compared **all match the owner's original 2022 Global v142 mission master**: prerequisite mission ID, number of battles, Energy use, EXP, Zel and Karma. Thus, **36 of 36 observed per-mission field equalities**, independently across these two archives. The same six IDs also have 2014 capture files in v178 whose **wave counts** match, but whose exact enemy rosters, stats and AI remain **2014-only**.

The following remain explicitly unverified: 2022 Global enemy formations, within-wave monster IDs/positions, original boss AI and drops, native damage algorithms, historical source capture dates for monster lineups, and any cross-era battle behavior. Do not infer such identity from matched quest-level wave counts or economies.

Run `python test_bf_historical_2015_mission_economy_v17900.py` from repository root. This test verifies exact source Git blobs, historical timestamps, source master SHA256, all six metadata fields × six missions, and cross-era separation. It also verifies that the new source fixture is not loaded by Android.

**Release gates:** v178 must first pass both exact-head feature CI and merged-main CI. v179 itself requires a feature exact-head green CI and subsequent merged-main green CI before declaring completion. No changes to app, quest progression, EXP, Zel, Gems, rewards, original AI, v7 save keys, signing or offline manifest. Owner's installed v124 untouched.

**Claude review:** not necessary to merge this read-only source comparison. A Claude source/mechanics review **must** precede any original 2022 enemy formation, AI or drop activation.
