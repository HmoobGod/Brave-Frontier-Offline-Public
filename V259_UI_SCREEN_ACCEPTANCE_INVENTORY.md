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

## Current merge/CI gates

1. **v256 PR #190:** exact head `75ba3cf00e868313b2fc4d7c51fe6e439c3e2230`, six source preflights and Android run **41440301032** observed successful. **Claude independent exact-head review still required** before ready/merge; no prior review was found in PR comments at this checkpoint.
2. **v257 PR #191:** draft; base on the v256 line. Rebase/retarget to merged main after v256 and get fresh current-head full Android CI; existing six source-preflight runs were green on original head.
3. **v258 PR #192:** draft; base on the v257 line. Rebase/retarget after v257 and run full source + Android image-byte assertions. Six source-preflight runs were green on original head; **full Android on current main not yet verified**.
4. **v259:** this test/documentation-only inventory PR must remain draft while upstream gates are open. Fresh exact-head CI is required for its own source changes and any subsequent rebase.

## Acceptance capture instructions (owner-controlled, no automatic install)

For each surface record: APK package/versionCode and SHA receipt; screen resolution and Android UI scaling; original archived Global screenshot/reference with provenance; a current-device screenshot at the same logical state; visible cropped or missing art; touch/scroll/focus behavior; navigation and Back; available/demo/unavailable copy; any blocking defect. Capture with no personal account credentials or sensitive save contents in screenshots. Mark each surface **ACCEPTED** only after both historical source comparison and phone acceptance, otherwise **PENDING**.

## Safety boundary

This v259 change adds **only** this audit ledger, a read-only source guard, and CI registration. It does not modify HTML/JS/CSS, game logic, original art, Gem economy, recruitment, save schema, installed APK, certificate, manifest, Java, versionCode or signing. Keep `org.bravefrontier.offline`, `bf_global_offline_demo_v7`, and the owner's installed v251 and existing backed-up save untouched.
