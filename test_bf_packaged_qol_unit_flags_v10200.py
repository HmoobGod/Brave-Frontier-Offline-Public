"""v102 signed APK packages owned-unit markers and preserves original identity."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 data=z.read('assets/bf10200_qol_unit_flags.js').decode('utf8')
 assert data.count('BF_GLOBAL_QOL_UNIT_FLAGS_V10200')==1
 assert 'advisoryOnly:true' in data
 assert 'assets/bf10100_qol_viewed_dialogue.js' in z.namelist()
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf10100_qol_viewed_dialogue.js")')<java.index('readPackagedText("bf10200_qol_unit_flags.js")')
g=(R/'app/build.gradle').read_text('utf8')
assert any("versionName '"+str(v)+".00.0-demo'" in g for v in range(102,200))
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v102 packaged unit markers; signing, v7 and package unchanged')
