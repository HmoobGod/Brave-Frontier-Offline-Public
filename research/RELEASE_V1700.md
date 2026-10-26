# Brave Frontier Global v17.00 — Squad Evolution Batch for the Optional Archive Draft

Based on verified v16.00 Build #199 / SHA ba966997d6fb1c3a515a04eb38fd35f13d31ef7d.

The existing v14.00 source evolution material planner now feeds a new **batch apply and undo** feature in the optional six-unit archive draft. The user can choose one recorded 2022 source evolution recipe per temporary form (or auto-fill missing available recipes), inspect original total Zel/Karma, distinct material IDs and grouped quantities, and advance the valid selections in one batch. A temporary source form keeps its party slot; forms without chosen recipes remain unchanged. All targets must be draft-eligible original catalog forms, with no duplicates or blocked source paths.

The batch prevalidates all 2022 source recipes, conflicting destinations and the current six-slot draft before changing anything. The existing v16.00 per-form temporary evolution and its undo history are reused. Each batch is undone in reverse order only when every recorded evolution remains eligible to reverse; no unrelated user moves are undone. The batch is blocked while a synthetic trial exists. Battle-test newly evolved temporary forms in the existing optional historic 2014 encounter sandbox.

**Not native evolution**: original source requirements are only a reference, no check or spending of real player materials/currencies, and no change to real party, roster, summons, quest progression, actual battle or v7 save. Experimental battle mechanics and 2014 enemy sources remain explicitly separate from original 2022 Global systems.

Release only after Playwright dynamic two-unit exact-recipe tests, batch UI, invalid/collision guards, trial lockout, unchanged save, full inherited suite and signed offline Android APK checks.
