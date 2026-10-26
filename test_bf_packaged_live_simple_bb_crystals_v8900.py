"""v89 original-source simple BB event module packaged in same offline APK and v7 save."""
from pathlib import Path
from zipfile import ZipFile
R=Path(__file__).resolve().parent
with ZipFile(R/'app/build/outputs/apk/debug/app-debug.apk') as z:
 assert 'assets/bf8900_live_simple_bb_crystals.js' in z.namelist()
 js=z.read('assets/bf8900_live_simple_bb_crystals.js').decode('utf8')
 assert js.count('BF_GLOBAL_LIVE_SIMPLE_BB_CRYSTAL_EVENTS_V8900')==1
 assert 'source.rollPerTarget(unitId,{overkill:false,random:Math.random})' in js
 assert 'bf_global_offline_demo_v7' in z.read('assets/index.html').decode('utf8')
 assert len(js.encode('utf8'))<65536
 assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid','fetch('))
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert java.index('readPackagedText("bf8500_original_all_bb_checks.js")')<java.index('readPackagedText("bf8900_live_simple_bb_crystals.js")')
g=(R/'app/build.gradle').read_text('utf8')
v=[x.strip() for x in g.splitlines() if x.strip().startswith('versionName ')]
assert len(v)==1 and int(v[0].split("'")[1].split('.')[0])>=89
assert "applicationId 'org.bravefrontier.offline'" in g
assert 'bf-development-debug.keystore' in g
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v89 source BB live reference event in signed offline APK, v7 save unchanged')
