# Brave Frontier Global v51.00 — Original Double-ATK Battle Item

Baseline: v50.00 Build #262 success, commit `1f6237ada3b30cdbfe051682fd5c9add09ad9afe`. The original 2022 translated item table in `mst-decoded.zip` supplies item #50401 (強撃薬), group 400, itemTargetArea=1 (one ally), passiveSkillInfo `0,100,0,0,0,3`. Its description explicitly says **double one ally's ATK for three turns**. These are source-backed. Existing #50400 all-ally +50%, #20400 +30% one ally, and all other recovered original content remain intact.

Optional v51 battle command selects a live actor and one living active beneficiary with less than +100% existing ATK boost, sets `ally.atkBuff={pct:100,untilRound:S.round+2}`, and uses the existing `currentAtkBoost`/`effectivePlayerAtk` combat path. It upgrades a weaker active item boost and never affects a KO target or an ally already at +100%. No changes to the original damage formula. Actor's Guard is reserved by v45, and v48's Auto safety is maintained.

**Still DEMO-only:** single temporary item charge per battle, actor Guard turn cost, enhancement replacement priority, cast-turn counted in three rounds, item equipment and inventory absent from persistence. No save schema or storage key changes.

Verification: original metadata, single-target and KO restriction, upgrading a +50% buff, natural expiration, battle damage path, blocked cross-item action double-spend, save-byte isolation, training reset, inherited regression suites and Android APK/identity checks. Signed debug APK still uses existing key. Only an exact green CI commit is releasable. Physical Android device testing remains separate.
