"""v108 signed Android APK bundles exact read-only 2022 encounter reference ledger."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 file='assets/bf10800_2022_encounter_reference_ledger.js'
 assert file in z.namelist()
 src=z.read(file).decode('utf8')
 assert 'BF_GLOBAL_2022_ENCOUNTER_REFERENCE_LEDGER_V10800' in src
 assert 'nativeEnemyIdsKnown:false' in src and 'meaningDecoded:false' in src
 assert 'localStorage' not in src and 'saveProgress(' not in src
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf10700_source_landed_crystal_eligibility.js")')<java.index('readPackagedText("bf10800_2022_encounter_reference_ledger.js")')
gradle=(R/'app/build.gradle').read_text('utf8')
assert any("versionName '"+str(v)+".00.0-demo'" in gradle for v in range(108,200))
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v108 original encounter-reference ledger, unchanged v7 save, Android package and signing')
