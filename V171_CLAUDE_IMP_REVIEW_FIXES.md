# v171 — Claude F1/F2/F3 Imp safety corrections (review candidate)

## Baseline and dependence
- Merged and verified v169 main SHA: `22ac563a21947823ae91cae70607e1dee0843f3c` (GitHub Build #619 SUCCESS).
- Pending v170 custom Gem PR #96: `feature/v170-custom-offline-gems-and-replay-reward`, source SHA `7c1f86f59b53f4332b57675f0cab22774bc25364` when this branch was cut.
- v171 feature `feature/v171-imp-save-integration-strict-cap` is **based on v170**, not directly on main; merge only after exact v171 CI and independent Claude review, with a fresh merged-main build. v171 must not be promoted before the dependent v170 PR.
- User-installed Android v124 is untouched. An owner's actual native save/app update has not been tested on-device.

## F1 — Strict personal cap, never above 125%
- The source-authenticated 2022 Global `unitImpCaps` for 2,291 unit forms remain exact.
- Custom cap: `max(original, floor((original * 5 / 4) / impStep) * impStep)`; step 50 HP and 20 ATK/DEF/REC. A zero source cap remains zero, and nonzero custom caps never exceed 125% of the original.
- Previously feed amounts are NOT deleted, sold or rewritten. Current applied stats clamp to the revised cap; a switched original cap mode continues to clamp without deleting investment.
- Rounding is **down**, not to nearest. 500 HP cap becomes 600 (not 650); DEF 120 becomes 140 (not 160). This intentionally errs under, rather than above, 25%.
- `test_bf_imp_strict_caps_v17100.py` checks all 2,291 source forms, 9,164 stats, and 129 four-zero original profiles.

## F2 — Main save and normal backups now include Imps
- A new **optional** `P._bfImpsV171` field is validated as version-one Imp progress or null **inside the same canonical `bf_global_offline_demo_v7` JSON**. The original v7 key, `P.version`, roster, quest, Gem metadata, signing identity, Android package and other gameplay are preserved.
- `patch_bf_imp_canonical_v17100.py` is applied after original Gem patches and v170 Gem wallet, before tests and APK compilation. A corrupt canonical Imp field fails closed through the existing save quarantine (never automatically resets other save data).
- The v169 Imp engine now saves all Imp inventory, applied amounts and earned Arton cursors through **the original `saveProgress()` transaction**, not an independent localStorage sidecar. Save failures roll back in-memory Imp modifications, and no Imp changes are committed on failed writes.
- Existing v97 three-slot rotating backups and v164 **EXPORT CURRENT SAVE** already capture the exact canonical JSON; they therefore include Imp progress with **no file-format wrapper or native export change**.
- No auto-association of an older v169 sidecar with a new or imported v7 save. A visible **IMPORT LEGACY v169 IMPS INTO THIS SAVE** action requires a user click and confirmation. The old sidecar is kept intact; the adapter imports its data into the current v7 save and clamps reward claim cursors to at least the current save's quest clear history, avoiding bonus Artons from another save.
- A standalone Imp backup pasted into the panel also imports into the current v7 save; for safety, the UI warns about choosing the correct save. Switching to a different parsed v7 save without `_bfImpsV171` makes old Imp bonuses immediately inactive.

## F3 — Arton stock ceiling
- Arton claim now only advances quest-clear cursors for pairs of Artons actually awarded. Near the 10,000-item inventory ceiling, partial zero-gain claims cannot consume uncredited earned claims.

## Tests and remaining risks
- Updated `test_bf_optional_imp_fusion_v16900.js` to simulate canonical save commits and quota rollback.
- Extended `test_bf_optional_imp_browser_v16900.py`: feed/claim, native-export bridge output, rotating backup slot inclusion, imported-save separation, explicit legacy v169 sidecar migration and restore.
- `test_bf_imp_strict_caps_v17100.py` checks every source cap value.
- `test_bf_packaged_imp_canonical_v17100.py` checks exact signed-APK asset, patch/validator and Android no-INTERNET/package/signing invariants.
- **No changes** to native original fusion Zel prices/animations, Gem spending, enemy AI or user installed v124 APK. Daily Gem claims remain opt-in.
- Downgrading to a pre-v171 APK can strip the new canonical Imp field; export a current v171 v7 save to external storage before downgrade. The old independent v169 sidecar is deliberately never auto-deleted, to provide a possible recovery reference.
- A canonical v7 save export now contains the potentially larger Imp record but must stay under the existing Android 1 MiB export and v97 512 KiB rotating slot limits. Extra-large saves are rejected rather than truncated; this is a relevant reviewer test.
- Source-accurate rounded caps may change effective stats relative to v169; still only affected in-memory battle stats, not persisted unit base stats.

## Independent review gate
Ask Claude to examine **the exact v171 GitHub PR diff**, reproduce browser tests independently, inspect save/import and effective-form transitions, compare a synthetic v124→v169→v170→v171 save timeline, validate the 10,000 Arton inventory edge, and return severity-ranked findings with file/line and concrete reproductions. Do not merge without green exact-head feature CI; after merge require green new main CI. Claude is not connected directly here, so a handoff/review link is required.