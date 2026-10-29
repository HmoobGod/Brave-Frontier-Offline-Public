# v190 — Quest quick access to existing Personal Offline Gem rewards

**Status:** Feature candidate. Independent review required before merge.

## Why

The owner successfully installed and tested v188 on Android, but had difficulty
finding the `GEMS · PERSONAL OFFLINE REWARDS` panel because v170 puts it **after
the complete Quest list**, below the fold. This small opt-in UI discovery fix
addresses a real owner-reported problem without altering original Global
mechanics or the personal reward policy.

## User-facing change

- Add a full-width **GEMS · DAILY REWARDS** button immediately **before the
  Quest list** (same parent); the existing v170 collapsible rewards panel
  remains immediately **after** the list.
- Clicking the new button expands the existing panel, refreshes its displayed
  balance/mode and smoothly scrolls to it.
- The existing reward mode, 1,000 one-time/100 daily claim buttons, 25/100
  first-clear and 1 replay reward rates, original-mode separation, and
  account-free local save logic are untouched.
- Reinjecting the script cannot duplicate either control because the existing
  `window.BFGlobalPersonalGemUIV17000` initialization guard is unchanged.
- The button is outside `#questlist`, so rerendering the quest list cannot
  destroy it; it follows normal Quest screen visibility and route navigation.

## Preserve original/experimental boundaries

There are **no** changes to `index.html`, Java loader, game economy,
`P`, `S`, original 2022 quest data, quest clear count, unit roster, Gems,
Imps, combat, summons, permissions, package name, Android signature or
original 2022 enemy behavior. This adds no free Gems and does not enable
Gem spending. The canonical player key is still
`bf_global_offline_demo_v7` with `P.version===7`.

## Verification

- `test_bf_personal_gem_quick_access_v19000.py` loads the actual prepared
  game HTML, navigation UI and Gem UI in Chromium at 390x844, verifies the
  new button is visible after navigating to Quest, confirms the panel
  opens/reopens through a real button click, avoids duplicate injection,
  and checks game `P`, `S`, v7 localStorage and storage write count remain
  unchanged.
- `test_bf_packaged_personal_gem_quick_access_v19000.py` runs after Android
  Gradle assembly and verifies the exact v190 Gem UI JS asset bytes in the
  built APK plus preserved v170 Gem module and canonical v7 save.
- All existing v170–v189 tests remain enabled; the feature uses the
  existing `bf17000_personal_gem_rewards_ui.js` load path.

## Merge and release conditions

**Do not merge** until previous v189 merged-main build #841 on SHA
`18e8f0d0c4d7fd0ab101c586f2d8fe2db3f6585a` passes, then the exact
v190 feature-head build succeeds, and independent Claude review accepts
the focused UI change. A new merged-main build must pass before calling
v190 CI verified. Do not replace the user's tested v188 APK solely for
this optional usability improvement. A later device upgrade still must
confirm v188 save persistence and both historical-art toggles.
