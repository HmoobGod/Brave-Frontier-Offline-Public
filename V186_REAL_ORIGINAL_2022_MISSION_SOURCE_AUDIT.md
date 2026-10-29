# v186 — Real owner-verified 2022 Global encounter source scan executed

**New evidence (not just synthetic CI):** The user's original private `mst-decoded.zip`, SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`, was present in the local working environment on October 29, 2026. Its original translated `F_MISSION_MST_1_Ver1118.json` was independently verified at SHA256 `d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83`.

The actual original archive—**not a fake fixture**—was scanned locally, across **both original 2022 translated mission master parts**, plus **145 other translated F_ tables**. The summary-only evidence is checked in at `source_data/bf_global_verified_original_2022_mission_reference_scan_v186.json`. The private source ZIP itself, raw mission rows, user details, and even example opaque reference tokens are **not uploaded**.

The 3,433 mission-master rows include 3,306 nonempty format-valid opaque encounter references and **327 distinct full strings**. Outside the mission masters, exact matches occur in only two translated tables: 294 rows in `F_GRAND_MISSION_SPOT_MST_Ver92.json` (128 matched strings), and 315 rows in `F_RAID_POINT_MST_Ver57.json` (94 matched strings). The entire scan had **zero oversized or non-array tables skipped**. Both match only the opaque mission reference field `MISSION_8f4NYKxb`, not source enemy IDs/wave formations. An identical reference token can be shared by many missions, and must not be treated as an original 2022 formation key without independent decoder evidence.

**This did not decode any native 2022 enemy roster, position, boss AI, 2022 battle sprite assignment or loot/drop schedule.** It does not inspect runtime server state or unparsed binary DAT content; absence of a join in translated F_ tables is not proof that original formations are unrecoverable.

To reproduce locally, run `python audit_bf_real_original_2022_sources_v18600.py --archive "/private/mst-decoded.zip" --output "/private/real-2022-audit.json"`. It verifies the full original archive SHA before parsing and refuses other files. CI runs `test_bf_original_real_2022_source_v18600.py` against the authenticated report plus synthetic negative probes; **CI does not have the private ZIP and does not rerun the authentic private-source scan**.

**No app effect:** This is source research only. No original game mechanics, battle code, app assets, Android signing/permissions, player unit roster, original drops, Gem/Imp state, or save key `bf_global_offline_demo_v7` are touched.

**Claude review:** Not required to retain the audit. Required before any inferred original 2022 formation, boss AI, drop rate or historical art is activated, and before the proposed read-only Android image integration. The downloaded private `mst-decoded.zip` is not committed to public GitHub.
