"""Verify signed Android artifact includes v95 without changing identity or saves."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 names=set(z.namelist())
 assert 'assets/bf9500_multihit_critical_combat.js' in names
 assert 'assets/bf9300_single_hit_critical_combat.js' in names
 src=z.read('assets/bf9500_multihit_critical_combat.js').decode('utf8')
 assert src.count('BF_GLOBAL_MULTIHIT_CRITICAL_COMBAT_V9500')==1
 assert 'window.splitDemoDamage=function' in src
 assert "local.unit.action?.kind!=='attack'" in src
 assert 'bf9500-critical-banner' in src
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text()
assert java.index('readPackagedText("bf9300_single_hit_critical_combat.js")')<java.index('readPackagedText("bf9500_multihit_critical_combat.js")')
gradle=(R/'app/build.gradle').read_text()
assert "versionName '95.00.0-demo'" in gradle
assert "applicationId 'org.bravefrontier.offline'" in gradle
assert 'bf-development-debug.keystore' in gradle
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text()
print('PASS v95 packaged source-backed multihit criticals; signing/package/save unchanged')
