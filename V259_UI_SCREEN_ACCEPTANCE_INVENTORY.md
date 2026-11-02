# v259 — Brave Frontier Global UI acceptance inventory (source-baselined)

**Purpose:** turn the UI-first-to-100% goal into a screen-by-screen evidence and phone-acceptance ledger. This is not a claim that a complete original 2022 Global UI has been reconstructed. Estimated UI completion stays **~65%, provisional**; estimated complete original game stays **~30%, provisional**.

**Dependency:** v259 is stacked on v258 PR #192 at exact parent `db7957f721c7e50dea7f4304f97da8e890b2c348`; v258 depends on v257 PR #191 and v256 PR #190. All must merge in order after exact-current-head review and CI. **v256 independently requires Claude review of the backup/reset UI**. No owner APK installation is authorized by these source changes.

## Evidence levels (not percentages)

- **Existing automated source/browser coverage**: a named test exists in source; pass/fail must be checked at each *exact PR head*.
- **Original-art filename integrity**: v258 checks static referenced image files in built Android CI, but not dynamic portraits or appearance.
- **Owner phone visual acceptance**: **PENDING for the full screen inventory**, even though the owner's v251 over-v124 upgrade and preservation of units/quests/Gems was reported as successful. Do not confuse upgrade smoke with pixel-level screen approval.
- **2022 archive screenshot comparison**: **PENDING** for all screens; a recovered source sprite is not proof of original layout fidelity.

## Auditable screen register

| UI surface | Existing automated evidence | Current offline availability | Still needed for UI acceptance |
| --- | --- | --- | --- |
| HOME | `test_bf_home_ui_release_readiness_v24900.py` | Five-route navigation, squad preview, recovered art | Original 2022 Home reference vs owner 320–540 px screenshots, fit and gestures |
| NAVIGATION | `test_bf_global_route_headers_v25200.py` | Home / Units / Quest / Summon / Menu | Android Back + safe-area/gesture screenshots and actual touch validation |
| QUEST / BATTLE | `test_bf_quest_mission_cards_v25300.py` | Offline **demo** quests and battles; original-art fragments | HUD and result screens, locked/empty states, narrow-screen screenshots, historical layout comparison |
| UNITS / BOX | `test_bf_unit_box_mobile_v25400.py` | Owned-unit listing and demo unit tools | Real long-name, scroll, selection, source portraits, portrait fallback and empty-list screenshots |
| SQUAD EDITOR | `test_bf_squad_editor_mobile_v25700.py` | Demo squad editing | Real six-unit roster, 320px tap targets, stat wrapping and confirmed cancel/return flows |
| SUMMON HALL | `test_bf_summon_hall_mobile_v25500.py` | **Demo** recruitment; native Global rates **not restored** | Original art fidelity, disclaimers, success/error and low-Gem UI on phone |
| MENU / SAVES | `test_bf_save_controls_mobile_v25600.py` | Export/import and explicit New Save reset controls | Claude review of destructive-control contrast, real backup/restore/error-state screenshots, no accidental reset |
| UNAVAILABLE LOCATIONS | `test_bf_home_semantic_hierarchy_v24500.py` | Vortex Gate, Arena, Raid Battle, Capital Randall, Exchange Hall: **art previews only** | Truthful disabled affordances with no action/reward paths, original source comparison |
| STATIC UI ART | `test_bf_ui_asset_paths_v25800.py` | Referenced original artwork built from source packs | CI-verifiable bytes, dynamic portrait coverage, actual screen image capture and positioning |

## Current merge/CI gates (November 2, 2026; source-only tracking)

1. **v256 PR #190:** Claude exact-head review APPROVE and merge confirmed; merged main SHA `5dc9de6f1ca3ba4a354bfad1d4591e86a6ffbaca`.
2. **v257 PR #191:** merged to main at `72fca1091c95780ddc20bbe50b13f903980ac304`, source and signed Android CI verified. Owner installation is separate.
3. **v258 PR #192:** merged to main at `80b004f037cdc96a189289f2abf4369f3d05af60`; source checks and PR merge-tree signed CI passed. The branch-push CI eventually completed successfully. The merge occurred while that branch run was still reported in progress; preserve this chronological exception in the master tracker rather than claiming that gate had already completed when merged.
4. **v259 PR #193:** retargeted to the v258 main merge, retaining only the original four-file evidence-guard scope. This documentation update refreshes stale review/CI information and triggers fresh exact-head source and signed Android CI. **Remain draft; do not merge until new checks are verified.**
5. **v260–v265:** still stacked drafts; v264 exact head `3bd812efe84a23e4452339e587762a0b9127e508` independently Claude APPROVED. v265 test-only PR #199 is under CI repair at updated head `ffe9c205d7c91cfa8ab89d253498a07846798f62` after an opaque-origin browser storage exception. Neither may leapfrog an upstream draft.

## Acceptance capture instructions (owner-controlled, no automatic install)

For each surface record: APK package/versionCode and SHA receipt; screen resolution and Android UI scaling; original archived Global screenshot/reference with provenance; a current-device screenshot at the same logical state; visible cropped or missing art; touch/scroll/focus behavior; navigation and Back; available/demo/unavailable copy; any blocking defect. Capture with no personal account credentials or sensitive save contents in screenshots. Mark each surface **ACCEPTED** only after both historical source comparison and phone acceptance, otherwise **PENDING**.

## Safety boundary

This v259 change adds **only** this audit ledger, a read-only source guard, and CI registration. It does not modify HTML/JS/CSS, game logic, original art, Gem economy, recruitment, save schema, installed APK, certificate, manifest, Java, versionCode or signing. Keep `org.bravefrontier.offline`, `bf_global_offline_demo_v7`, and the owner's installed v251 and existing backed-up save untouched.
