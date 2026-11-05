# UI-first Equipment screen

Adds an Equipment entry to Units, below the four existing unit actions. It
opens a read-only inspector for resolved owned units, showing their existing
name, portrait, rarity, element and archived ID. Search, selection and returning
to the Unit Box work as UI navigation. These operations never equip anything.

Two sphere-slot placeholders and the inventory panel are explicitly unavailable.
The UI does not assert that either slot is equipped/unlocked, show invented
sphere ownership or quantities, grant inventory, apply stats or enable unlocks.
Empty, filtered-out and unavailable-profile states remain readable and preserve
the roster. Missing portraits use the existing accessible fallback. Layout,
lettering and decorative sockets are a reconstruction, not recovered original
Equipment screen art or proof of complete Global visual fidelity.

## Integration and safety

The new Units subtab participates in the existing selected-button semantics,
route hide/show and return-to-Box flow. The four previous functions keep their
existing behavior and space; the Equipment entry spans a new row. The Equipment
anchor measures the existing sticky header with resize updates so that scrolling
to the screen does not cover its heading. Android Back routing remains unchanged
from the existing Units route. No new Java, assets, signing, build identity,
save schema, persistent equipment fields, economy, Gem/Imp or gameplay changes.

Built directly on merged main `6c79a06ee92a982bbd744179b97edb401c150cc0`,
which includes reviewed #224. No dependency on parked gameplay PRs.

## Evidence

All 63 source preparations passed in a disposable copy. New browser testing uses
actual prepared HTML, full navigation JS/CSS and locally served original assets.
At 320x740, 393x852, 540x900 and landscape740x360 it verifies owned selection,
search/clear/no-match, long names, empty/unresolved rosters, disabled service
buttons, fallback portrait, touch sizes, focus, Unit Box return, main-route
hide/show and duplicate injection. Full synthetic P, S, storage bytes and write
counts stay unchanged. Synthetic empty/unresolved/name fixtures are test data;
no owner save is loaded or normalized. No external/missing asset requests or JS
errors were seen. Screenshots exposed sticky-header overlap; the anchor offset
was corrected and heading hit tests plus the complete matrix passed again.

CI captures 20 unmodified viewport images and four full-component images with
hashed receipts under `source_audit_reports/equipment-ui/`. Only for the tall
component captures, the fixed bottom toolbar is hidden through Playwright's
screenshot style so it cannot cover the middle of the component image. This is
explicit in the receipt; unmodified viewport captures show the actual browser
chrome/layout. Neither form proves physical-device behavior.

The complete 52-command UI source preflight passes. Existing source guards now
include the fifth portrait-helper call site (Equipment), and the location test
isolates its own IIFE before applying its presentation-only assertions instead
of accidentally inspecting later modules. The legacy portrait test still checks
its existing 12 valid/broken/empty browser scenarios. Existing location previews,
squad editor, Training feedback, Unit Box detail controls and active counts pass
against the combined prepared candidate. These source/test adjustments do not
change game data or broaden the existing location module's allowed behavior.

Fresh exact-head GitHub source and Android CI plus independent Codex review are
required before normal merge. Actual Android rendering, owner phone acceptance,
complete equipment functionality and original UI parity remain unverified.
Preserve existing APKs and saves; no install or public release is authorized.
