"""v111 signed APK contains verified 2022 starter leader bridge without save changes."""
from pathlib import Path
from zipfile import ZipFile
from hashlib import sha256
R=Path(__file__).resolve().parent
path='assets/bf11100_original_starter_leader_combat.js'
src=(R/'app/src/main/assets/bf11100_original_starter_leader_combat.js').read_bytes()
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert path in z.namelist()
 packaged=z.read(path)
 assert sha256(packaged).digest()==sha256(src).digest()
 assert b'BF_GLOBAL_ORIGINAL_STARTER_LEADER_COMBAT_V11100' in packaged
 assert b'baseStatsAndDamageFormulaStillDemo:true' in packaged
 assert b'nativeRoundingVerified:false' in packaged
 assert b'localStorage' not in packaged and b'saveProgress(' not in packaged
 assert b'bf_global_offline_demo_v7' in z.read('assets/index.html')
 assert sha256(z.read('assets/index.html')).digest()==sha256((R/'app/src/main/assets/index.html').read_bytes()).digest()
 assert b'function playerUnit(i){' in z.read('assets/index.html')
 assert b'party:Array.from({length:6},(_,i)=>playerUnit(i))' in z.read('assets/index.html')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf11000_source_starter_leader_skills.js")')<java.index('readPackagedText("bf11100_original_starter_leader_combat.js")')
g=(R/'app/build.gradle').read_text('utf8')
assert "versionName '111.00.0-demo'" in g
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v111 source leader APK, exact core, Android signing identity, schema v7')
