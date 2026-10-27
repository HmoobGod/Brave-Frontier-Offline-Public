"""v113 source-qualified type2 leader bonuses extend to all playable recipients."""
from pathlib import Path
from zipfile import ZipFile
from hashlib import sha256
R=Path(__file__).resolve().parent
asset=R/'app/src/main/assets/bf11300_all_playable_leader_recipients.js'
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 name='assets/'+asset.name
 assert name in z.namelist()
 blob=z.read(name)
 assert sha256(blob).digest()==sha256(asset.read_bytes()).digest()
 assert b'BF_GLOBAL_SOURCE_ALL_PLAYABLE_LEADER_RECIPIENTS_V11300' in blob
 assert b'originalLeaderTypes31Or5Activated:false' in blob
 assert b'recipientLeaderSkillActivated:false' in blob
 assert b'window.playerUnit=function(i)' in blob
 assert b'localStorage' not in blob and b'saveProgress(' not in blob
 assert b'bf_global_offline_demo_v7' in z.read('assets/index.html')
 assert sha256(z.read('assets/index.html')).digest()==sha256(
   (R/'app/src/main/assets/index.html').read_bytes()).digest()
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf11100_original_starter_leader_combat.js")')<java.index('readPackagedText("bf11200_all_playable_leader_source.js")')<java.index('readPackagedText("bf11300_all_playable_leader_recipients.js")')
g=(R/'app/build.gradle').read_text('utf8')
assert any("versionName '"+str(v)+".00.0-demo'" in g for v in range(113,200))
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v113 source-backed 72-form recipient bonuses APK, prepared core, unchanged signing and v7')
