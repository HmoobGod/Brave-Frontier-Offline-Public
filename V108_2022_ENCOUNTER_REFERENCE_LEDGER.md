# v108 — Brave Frontier Global 2022 Mission Reference Recovery

Parent: v107 original landed-hit source audit (merged to main; a successful main CI run is a separate gate).

## Original evidence recovered, without mechanic guesses

The 2022 \`F_MISSION_MST_1_Ver1118.json\` mission master (SHA-256 \`d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83\`) carries an opaque \`MISSION_8f4NYKxb\` serialized field.

- **34 Mistral mission records** from the already bundled v56 original raw archive.
- **36 Morgan mission records** from v80 original 2022 quest dataset.
- **70 exact mission references** and **31 distinct opaque right-hand tokens** across both regions.
- Each source pair is preserved as \`opaqueLabel:opaqueRef\` *text*. Their numeric meaning is **unknown**, so the ledger does not interpret those as wave placements, enemies, encounter odds, animation IDs or AI scripts.
- Source-only read UI under the Global Quest Journal shows the exact raw token field for each mission. No gameplay state, inventory, mission clears, enemy waves, RNG, rewards, summon currency or Android save changes.

## Why this matters

Research can now cross-reference repeated source tokens across quests without accidentally treating raw serialized references as decoded native enemy wave formations. The v57 Mistral source and v80 Morgan source are checked against the *same* original mission-master SHA-256; corrupt or mismatched data disables this module.

Future v109+ research should locate \`F_BATTLE_MST\`/mission group maps and verify how these opaque references resolve, with exact version/hash joins, before adjusting gameplay.

## Gates

- Browser validates the actual checked-in 70-record source JSON, all 31 tokens, malformed rejection, re-injection safety, UI visibility, and v7 save integrity.
- Signed APK verifies the independently bundled v108 module, Android identity and no network permission.
- Original enemy AI, overkill, pickup recipient, actual mission formations and rewards are still unreconstructed.
- Device installation and gameplay still require direct Android verification; feature CI alone does not certify them.
