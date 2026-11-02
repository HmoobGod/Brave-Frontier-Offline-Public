# v257 — Owner squad editor readability on small Android screens

**Owner UI-only directive:** Focus on audited Brave Frontier Global offline UI until 100%. This is a display-only patch. Source screenshot audit of isolated v251 packaged WebView at mobile width showed excessively dense squad roster cards with names and statistics crowded together. The screenshot fixture lacked some archived art, so this identifies layout/readability only, not original Global screenshot parity.

**Stacked dependency:** v257 builds on v256 PR #190 exact source head `b7afc4d0b13656fcaa760fba5a68b0e556b0cc43`, which is draft and stacked on v255 #189. v255 depends on v254 #188 (merged). Do **not** merge v257 until v255 and v256 are separately approved, merged, and v257 is retargeted to current main and receives fresh exact-head source and signed Android CI. v256 requires independent Claude source review of save-reset UI. This patch itself must not modify save-selection behavior.

## Scope

In the *existing* `.squadsetup .squadpicker` roster:
- Keep original checkbox handlers, owned/locked status, portrait source, squad lineup, unit names and actual saved roster.
- Permit long unit names and metadata to wrap onto readable lines rather than clip or overflow. Keep text at least 10–12px with more line-height.
- Give each roster card a larger and more comfortable touch target (85px minimum at up to 359px, 100px elsewhere) and visible keyboard focus.
- At 320–359px stack the roster in one full-width column. From 360px up, use two columns, including 540px where the prior three-column layout was too cramped for names/stat details.

**Runtime delta: CSS only.** No JavaScript, Java, Gradle, Android permissions, save schema, checkbox event handlers, balance/unlock/gem code, unit identities, gameplay or original asset files.

## Source and browser checks

`test_bf_squad_editor_mobile_v25700.py` source-only mode verifies the CSS-only selectors, text wrapping, layout and CI wiring with no storage/game writes or Internet permission. Browser mode uses actual navigation bootstrap with representative interactive squad labels, long original unit descriptions, owned and unowned checkboxes, 320/359/360/393/412/540px viewports, 1/2 grid column expectations, target height, focus state, route visibility and no overflow.

The UI remains approximately **65% provisional**, not a device-verified or 2022 screenshot parity percentage. Owner installed v251 APK and real save remain untouched. Validate original art on device with owner screenshots separately; no automatic APK installation.
