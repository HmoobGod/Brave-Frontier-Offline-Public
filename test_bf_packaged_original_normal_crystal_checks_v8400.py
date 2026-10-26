"""v84 2258 original unit normal-drop profiles in signed offline APK."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 names=z.namelist()
 assert 'assets/bf8400_original_normal_crystal_checks.js' in names
 js=z.read('assets/bf8400_original_normal_crystal_checks.js').decode('utf8')
 assert 'BF_GLOBAL_FULL_NORMAL_CRYSTAL_CHECKS_V8400' in js
 assert 'profileCount:2258,excludedSourceRows:32' in js
 assert "if(fnv(packed)!=='690fb10d')return;" in js
 assert len(js.encode('utf8'))<65536
 assert all(s not in js for s in ('localStorage','saveProgress(', 'BFAndroid'))
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf8300_original_burst_crystal_checks.js")')<java.index('readPackagedText("bf8400_original_normal_crystal_checks.js")')
g=(R/'app/build.gradle').read_text('utf8')
version=[s.strip() for s in g.splitlines() if s.strip().startswith('versionName ')]
assert len(version)==1 and int(version[0].split("'")[1].split('.')[0])>=84
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v84 2258 original source normal profiles packaged, Android signed offline, v7 saves unchanged')