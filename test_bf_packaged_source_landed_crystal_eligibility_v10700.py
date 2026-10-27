"""v107 APK includes the source-bound landed-hit crystal eligibility audit."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 path='assets/bf10700_source_landed_crystal_eligibility.js'
 assert path in z.namelist()
 src=z.read(path).decode('utf8')
 assert src.count('BF_GLOBAL_ORIGINAL_LANDED_CRYSTAL_ELIGIBILITY_V10700')==1
 assert 'source.lookup(event.unitId)' in src
 assert 'const eligibleBCChecks=landed*profile.checksPerHit' in src
 assert 'nativePickupNotImplemented:true' in src
 assert 'Math.random' not in src and 'saveProgress(' not in src
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf9500_multihit_critical_combat.js")')<java.index('readPackagedText("bf10700_source_landed_crystal_eligibility.js")')
gradle=(R/'app/build.gradle').read_text('utf8')
assert "versionName '107.00.0-demo'" in gradle
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v107 signed APK source-hit eligibility, unchanged signing, package and v7 save')
