# v1.20: historical encounter records

2014 Global parsed battle records were recovered from https://github.com/cheahjs/bravefrontier_data for Missions 1, 2, 10, and 20. They provide 16 wave groups and 33 historical enemy entries with names, unit identifiers, HP, ATK, DEF and AI reference numbers. Exact source file paths and immutable Git blob hashes are recorded in the JSON fixture.

These historical 2014 encounters ARE NOT verified as original 2022 Global formations. No join between 2022 opaque MISSION_8f4NYKxb tokens and 2014 parsed encounters has been established. Sprite links, original AI implementations, drops and native combat calculations are not verified. The new in-game panel is completely read-only. Battle engine, rewards and save v7 remain unchanged.

Future v1.30–v1.50 research: validate cross-era encounter mappings and native spawn data; restore battle mechanics only where independently supported. Preserve app ID, signing key, save schema v7 and source-vs-DEMO clarity.
