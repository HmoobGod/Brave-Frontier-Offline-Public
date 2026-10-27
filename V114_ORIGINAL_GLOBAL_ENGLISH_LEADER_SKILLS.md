# v114 — Authentic Global English Leader Skill Descriptions

## Original archived sources
Owner's `BF1_sgtext_part001.zip` SHA256 `4dccce4eeb6a89cc0cf5718badff7af95046c891882e42c05c6eaca81f9d6285`, distinct from the decoded 2022 F_UNIT/F_LEADER master archive. Nested `sgtext_leaderSkillName_411.zip` and `sgtext_leaderSkillDescription_497.zip` (original base64 UTF-8 CSV) supply the original Global English second-field translations. Nested ZIP SHA256s and all 36 original `MST_LEADERSKILLS_<id>_NAME/DESCRIPTION` pairs are preserved in the JSON source manifest.

### Important noninterchangeable mechanics in original text
- LS #500/502/504/506/508/510: 10% incoming damage reduction from the named element; **no source-verified elemental attack identity** exists for current simulated enemies, so live mitigation remains unimplemented.
- #1300–1303: bonus damage during **Spark**, NOT ordinary ATK.
- #1400–1402: bonus Battle Crystals produced during **Spark**, NOT Spark damage.
- #1313 and #1314: Spark damage plus original critical damage and potential DEF-ignore respectively.
- #1410/1411/1412: Spark-generated BC bonuses with distinct reduction in required BB gauge, reduction in consumed BB gauge, or enhanced BB fill rate. Preserve these wording differences without guessing numeric proc rules.

## What changes
- Add the exact original English localized leader names/descriptions to the existing v112 72-playable-form selector and a clearly-labeled original English description area.
- v111/v113 original starter type2 stat bonuses remain live and unchanged. Spark timing/BC distribution, enemy elemental mitigation, native damage calculation, other passives and unresolved compound groups remain **not implemented**.
- UI/source read-only; original P.version=7, original signed package identity, quests, saves and training remain unchanged.

## Verification
36 original records, strict source hash checks, exact embedded JS / source JSON equality, stable 72 form mapping, browser test for live/raw distinction, idempotent UI and no save writes. Signed APK checks exact module bytes/loader order and Android signing/no-Internet invariants.
