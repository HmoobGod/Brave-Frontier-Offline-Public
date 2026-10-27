# v123 — Source-authenticated original Global Imp bonus caps (archive reference)

The owner's original 2022 Global `mst-decoded.zip` SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9` includes the original `unitImpCaps` four-number field in every one of 2,291 unique `F_UNIT_MST_1/2_Ver1084.json` unit rows.

Read-only archive mapping of `[unitId, Imp HP, Imp ATK, Imp DEF, Imp REC]` sorted by original unit ID has independently source-derived SHA256 `3ab0bc3efaf968dd1959490f892dbfde01c5cad882b0bd3377ee98362c3375de`. All values fit unsigned 16-bit integers; 147 distinct bonus-cap tuples cover 2,291 forms (129 tuples are all zero). Compact lookup: 2,291 bytes of indices and 147 eight-byte big-endian tuples, with pinned SHA256 digests `99d6b3476f1c3ded0335de55b449eba44fa511624861c1693bfc35ae70d8149c` and `40ea95d51f6433bf2bd3cb9a3aebb6403445cb3f8bfeafd3ff1eb420517a1518`.

Sample source rows: unit 10011 has HP +400, ATK +160, DEF +80, REC +80; unit 10017 has +2200/+880/+460/+460; unit 10025 has +1000/+240/+560/+400.

The existing encyclopedia details can display these archived cap numbers only. **This does not mean that native Imp enhancement, stat growth, or numeric unit EXP was implemented.** It changes no original archive records, live demo combat stats, unit ownership, v7 saves, progression thresholds, RNG, Android package/signing, or storage schema. It introduces a fail-closed optional lookup attached to the already packaged archive viewer; no new Java or Android loaders.

`test_bf_original_imp_caps_v12300.py` validates 2,291 original IDs, packed binary contents against independent 2022 source digests, browser lookups and detail text, and unchanged local save storage. Future Imp feeding/stat migration requires separate original-game mechanics and compatibility verification; this source reference does not authorize game-state mutation.
