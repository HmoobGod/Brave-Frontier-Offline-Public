"""v112 original 2022 72-unit leader research is packaged but does not change combat."""
from pathlib import Path
from zipfile import ZipFile
from hashlib import sha256
R=Path(__file__).resolve().parent
src=(R/'app/src/main/assets/bf11200_all_playable_leader_source.js').read_bytes()
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 name='assets/bf11200_all_playable_leader_source.js'
 assert name in z.namelist()
 blob=z.read(name)
 assert sha256(blob).digest()==sha256(src).digest()
 assert b'BF_GLOBAL_ALL_PLAYABLE_LEADER_SOURCE_V11200' in blob
 assert b'byId.size!==72' in blob
 assert b'combatChanges:false' in blob
 assert b'localStorage' not in blob and b'saveProgress(' not in blob
 assert b'bf_global_offline_demo_v7' in z.read('assets/index.html')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf11100_original_starter_leader_combat.js")')<java.index('readPackagedText("bf11200_all_playable_leader_source.js")')
g=(R/'app/build.gradle').read_text('utf8')
assert any("versionName '"+str(v)+".00.0-demo'" in g for v in range(112,200))
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v112 packaged all 72 original Global 2022 leader sources, Android signing and schema v7')
