# v230 — Engine/UI combined integration candidate (NO MERGE)

## Purpose

Consolidate the five already independently Claude-reviewed engine/UI development patches into **one read-only validation branch**, based on merged v223 main plus v225/v226/v229 source commits:

- **v225:** Android Back in Quest/Units/Summon/Menu returns to Home, with no save write.
- **v226:** bounded Back callback, stale generation guard, renderer termination and opt-in native restart/close.
- **v227:** touch-action, focus outlines, preserved 60px nav buttons, reduced-motion limited to Home/nav.
- **v228:** bounded 128 KiB read allowance only for packaged `bf_home_nav.js`/`bf_home_nav.css`; all other optional resources remain 64 KiB.
- **v229:** main-frame-only packaged-page load failure Retry/Close, fail-closed script injection guard, corrected legacy v208 source assertion.

The branch copies the final approved v227/v228 files byte-for-byte and transplants **only** v228's `readPackagedText` method/budget into v229's MainActivity, preserving the v225 Back, v226 renderer and v229 error handling. The shared `.github/workflows/build-debug-apk.yml` test insertion is resolved by running all v225, v226, v227, v228, v229 and v230 tests. New source preflight checks the entire combined feature set and Android CI compiles the actual composite activity.

## Verification boundaries

This branch is **not merged**, is not an installable/promoted Current build, and has not been accepted on the owner's device. Existing old v7 saves are never written by the new native code; game asset content and gameplay source are untouched. Original gameplay, source quests, inventory, Gem economy, user/enemy AI, signing, application ID, INTERNET permission and package manifest are unchanged.

Individual Claude exact-head reviews and CI results on the original PRs **do not approve this combined v230 HEAD**. Require new Claude independent base-to-head review and exact-head source and Android CI. Device testing remains mandatory: Back on all five routes, Home fallback, quick double Back, active battle navigation, background/return, save integrity, native renderer recovery, missing main index cold-start/retry, and 320px / font-scaling layout.

**Not a replacement for PR ordering:** v224 archival research stays on hold; v225-v229 original PRs stay unmerged. Use the integrated PR as a single conservative CI and review candidate only after discussing merge plan and device acceptance, rather than silently combining into main.
