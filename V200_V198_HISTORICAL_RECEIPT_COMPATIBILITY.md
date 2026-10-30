# v200 — Protect historical v198 offline Gem purchases against future recruit-ID changes

**Status:** read-only historical save compatibility regression. This is not a
summon banner, original 2022 unit economy, new playable unit, wallet migration,
or Android gameplay patch.

## Provenance (real source baseline, not guessed IDs)

The merged v198 `main` commit
`e40924d7b54960ff0ca4d685835c84b5e33ac18a` contains HTML Git blob
`4ef5f1a1a4c3c0817828f29c0646a51a98843c77`. Its literal
`window.BF_STARTER_UNITS` JSON contains the following historical unit IDs.
The HTML defines six `STARTER_IDS` and `RECRUIT_IDS=STARTERS.slice(6)`.

- Original six **DEMO starter IDs**: `10011, 20011, 30011, 40011, 50011, 60011`.
- Historical **DEMO summonable IDs**: `10021, 20021, 30021, 40021, 50021, 60021,
  10041, 20041, 30041, 40041, 50041, 60041`.

These 12 IDs are **not** original 2022 Global Gem banner units/rates. The
source pins the **checked-in merged v198** unit definitions, rather than
pretending this list was extracted from an Actions build artifact or the
user's actual Android save.

Previously a test could only prove that units purchased during the current
test session still appeared in the current roster. That test could pass even
if a future build silently removed a previously purchasable unit ID.

## New files and checks

- `source_data/bf_v198_recruit_id_compat_baseline_v200.json` preserves the
  historical ID list plus its original Git blob and v198 commit provenance.
- `test_bf_v198_recruit_save_compat_v20000.py` checks that **all** twelve
  historical purchased IDs are still members of `RECRUIT_IDS`,
  `ALL_IDS`, and `UNIT_BY_ID`, and that all six starters retain their
  starter classification. Future additions are allowed, but removals,
  renumbering, or reclassification of existing IDs fail CI until a deliberate
  save migration is independently reviewed.
- The test takes the existing **synthetic signed-v124 save fixture**
  (`source_data/bf165_real_signed_v124_first_clear_save.json`) and constructs
  a **synthetic** schema-2 purchased-wallet state with two frozen old IDs,
  1,000 earned PERSONAL OFFLINE Gems, 200 spent and 800 remaining. It verifies
  the real current `parseProgress` accepts it, preserves the six-unit squad
  and original Gem ledger, and persists/reloads it through the exact canonical
  `bf_global_offline_demo_v7` save key.
- It subsequently awards a 100-Gem *PERSONAL OFFLINE* finale first clear for
  mission 23, then a +1 replay, and confirms both survive parser validation.
  This tests the previous Claude W6 coverage gap. It does **not** change the
  original source-based Global Gem ledger.
- Tests are registered in GitHub Actions after the v198.02 checks.

**Not tested:** This is *not* an archival production-save fixture from a
specific owner's real Android gameplay. No device or WebView was tested.
Building an earlier APK and playing over this newer purchased state remains
unsafe. Before installing an APK on the owner's device, back up via
`Download Save File` **and** `EXPORT CURRENT SAVE`.

## Change boundary / release gate

Only a public compact JSON, Python CI regression and this research doc plus
one workflow line are modified. No `app/src`, Java, Gradle, signing material,
unit assets, original combat mechanics, Gem spending, Imp state, save parser,
save schema, or stored player data are changed. The prior V198 warning can now
distinguish this **fixed historical ID pin** from more complex original 2022
formation/AI evidence gaps.

Require exact-head green Actions CI then a clean SHA-guarded merge and a fresh
merged-main Actions result. Because the patch does not alter runtime, Claude
review is not required to merge the read-only test, but **future changes to
RECRUIT_IDS, purchase semantics or the save validator require independent
review** and device compatibility testing.
