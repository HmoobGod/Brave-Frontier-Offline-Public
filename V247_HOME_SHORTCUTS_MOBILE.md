# v247 — Readable, finger-sized Original Global Home shortcuts on small phones

**Base checkpoint:** v246 PR #180 merged to `main` as `ab3e9965ed1b52afd2a81548dac1c5c752442575` after successful exact-head Android Build #1440 and six source preflights. PR #181 is now retargeted to `main`. The v247 branch still includes the original v246 head as its ancestor, and this documentation update intentionally triggers a fresh exact-head Android run before v247 can merge.

## UI-only change
The existing five Home shortcut tiles (QUESTS, UNITS, SAVES, UNIT BOX and unavailable EXCHANGE · LATER) currently occupy five narrow columns even on 320px phones. At viewport widths **320–412px** the same original Global art tiles display in three columns, giving readable 11px captions and ample finger targets. At larger widths the existing five-column arrangement stays. All shortcut routes, the read-only Exchange state, original art bytes, and native controls remain unchanged.

## Safety and gates
`bf_home_nav.css` is the **only runtime asset modified**. No JavaScript, Java/manifest, game/save schema, battle or economy logic, sprite/asset archives, network permission, package/signing ID or Current change. Source-only `test_bf_home_shortcuts_mobile_v24700.py` verifies the CSS selectors, unchanged source labels, no added save/game timers, size budget and CI registration. Full headless Chromium verifies 3 columns (320, 360, 393, 412px) and 5 columns (540px), tap targets at least 44px wide and 88px high, labels at least 10px, no layout overflow, inert Exchange Hall and unchanged Quest/Units/Saves navigation. Dedicated UI source preflight plus full Android/browser pipeline run this test, keeping previous v242–246 coverage.

Merge policy: do not merge while v246 remains blocked or v247's **exact-head** source/full Android tests are incomplete. As low-risk UI-only, green automated gates suffice unless material regression arises; schedule independent Claude review at v250 APK release checkpoint. v250 remains owner's planned device/install review.
