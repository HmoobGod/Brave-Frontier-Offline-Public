"""v83 packaged source BB/SBB crystal check reference and offline/signing identity."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 names=z.namelist()
 assert 'assets/bf8300_original_burst_crystal_checks.js' in names
 js=z.read('assets/bf8300_original_burst_crystal_checks.js').decode('utf8')
 assert js.count('BF_GLOBAL_SOURCE_BURST_CRYSTAL_CHECKS_V8300')==1
 assert 'bbProfiles:71,sbbProfiles:12,simpleDamageGroups:61,offensiveSimpleGroups:48' in js
 assert 'unknownComplexDamageGroups:events===null' in js
 assert 'nonOffensiveEffect:events!==null&&!isOffensiveDamage' in js
 assert all(s not in js for s in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf8100_original_crystal_drop_core.js")')<java.index('readPackagedText("bf8200_original_normal_crystal_checks.js")')<java.index('readPackagedText("bf8300_original_burst_crystal_checks.js")')
g=(R/'app/build.gradle').read_text('utf8')
versions=[x.strip() for x in g.splitlines() if x.strip().startswith('versionName ')]
assert len(versions)==1 and int(versions[0].split("'")[1].split('.')[0])>=83
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v83 BB/SBB original source checks packaged read-only, signed and offline with v7 saves')
