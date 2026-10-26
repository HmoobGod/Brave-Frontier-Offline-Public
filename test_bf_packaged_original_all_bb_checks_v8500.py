"""v85 all original source BB drop counts packaged safe in signed Android."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 js=z.read('assets/bf8500_original_all_bb_checks.js').decode('utf8')
 assert 'BF_GLOBAL_ALL_BB_DROP_CHECKS_V8500' in js
 assert 'joinedBBProfiles:2125,missingBBSkillLinks:133,offensiveSingleGroups:213' in js
 assert "if(fnv(packed)!=='3ee23008')return;" in js
 assert len(js.encode('utf8'))<65536
 assert all(s not in js for s in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf8400_original_normal_crystal_checks.js")')<java.index('readPackagedText("bf8500_original_all_bb_checks.js")')
g=(R/'app/build.gradle').read_text('utf8')
version=[s.strip() for s in g.splitlines() if s.strip().startswith('versionName ')]
assert len(version)==1 and int(version[0].split("'")[1].split('.')[0])>=85
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v85 2125 original BB checks read-only in signed offline APK with v7 saves')