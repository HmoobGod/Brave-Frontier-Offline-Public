"""v67 packaged source-backed recipient REC for original Lv1 heal BBs."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert 'assets/bf6700_burst_recipient_rec.js' in z.namelist()
 js=z.read('assets/bf6700_burst_recipient_rec.js').decode('utf8')
 assert 'BF_GLOBAL_BURST_RECIPIENT_RECOVERY_V6700' in js
 assert 'Math.round(ally.rec)' in js
 index=z.read('assets/index.html').decode('utf8')
 assert index.count('BFGlobalBurstRecipientRecoveryV6700?.healAmount(base,ally)')==1
 assert 'bf_global_offline_demo_v7' in index
j=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert 'readPackagedText("bf6700_burst_recipient_rec.js")' in j
g=(R/'app/build.gradle').read_text('utf8')
versions=[s.strip() for s in g.splitlines() if s.strip().startswith('versionName ')]
assert len(versions)==1
version=versions[0].split("'")[1]
assert version.endswith('.00.0-demo') and int(version.split('.')[0])>=67
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v67 source-recipient REC heal, signed Android/v7 save/offline compatibility')
