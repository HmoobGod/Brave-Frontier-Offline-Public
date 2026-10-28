"""v168 Android signing and original-source level-one Lord gameplay guard."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
bridge=(R/'app/src/main/assets/bf11100_original_starter_leader_combat.js').read_text('utf8')
assert 'BFGlobalOriginalLevelOneLordV16800?.apply?.(unit,i)' in bridge
assert java.index('readPackagedText("bf11600_original_lord_stats_reference.js")')<java.index(
 'readPackagedText("bf16800_original_level_one_lord_combat.js")')
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 paths=set(z.namelist())
 assert 'assets/bf16800_original_level_one_lord_combat.js' in paths
 assert 'assets/bf11600_original_lord_stats_data.js' in paths
 assert 'assets/bf11600_original_lord_stats_reference.js' in paths
 script=z.read('assets/bf16800_original_level_one_lord_combat.js').decode('utf8')
 assert 'BF_GLOBAL_ORIGINAL_LEVEL1_LORD_COMBAT_V16800' in script
 assert "unit.level!==1" in script
 assert "(P.unitExp?.[unit.baseId]??0)!==0" in script
 assert 'originalMidlevelStatsApplied:false' in script
 assert 'originalTypeRollsApplied:false' in script
 assert 'saveFieldsAdded:0' in script
 assert 'BFGlobalOriginalLevelOneLordV16800?.apply?.(unit,i)' in z.read(
    'assets/bf11100_original_starter_leader_combat.js').decode('utf8')
 assert not any(t in script for t in ('saveProgress(', 'localStorage', 'P.unitExp=', 'P.roster='))
 html=z.read('assets/index.html').decode('utf8')
 assert "bf_global_offline_demo_v7" in html
 assert 'function playerUnit(i){' in html
 assert 'party:Array.from({length:6},(_,i)=>playerUnit(i))' in html
 g=(R/'app/build.gradle').read_text('utf8')
 assert "applicationId 'org.bravefrontier.offline'" in g
 assert 'bf-development-debug.keystore' in g
 assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v168 signed APK exact 2022 zero-EXP Lord base stat bridge; no midlevel invention or save compatibility changes')
