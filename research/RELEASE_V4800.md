# Brave Frontier Global v48.00 — Prevent Auto Battle from bypassing DEMO item action reservations

Baseline: v47 source-backed full-HP revive on the newest **verified successful** APK commit. This is a bounded gameplay **correctness** fix; it does not claim to reproduce 2022 native auto AI or item timing.

The optional v42–v47 battle-item prototypes apply effects immediately but use an actor's Guard as simulated action cost, protected by v45 shared item-turn reservations. Native Auto Battle can otherwise be toggled on after an item use, enqueue Attack/BB for every living unit (including those with reserved item turns), and execute through a programmatic path that bypasses the Execute-button Guard capture. That creates a free-item-then-Auto-Attack loophole.

v48 inserts an early DOM Auto `change` capture listener. It reads the existing v45 in-memory ledger. If a story/archive battle has pending item reservations, enabling Auto is blocked and the checkbox stays off, with a clear battle log reason. Turning Auto off always works; switching Auto on when no item turns are pending remains unchanged. Training, unrelated controls, enemy logic and auto-planner internals remain untouched. Reservations release automatically on the next round or new battle, so Auto can be enabled then.

The source-backed v43 party heal scope (#20100), v44 +30% ATK (#20400), v46 BB gauge maximum (#21000), v47 full-HP revive (#52400), and synthetic v42 Potion are not reinterpreted. No source asset, original item metadata, package identity, development certificate, v7 saves or player progress are modified.

Verification: comprehensive existing browser and APK regression suites plus a new live-browser test that uses an item, clears its action, attempts Auto, confirms Auto remains off and item Guard protection intact; then starts a clean battle and checks Auto is permitted. No physical-device acceptance is inferred from CI.
