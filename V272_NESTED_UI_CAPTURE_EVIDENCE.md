# v272 — Nested UI source-browser screenshot receipts

**Dependency:** draft v271 PR #206, source head `1c86beae8913053df86c8286b8e957e328d8e6ae`. This patch must remain stacked and draft until v271 independently passes Claude review, signed CI and merge. After v271 merges, retarget/rebase v272 to the new merged main and rerun exact-head validation; earlier stacked approvals cannot substitute.

## Why

v263 source evidence captures ten screenshots of five **top-level** navigation routes, but the v259 nine-surface screen inventory still lacks reproducible visual receipts for several important **nested** presentation states. This v272 patch adds a second, separate artifact with screenshots of six real nested UI views: active squad editor, owned Unit Box, evolution lab, training lab, selected quest details and menu save controls.

The real packaged `app/src/main/assets/index.html` and repository nav JS/CSS are rendered in disposable, network-blocked Chromium contexts with prepared repository artwork. The script visits views using existing navigation/Unit Box APIs; it **does not click Summon, Begin Quest, New Save, Import, Export, training rewards or evolution actions**. It does not restore, overwrite, delete or otherwise access the owner's APK or save.

## CI and evidence

- `test_bf_nested_ui_capture_v27200.py --source-only` runs within the Android Back/UI source preflight and checks CI registration, loader budgets and lack of Internet permission.
- In the existing **signed Android PR build**, after source art preparation and alongside the prior v263 captures, run `--capture` and publish artifact **`BraveFrontier-v272-nested-ui-screen-receipts`**, 90-day retention.
- Exactly **12 PNGs**: six named nested screens at **320 × 740** and **393 × 852** viewport sizes, DPR 2, reduced-motion mode. Viewport-only capture; no full-page fake panorama.
- A `capture-manifest.json` records each screenshot's SHA-256, byte count, viewport, selected route/tab, scroll position, no extra horizontal overflow, unchanged synthetic player state and missing/blocklisted requests. Images and original art remain source-derived; no screenshots or blobs are committed to the repo.
- Browser requests are fulfilled only from the checked-out local `app/src/main/assets` path; external requests and path traversal are blocked.
- The script compares the same synthetic player state before and after each view: roster, squad, unit EXP/evolution, Gems, Zel, Karma and the in-memory `bf_global_offline_demo_v7` save string. A fresh opaque-origin browser uses an in-memory replacement for localStorage; no owner storage is mounted or read. No gameplay actions or writes.

## Local evidence and limits

A disposable local run against **actual signed v270 APK-extracted `index.html` and source artwork** with the unmodified v270 nav CSS/JS passed all **12/12** captures, six views at two widths. No JavaScript exceptions, missing original-art references or state mutations; document scrollWidth was <= viewport + 1 px, matching previously documented rounding behavior. This verifies script feasibility. New v272 exact-head CI must still run the same checks with the merged v271 candidate assets before the patch may merge.

**This is navigation-shell + nested presentation source evidence, not a complete Android WebView render, original Brave Frontier 2022 Global reference screenshot, or owner phone inspection.** Do not mark any v259 screen as fully visually accepted until historical screenshot comparison and owner-device acceptance. The screenshot evidence helps prioritize future visual work but does not increase progress estimates on its own.

## Safety and merge gates

Expected scope is **four files only**: this document, new Python read-only capture script, one source-preflight registration and one signed-build capture/artifact registration. There must be **zero edits** to `index.html`, `bf_home_nav.js`, `bf_home_nav.css`, Android Java, manifest, Gradle, signing, gameplay/summon/quest, original art, save parser, `bf_global_offline_demo_v7` key, or any owner's APK/save.

Do not merge before v271 is approved and merged, then v272 is retargeted to merged main, all six exact-head source preflights pass, the full signed Android build and standard/identity/diagnostic/missing-index artifacts are verified, and Claude independently reviews the **exact final v272 head**. Do not install or reset the owner's working v265 device. UI estimate ~65%, entire original 2022 reconstruction estimate ~30%, both provisional and unchanged.
