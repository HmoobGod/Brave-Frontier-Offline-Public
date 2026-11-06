# Source-backed single-ally DEF +50% item

Makes archived item #20601 usable through the existing DEF-item command. The
selector defaults to the existing +30% item #20600. Players may choose +50%
instead; both choices share the existing one temporary DEMO charge per battle.
No items, Zel, Gems or ownership are granted, consumed or persisted.

Two committed source records contain #20601, original name 堅牢薬,
effect group 410, target type/area 1, skill type 5 and parameters
`0,0,50,0,0,3`: one ally DEF +50% for three turns. See the immutable v4900 evidence
and v5100 compressed battle-item effect catalog. No canonical English name, shop
price, enemy drop, native inventory or RNG is invented. This does not complete
original inventory/equipment reconstruction.

The shared `file` and `sha256` on profiles #20600 and #20601 identify the
**complete** `3-mst-translated/F_ITEM_MST_Ver1027.json` table, SHA-256
`0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474`.
They are not per-item digests. The committed v4900 evidence lists both rows
under that single table-level provenance. The regression pins that identity
and compares both live profiles against it; the independent effect catalog
separately corroborates #20601's exact tuple. The private archive was not
freshly downloaded or rehashed for this clarification.

The existing DEMO interpretation remains authoritative: current battle DEF is
rounded with Math.round(baseDEF*1.5), actor uses Guard and reserves its turn,
cast turn counts in the three-round window, stronger/party DEF effects cannot
stack, and exact base DEF is restored on expiration. Those timings, rounding,
stock and stacking are DEMO behavior, not a claim of native-client equivalence.
Legacy two-argument useDefItem calls and the source property retain #20600;
new optional third argument accepts only integer #20600/#20601. The selected
profile and active-buff source IDs are exposed for testing. New battles reset
selection to #20600. Auto, busy, finished battle and invalid actor/recipient
restrictions are unchanged. No P or storage writing API is added.

New source and four-width browser regression verifies source parity, strict IDs,
blocked phases, the real selector/action wiring, shared charge/Guard/turn locks,
mutual exclusion with existing double/party DEF, duration and exact restore.
Weakness now reads the supported +50% item metadata rather than assuming +30%;
+50% and the existing -50% penalty cancel to base DEF, with live DEF restored
after the enemy callback. Existing +30/+100/party cases keep their prior rules.
A deterministic synthetic party/enemy fixture runs the actual existing DEMO
enemy phase before/after the buff and observes reduced damage. Entire synthetic
P and storage bytes/write count remain identical. This is not native damage,
physical Android or actual owner-save acceptance. The test temporarily restricts
living targets and resets the existing engine seed to compare two real enemy
phases fairly; no native damage formula is inferred. Existing v49/v52/v53/v61
regressions must also pass, plus fresh signed Android CI and independent review.

Preserve signing, package ID, original source assets/data, v7 schema, existing
APKs, authentic saves and custom Gem/Imp behavior. Keep this gameplay candidate
isolated from unmerged dependencies; no install or release is authorized.

Local evidence, November 5, 2026: all 63 source-preparation steps passed in a
disposable copy. The new four-width source/actual-DEMO-enemy-phase regression
passed, including source profile parity, defaults, metadata, phase/ID rejections,
charge/Guard/exclusion, Weakness subtractive calculation and exact expiry.
Legacy v49 single DEF, v52 double DEF, v53 party DEF and v61 Weakness browser
regressions all passed. Node syntax and git diff checks passed. An initial test
fixture assumed the engine would target party slot 3; the assertion failed. The
fixture now restricts eligible targets and resets the existing engine seed;
it does not replace the enemy engine. Fresh GitHub source/full Android CI and
separate independent review remain pending at publication.
