"""v114 original Global English leader names/descriptions signed APK gate."""
from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile
R=Path(__file__).resolve().parent
path='assets/bf11400_original_global_leader_english.js'
source=(R/'app/src/main/assets/bf11400_original_global_leader_english.js').read_bytes()
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert path in z.namelist()
 blob=z.read(path)
 assert sha256(blob).digest()==sha256(source).digest()
 assert b'BF_GLOBAL_ORIGINAL_LEADER_ENGLISH_V11400' in blob
 assert b'combatChanges:false' in blob and b'savedFieldsAdded:0' in blob
 assert b'localStorage' not in blob and b'saveProgress(' not in blob
 assert b'bf_global_offline_demo_v7' in z.read('assets/index.html')
 assert sha256(z.read('assets/index.html')).digest()==sha256((R/'app/src/main/assets/index.html').read_bytes()).digest()
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf11300_all_playable_leader_recipients.js")')<java.index('readPackagedText("bf11400_original_global_leader_english.js")')
g=(R/'app/build.gradle').read_text('utf8')
assert any("versionName '"+str(v)+".00.0-demo'" in g for v in range(114,200))
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v114 byte-accurate original Global English 36 LS APK, original signing and v7')
