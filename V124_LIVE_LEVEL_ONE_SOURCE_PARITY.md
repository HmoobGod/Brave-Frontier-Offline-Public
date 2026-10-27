# v124 — 2022 Global level-one live combat parity regression

The original owner's `mst-decoded.zip` SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9` contains source-exact `unitBaseHp/Atk/Def/Rec` values. These are the **level-one** stat fields for the 72 original Global unit forms already implemented in the offline reconstruction.

## Purpose

Before migrating native EXP or level-dependent growth, lock down what the current playable battle constructor actually does at level one, not merely what is shown in the source archive or in the squad reference panel.

`test_bf_live_level_one_2022_parity_v12400.py` runs **after all unit-preparation scripts** on the APK-bound `app/src/main/assets/index.html`. It requires exactly 18 recruitable bases and 54 evolved forms; matches all 72 effective form IDs and base stat blocks against the separately authenticated v116 source JSON; then calls the actual `playerUnit(0)` battle constructor for every form in headless Chromium with temporary, zero-EXP test state. Every observed HP/maxHP/ATK/DEF/REC must match the original level-one values. The test restores its temporary state and verifies unchanged `P.version === 7`, `bf_global_offline_demo_v7` storage, and the existing DEMO EXP thresholds.

This is an automated **fidelity and regression gate**, not a new playable unit, unit-type assignment, native growth formula, original XP threshold implementation or save migration. Intermediate levels still use DEMO growth, and source-max Lord endpoints remain read-only until exact 2022 native rules are established.

## Safety / maintenance

The patch adds only this test, one GitHub Actions test invocation, and this documentation file. No `index.html`, original assets, Android source, signing, saved units, or gameplay code is modified. Fail closed if the prepared APK catalog diverges from authenticated 2022 source: **do not make a fake interpolation to pass the test**.

Relevant blockers remain #25, #27, #29, #31. Authentic 2022 EXP patterns, intermediate level stat growth, and non-Lord type behavior still require version-specific evidence.
