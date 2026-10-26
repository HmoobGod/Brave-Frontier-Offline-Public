"""v90 signed APK source-ledger preservation and packaging checks."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert 'assets/bf9000_live_crystal_provenance.js' in z.namelist()
 js=z.read('assets/bf9000_live_crystal_provenance.js').decode()
 assert len(js.encode())<65536
 assert js.count('BF_GLOBAL_LIVE_CRYSTAL_PROVENANCE_V9000')==1
 assert all(v not in js for v in ('localStorage','saveProgress(', 'BFAndroid','fetch('))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode()
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text()
assert java.index('readPackagedText("bf8900_live_simple_bb_crystals.js")')<java.index('readPackagedText("bf9000_live_crystal_provenance.js")')
g=(R/'app/build.gradle').read_text()
assert any("versionName '"+str(v)+".00.0-demo'" in g for v in range(90,200)), "v90+ app version required"
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text()
print('PASS v90 signed offline APK carries reference ledger; save/signing/app ID unchanged')
