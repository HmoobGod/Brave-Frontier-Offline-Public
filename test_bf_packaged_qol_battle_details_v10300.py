"""v103 APK includes live battle metrics, preserving original app and save."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 data=z.read('assets/bf10300_qol_battle_details.js').decode('utf8')
 assert 'BF_GLOBAL_QOL_BATTLE_DETAILS_V10300' in data
 assert 'sourceScopedCriticalHits' in data
 assert 'assets/bf10200_qol_unit_flags.js' in z.namelist()
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf10200_qol_unit_flags.js")')<java.index('readPackagedText("bf10300_qol_battle_details.js")')
g=(R/'app/build.gradle').read_text('utf8')
assert any("versionName '"+str(v)+".00.0-demo'" in g for v in range(103,200))
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v103 packaged read-only HUD with stable signing and v7')
