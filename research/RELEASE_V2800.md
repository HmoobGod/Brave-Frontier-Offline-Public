# v28.00 — Authentic Script-driven Dialogue Speaker Cues

Baseline: v27.00 original 2022 scene backgrounds and v26.00 source event portraits.

Original `BF1_event_part001.zip` event-script `PARAM,id=2,param=chrN_*` tags were scanned immediately before each original `MSGDRAW` for all 20 supported original Mistral/Morgan/St. Lamia dungeon scripts. Frame counts match the already bundled original 2022 Global dialogue text for every supported scene. Source codes 1/2/3 identify the corresponding original art families Tilith/Karl/Seria, respectively. The exact 20 source sequences are embedded read-only.

The scene reader now automatically uses the appropriate already-packaged *neutral* 2022 character illustration as the dialogue advances. Character selection never triggers save or combat changes. This is not recreation of exact per-line facial expressions or original cutscene animation timing; those remain unimplemented. Cave of Malice is excluded as before.

Full source test checks Morgan Karl→Seria→Karl transition and St Lamia Tilith→Seria. APK test asserts 2022 script/map/portrait layers, unchanged offline package/signing, v7 saves and 64KiB Android script cap.
