# v261 — Mobile Battle Results presentation

**UI-only continuation.** The optional v30.00 battle-results block injects its own CSS at runtime, including 44px action buttons. On small Android screens this leaves Replay, Next Story Mission and Read Original Clear Scene less accessible than the project's 48–50px touch-target standard. The original quest battle and simulated rewards are **not** being changed.

**Stacked:** v261 follows v260 PR #194 at exact parent `aed6284b03405dade3d14f5fb1cb0f6362f11135`, then v259 #193, v258 #192, v257 #191 and v256 #190. **Do not merge** until those upstream versions are promoted sequentially and the independent Claude exact-head review of v256 backup/reset controls is approved. After each upstream merge, retarget to current main and reverify exact-current-head source and complete signed Android CI.

## Actual UI difference

- Append **scoped CSS only** in `app/src/main/assets/bf_home_nav.css` for the existing `#resultpanel #bf3000-result` block. No replacement or migration of original HTML or runtime JS.
- Use grid button layout: one column for 320–359px; two columns at 360px and wider. Replay, Next and Clear Scene maintain real button IDs, event listeners and disabled/hidden attributes.
- Raise the action buttons to **at least 50px tall**; make long original mission names, simulated reward summaries, and result notes wrap without overflowing.
- Give keyboard-focus and disabled states clear visual behavior; preserve the original result panel's hiding/showing in the actual battle flow.
- The selector specificity intentionally outranks the CSS injected **after** nav styles by `bf3000_battle_results.js`. It does not change that script.

## Tests and unverified acceptance

`test_bf_battle_results_mobile_v26100.py` runs a source-only no-save/no-network guard and an isolated Chromium fixture at 320, 359, 360, 393, 412 and 540px. The test loads nav CSS, then a representative later v30 runtime CSS cascade. It measures computed heights, wrapping, overflow, hidden scene controls, disabled Next, keyboard focus, click routing, and navigation hiding the result panel. It does not pretend to execute the real battle, alter owner saves, prove original 2022 visual fidelity, or approve Android device rendering. Register it in both the source preflight and full signed Android workflow.

**Visual acceptance still pending:** screenshot pairs showing victory/defeat/archived rewards on a real owner-approved APK; original archived Global reference comparison; Android Back/gesture accessibility and long mission names. UI estimated **~65% provisional**, reconstructed whole game **~30% provisional**.

## Safety

Do not touch the owner's installed signed v251 APK or backed-up existing save. No Java, manifest, Gradle, package/signing, network permissions, original artwork, enemy AI, turn execution, auto combat, progress, Gems, replay actions, save handlers, save schema or reward grants change. Preserve `org.bravefrontier.offline` and `bf_global_offline_demo_v7`. No auto-install.
