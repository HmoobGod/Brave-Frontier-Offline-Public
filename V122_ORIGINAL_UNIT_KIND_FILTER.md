# v122 — Original Global unit-kind archive filter fidelity

The owner's verified 2022 Global F_UNIT_MST_1/2 source has 2,291 records: 2,164 records carry original unitKind 0, and 127 records carry a nonzero kind code (1=40, 2=55, 3=5, and 27 other records). This is a source-code category, not proof that every nonzero record is a material.

Previously, the encyclopedia's Special/material filter only matched kind 1, thus hiding 87 other nonzero-kind records under that filter. The selector now reads Other original kind codes and correctly includes all 127 records.

Independent 2022 source digest of sorted [unitId,unitKind] pairs: 0843acff8014d1b06f22004a61b2757b03ebb1d081c96a125265cecd8af9dbb2. Source: user's mst-decoded.zip SHA256 69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9. The Python/Chromium regression exercises all original kinds, UI filter totals, and no save writes.

Archive only: no live unit ownership, battle, level calculation, data change, Java/signing change, or v7 save migration.
