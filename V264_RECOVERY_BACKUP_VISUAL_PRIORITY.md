# v264 — Recovery backup visual priority and safe New Save separation

This is a follow-up to **Claude's v256 PR #190 independent APPROVE with non-blocking N2/N3/N4**. v256 is already merged at `5dc9de6f1ca3ba4a354bfad1d4591e86a6ffbaca`. This v264 patch is separately reviewed and must not retroactively alter the reviewed v256 exact HEAD.

## Problem and actual limited changes

- Recovery-mode **Download Unreadable Save Backup** (`#quarantineexport`) was beige and 36px high, visually less prominent than the already warning-colored destructive **Continue with New Save**. Give the backup action the same gold, 48px minimum, focus-accessible export treatment as ordinary **Download Save File**. Use 50px at 320–359px.
- Ordinary **Download Save File** had ~4.0:1 text contrast over the top of its gold gradient. Darken its light gradient end to `#6b592d` and the other end to `#253e34`. Do not change labels, events or data.
- At widths **360px and larger**, visually separate the **New Save** button from **Undo Last Import** by giving New Save its own full-width flex row with additional top spacing. At 320–359px retain the already single-column export/import grid.

## Evidence

`test_bf_recovery_backup_hierarchy_v26400.py` asserts the real `index.html` has the five existing target IDs, no runtime/app/network/save code changes, source and Android workflow registration. Its six-width isolated Chromium fixture includes the original `flex:1 1 140px` rule from `index.html` instead of CSS navigation alone, and tests both safe backup visuals, reset separation, min 48px target sizes, narrow recovery 50px, focus, overflow and safe Home route. This is still **not** an actual Android install, full WebView+injected-modules test, real save test or original 2022 screenshot comparison. Claude's earlier real-index render of v256 is not a review of this new patch.

**Do not merge without a NEW independent Claude exact-head review of v264's reset-sensitive CSS, plus six source preflights and signed Android build on exact current HEAD and retargeted main.**

## Stack and preservation

v264 follows v263 PR #197, v262 #196, v261 #195, v260 #194, v259 #193, v258 #192 and v257 #191. Prior v256 PR #190 is MERGED. Future stacked PRs must land sequentially on updated main after merge-time CI. No runtime JS, HTML, assets, Java, manifest, Gradle, signing, network, gameplay, Gem economy, battle, rewards, existing save handlers, actual confirmation prompts, local storage key, archive source, user installed signed v251 APK or user save changes. Preserve `org.bravefrontier.offline` and `bf_global_offline_demo_v7`. UI ~65% provisional; whole original game ~30% provisional. Owner visual parity PENDING.
