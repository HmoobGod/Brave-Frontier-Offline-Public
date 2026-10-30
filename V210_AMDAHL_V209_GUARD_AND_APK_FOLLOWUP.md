# v210 — Complete v209 source-guard + compiled APK test follow-up

**Regression-only. No changes to Android Java, packaged runtime JS, rewards, saves,
permissions or the gameplay engine.**

Responds to independent Claude review of v209 PR #140:

- **N1:** Extends the existing v209 Chromium test with 20 negative/restore probes
  before initial v209 initialization. It covers both original v206 SHA guards;
  source-only vs playable state; source mission counts; v151 SHA/meaning/counts;
  changed v151 raw encounter string/dungeon ID/playable flag/missing row;
  mismatched v206 lookup dungeon; extra playable quest; missing v206/v151
  dependencies; missing dropdown options; and missing DOM host/select/list.
  Every probe must build neither the v209 DOM nor its public API. After all
  restores, all 36 source rows still render and the v7 player/save snapshot
  and zero-write count must remain identical.
- **N3:** Extends `test_bf_packaged_amdahl_story_guide_v20700.py`, already run
  after `assembleDebug`, to check exact source-byte equality of the compiled
  v209 optional asset, full pinned 2022 SHA constants, one DEX string-pool
  reference to the asset name, Android source `evaluateJavascript` call and
  the existing v149/v151/v206/v209/v174 Java injection order.
- **N4:** Clarifies docs: Amdahl's opaque `8:0:1:0:0` text is not
  interpreted as a reward and never triggers any payout.

No CI workflow edits are needed: these two tests were already wired into the
existing verified full Android build pipeline. Require an **exact-head
successful complete GitHub Actions run**. All real Android device validation
remains open, including in-place update and owner save export comparisons.
