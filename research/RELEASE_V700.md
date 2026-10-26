# Brave Frontier Global v7.00.0-demo — Original Normal-Hit Timeline

Baseline: v6.00 Build #174, commit 59568d4d79e5b1b5d6b1e82e4f4c4beb1cdb4266.

The original 2022 Global F_UNIT_MST source contains **72** recovered normal-attack damage-frame rows. Exactly **71** sum to 100% source weights and are usable for reference; original form 10023 sums to 130%, deliberately rejected without normalizing weights. The new BFOriginalHitSequenceV700 reference exposes source frame/weight pairs with copy-out behavior.

The optional tactical practice now records each normal attack using recovered frame/weight events for supported unit forms. It divides the already synthetic damage total across source weights using cumulative integer rounding, preserving the total and presenting a per-round multi-hit display. It does not assert that 60 ticks/second is original, and does not change underlying native combat rules.

Round undo restores hit telemetry. v6.00 original BB levels, historical source disclaimers and real v7 save remain preserved. All prior tests and Android packaging must pass.
