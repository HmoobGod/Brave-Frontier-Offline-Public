"""v169: packaged optional original Imp effects and canonical save isolation."""
from pathlib import Path
from zipfile import ZipFile
from hashlib import sha256
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
source=(A/'bf16900_optional_imp_fusion.js').read_bytes()
bridge=(A/'bf11100_original_starter_leader_combat.js').read_text('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf_global_unit_archive.js")') < java.index(
 'readPackagedText("bf16900_optional_imp_fusion.js")')
assert java.index('readPackagedText("bf16800_original_level_one_lord_combat.js")') < java.index(
 'readPackagedText("bf16900_optional_imp_fusion.js")')
assert bridge.index('BFGlobalOriginalLevelOneLordV16800?.apply?.(unit,i)')<bridge.index(
 'BFGlobalOptionalImpsV16900?.apply?.(unit,i)')<bridge.index('return apply(unit,i);')
assert not any(x in source.decode('utf8') for x in (
 'saveProgress(', 'P.unitExp=', 'P.roster=', 'P.questClears=', 'awardDemoRewards(', 'Math.random','fetch('))
g=(R/'app/build.gradle').read_text('utf8')
assert "versionName '169.00.0-demo'" in g
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
    path='assets/bf16900_optional_imp_fusion.js'
    assert path in z.namelist()
    assert sha256(z.read(path)).digest()==sha256(source).digest()
    assert b'BF_GLOBAL_OPTIONAL_IMP_FUSION_V16900' in z.read(path)
    assert b'bf_global_offline_optional_imps_v169' in z.read(path)
    assert b'bf_global_offline_demo_v7' in z.read('assets/index.html')
    assert b'BFGlobalOptionalImpsV16900?.apply?.(unit,i)' in z.read(
      'assets/bf11100_original_starter_leader_combat.js')
    assert b'function playerUnit(i){' in z.read('assets/index.html')
    assert b'party:Array.from({length:6},(_,i)=>playerUnit(i))' in z.read('assets/index.html')
print('PASS v169 optional original Imp gains, +25% cap, earned Arton supply, signed APK, v7 identity/save untouched')
