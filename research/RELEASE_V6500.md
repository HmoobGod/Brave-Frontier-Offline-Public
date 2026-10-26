# Brave Frontier Global v65.00 — Sickness Recovery Penalty

Candidate based on v64.00 remedy-command candidate c0cd18f4441e88f913b91f86bb035f760855d6f5 (do not promote without successful complete CI).

The original 2022 item master includes ailment code 3 in group cure #20210. Global-era mechanics documentation [Status Infliction](https://bravefrontierglobal.fandom.com/wiki/Status_Infliction) identifies that status as **Sickness**, applying a subtractive **-50% REC** stat penalty lasting **three player turns**. v65 normalizes the player-facing status name to Sickness, reports original effect provenance, and implements a temporary reduction of living afflicted units' `rec` within DEMO player action resolution. It restores original REC after each action, including failures; avoids undoing concurrent stat mutations, and exposes `effectiveRecovery(slot)` for future native-verified healing logic.

Per-infliction generation tokens enforce independent three-observed-round duration, with selective status code 3 expiration. Cures from v57/v64 #20210 continue clearing codes 2,3,4. The current battle prototype's Lv1 BB healing still uses source base ranges but **does not have the original REC healing formula**. Therefore the v65 penalty is accurately reflected in in-action REC and status snapshots; **it does not falsely re-scale DEMO flat item cures or claim native healing effects**. Original enemy infliction rolls and status icons remain out of scope.

All changes remain battle-local and additive. No modifications to P/save v7, localStorage, item ownership, source binaries, package ID, signing key or INTERNET permission. CI must pass full inherited Chromium and signed APK regression gates.
