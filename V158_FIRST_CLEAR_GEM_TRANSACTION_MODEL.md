# v158 — Save-safe first-clear Gem transaction model (research-only)

## Verified evidence and why activation is blocked

- Owner-2022 Global mission-master source confirms `missionRewards=8:0:1:0:0` exactly on 29 final-dungeon missions, 22 currently playable and seven Amdahl source-only (v155/v156), with separate 2015 historical Global `clear_bonus:[{"gem":"1"}]` for 29/29 and eight negative controls (v157).
- Current production `P.version=7`, `bf_global_offline_demo_v7` parser and `P.questClears` include **no persistently parsed Gem wallet or claim ledger**. Simply adding a live payout would be unsafe, so v158 introduces **no runtime code, Android modifications or player save writes**.
- There is still **no 2022-original proof** of per-account historic Gem balances, exact first-clear delivery, replay/claim transaction boundaries, Gem spending semantics or retroactive old-player reimbursement policy.

## What this checkpoint adds

The pure, independently executable `test_bf_gem_first_clear_transaction_model_v15800.py` models a prospective *atomic* migration and award transaction. It is **not shipped in APK**. Inputs are authenticated v156/v157 source manifests, from which exactly 22 playable eligible finale IDs and seven unplayable Amdahl IDs are derived.

The model tests deterministic replay exclusion; no Amdahl or non-final awards; ability to crash before commit and retry exactly once; no second payout after persisted commit; legacy v7 saves with previously-cleared finales conservatively excluded from retroactive awards; corrupt version/negative/boolean counters rejected; and 10,000 deterministic randomized quest-clear simulations. Source model and actual owner Android save are never modified. `999999` is only a **model safety bound**; NOT a verified 2022 native wallet cap. The candidate legacy-quarantine policy is **not a final gameplay decision**: adopting or reimbursing pre-existing clears needs explicit migration semantics and regression on old v124 backups.

## Next implementation gate

Build a versioned, recoverable, exported, signed-APK-tested save adapter with one-time claim ledger and strong rollback, complete source-compatible original Gem acquisition/spending design and old-account handling. Then test device update without clearing `bf_global_offline_demo_v7`. Only after all checks may the 22 playable finale awards be activated; seven Amdahl still cannot pay. The one-Gem amount is now strongly historically corroborated, but native 2022 commit semantics remain unknown.

The v158 test runs under GitHub Actions. Merge only after v157 merged-main Build #538 green and exact v158 feature CI green; require fresh merged-main CI green.
