# Brave Frontier Global 2.00.0-demo — Archive Trials

Based on the independently successful v1.50 Build #160. The **original
2022 Global storyline and existing 106 playable DEMO missions** are left
unchanged. Android application ID, debug signing identity, v7 local save,
roster, progress, replay navigation and old asset sets are preserved.

## v2.00 additions
Recovered 17 more **historical 2014** Global parsed mission encounter files
(on top of four already audited in v1.20). Total research-only coverage:
21 early Mistral/Morgan missions, 112 wave groups, 264 enemy slots,
42 distinct enemy IDs. Each file is held locally and records its original
upstream Git SHA from https://github.com/cheahjs/bravefrontier_data.

The Quest page now offers an *optional* Archive Trials section: per-wave
historical enemy names, original parsed HP/ATK/DEF, optional 2022 encyclopedia
thumbnails when linked by matching numeric unit ID, and a playable training
sandbox for currently unlocked missions.

**Training is a deliberately separate and synthetic practice exercise:**
fixed practice squad HP, invented neutral attack/Guard/Burst/healing math
clearly labeled, enemy replies using a simple synthetic calculation.
Practice never uses actual player units or the native battle state. It is
memory-only, saves no results, costs no energy, and grants no game EXP, Zel,
Karma, units, drops, or mission clears. It is explicitly **NOT** original
Brave Frontier 2022 battle reconstruction.

Historical English mission-title matches alone DO NOT verify the same
enemy formations, spawn probabilities or damage existed in 2022.
No original 2022 enemy AI, drop chances, damage, summon rates, original
cutscenes or post-St. Lamia continents are represented as restored.

## Verification gates
The deterministic build-time preparer requires the exact 21 record IDs and
provenance SHAs and the 112/264/42 summary. It does not use the network.
The resulting self-contained WebView asset is bounded below 64KiB and
must pass browser action-isolation and APK packaging checks along with
all existing regressions. Android device installation remains a separate
step requiring user verification after GitHub CI succeeds.

**Save warning:** Export your current save before in-place APK installation.
Do not uninstall, clear app storage, or replace the project's existing
development signing key.
