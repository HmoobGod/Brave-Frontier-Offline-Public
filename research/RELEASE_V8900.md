# Brave Frontier Global v89.00 — Live Simple Offensive Brave Burst Crystal Evidence

**Verified parent:** v88.00 Build #328, commit `8e33d87c8e28be04ef496d72df511d3da03f48b4`, successful GitHub Actions signed debug APK artifact #12592592505.

## Source-backed native-data expansion during real demo battles
The 2022 F_UNIT_MST_1/2_Ver1084 and F_SKILL_MST_1..9_Ver1535 exact joins (v85 source audit) identify 2,125 linked BB skills. Of these, only 213 simple single-group offensive profiles have source-constrained per-target damage-event counts and original `dropCheckCount`. 1,808 complex/multi-group, 95 nonoffensive and 9 invalid-weight profiles **cannot** support valid BC event totals and are excluded.

The new `BFGlobalLiveSimpleBBCrystalsV8900` wraps an actual player DEMO Brave Burst command, observes BB gauge expenditure and HP damage on each surviving enemy, and calculates per-target reference BC production at the original community-documented base **35% chance per source drop check** and HC at **10% chance per supported damage hit**. It retains a small current-battle log and source counts in a separate expandable panel. The existing v88 source-normal attack events remain independent, and no module invents overkill or alters original damage execution.

**Native mechanics not yet established:** original per-target skill damage splitting, hit chronology, crystal pickup/recipient distribution, BC-to-BB charging, HC-to-HP healing, elemental resistance, enemy AI, reward and item grants. This is **source-informed reference production after a live DEMO event**, not complete original 2022 combat. Unsupported BBs cannot produce calculated reference drops. Overkill is always explicitly false.

## Safety contract and CI gates
- No edits to `P`, saves, `bf_global_offline_demo_v7` (schema 7), HP, BB, inventory, summons, quest state or rewards.
- Package remains `org.bravefrontier.offline`, development debug signing key unchanged, no INTERNET permission.
- Read-only, optional extension (under 64 KiB). No external DecompFrontier server calls or license-incompatible code copied.
- Full original browser and signed APK regressions, deterministic source BB tests, support-skill exclusions, coexistence with v88, and save-isolation checks required.
- Only exact green Actions run with uploaded signed debug APK artifact may become verified Current; physical Android install remains unverified.

Next gate: recover original crystal pickup recipient rules and HC/BB conversion, then integrate pickups only with source-backed exact constraints.
