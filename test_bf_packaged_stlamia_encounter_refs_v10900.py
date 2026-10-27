"""v109 signed APK has St. Lamia source extension with stable Android identity."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 file='assets/bf10900_stlamia_encounter_refs.js'
 assert file in z.namelist()
 src=z.read(file).decode('utf8')
 assert 'BF_GLOBAL_2022_STLAMIA_ENCOUNTER_REFERENCE_EXTENSION_V10900' in src
 assert 'nativeEnemyIdsKnown:false' in src
 assert 'nativeWaveIdentitiesKnown:false' in src
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf10800_2022_encounter_reference_ledger.js")')<java.index('readPackagedText("bf10900_stlamia_encounter_refs.js")')
g=(R/'app/build.gradle').read_text('utf8')
assert any("versionName '"+str(v)+".00.0-demo'" in g for v in range(109,200))
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v109 packaged original 106-mission source refs, Android identity and v7 save')
