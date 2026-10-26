# v31.00 — Optional Tactical Target Focus

Baseline: v30.00 battle results, SHA 764b819540587f6429d010d6d5e8fff7dfec242f. Promote only if v30 full workflow passes.

The new in-battle **focus and squad queue** UI proposes a target using one of three criteria computed only from current visible demo enemy stats: lowest remaining HP, highest ATK or lowest DEF. Each button selects its target through the preexisting v21 native targeting UI and queues six active squad commands through its existing input handlers, never spawning attacks or rewards. A fourth action queues Brave Bursts when gauges are ready, otherwise standard attacks. Execute remains manual.

No native 2022 Global attack AI or source enemy formations are claimed. Busy, Auto Battle, ended or invalid-target states are blocked. Queuing can replace older orders, clearly labeled. Does not save or write to the campaign schema.

New browser and Android package regressions plus inherited test suite remain required. Physical Android device QA pending.
