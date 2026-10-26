"""v64 package includes the source-backed demo status remedy UI without changing signer/save."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 names=z.namelist()
 assert 'assets/bf6400_status_remedy_command.js' in names
 js=z.read('assets/bf6400_status_remedy_command.js').decode('utf8')
 assert 'BF_GLOBAL_STATUS_REMEDY_COMMAND_V6400' in js
 assert 'ail.cure(targetId,itemId)' in js
 assert all(s not in js for s in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert j.index('readPackagedText("bf6200_injury_attack.js")')<j.index('readPackagedText("bf6400_status_remedy_command.js")')
gradle=(R/'app/build.gradle').read_text('utf8')
v=[line.strip() for line in gradle.splitlines() if line.strip().startswith('versionName ')]
assert len(v)==1 and v[0].split("'")[1].endswith('.00.0-demo')
assert int(v[0].split("'")[1].split('.')[0])>=64
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v64 original-source cure scopes, offline signed APK, v7 save identity')
