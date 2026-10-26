# Brave Frontier Global v71.00 — Original Ten-Level ATK Support Brave Bursts

Parent: v70.00 original Blessing Light source correction, containing v69 elemental combat and v68 healing skill-level preview. Requires exact green CI for v70 and v71; never promote unverified. No promotion until exact v71 GitHub Actions success and signed debug APK upload.

The 2022 archived Global F_SKILL_LEVEL_MST_1_Ver1487.json, checked in as source_data/bf_global_original_bb_support_v029.json, contains exact Lv1–10 ATK buff parameters for two source-known skills: Thunder's Command (skill 40021, effect 1300, +30/+31/+32/+33/+34/+35/+36/+37/+38/+40%) and Thunder's Rage (40022, effect 1600, +40/+41/+42/+43/+44/+45/+46/+47/+48/+50%). Both have the source 3-turn duration. There is no need to approximate percentages.

The optional v71 module reads the existing battle-only level preview from v68; without a requested level (default 1), the original v29 Lv1 party boost remains completely unchanged. A guarded post-preparation patch replaces only the source support skill percent used during the already simulated ATK buff branch. The optional module is allowed to be absent, falling back to old values. No saved BB level, new leveling currency, default Auto Battle behavior, native stacking, inventory or enemy AI is invented.

Tests verify all 20 source rows, source display, Lv10 real party boost, one-at-a-time effects, no unit base-ATK mutation, cross-feature v67 heals and v69 elemental combat, reset, training isolation, v7 save compatibility and original APK signing/offline manifest.