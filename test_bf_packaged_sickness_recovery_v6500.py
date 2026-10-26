"""v65 packaged Sickness REC modifier, exact signer and save preservation."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert 'assets/bf6500_sickness_recovery.js' in z.namelist()
 js=z.read('assets/bf6500_sickness_recovery.js').decode('utf8')
 assert 'BF_GLOBAL_SICKNESS_RECOVERY_V6500' in js
 assert 'penaltyPercent:50' in js and 'statusCode:3' in js
 assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert j.index('readPackagedText("bf6400_status_remedy_command.js")')<j.index('readPackagedText("bf6500_sickness_recovery.js")')
g=(R/'app/build.gradle').read_text('utf8')
v=[line.strip() for line in g.splitlines() if line.strip().startswith('versionName ')]
assert len(v)==1 and v[0].split("'")[1].endswith('.00.0-demo')
assert int(v[0].split("'")[1].split('.')[0])>=65
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v65 Sickness source identity / REC modifier and signed offline v7 package')
