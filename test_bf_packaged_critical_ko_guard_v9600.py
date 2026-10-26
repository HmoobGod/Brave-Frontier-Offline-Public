"""v96 signed APK: post-KO strike suppression, stable package and save contract."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 src=z.read('assets/bf9500_multihit_critical_combat.js').decode('utf8')
 assert 'V9600_OVERKILL_GUARD' in src
 assert 'const landed=damage>0&&remaining>0;' in src
 assert 'const critical=landed&&roll()===true;' in src
 assert 'appliedDamage' in src
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
gradle=(R/'app/build.gradle').read_text('utf8')
assert "versionName '96.00.0-demo'" in gradle
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf9300_single_hit_critical_combat.js")')<java.index('readPackagedText("bf9500_multihit_critical_combat.js")')
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v96 signed APK has post-KO critical guard, original identity/signing and v7 save')
