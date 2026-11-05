# UI-first milestone: five Global location previews

Home previously displayed locked artwork for these destinations without any
screens to explore. A new **Explore UI previews** entry opens a location
directory and five reconstructed screens: Vortex Gate, Arena, Raid Battle,
Capital Randall and Exchange Hall. Capital Randall also links to the Exchange
Hall preview, with a nested Back path.

The existing gameplay destinations stay unavailable. The new screens show
explicit UI-preview/availability states and disabled gameplay/transaction
buttons. No fake opponents, ranks, events, currency balances or rewards are
created. The prose, cards and arrangement are reconstructed presentation, not
recovered original screen layouts or a claim of native Global visual parity.
These are initial location shells, not completion of all original subpages.

## Implementation and safety

The presentation is appended to the existing bounded Home JS/CSS. Existing
original-art bytes are reused unchanged; the Exchange icon stays at its native
100x80 size in the detail view. No new assets, network calls, Java, signing,
Gradle, save schema, inventory, Gem/Imp or gameplay changes. Existing locked Home
cards retain their truthful unavailable semantics and no active children.

A native modal dialog makes the background inert. Explicit Tab/Shift+Tab
wrapping prevents keyboard focus leaving the dialog; Close and Escape restore
the opener. Back returns through nested views and finally closes the directory.
The existing Android Back expression uses the nav object's presentation state
and its Home action to invoke the same Back path; Java remains unchanged.
Programmatic navigation to another main route closes the preview first.
Unsupported dialog APIs fail closed. Native Android/WebView rendering still
requires actual device testing.

## Verification

All 63 CI source preparations passed in a disposable copy of current main plus
this patch. The new browser regression uses actual prepared HTML, all navigation
modules and local original assets, with network requests intercepted locally.
At 320x740, 393x852, 540x900 and 740x360 it verifies all five destinations,
directory, disabled actions, nested Back using the actual Java expression,
Close/Escape/focus restore, forward/reverse focus wrapping, programmatic route
exit, duplicate injection and bounded layouts. Full synthetic player P, battle
S, every storage entry and storage write counts remain unchanged. No real save
is loaded. Twenty-four browser screenshots and hashed receipts are produced in
`source_audit_reports/location-ui-previews/` and uploaded by Android CI.

Initial keyboard testing exposed focus leaving the native modal; explicit
wrapping fixed it and the full new matrix subsequently passed. Representative
320px, 393px, 540px and landscape images were visually inspected. The Exchange
hero sizing was then corrected to avoid scaling its small original icon.

Legacy actual Android Back-expression browser tests, Home release readiness and
route-heading regressions at five phone widths passed, as did staged 42-image
path validation, v278.1 source registration, navigation resource budget audit,
integrated engine UI and touch/accessibility source checks. After the icon-size
correction, the complete four-viewport browser matrix passed again and all
24 screenshots were regenerated from the prepared snapshot.
Fresh GitHub exact-head Android CI and independent Codex review are separate
pending requirements. Browser rendering is not physical-device acceptance or
proof that gameplay systems work. Preserve all APKs and owner progress.

## CI compatibility follow-up

The first GitHub UI source preflight failed because inherited v264/v271/v273–277
checks searched every later CSS section for `display:none`, including this
unrelated preview's hidden directory Back button. Seven visibility assertions
now inspect the relevant save/Training/Unit Box selectors across the stylesheet,
including later overrides; no runtime styling was changed to silence the guard.
All 51 Python commands from the complete UI preflight pass locally. All seven
affected legacy browser suites pass, including backup/reset visual distinction,
unresolved Unit Box profiles, Training feedback/actions/forms and Box toolbar/
detail controls. Seven late-hidden-control negative mutations are rejected,
including a spaced `display : none` declaration. The initial failing CI and
old-head Android run are historical, not current-head approval. Fresh CI must
pass again after the append-only correction commit.
