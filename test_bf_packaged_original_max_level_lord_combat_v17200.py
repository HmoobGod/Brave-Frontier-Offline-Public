"""v172: signed APK includes original source Lord max-level endpoint bridge."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
src=(A/'bf17200_original_max_level_lord_combat.js').read_bytes()
bridge=(A/'bf11100_original_starter_leader_combat.js').read_bytes()
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert src.count(b'BF_GLOBAL_ORIGINAL_MAX_LEVEL_LORD_COMBAT_V17200')==1
assert b'BFGlobalOriginalMaxLevelLordV17200?.apply?.(unit,i)' in bridge
assert java.index('readPackagedText("bf11600_original_lord_stats_reference.js")')<java.index(
 'readPackagedText("bf17200_original_max_level_lord_combat.js")')<java.index(
 'readPackagedText("bf16900_optional_imp_fusion.js")')
assert not any(x in src for x in (b'saveProgress(',b'localStorage',b'P.unitExp=',b'P.roster=',b'Math.random',b'fetch('))
g=(R/'app/build.gradle').read_text('utf8')
assert any("versionName '"+str(v)+".00.0-demo'" in g for v in range(172,200))
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert z.read('assets/bf17200_original_max_level_lord_combat.js')==src
 assert z.read('assets/bf11100_original_starter_leader_combat.js')==bridge
 html=z.read('assets/index.html')
 assert b'bf_global_offline_demo_v7' in html
 assert b'_bfGemV170Custom' in html and b'_bfImpsV171' in html
 assert b'party:Array.from({length:6},(_,i)=>playerUnit(i))' in html
 assert b'BF_GLOBAL_ORIGINAL_MAX_LEVEL_LORD_COMBAT_V17200' in src
print('PASS v172: signed original max-level Lord endpoint, stable Android identity, v170 Gems and v171 Imp save retained')
