# v169 — Optional source-capped Imp fusion and low-grind Arton supply

Baseline: v168 merged to main at `b5d80f5fa66761afed81e864e8ebcf35ba12a899` (fresh main Build #602 must pass before merging this PR). User remains on installed v124 until requesting another APK.

## Authentic Global data

- The original owner-provided 2022 Global masters define `unitImpCaps` for all **2,291** catalog forms (147 cap tuples; 129 four-zero forms), checked in v123 against SHA-256 `3ab0bc3efaf968dd1959490f892dbfde01c5cad882b0bd3377ee98362c3375de`.
- Original feeding increments corroborated by historical game documentation: Molin +50 HP; Pakpak +20 ATK; Ganju +20 DEF; Fwahl +20 REC; Almighty Imp Arton +150 HP, +60 ATK, +60 DEF, +60 REC.
- No source indicates the 25% custom ceiling or the Arton supply policy is original. They are clearly labeled **optional offline QoL**.

## User-approved changes

1. Retain exact source per-form caps for the `original` mode; add opt-in `custom` mode multiplying each **nonzero** stat cap by 125%, rounding to practical per-Imp stat steps (50 HP, 20 ATK/DEF/REC). Four-zero original cap remains zero. Eligible owned units only.
2. User-activated `bf_global_offline_optional_imps_v169` local sidecar stores Imps, amounts fed to each **owned base ID** (persists across evolving form), and quest-count receipt cursor. Canonical `bf_global_offline_demo_v7` remains untouched.
3. Five original feed types supported. Material stock is spent only for real stat gains, clamped to the active unit's verified cap. Multi-Imp "smart batch" selects highest remaining benefit and only consumes materials after the whole optional sidecar save succeeds.
4. User explicitly activates optional feeding and receives a **one-time local convenience bundle of five Artons**. Thereafter, after actual increases in existing DEMO `P.questClears` counters, the user can manually claim **two Artons per new recorded clear**. Prior clears at activation are not retroactively rewarded. This is a local QoL supply, **not** an original mission drop, currency or Gem grant.
5. New archive DEMO battle unit construction applies saved Imp bonuses once in memory, after v168 level-one source stats and before original-source leader multipliers. No training, EXP, enemy, reward, save migration or native damage formula changes. Existing battles are not retroactively edited.
6. Original cap mode clips *effective* bonuses without destroying the recorded Imp investment; switching back to custom restores the higher effective cap. Original 2022 evolution source and learned skills remain unchanged.
7. An in-game control displays owned units, inventory, caps and smart-plan preview. Optional Imp progress **requires separate JSON backup** before transferring or importing the canonical v7 save; in-app export/restore controls preserve it. Invalid/corrupted sidecar fails closed until the user explicitly supplies a valid backup.

## Verification and limitations

`test_bf_optional_imp_fusion_v16900.js`: source-checked real v123 cap values, cap multiplier, input validation, Arton and basic increment values, initial five Artons, no retroactive clear rewards, idempotent repeat-claim, 4-Arton Vargas smart feed, no zero-gain waste, new-battle stat effects only, original-mode clipping, memory-only effects, sidecar rollback on localStorage failure, invalid-sidecar restore, unchanged v7 save.

`test_bf_packaged_optional_imp_fusion_v16900.py`: exact module bytes, loader ordering, v111 bridge, Android signing, package and canonical save identity.

Limits: real 2022 native Imp fusing animation/Zel costs and all original drop tables remain unverified. The QoL Arton earn rate is explicitly nonoriginal. Standard Imps are supported by the feeding engine and inventory, but the new convenience supply awards Artons, not arbitrary invented original materials. The source archive includes many forms not yet actively playable; the live engine modifies **only valid owned playable forms**. Sidecar is not automatically included in the native v7 backup file; export it separately to retain fed enhancements.

Merge only when **#602 v168 merged-main** and **v169 exact-head feature** CI are both SUCCESS, guarded PR merge and fresh v169 merged-main CI SUCCESS. Do not deliver APK unless user requests it. Gem changes stay out of scope and require user follow-up once Imp system is confirmed.
