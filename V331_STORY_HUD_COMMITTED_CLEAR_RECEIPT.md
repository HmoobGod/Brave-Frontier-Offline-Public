# V331 — HUD next-story navigation must require a committed v7 clear receipt

## Defect fixed
The built-in v2000 story battle HUD has its own **Next Story Mission** button. Its previous gate trusted in-memory P.questClears plus saveEnabled and saveRecoveryPending. After the v3000 Battle Results receipt hardening in the pending #330 batch, the HUD's older gate could still advance on a stale or externally restored canonical save.

## Real playable change
The v2000 HUD now queries the existing v3000 read-only committedClearCount(missionId) **at snapshot/advance time**, only for an archived victory. The canonical v7 clear count must be a positive safe integer and must match the persisted record. Missing, stale, corrupt or throwing receipts fail closed; the visible Next button and its action share that gate. If the v3000 results extension is not present in an older isolated embedded page, the established v20 core gate stays unchanged. The current Android script chain does load v3000.

## Regression and owner compatibility
A Chromium test injects the result API into the original real-page v20 harness and verifies stale receipt denial, thrown getter denial, recovery after exact receipt, no quest change, and byte-identical P and stored v7 save. The packaged-APK test verifies read-only API integration and unchanged signer/manifest paths.

No reward, battle, source enemy, Auto Battle, AI, Android package ID, save schema, signing, or installed owner APK changes. This patch is deliberately **disjoint** from draft #330. Require complete exact-head signed Android + Chromium + packaged + v7 regressions and reconciliation if main moves.
